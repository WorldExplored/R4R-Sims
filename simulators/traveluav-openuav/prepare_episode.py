#!/usr/bin/env python3
"""Run unchanged author metadata preprocessing; no policy/image-feature training."""
import argparse,hashlib,json,random,runpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
assets=root/'artifacts/traveluav-openuav/dependencies/assets';up=assets.parent/'upstream'
p=assets/'dataset/ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f/merged_data.json'
if p.exists():raise SystemExit('Preserving existing merged_data.json; do not regenerate silently')
script=up/'Model/LLaMA-UAV/tools/generate_merged_json.py'
random.seed(100)
sys.argv=[str(script),'--root_dir',str(assets/'dataset'),'--map_list','ModernCityMap']
runpy.run_path(str(script),run_name='__main__')
d=json.loads(p.read_text())
print(json.dumps({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'instruction':d['conversations'][0]['value'],'reference_state_count':len(d['trajectory_raw_detailed']),'preprocessing_seed':100,'provenance':'author documented preprocessing; original random description choice unknown'},indent=2))
