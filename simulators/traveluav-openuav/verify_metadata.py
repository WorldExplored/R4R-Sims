#!/usr/bin/env python3
"""Verify isolated author preprocessing twice; preserve the runtime episode unchanged."""
import argparse,difflib,hashlib,json,shutil,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('assets',type=Path);p.add_argument('upstream',type=Path);p.add_argument('record',type=Path);p.add_argument('capture',type=Path);a=p.parse_args()
a.record.mkdir(parents=True,exist_ok=True);a.capture.mkdir(parents=True,exist_ok=True)
rel=Path('ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f')
source=a.assets/'dataset'/rel;isolated=a.capture/'isolated-dataset';dest=isolated/rel
shutil.copytree(source,dest,ignore=shutil.ignore_patterns('merged_data.json'))
script=a.upstream/'Model/LLaMA-UAV/tools/generate_merged_json.py';old=script.read_text();assert old.count('random.seed = 1')==1
new=old.replace('random.seed = 1','random.seed(100)');patched=a.capture/'generate_merged_json_seed100.py';patched.write_text(new)
(a.record/'metadata_seed.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/Model/LLaMA-UAV/tools/generate_merged_json.py',tofile='b/Model/LLaMA-UAV/tools/generate_merged_json.py')))
wrapper='''import random,runpy,sys,json
choice=random.choice
selected=[]
def observed(seq):
 result=choice(seq);selected.append(result);return result
random.choice=observed
script,root=sys.argv[1:];sys.argv=[script,'--root_dir',root,'--map_list','ModernCityMap'];runpy.run_path(script,run_name='__main__')
assert callable(random.seed)
print(json.dumps({'selected_descriptions':selected,'seed_function_callable':callable(random.seed)}))
'''
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
outputs=[]
for i in range(2):
 result=subprocess.run([sys.executable,'-c',wrapper,str(patched),str(isolated)],text=True,capture_output=True)
 (a.record/f'generation-{i+1}.log').write_text(result.stdout+result.stderr);result.check_returncode()
 generated=dest/'merged_data.json';saved=a.record/f'merged-generation-{i+1}.json';shutil.copy2(generated,saved);outputs.append({'sha256':sha(saved),'selection':json.loads(result.stdout.splitlines()[-1])});generated.unlink()
assert outputs[0]['sha256']==outputs[1]['sha256'],'Nondeterministic metadata'
d=json.loads((a.record/'merged-generation-1.json').read_text());runtime=json.loads((source/'merged_data.json').read_text())
# Only absolute image-feature path changes when isolating author preprocessing.
changes={k:{'isolated':d.get(k),'runtime':runtime.get(k)} for k in set(d)|set(runtime) if d.get(k)!=runtime.get(k)}
assert set(changes).issubset({'image_feature_path'}),changes
inputs=[script]+sorted(f for f in source.rglob('*') if f.is_file() and f.name!='merged_data.json')
record={'status':'matching_hashes','seed':100,'generations':outputs,'source_script_sha256':sha(script),'patched_script_sha256':sha(patched),'source_inputs':[{'path':str(f),'sha256':sha(f),'bytes':f.stat().st_size} for f in inputs], 'runtime_episode_sha256':sha(source/'merged_data.json'),'isolated_path_changes':changes,'instruction':d['conversations'][0]['value'],'C_metadata_provenance':'regenerated episode metadata; original released description selection unavailable'}
(a.record/'metadata-verification.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'status':record['status'],'hash':outputs[0]['sha256'],'instruction':record['instruction'],'differences':list(changes)},indent=2))
