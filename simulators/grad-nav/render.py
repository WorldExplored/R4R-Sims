"""Native Gaussian scene diagnostics and direct dynamics-to-render coupling."""
import argparse, copy, hashlib, importlib.util, json, os, sys, time, datetime, subprocess
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['a','d']);p.add_argument('--upstream',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    import torch, numpy as np, yaml
    from PIL import Image
    from scipy.spatial.transform import Rotation
    torch.manual_seed(0);torch.set_num_threads(2)
    out=a.out;out.mkdir(parents=True,exist_ok=True);(out/'frames').mkdir(exist_ok=True)
    sys.path.insert(0,str(a.upstream))
    from utils.gs_local import GS, pose2nerf_transform
    deps=Path.home()/'grad-nav-deps'
    scene=deps/'scenes/gs_data/sv_1007_gate_mid/splatfacto/2024-10-07_145741'
    original=scene/'config.yml'
    cfg=yaml.load(original.read_text(),Loader=yaml.Loader)
    cfg.data=scene/'data';cfg.pipeline.datamanager.data=scene/'data';cfg.pipeline.datamanager.dataparser.data=scene/'data'
    cfg.load_dir=scene/'nerfstudio_models'
    cfg.output_dir=scene.parents[2]
    resolved=out/'resolved-config.yml';resolved.write_text(yaml.dump(cfg))
    gs=GS(resolved,res=0.4);camera=gs.camera_out;device=gs.device
    dp=gs.pipeline.datamanager.train_dataparser_outputs
    dp_info={'dataparser_transform':dp.dataparser_transform.cpu().tolist(),'dataparser_scale':float(dp.dataparser_scale),
       'original_config':str(original),'resolved_config':str(resolved),'scene_path':str(scene),'step':gs.pipeline.model.step,
       'gaussian_count':len(gs.pipeline.model.means),'camera_fx_fy_cx_cy':[float(camera.fx.item()),float(camera.fy.item()),float(camera.cx.item()),float(camera.cy.item())],
       'width':int(camera.width.item()),'height':int(camera.height.item()),'camera_convention':'Nerfstudio/OpenGL camera-to-world, x right y up z backward',
       'quaternion_helper':'xyzw','dynamics':'wxyz','rgb_encoding':'clamped model float [0,1]; PNG uint8 quantization without extra gamma; linear radiance not established',
       'depth':'gsplat RGB+ED alpha-normalized expected camera-space axial depth; scene units, no metric calibration',
       'background_depth':'Nerfstudio replaces alpha==0 pixels with max rendered depth, not geometric no-hit truth',
       'scale_status':'dataparser scale recorded; external physical metric calibration not supplied',
       'source_camera_file':str(gs.pipeline.datamanager.eval_dataset.image_filenames[0]),
       'original_camera_intrinsics':[float(gs.camera_ref.fx.item()),float(gs.camera_ref.fy.item()),float(gs.camera_ref.cx.item()),float(gs.camera_ref.cy.item())]}
    (out/'camera_config.json').write_text(json.dumps(dp_info,indent=2)+'\n')
    def sync():torch.cuda.synchronize()
    def save(index,label,rgb,depth,alpha=None):
        rgb=rgb.detach().cpu().numpy();depth=depth.detach().cpu().numpy()
        if not np.isfinite(rgb).all() or not np.isfinite(depth).all():raise ValueError('nonfinite render')
        Image.fromarray((np.clip(rgb,0,1)*255).round().astype('uint8')).save(out/'frames'/f'{index:03d}-{label}.png')
        np.save(out/'frames'/f'{index:03d}-{label}-depth.npy',depth)
        np.save(out/'frames'/f'{index:03d}-{label}-rgb.npy',rgb)
        if alpha is not None:np.save(out/'frames'/f'{index:03d}-{label}-alpha.npy',alpha.detach().cpu().numpy())
        return {'rgb_min':float(rgb.min()),'rgb_max':float(rgb.max()),'depth_min':float(depth.min()),'depth_max':float(depth.max()),'shape':list(rgb.shape)}
    import nerfstudio.models.splatfacto as splat_module
    native_raster=splat_module.rasterization
    last={}
    def audited_raster(*args,**kwargs):
        result=native_raster(*args,**kwargs)
        last.update(render=result[0],alpha=result[1],viewmats=kwargs['viewmats'],K=kwargs['Ks'],mode=kwargs['render_mode'])
        return result
    splat_module.rasterization=audited_raster
    def direct(c2w):
        camera.camera_to_worlds=c2w[None,:3,:].float()
        return gs.pipeline.model.get_outputs_for_camera(camera,obb_box=None)
    if a.mode=='a':
        ref=gs.camera_ref.camera_to_worlds.reshape(-1,3,4)[0].detach().cpu().numpy();ref4=np.eye(4);ref4[:3]=ref
        F=np.diag([1.,-1.,-1.,1.]);M=np.array([[.990,0,.140,.152],[0,1,0,-.031],[-.140,0,.990,-.012],[0,0,0,1.]])
        C=np.array([[0,0,-1,0],[1,0,0,0],[0,-1,0,0],[0,0,0,1.]])
        body=F@ref4@np.linalg.inv(M@C)
        q=Rotation.from_matrix(body[:3,:3]).as_quat()
        R=Rotation.from_quat(q).as_matrix();position=(F@ref4)[:3,3]-R@M[:3,3]
        offsets=[(0,0,0),(.1,0,0),(-.1,0,0),(0,.1,0),(0,-.1,0)]
        rows=[];xs=[]
        for i,offset in enumerate(offsets):
            x=torch.tensor(np.r_[position+np.array(offset)*[1,-1,-1],np.zeros(3),q][None],device=device,dtype=torch.float32)
            c2w=pose2nerf_transform(x[:,:3],x[:,6:10],device)[0]
            rows.append({'pose_id':i,'offset_scene_units':offset,'source':'prior relative offsets, derived from first eval camera',
                'helper_xcr10':x[0].cpu().tolist(),'camera_to_world':c2w.cpu().tolist(),'reference_camera_to_world':ref4.tolist(),
                'body_rotation_orthogonalization':'SciPy Rotation.from_matrix of inverse rounded mount',
                'scene_scale_m_per_unit':None});xs.append(x)
        frozen=Path('/home/ubuntu/R4R-Sims-grad-nav/results/grad-nav/20261009T013743Z-a-b58f3b/reference_route.jsonl')
        old=[json.loads(line) for line in frozen.read_text().splitlines()]
        assert max(np.max(np.abs(np.array(x['camera_to_world'])-np.array(y['camera_to_world']))) for x,y in zip(rows,old)) < 1e-6
        rows=old
        xs=[torch.tensor(row['helper_xcr10'],device=device,dtype=torch.float32)[None] for row in rows]
        dp_info['frozen_route_source']=str(frozen)
        dp_info['frozen_route_sha256']=hashlib.sha256(frozen.read_bytes()).hexdigest()
        (out/'camera_config.json').write_text(json.dumps(dp_info,indent=2)+'\n')
        # Freeze numerical route before first GPU render.
        (out/'reference_route.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        (out/'state.jsonl').write_text('{"applicable":false,"reason":"known-camera render"}\n');(out/'actions.jsonl').write_text('{"applicable":false,"reason":"known-camera render"}\n')
        comparisons=[]
        with (out/'camera_poses.jsonl').open('w') as poses,torch.inference_mode():
            for i,(row,x) in enumerate(zip(rows,xs)):
                d=direct(torch.tensor(row['camera_to_world'],device=device))
                raw_depth=last['render'][0,...,3:4].clone();raw_alpha=last['alpha'][0].clone()
                viewmat=last['viewmats'].clone();K=last['K'].clone()
                dep,rgb=gs.render(x)
                sync();stats=save(i,'direct',d['rgb'],d['depth'],d['accumulation']);save(i,'author',rgb[0],dep[0])
                comp={'pose_id':i,'rgb_max_abs_delta':float((d['rgb']-rgb[0]).abs().max()),'depth_max_abs_delta':float((d['depth']-dep[0]).abs().max()),
                    'camera_transform_max_delta':float((camera.camera_to_worlds[0]-torch.tensor(row['camera_to_world'],device=device)[:3]).abs().max()),**stats,
                    'zero_alpha_fraction':float((d['accumulation']==0).float().mean())}
                alpha=d['accumulation']; mask=alpha>0; zero=~mask
                comp.update(raw_depth_max_abs_delta_nonzero_alpha=float((d['depth'][mask]-raw_depth[mask]).abs().max()) if mask.any() else None,
                    background_depth_equals_raster_max=bool(torch.all(d['depth'][zero]==raw_depth.max())) if zero.any() else None,
                    rgb_background_formula_max_delta=float((d['rgb']-torch.clamp(last['render'][0,...,:3]+(1-alpha)*d['background'],0,1)).abs().max()),
                    raster_mode=last['mode'],alpha_min=float(alpha.min()),alpha_max=float(alpha.max()))
                for name,value in [('raster-depth',raw_depth),('viewmat',viewmat),('K',K)]:np.save(out/'frames'/f'{i:03d}-direct-{name}.npy',value.detach().cpu().numpy())
                comparisons.append(comp);poses.write(json.dumps({**row,**comp})+'\n');poses.flush()
            timing={}
            fixed_c2w=torch.tensor(rows[0]['camera_to_world'],device=device)
            for label in ['direct','author','raw_observation']:
                for _ in range(5):
                    if label=='direct':direct(fixed_c2w)
                    else:gs.render(xs[0])
                sync();torch.cuda.reset_peak_memory_stats();samples=[]
                for _ in range(50):
                    sync();t=time.perf_counter()
                    if label=='direct':d=direct(fixed_c2w)
                    else:dep,rgb=gs.render(xs[0])
                    if label=='raw_observation':dep.cpu();rgb.cpu()
                    sync();samples.append(time.perf_counter()-t)
                timing[label]={'samples':samples,'median_s':float(np.median(samples)),'p95_s':float(np.percentile(samples,95)),
                    'images_per_wall_s':50/sum(samples),'peak_torch_allocated_bytes':torch.cuda.max_memory_allocated(),
                    'peak_torch_reserved_bytes':torch.cuda.max_memory_reserved(),'warmup':5,'measured':50,
                    'includes':'CPU transfer, excludes file writes' if label=='raw_observation' else 'render call, excludes CPU transfer and file writes'}
        (out/'metrics.json').write_text(json.dumps({'comparisons':comparisons,'timing':timing,'complete_learned_observation_timing':'blocked: trained visual projection and CENet unavailable',
            'reference_pose_rounding_max_abs_delta':float(np.max(np.abs(np.array(rows[0]['camera_to_world'])-ref4))),
            'render_dimensions':[dp_info['width'],dp_info['height']],'policy_latency':None,'video_playback_fps':None},indent=2)+'\n')
    else:
        spec=importlib.util.spec_from_file_location('quad',a.upstream/'envs/assets/quadrotor_dynamics_advanced.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        dynamics=module.QuadrotorSimulator(mass=torch.tensor([1.],device=device),max_thrust=torch.tensor([24.],device=device),freq=200.,total_time=.05,rotor_noise_std=0.,br_noise_std=0.)
        pos=torch.tensor([[0.,0.,1.15]],device=device);vel=torch.zeros((1,3),device=device);omega=vel.clone();q=torch.tensor([[1.,0.,0.,0.]],device=device)
        config={'ticks':20,'outer_dt_s':.05,'start_position':[0.,0.,1.15],'setpoint_z':1.25,'controller':'adapter height PD kp2 kd0.8, body rates zero',
            'origin_offset':[-6,0,0],'physical_interpretation':'blocked pending independent metric scale/alignment','bypasses':['native env observations','policy','VAE','CNN','native delay/filter','collision response']}
        (out/'config.json').write_text(json.dumps(config,indent=2)+'\n');(out/'reference_route.jsonl').write_text(json.dumps({'height_setpoint':1.25,'origin':'native gate_mid start and small -0.1 perturbation'})+'\n')
        stats=[];wall0=time.perf_counter()
        def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
        with (out/'state.jsonl').open('w') as states,(out/'actions.jsonl').open('w') as actions,(out/'camera_poses.jsonl').open('w') as poses,torch.inference_mode():
            states.write(json.dumps({'step':0,'sim_time_s':0.,'position_m':pos[0].cpu().tolist(),'velocity_m_s':vel[0].cpu().tolist(),'quaternion_wxyz':q[0].cpu().tolist(),'wall_utc':stamp()})+'\n')
            for i in range(20):
                thrust=max(0.,min(1.,(9.81+2*(1.25-float(pos[0,2]))-.8*float(vel[0,2]))/24.))
                actions.write(json.dumps({'step':i,'sim_time_s':i*.05,'wall_utc':stamp(),'requested_body_rates':[0,0,0],'applied_body_rates':[0,0,0],'requested_normalized_thrust':thrust,'applied_normalized_thrust':thrust})+'\n')
                pos,vel,omega,q,acc,alpha=dynamics.run_simulation(pos,vel,q,omega,(torch.zeros((1,3),device=device),torch.tensor([thrust],device=device)))
                helper_pos=(pos+torch.tensor([[-6.,0.,0.]],device=device))*torch.tensor([[1.,-1.,-1.]],device=device)
                x=torch.cat([helper_pos,torch.zeros((1,3),device=device),q[:,[1,2,3,0]]],dim=1)
                c2w=pose2nerf_transform(x[:,:3],x[:,6:10],device)[0]
                dep,rgb=gs.render(x);sync();s=save(i,'coupled',rgb[0],dep[0])
                row={'step':i+1,'sim_time_s':(i+1)*.05,'wall_since_start_s':time.perf_counter()-wall0,'position_m':pos[0].cpu().tolist(),'velocity_m_s':vel[0].cpu().tolist(),'quaternion_wxyz':q[0].cpu().tolist(),'body_rates_rad_s':omega[0].cpu().tolist(),'wall_utc':stamp()}
                states.write(json.dumps(row)+'\n');poses.write(json.dumps({**row,'camera_to_world':c2w.cpu().tolist(),'helper_xcr10':x[0].cpu().tolist(),'derived_from':'achieved dynamics state','environment_helper_position':helper_pos[0].cpu().tolist(),'origin_offset':[-6,0,0],'environment_axis_flip':[1,-1,-1],'output_frame':f'frames/{i:03d}-coupled.png'})+'\n')
                for f in [states,actions,poses]:f.flush()
                stats.append(s)
        video_cmd=['ffmpeg','-nostdin','-y','-framerate','20','-i',str(out/'frames/%03d-coupled.png'),'-c:v','libx264','-pix_fmt','yuv420p',str(out/'coupled.mp4')]
        (out/'video-command.json').write_text(json.dumps(video_cmd)+'\n')
        subprocess.run(video_cmd,check=True)
        (out/'metrics.json').write_text(json.dumps({'ticks':20,'sim_duration_s':1.,'wall_s':time.perf_counter()-wall0,'initial_z_m':1.15,'final_z_m':float(pos[0,2]),
            'camera_translation_change_z':float(pos[0,2])-1.15,'frame_stats':stats,'causal_path':'action to dynamics to achieved state to mounted camera to GS RGB/depth',
            'physical_metric_alignment':'not independently validated','policy':'none','timing_scope':'integrated with CPU transfers and file writes'},indent=2)+'\n')
    print('completed',a.mode,flush=True)

if __name__=='__main__':main()
