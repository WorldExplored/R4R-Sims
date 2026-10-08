"""Passive capture for the pinned single-episode policy; adds RPC/disk timing cost."""
import json,math,os,time
from pathlib import Path
import numpy as np
from PIL import Image

def v(x): return [float(x.x_val),float(x.y_val),float(x.z_val)]
def q(x): return [float(x.x_val),float(x.y_val),float(x.z_val),float(x.w_val)]
def emit(name,data):
 root=os.environ.get('R4R_RECORD_DIR')
 if root:
  with (Path(root)/name).open('a') as f:f.write(json.dumps(data)+'\n')

def capture_images(client,responses,cameras,rpc_s):
 root=os.environ.get('R4R_CAPTURE_DIR')
 if not root:return
 stamp=time.time_ns();folder=Path(root)/'observations'/str(stamp);folder.mkdir(parents=True)
 times=[int(r.time_stamp) for r in responses]
 for i,name in enumerate(cameras):
  rgb,depth=responses[2*i:2*i+2];info=client.simGetCameraInfo(name)
  rgb_path=folder/f'{name}.png';depth_path=folder/f'{name}_depth_m.npy'
  Image.fromarray(np.frombuffer(rgb.image_data_uint8,np.uint8).reshape(rgb.height,rgb.width,3)).save(rgb_path)
  np.save(depth_path,np.asarray(depth.image_data_float,np.float32).reshape(depth.height,depth.width))
  emit('camera_observations.jsonl',{'sample_id':stamp,'camera':name,'wall_utc_ns':time.time_ns(),
    'image_timestamp_ns':int(rgb.time_stamp),'depth_timestamp_ns':int(depth.time_stamp),
    'timestamp_spread_ns':max(times)-min(times),'position_ned_m':v(rgb.camera_position),
    'orientation_xyzw':q(rgb.camera_orientation),'fov_deg':float(info.fov),
    'width':rgb.width,'height':rgb.height,'projection_matrix':info.proj_mat.matrix,
    'rgb_path':str(rgb_path),'depth_path':str(depth_path),'depth_semantics':'DepthPerspective ray distance metres',
    'rpc_wall_s':rpc_s,'measurement':'instrumented; extra camera-info RPC and disk writes'})

def trace_decision(state,step,model,latency_s,guidance):
 for i,episode_id in enumerate(state.ori_data_dirs):
  if i in state.envs_to_pause:continue
  emit('policy_trace.jsonl',{'step':step,'episode_id':episode_id,'instruction':state.episodes[i][-1]['instruction'],
   'assistant_guidance':guidance[i] if guidance is not None else None,
   'coarse_waypoint':model.last_coarse_waypoints[i].tolist(),
   'refined_waypoints':model.last_refined_waypoints[i].tolist(),'policy_waypoint_latency_s':latency_s,
   'warmup':step==0,'wall_utc':time.time()})

def trace_outcome(state,step,dino_s):
 for i,episode_id in enumerate(state.ori_data_dirs):
  emit('policy_outcomes.jsonl',{'step':step,'episode_id':episode_id,'predicted_stop':bool(state.predict_dones[i]),
   'done':bool(state.dones[i]),'collision':bool(state.collisions[i]),'success':bool(state.success[i]),
   'oracle_success':bool(state.oracle_success[i]),'early_end':bool(state.early_end[i]),
   'goal_distance_m':float(state.distance_to_ends[i][-1]),'dino_latency_s':dino_s,'wall_utc':time.time()})

def terminate(state,step,budget):
 root=os.environ.get('R4R_RECORD_DIR')
 if not root:return
 items=[]
 for i,episode_id in enumerate(state.ori_data_dirs):
  truncated=step>=budget and not state.success[i] and not state.collisions[i] and not (state.oracle_success[i] and state.early_end[i])
  reason='budget_truncation' if truncated else ('success' if state.success[i] else ('collision' if state.collisions[i] else 'task_termination'))
  items.append({'episode_id':episode_id,'learned_decisions':step,'reason':reason,'budget_truncated':bool(truncated),
   'official_evaluation_completed':not bool(truncated),'predicted_stop':bool(state.predict_dones[i]),
   'success':bool(state.success[i]),'oracle_success':bool(state.oracle_success[i])})
 (Path(root)/'termination.json').write_text(json.dumps(items,indent=2)+'\n')
