"""CPU-only review of immutable preserved inputs; no simulator/network operations."""
import argparse, hashlib, json, math, re, zipfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def rows(p): return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
def digest(b):return hashlib.sha256(b).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def ranges(a):return {'min':np.min(a,axis=0).tolist(),'max':np.max(a,axis=0).tolist(),'median':np.median(a,axis=0).tolist()}
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 raw=a.root/'artifacts/unreal'; assets=a.root/'third_party/unreal/assets'
 if a.output.resolve().is_relative_to(raw.resolve()) or a.output.resolve().is_relative_to(assets.resolve()):raise ValueError('Output must be outside preserved evidence/inputs')
 a.output.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(assets/'PlyExamples.zip') as z:b=z.read('chinese_vase.ply');entries=z.namelist()
 header,body=b.split(b'end_header\n',1);names=[s.split()[2] for s in header.decode().splitlines() if s.startswith('property float ')]
 data=np.frombuffer(body,dtype='<f4').reshape(-1,len(names)).astype(np.float64)
 def take(ns):return data[:,[names.index(n) for n in ns]]
 pos=take(['x','y','z']);ls=take(['scale_'+str(i) for i in range(3)]);q=take(['rot_'+str(i) for i in range(4)]);dc=take(['f_dc_'+str(i) for i in range(3)]);rest=take(['f_rest_'+str(i) for i in range(45)]);op=take(['opacity']);color=0.28209479177387814*dc+.5;lin=np.where(color<=.04045,color/12.92,np.maximum((color+.055)/1.055,0)**2.4)
 ply={'entry':'chinese_vase.ply','sha256':digest(b),'bytes':len(b),'archive_entries':entries,'header':header.decode()+'end_header\n','vertices':len(data),'properties':names,'all_values_finite':bool(np.isfinite(data).all()),'positions_native':ranges(pos),'log_scale':ranges(ls),'exp_scale_native':ranges(np.exp(ls)),'rot_wxyz':ranges(q),'quaternion_norm':ranges(np.linalg.norm(q,axis=1)),'opacity_logit':ranges(op),'opacity_sigmoid':ranges(1/(1+np.exp(-op))),'dc_sh':ranges(dc),'dc_decoded_color':ranges(color),'importer_srgb_to_linear_color':ranges(lin),'higher_order_sh':ranges(rest),'nonzero_rest_count':int(np.count_nonzero(rest)),'vertices_with_nonzero_rest':int(np.count_nonzero(np.any(rest!=0,axis=1))),'normals':ranges(take(['nx','ny','nz'])),'metric_scale_proven':False,'sample_training_producer_camera_frame':'not recorded'}
 # Static covariance check under canonical producer R diag(s^2) R.T; actual Niagara shader convention unverified.
 def rotation(q):
  q=q/np.linalg.norm(q,axis=1)[:,None];w,x,y,z=q.T;return np.stack([1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y),2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x),2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)],axis=1).reshape(-1,3,3)
 M=np.array([[1,0,0],[0,0,-1],[0,-1,0]]);r=rotation(q);s=np.exp(ls);cov=(r*s[:,None,:]**2)@r.transpose(0,2,1);expected=M@cov@M.T
 qi=q[:,[0,1,3,2]].copy();qi[:,2:]*=-1;ri=rotation(qi);si=s[:,[0,2,1]];actual=(ri*si[:,None,:]**2)@ri.transpose(0,2,1);err=np.linalg.norm(actual-expected,axis=(1,2))/np.maximum(np.linalg.norm(expected,axis=(1,2)),1e-30)
 ply['conditional_covariance_check']={'assumption':'Both consumers use canonical active quaternion R and R diag(s^2) R.T; Niagara consumer not decoded','basis':M.tolist(),'determinant':float(np.linalg.det(M)),'relative_frobenius_error':ranges(err),'fraction_error_gt_1e_6':float((err>1e-6).mean()),'conclusion':'Scalar-first ordering matches canonical 3DGS. Basis-conjugation differs under this assumption; not a confirmed rendering bug.'}
 write(a.output/'ply-review.json',ply)
 B=np.array([[0,0,-1],[0,1,0],[1,0,0]]);assert np.allclose(B.T@B,np.eye(3)) and np.linalg.det(B)==1
 write(a.output/'reference-camera-conversion.json',{'status':'statically derived, not reference-rendered','position_basis_ply_to_ue_cm':(100*M).tolist(),'final_camera_ply_units':[9,0,0],'cv_camera_to_ply_world_rotation_columns_right_down_forward':B.tolist(),'intrinsics_assumed':{'fx':554.2562584220408,'fy':554.2562584220408,'cx':320,'cy':240,'width':640,'height':480},'conventions':'UE local +X forward/+Y right/+Z up; CV local +X right/+Y down/+Z forward; sample metric scale unknown','world_to_cv':'R_cw=R_wc.T; translation=-R_cw@camera_center'})
 ids={'A':'ue-20261008T215319Z-a-5fe9b7c3','B':'ue-20261008T220451Z-b-a3d4be49','yaw':'ue-20261008T232215Z-yaw-6b9a9962','S_route':'ue-20261008T224031Z-s-fe9a3ea3','S_final':'ue-20261008T232833Z-s-light-573e44a0'};pipes={}
 for key,rid in ids.items():
  d=raw/rid;cam=d/('capture-output/camera.jsonl' if key=='S_route' else 'camera.jsonl');row={'run_id':rid,'root':str(d),'run':json.loads((d/'run.json').read_text()),'camera_records':rows(cam)}
  for name in ['reference_route.json','settings.json','collision_baseline.json','diagnostics.json']:
   if (d/name).exists():row[name]=json.loads((d/name).read_text())
  if key=='B':row['waypoint_completions']=[x for x in rows(d/'actions.jsonl') if x['type']=='waypoint_reached']
  if key in ['A','B']:row['preserved_analysis']=json.loads((d/'analysis.json').read_text())
  pipes[key]=row
 write(a.output/'pipelines.json',pipes)
 camera_review={}
 def distance(a,b):return math.sqrt(sum((a[k]-b[k])**2 for k in ['x','y','z']))
 def angle(a,b):
  x=np.array([a[k] for k in ['w','x','y','z']]);y=np.array([b[k] for k in ['w','x','y','z']]);return math.degrees(2*math.acos(min(1,abs(float(x@y)/(np.linalg.norm(x)*np.linalg.norm(y))))))
 for key in ['A','B','yaw']:
  d=raw/ids[key];cams=rows(d/'camera.jsonl');r={'decoded_depth':[]}
  for c in cams:
   idx=c['index'];z=np.load(d/'depth'/f'{idx:04d}.npy',allow_pickle=False);r['decoded_depth'].append({'index':idx,'shape':list(z.shape),'positive_finite_fraction':float((np.isfinite(z)&(z>0)).mean()),'min_m':float(z.min()),'max_m':float(z.max()),'median_m':float(np.median(z))})
  if key=='yaw':
   r['max_requested_rgb_position_error_m']=max(distance(c['requested_pose_ned']['position_ned_m'],c['rgb_capture_pose_ned']['position_ned_m']) for c in cams)
   r['max_requested_rgb_angle_error_deg']=max(angle(c['requested_pose_ned']['orientation_xyzw_ned'],c['rgb_capture_pose_ned']['orientation_wxyz']) for c in cams)
   r['depth_minus_rgb_timestamp_ms']=[(c['depth_timestamp_raw_ns']-c['rgb_timestamp_raw_ns'])/1e6 for c in cams]
   r['max_rgb_depth_angle_error_deg']=max(angle(c['rgb_capture_pose_ned']['orientation_wxyz'],c['depth_capture_pose_ned']['orientation_wxyz']) for c in cams)
   ims=[np.array(Image.open(d/'frames'/f"{c['index']:04d}.png"))[...,:3].astype(np.int16) for c in cams];r['pixel_differences']=[{'indices':[i,j],'mean_absolute_rgb_difference':float(np.abs(ims[i]-ims[j]).mean()),'different_pixel_fraction':float(np.any(ims[i]!=ims[j],axis=2).mean())} for i,j in [(0,1),(1,2),(2,3),(3,4),(0,4)]]
  else:
   r['max_rgb_capture_to_later_camera_info_position_m']=max(distance(c['camera_pose_response_ned']['position_ned_m'],c['camera_info_pose_ned']['position_ned_m']) for c in cams)
   if key=='A':
    target=json.loads((d/'reference_route.json').read_text())['poses_xyz'];r['max_requested_capture_position_error_m']=max(distance(dict(zip(['x','y','z'],t)),c['camera_pose_response_ned']['position_ned_m']) for t,c in zip(target,cams))
    z=np.load(d/'depth/0000.npy');im=np.array(Image.open(d/'frames/0000.png'))[...,:3].astype(float).mean(2);edges=[]
    for x in [100,200,300,400,500]:
     y=int(np.argmax(np.abs(np.diff(z[:,x]))));low=max(y-5,0);high=min(y+6,479);rgb_y=low+int(np.argmax(np.abs(np.diff(im[:,x]))[low:high]));edges.append({'column':x,'strongest_depth_edge_row':y,'local_rgb_edge_row':rgb_y})
    r['first_frame_five_column_edge_check']=edges
  camera_review[key]=r
 write(a.output/'camera-depth-review.json',camera_review)

 rid='ue-20261008T232723Z-land-observed-c1f84706';d=raw/rid;state=rows(d/'state.jsonl');descent=rows(d/'descent.jsonl');hover=[r for r in descent if r['phase']=='hover'];landing=[r for r in descent if r['phase']=='landAsync'];air=next(r for r in descent if r['altitude_above_settled_spawn_ground_m'] is not None and r['altitude_above_settled_spawn_ground_m']>.5 and r['landed_state']==1);contact=next(r for r in landing if r['new_collision_after_spawn_baseline'])
 timeline={'run_id':rid,'actions':rows(d/'actions.jsonl'),'baseline':json.loads((d/'collision_baseline.json').read_text()),'first_airborne_gt_0_5m':air,'hover_height_m':ranges(np.array([r['altitude_above_settled_spawn_ground_m'] for r in hover])),'hover_samples':len(hover),'first_floor_contact_observed':contact,'last':landing[-1],'last_full_state':state[-1],'state_samples':len(state),'descent_samples':len(landing),'peak_descent_down_mps':max(r['vertical_velocity_ned_down_mps'] for r in landing),'descent_rate_median_hz':float(1/np.median(np.diff([r['wall_elapsed_s'] for r in landing]))),'validation':json.loads((d/'validation.json').read_text())};write(a.output/'landing-timeline.json',timeline)
 final=raw/ids['S_final'];stats={};sheet=Image.new('RGB',(1280,540),(242,242,242));draw=ImageDraw.Draw(sheet)
 try:font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
 except OSError:font=ImageFont.load_default()
 for i,name in enumerate(['cube_final.png','splat_final.png']):
  im=Image.open(final/name);im.load();v=np.array(im)[...,:3];mask=v.max(2)>10;ys,xs=np.where(mask);stats[name]={'source':str(final/name),'sha256':digest((final/name).read_bytes()),'shape':list(v.shape),'min':int(v.min()),'max':int(v.max()),'mean_rgb':float(v.mean()),'mean_per_channel':v.mean((0,1)).tolist(),'fraction_any_channel_gt10':float(mask.mean()),'fraction_any_channel_ge250':float((v.max(2)>=250).mean()),'gt10_bbox_xyxy':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]};sheet.paste(im.convert('RGB'),(i*640,60));draw.text((i*640+12,10),'Mesh control (splat still active)' if i==0 else 'Splat only: dark; appearance unvalidated',fill=(20,20,20),font=font)
 sheet.save(a.output/'mesh-splat-contact.png');write(a.output/'image-statistics.json',stats)
 failures=[]
 for d in sorted(raw.glob('ue-*')):
  if not (d/'run.json').exists():failures.append({'run_id':d.name,'files':[p.name for p in d.iterdir()]});continue
  m=json.loads((d/'run.json').read_text());row={'run_id':d.name,'status':m.get('status'),'exit':m.get('exit_status',m.get('render_exit_status')),'errors':m.get('errors',[]),'trace_lines':[]}
  for f in ['console.log','render.log']:
   if (d/f).exists():
    for i,s in enumerate((d/f).read_text(errors='replace').splitlines()):
     if any(k in s for k in ['RuntimeError:','AttributeError:','Traceback (most recent call last)']):row['trace_lines'].append({'file':f,'line':i+1,'text':s})
  failures.append(row)
 write(a.output/'failure-index.json',failures)
 print('Created derived CPU review; raw files unchanged. PLY',len(data),'SH nonzero',ply['nonzero_rest_count'],'quaternion conditional median',float(np.median(err)));print(json.dumps(stats,indent=2))
if __name__=='__main__':main()
