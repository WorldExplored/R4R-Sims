"""Read-only source-manifest verification and PNG/depth decoding; no remote operations."""
from pathlib import Path
import argparse,json,hashlib,zipfile,datetime
import numpy as np
from PIL import Image
parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--records',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
root=args.root;work=args.records;out=args.output
if out.resolve().is_relative_to((root/'artifacts').resolve()) or out.resolve().is_relative_to((root/'third_party').resolve()):raise ValueError('Output must be outside preserved evidence/inputs')
out.mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(8*1024*1024):h.update(b)
 return h.hexdigest()
old=json.loads((work/'results/unreal/closeout-20261008/recovery.json').read_text()); expected={x['run_id']:x['source_manifest_sha256'] for x in old['runs']}
r={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'basis':'retained VM source manifests, anchored to committed recovery record / residual manifest; archives against previously recorded source size/hash','groups':[],'archives':[],'errors':[],'decoded_png':0,'decoded_npy':0}
paths=[root/'artifacts/unreal'/name/'source-manifest.json' for name in expected]+[root/'artifacts/unreal/unreal-final-backup-20261008/source-manifest.json',root/'third_party/unreal/assets/italink-plugin-ue55-linux/source-manifest.json']
for p in paths:
 if not p.is_file():r['errors'].append('missing source manifest '+str(p));continue
 m=json.loads(p.read_text()); digest=sha(p); name=p.parent.name
 anchor=expected.get(name)
 if name=='unreal-final-backup-20261008': anchor=sha(work/'results/unreal/a5000-cleanup-20261008/residual-source-manifest.json')
 if name=='italink-plugin-ue55-linux':anchor=old['compiled_plugin']['source_manifest_sha256']
 errors=[]
 if digest!=anchor:errors.append('source manifest differs from committed anchor')
 for e in m['files']:
  f=p.parent/e['path']
  if not f.is_file():errors.append('missing '+e['path']);continue
  if f.stat().st_size!=e['bytes'] or sha(f)!=e['sha256']:errors.append('changed '+e['path'])
  try:
   if f.suffix.lower()=='.png':
    with Image.open(f) as im:im.load()
    r['decoded_png']+=1
   if f.suffix.lower()=='.npy':
    a=np.load(f,allow_pickle=False);assert a.shape==(480,640);assert np.isfinite(a).all();r['decoded_npy']+=1
  except Exception as ex:errors.append('decode '+e['path']+':'+str(ex))
 r['groups'].append({'local_path':str(p.parent),'source_manifest_sha256':digest,'files':len(m['files']),'bytes':sum(x['bytes'] for x in m['files']),'errors':errors});r['errors']+=errors
for e in old['archives']:
 p=root/'third_party/unreal/assets'/Path(e['local_path']).name
 if not p.is_file():r['errors'].append('missing archive '+str(p));continue
 d=sha(p);ok=p.stat().st_size==e['bytes'] and d==e['sha256'];r['archives'].append({'path':str(p),'bytes':p.stat().st_size,'sha256':d,'source_match':ok})
 if not ok:r['errors'].append('archive mismatch '+str(p))
p=root/'artifacts/unreal/ue-20261008T215415Z-b-e868ec1c/supervisor.log';q=root/'artifacts/unreal/unreal-final-backup-20261008/tmp/ue-20261008T215415Z-b-e868ec1c-supervisor.log'
r['preflight_log']={'path':str(p),'sha256':sha(p) if p.is_file() else None,'source_manifested_residual_copy':str(q),'identical_to_residual_source_copy':p.is_file() and q.is_file() and p.read_bytes()==q.read_bytes()}
if not r['preflight_log']['identical_to_residual_source_copy']:r['errors'].append('preflight log missing or differs from residual copy')
checks=[]
summary_manifest=work/'results/unreal/focused-validation-20261008T232000Z/source-manifest.json'
for e in json.loads(summary_manifest.read_text())['files']:
 f=summary_manifest.parent/e['path'];match=f.is_file() and f.stat().st_size==e['bytes'] and sha(f)==e['sha256'];checks.append({'path':str(f),'source_match':match,'sha256':sha(f) if f.is_file() else None})
 if not match:r['errors'].append('published focused summary mismatch '+e['path'])
r['published_focused_summary_checks']=checks
r['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['groups','archives']},indent=2));print('groups',len(r['groups']),'files',sum(x['files'] for x in r['groups']))

raise SystemExit(1 if r['errors'] else 0)
