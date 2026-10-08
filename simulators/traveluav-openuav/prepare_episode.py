#!/usr/bin/env python3
"""Run author preprocessing with documented seed-function fix; no training."""
import argparse,difflib,hashlib,json,random,runpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
assets=root/'artifacts/traveluav-openuav/dependencies/assets';up=assets.parent/'upstream'
p=assets/'dataset/ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f/merged_data.json'
if p.exists():raise SystemExit('Preserving existing merged_data.json; do not regenerate silently')
script=up/'Model/LLaMA-UAV/tools/generate_merged_json.py'
old=script.read_text();assert old.count("random.seed = 1")==1
patched=old.replace("random.seed = 1","random.seed(100)")
record=assets/"runtime/metadata";record.mkdir(parents=True,exist_ok=True)
(record/"metadata_seed.patch").write_text("".join(difflib.unified_diff(old.splitlines(True),patched.splitlines(True),fromfile="a/Model/LLaMA-UAV/tools/generate_merged_json.py",tofile="b/Model/LLaMA-UAV/tools/generate_merged_json.py")))
sys.argv=[str(script),'--root_dir',str(assets/'dataset'),'--map_list','ModernCityMap']
exec(compile(patched,str(script),'exec'),{'__name__':'__main__','__file__':str(script)})
assert callable(random.seed)
d=json.loads(p.read_text())
print(json.dumps({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'instruction':d['conversations'][0]['value'],'reference_state_count':len(d['trajectory_raw_detailed']),'preprocessing_seed':100,'provenance':'regenerated author metadata with random.seed(100) correction; original description choice unknown'},indent=2))
