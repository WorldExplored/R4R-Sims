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
  data=dict(data);data.setdefault('wall_utc',time.time())
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
  emit('camera_observations.jsonl',{'sample_id':stamp,'camera_batch_views':len(cameras),'camera':name,'wall_utc_ns':time.time_ns(),
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


def observe_state(state,imu):
    last=getattr(observe_state,"last",0)
    now=time.monotonic()
    if now-last>=0.2:
        observe_state.last=now
        emit("actual_vehicle.jsonl",{"wall_monotonic_s":now,"wall_utc":time.time(),"source":"raw unpadded controller sample","state":state,"imu":imu})

def input_contract(inputs,targets,rotations):
    emit("model_inputs.jsonl",{"wall_utc":time.time(),"known_target_positions_ned_m":[np.asarray(t).tolist() for t in targets],
      "target_frame_rotations":[np.asarray(r).tolist() if r is not None else None for r in rotations],
      "input_ids":inputs["input_ids"].detach().cpu().tolist(),
      "prompts":inputs.get("prompts"),"historys":[x.detach().cpu().tolist() for x in inputs.get("historys",[])],
      "images":[{"shape":list(x.shape),"dtype":str(x.dtype),"device":str(x.device)} for x in inputs.get("images",[])],
      "privileged_input":"known target orients history frame; GT assistant retained"})

def load_result(label,module,weights,result):
    known=set(module.state_dict());matched=sorted(known&set(weights))
    emit("checkpoint_loads.jsonl",{"label":label,"checkpoint_key_count":len(weights),"matched_key_count":len(matched),
      "matched_keys":matched,"missing_keys":list(result.missing_keys),"unexpected_keys":list(result.unexpected_keys)})
    allowed_unused = {"label_enc.weight", "bert.embeddings.position_ids"} if label == "detector" else set()
    if label in ["non_lora", "mm_projector"]:
        allowed_unused = {"base_model.model.waypoints_predictor."+k for k in ["weight_ih","weight_hh","bias_ih","bias_hh"]} | {"base_model.model."+module+"."+layer+"."+kind for module in ["is_help_predictor","history_predictor"] for layer in ["0","2"] for kind in ["weight","bias"]}
        required_core = {"base_model.model."+name for name in ["waypoint_emb.weight","waypoints_fc.0.weight","waypoints_fc.0.bias","waypoints_fc.2.weight","waypoints_fc.2.bias","waypoints_output.weight","waypoints_output.bias","history_preprocessor.0.weight","history_preprocessor.0.bias","history_preprocessor.2.weight","history_preprocessor.2.bias","model.embed_tokens.weight"]}
        if not required_core.issubset(matched):raise RuntimeError("Missing required learned waypoint/history/embedding modules")
    unknown = set(result.unexpected_keys) - allowed_unused
    required_missing = set(result.missing_keys) & set(dict(module.named_parameters()))
    emit("checkpoint_gate.jsonl", {"label":label, "allowed_unused_keys":sorted(set(result.unexpected_keys)&allowed_unused), "unknown_keys":sorted(unknown), "missing_learned_parameters":sorted(required_missing) if label in ["trajectory","detector"] else "partial checkpoint; base/adapter provide other modules"})
    if not matched or unknown or (label in ["trajectory","detector"] and required_missing):
        raise RuntimeError("Checkpoint eligibility gate failed for "+label)

def placement(model):
    import torch
    params=list(model.parameters())
    emit("model_placement.jsonl",{"dtypes":sorted(set(str(p.dtype) for p in params)),"devices":sorted(set(str(p.device) for p in params)),
      "parameter_count":sum(p.numel() for p in params),"cuda_allocated_bytes":torch.cuda.memory_allocated(),
      "cuda_reserved_bytes":torch.cuda.memory_reserved(),"cuda_max_allocated_bytes":torch.cuda.max_memory_allocated(),
      "scope":"this Python process; allocator excludes UE and non-PyTorch allocations"})


def verify_lora(model,path):
    import torch
    from peft import get_peft_model_state_dict
    actual=get_peft_model_state_dict(model)
    saved=torch.load(Path(path)/"adapter_model.bin",map_location="cpu")
    missing=sorted(set(saved)-set(actual));different=[]
    for key,tensor in saved.items():
        if key in actual and not torch.equal(actual[key].detach().cpu(),tensor.to(dtype=actual[key].dtype)):different.append(key)
    emit("checkpoint_loads.jsonl",{"label":"LoRA exact tensor comparison after dtype conversion","saved_keys":len(saved),"actual_keys":len(actual),"missing_keys":missing,"different_keys":different})
    if missing or different:raise RuntimeError("Released LoRA tensor verification failed")
