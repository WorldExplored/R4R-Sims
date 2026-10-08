#!/usr/bin/env python3
"""Route released checkpoint config paths to verified local assets; preserve originals."""
import json,os,shutil,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2];sim=Path(__file__).parent
assets=root/'artifacts/traveluav-openuav/dependencies/assets';upstream=assets.parent/'upstream'
source=assets/'models/llama-uav-7b';runtime=assets/'runtime/llama-uav-7b';runtime.mkdir(parents=True,exist_ok=True)
changes=[]
for f in source.iterdir():
 if not f.is_file():continue
 if f.name in ['config.json','adapter_config.json']:
  before=json.loads(f.read_text());after=dict(before)
  if f.name=='config.json':
   after['mm_vision_tower']=str(assets/'models/LAVIS/eva_vit_g.pth')
   after['image_processor']=str(upstream/'Model/LLaMA-UAV/llamavid/processor/clip-patch14-224')
   if after.get('pretrain_qformer'):after['pretrain_qformer']=str(assets/'models/LAVIS/instruct_blip_vicuna7b_trimmed.pth')
  else:after['base_model_name_or_path']=str(assets/'models/vicuna-7b-v1.5')
  (runtime/f.name).write_text(json.dumps(after,indent=2)+'\n')
  changes.append({'file':f.name,'original':before,'runtime':after,'purpose':'filesystem routing only; architecture/learned parameters unchanged'})
 elif not (runtime/f.name).exists():(runtime/f.name).symlink_to(f)
(assets/'runtime/config-rewrites.json').write_text(json.dumps(changes,indent=2)+'\n')
subprocess.run(['git','-C',str(upstream),'apply','--check',str(sim/'eval_observe.patch')],check=True)
subprocess.run(['git','-C',str(upstream),'apply',str(sim/'eval_observe.patch')],check=True)
print('Runtime paths and instrumented source prepared')
