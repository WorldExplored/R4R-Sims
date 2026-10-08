#!/usr/bin/env python3
import argparse,gc,json,time
from pathlib import Path
import torch
p=argparse.ArgumentParser();p.add_argument('assets',type=Path);p.add_argument('record',type=Path);a=p.parse_args();records=[]
files=[a.assets/'models/llama-uav-7b'/n for n in ['adapter_model.bin','mm_projector.bin','non_lora_trainables.bin']]+[a.assets/'models/traj/model_5.pth',a.assets/'models/groundingdino_swint_ogc.pth',a.assets/'models/LAVIS/eva_vit_g.pth',a.assets/'models/LAVIS/instruct_blip_vicuna7b_trimmed.pth']
for f in files:
 start=time.monotonic();weights=torch.load(f,map_location='cpu');weights=weights.get('model',weights) if isinstance(weights,dict) else weights
 if not isinstance(weights,dict):raise RuntimeError('Unexpected checkpoint schema '+str(f))
 tensors={k:v for k,v in weights.items() if isinstance(v,torch.Tensor)}
 if not tensors:raise RuntimeError('No tensors in '+str(f))
 records.append({'path':str(f),'tensor_key_count':len(tensors),'dtype_counts':{dtype:sum(str(t.dtype)==dtype for t in tensors.values()) for dtype in sorted(set(str(t.dtype) for t in tensors.values()))},'tensor_elements':sum(t.numel() for t in tensors.values()),'representative_keys':[{ 'key':k,'shape':list(v.shape)} for k,v in list(tensors.items())[:8]],'cpu_load_wall_s':time.monotonic()-start})
 a.record.write_text(json.dumps({'status':'checkpoint_files_parsed','runtime_module_eligibility':'separate gates in eval_observe.patch','checkpoints':records},indent=2)+'\n')
 del tensors,weights;gc.collect()
print(a.record)
