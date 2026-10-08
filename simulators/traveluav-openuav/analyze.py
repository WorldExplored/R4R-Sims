#!/usr/bin/env python3
"""Validate raw captures and compute geometric/timing evidence, without policy scores."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def rows(p):return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def path_error(points,path):
 a=path[:-1];v=path[1:]-a;den=(v*v).sum(1)
 t=np.clip(((points[:,None,:]-a)*v).sum(2)/np.maximum(den,1e-20),0,1)
 return np.sqrt(((points[:,None,:]-(a+t[:,:,None]*v))**2).sum(2).min(1))
def rot(q):
 x,y,z,w=q;return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def main():
 p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('capture',type=Path);a=p.parse_args();run=a.run;capture=a.capture
 stats=[];errors=[]
 for f in sorted(capture.rglob('*.png')):
  try:
   with Image.open(f) as im:im.load();stats.append({'path':str(f.relative_to(capture)),'kind':'png','shape':[im.height,im.width,len(im.getbands())]})
  except Exception as e:errors.append(f'{f}: {e}')
 for f in sorted(capture.rglob('*.npy')):
  try:
   arr=np.load(f,allow_pickle=False);finite=np.isfinite(arr);valid=finite&(arr>0)&(arr<1e6)
   stats.append({'path':str(f.relative_to(capture)),'kind':'depth','shape':list(arr.shape),'dtype':str(arr.dtype),'finite_count':int(finite.sum()),'invalid_nonfinite_count':int((~finite).sum()),'nonpositive_count':int((finite&(arr<=0)).sum()),'ge_1e6_count':int((finite&(arr>=1e6)).sum()),'min_finite':float(arr[finite].min()) if finite.any() else None,'max_finite':float(arr[finite].max()) if finite.any() else None,'valid_positive_lt_1e6_count':int(valid.sum())})
  except Exception as e:errors.append(f'{f}: {e}')
 for base in [run,capture]:
  for f in base.rglob('*.json'):
   try:json.loads(f.read_text())
   except Exception as e:errors.append(f'{f}: {e}')
  for f in base.rglob('*.jsonl'):
   try:rows(f)
   except Exception as e:errors.append(f'{f}: {e}')
 state=rows(run/'actual_vehicle.jsonl');camera=rows(run/'actual_camera.jsonl');ref=rows(run/'reference_route.jsonl')
 metrics={'validation_errors':errors,'decoded_files':len(stats),'depth_semantics':'DepthPerspective ray distance metres; raw floats retained; previews clamp 0..100 m only','files':stats}
 if camera:
  metrics['camera_dimensions']=sorted(set((c['height'],c['width']) for c in camera));metrics['timestamp_spread_ns_by_sample']={str(c['index']):c['camera_rgb_depth_timestamp_spread_ns'] for c in camera}
  lat={c['index']:c['render_rpc_s'] for c in camera};steady=[v for k,v in lat.items() if k>0]
  metrics['rgb_depth_rpc_wall_s']={'first_batch':lat.get(0),'steady_count':len(steady),'steady_mean':float(np.mean(steady)) if steady else None,'steady_min':min(steady) if steady else None,'steady_max':max(steady) if steady else None,'meaning':'five-camera RGB+depth RPC plus renderer/transport; excludes client file writes; not pure GPU render time'}
 if state:
  pts=np.array([s['position_ned_m'] for s in state]);metrics['state_sample_count']=len(pts);metrics['endpoint_displacement_m']=float(np.linalg.norm(pts[-1]-pts[0]));metrics['achieved_path_length_m']=float(np.linalg.norm(np.diff(pts,axis=0),axis=1).sum())
  wall=np.array([s['wall_s'] for s in state]);sim=np.array([s['sim_timestamp_ns'] for s in state],np.float64)/1e9
  metrics.update(state_wall_span_s=float(wall[-1]-wall[0]),simulation_span_s=float(sim[-1]-sim[0]),requested_sleep_cadence_s=0.2,achieved_wall_interval_mean_s=float(np.diff(wall).mean()) if len(wall)>1 else None,simulator_contact_count=sum(s['collision'] for s in state))
  if ref:
   path=np.array([r['pose']['position'] for r in ref]);err=path_error(pts,path)
   metrics.update(final_endpoint_error_m=float(np.linalg.norm(pts[-1]-path[-1])),point_to_requested_polyline_rmse_m=float(np.sqrt(np.mean(err*err))),point_to_requested_polyline_max_m=float(err.max()),error_weighting='one equal weight per achieved state sample; purely geometric, no timed-reference alignment')
   fig=plt.figure(figsize=(7,5));ax=fig.add_subplot(111,projection='3d');ax.plot(path[:,0],path[:,1],-path[:,2],'o--',label='reference/requested');ax.plot(pts[:,0],pts[:,1],-pts[:,2],'.-',label='achieved');ax.scatter(*[pts[-1,0],pts[-1,1],-pts[-1,2]],marker='X',s=80,label='termination')
   contacts=pts[[s['collision'] for s in state]]
   if len(contacts):ax.scatter(contacts[:,0],contacts[:,1],-contacts[:,2],c='r',marker='x',label='simulator contact')
   for c in camera[::max(1,len(camera)//10)]:
    xyz=np.array(c['position_ned_m']);d=rot(c['orientation_xyzw'])[:,0];ax.quiver(xyz[0],xyz[1],-xyz[2],d[0],d[1],-d[2],length=.5,color='gray')
   ax.set(xlabel='North x (m)',ylabel='East y (m)',zlabel='Height -Down (m)',title=run.name);ax.legend();fig.tight_layout();fig.savefig(run/'trajectory.png',dpi=140);plt.close(fig)
   if run.name.split('-')[-2]=='a':metrics['requested_vehicle_pose_error_m']=[float(np.linalg.norm(np.array(s['position_ned_m'])-path[i])) for i,s in enumerate(state)]
 if camera:
  names=['FrontCamera','LeftCamera','RightCamera','RearCamera','DownCamera'];sheet=Image.new('RGB',(256*5,256*2+40),'white');draw=ImageDraw.Draw(sheet)
  for i,name in enumerate(names):
   c=next(c for c in camera if c['camera']==name)
   rgb=Image.open(c['rgb_path']).convert('RGB').resize((256,256));d=np.load(c['depth_path']);g=np.nan_to_num(np.clip(d/100,0,1),nan=0,posinf=1,neginf=0);gray=Image.fromarray((g*255).astype(np.uint8)).convert('RGB').resize((256,256));sheet.paste(rgb,(i*256,20));sheet.paste(gray,(i*256,276));draw.text((i*256+5,3),name,fill='black')
  draw.text((5,535),'DepthPerspective: fixed 0..100 m grayscale preview; raw arrays preserved',fill='black');sheet.save(capture/'five_view_rgb_depth.png')
 metrics['gpu_wide_memory_mib_samples']=[]
 for line in (run/'gpu-samples.log').read_text().splitlines() if (run/'gpu-samples.log').exists() else []:
  fields=line.split(',')
  if len(fields)>=4:
   try:metrics['gpu_wide_memory_mib_samples'].append(float(fields[2]))
   except ValueError:pass
 if metrics['gpu_wide_memory_mib_samples']:metrics['sampled_gpu_wide_peak_mib']=max(metrics['gpu_wide_memory_mib_samples'])
 (run/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
 (run/'validation.json').write_text(json.dumps({'errors':errors,'decoded_png_depth_files':len(stats),'all_opened':not errors},indent=2)+'\n')
 manifest=[]
 for kind,base in [('record',run),('artifact',capture)]:
  for f in sorted(base.rglob('*')):
   if not f.is_file() or f.name in ['artifact_manifest.json','output-sha256.txt']:continue
   manifest.append({'location':kind,'relative_path':str(f.relative_to(base)),'bytes':f.stat().st_size,'sha256':sha(f)})
 (run/'artifact_manifest.json').write_text(json.dumps({'files':manifest,'remote_records':str(run.resolve()),'remote_artifacts':str(capture.resolve()),'local_verification':'pending transfer'},indent=2)+'\n')
 if errors:raise SystemExit('\n'.join(errors))
 print(json.dumps({k:v for k,v in metrics.items() if k not in ['files','gpu_wide_memory_mib_samples']},indent=2))
if __name__=='__main__':main()
