"""Bounded scene-frame/background diagnostics; does not replace frozen A route."""
import argparse,json,sys
from pathlib import Path
def main():
 p=argparse.ArgumentParser();p.add_argument('mode');p.add_argument('--upstream',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 import numpy as np,torch
 from PIL import Image
 from nerfstudio.data.utils.colmap_parsing_utils import read_images_binary
 sys.path.insert(0,str(a.upstream));from utils.gs_local import GS
 out=a.out;(out/'frames').mkdir(exist_ok=True)
 scene=Path('/home/ubuntu/grad-nav-deps/scenes/gs_data/sv_1007_gate_mid/splatfacto/2024-10-07_145741')
 cfg=Path('/home/ubuntu/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T020714Z-a-1004f1/resolved-config.yml')
 gs=GS(cfg,res=.4);device=gs.device
 import nerfstudio.models.splatfacto as sm
 raster=sm.rasterization;last={}
 def capture(*args,**kwargs):
  r=raster(*args,**kwargs);last.update(raw=r[0],alpha=r[1],viewmat=kwargs['viewmats'],K=kwargs['Ks']);return r
 sm.rasterization=capture
 data=json.loads((scene/'data/transforms.json').read_text())
 im=next(x for x in read_images_binary(scene/'data/colmap/sparse/0/images.bin').values() if x.name=='frame_00010.png')
 w=np.eye(4);w[:3,:3]=im.qvec2rotmat();w[:3,3]=im.tvec;c=np.linalg.inv(w);c[:3,1:3]*=-1;c=c[[0,2,1,3],:];c[2]*=-1
 source=next(x['transform_matrix'] for x in data['frames'] if '00010' in x['file_path'])
 cpfile=next((scene/'data/camera_paths').glob('*.json'));cp=json.loads(cpfile.read_text())
 saved=np.array(cp['camera_path'][0]['camera_to_world']).reshape(4,4)
 empty=np.eye(4);empty[:3,3]=[0,0,-1000]
 diagnostics={'colmap_to_saved_pose_max_delta':float(np.max(np.abs(c-np.array(source)))),'training_dataparser_record':json.loads((scene/'dataparser_transforms.json').read_text()),'loaded_dataparser_transform':gs.pipeline.datamanager.train_dataparser_outputs.dataparser_transform.cpu().tolist(),'scene_camera_path':str(cpfile),'scene_camera_path_fov_deg':cp['camera_path'][0]['fov'],'scale_m_per_scene_unit':None,'policy':'none','renders':[]}
 poses=[]
 with torch.inference_mode():
  for index,(label,pose) in enumerate([('source-pose-original-K',c),('released-camera-path-hardcoded-K',saved),('no-hit-background',empty)]):
   camera=gs.camera_out
   if index==0:
    camera=gs.camera_ref.reshape((1,));camera.rescale_output_resolution(.2)
   camera.camera_to_worlds=torch.tensor(pose[None,:3,:],device=device,dtype=torch.float32)
   d=gs.pipeline.model.get_outputs_for_camera(camera);torch.cuda.synchronize()
   rgb=d['rgb'].cpu().numpy();dep=d['depth'].cpu().numpy();alpha=d['accumulation'].cpu().numpy();raw=last['raw'][0].cpu().numpy()
   Image.fromarray((rgb*255).round().astype('uint8')).save(out/'frames'/f'{index:03d}-{label}.png')
   for name,val in [('rgb',rgb),('depth',dep),('alpha',alpha),('raster',raw)]:np.save(out/'frames'/f'{index:03d}-{label}-{name}.npy',val)
   zero=alpha==0
   diagnostics['renders'].append({'label':label,'shape':list(rgb.shape),'rgb_range':[float(rgb.min()),float(rgb.max())],'depth_range':[float(dep.min()),float(dep.max())],'zero_alpha_fraction':float(zero.mean()),'zero_alpha_depth_equals_raw_max':bool(np.all(dep[zero]==raw[...,3:4].max())) if zero.any() else None,'background_rgb_max_delta':float(np.max(np.abs(rgb[zero[...,0]]-d['background'].cpu().numpy()[zero[...,0]]))) if zero.any() else None})
   poses.append({'label':label,'camera_to_world':pose.tolist(),'K':camera.get_intrinsics_matrices().cpu().tolist(),'frame':f'frames/{index:03d}-{label}.png','status':'diagnostic, not frozen A route'})
 (out/'camera_poses.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in poses));(out/'diagnostics.json').write_text(json.dumps(diagnostics,indent=2)+'\n')
 print('scene diagnostics complete')
if __name__=='__main__':main()
