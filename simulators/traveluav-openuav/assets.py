#!/usr/bin/env python3
"""Fetch only pinned smoke assets; verify by path, never manifest line position."""
import argparse, hashlib, json, os, time, urllib.request
from pathlib import Path
from huggingface_hub import HfApi, snapshot_download

ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/'artifacts/traveluav-openuav/dependencies/assets'
EXPECTED={line.split(None,1)[1].strip().removeprefix('assets/'):line.split()[0] for line in (Path(__file__).parent/'expected-sha256.txt').read_text().splitlines()}
SPECS={
'ab':[
('wangxiangyu0814/TravelUAV_env','dataset','44de5739a95a2f6a88767446421cddada9606642','downloads/env',['closeloop_envs.*']),
('wangxiangyu0814/TravelUAV','dataset','faa8f2514156455ea7423464cc1295e6f92575cb','downloads/data',['ModernCityMap.*']),
('wangxiangyu0814/TravelUAV_data_json','dataset','5a1ed4c99d3e7bb2b35fa34135910cb7687fc831','metadata-release',['data/uav_dataset/seen_valset.json','data/meta/map_spawnarea_info.json','data/meta/object_description.json'])],
'c':[
('wangxiangyu0814/llama-uav-7b','model','6cd1a273ba26338a1be4eb93b43489ee0099fbce','models/llama-uav-7b',['*']),
('wangxiangyu0814/traveluav-traj-model','model','583a3f6b9111fd80e76d6905eaa0f1793f3fd03f','models/traj',['model_5.pth']),
('lmsys/vicuna-7b-v1.5','model','3321f76e3f527bd14065daf69dad9344000a201d','models/vicuna-7b-v1.5',['*.json','*.model','pytorch_model-*.bin']),
('google-bert/bert-base-uncased','model',None,'models/bert-base-uncased',['config.json','tokenizer*','vocab.txt','pytorch_model.bin']),
('ShilongLiu/GroundingDINO','model',None,'models/dino',['groundingdino_swint_ogc.pth'])]}

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()

def main():
 p=argparse.ArgumentParser();p.add_argument('level',choices=['ab','c']);p.add_argument('--record',required=True,type=Path);a=p.parse_args()
 records=[];api=HfApi()
 def save(): a.record.write_text(json.dumps({'assets':records,'updated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())},indent=2)+'\n')
 for repo,kind,rev,rel,patterns in SPECS[a.level]:
  info=api.repo_info(repo,repo_type=kind,revision=rev,files_metadata=True);rev=info.sha
  target=ASSETS/rel;target.mkdir(parents=True,exist_ok=True)
  rec={'repo':repo,'revision':rev,'repo_type':kind,'root':str(target),'status':'downloading','files':[]};records.append(rec);save()
  snapshot_download(repo,repo_type=kind,revision=rev,allow_patterns=patterns,local_dir=target,max_workers=2)
  siblings={f.rfilename:f for f in info.siblings}
  for f in sorted(target.rglob('*')):
   if not f.is_file() or '.cache' in f.parts:continue
   name=str(f.relative_to(target));metadata=siblings.get(name);actual=sha(f)
   expected=EXPECTED.get(str(f.relative_to(ASSETS)))
   if expected is None and metadata and metadata.lfs: expected=metadata.lfs.sha256
   if expected and actual!=expected: raise ValueError(f'Hash mismatch {f}: {actual} != {expected}')
   rec['files'].append({'path':str(f),'url':f'https://huggingface.co/{"datasets/" if kind=="dataset" else ""}{repo}/resolve/{rev}/{name}','bytes':f.stat().st_size,'sha256':actual,'expected_sha256':expected,'verified':expected is None or actual==expected})
  rec['status']='verified';save()
 if a.level=='ab':
  meta=ASSETS/'metadata';meta.mkdir(exist_ok=True)
  import shutil
  release=ASSETS/'metadata-release/data'
  for src in [release/'uav_dataset/seen_valset.json',release/'meta/map_spawnarea_info.json',release/'meta/object_description.json']: shutil.copy2(src,meta/src.name)
  rows=json.loads((meta/'seen_valset.json').read_text());chosen=[x for x in rows if x['json']=='ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f/merged_data.json']
  if len(chosen)!=33:raise ValueError(f'Expected 33 rows for one episode, got {len(chosen)}')
  (meta/'selected_seen_one.json').write_text(json.dumps(chosen[:1],indent=2)+'\n')
 else:
  for name,url in [('eva_vit_g.pth','https://storage.googleapis.com/sfr-vision-language-research/LAVIS/models/BLIP2/eva_vit_g.pth'),('instruct_blip_vicuna7b_trimmed.pth','https://storage.googleapis.com/sfr-vision-language-research/LAVIS/models/InstructBLIP/instruct_blip_vicuna7b_trimmed.pth')]:
   target=ASSETS/'models/LAVIS'/name;target.parent.mkdir(parents=True,exist_ok=True)
   rec={'url':url,'path':str(target),'status':'downloading'};records.append(rec);save()
   if not target.exists():
    with urllib.request.urlopen(url,timeout=60) as response,target.with_suffix('.partial').open('wb') as f:
     import shutil;shutil.copyfileobj(response,f)
    target.with_suffix('.partial').rename(target)
   rec.update(status='downloaded',bytes=target.stat().st_size,sha256=sha(target),expected_sha256=None);save()
  import shutil
  shutil.copy2(ASSETS/'models/dino/groundingdino_swint_ogc.pth',ASSETS/'models/groundingdino_swint_ogc.pth')
 (ASSETS/f'verified-{a.level}.json').write_text(a.record.read_text())
 print(a.record)
if __name__=='__main__': main()
