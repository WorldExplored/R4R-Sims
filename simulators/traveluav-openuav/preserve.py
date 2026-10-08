#!/usr/bin/env python3
"""Settle run inventory, or verify a transferred run using destination bytes."""
import argparse,hashlib,json,tarfile,time
from pathlib import Path

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8388608),b''):h.update(b)
 return h.hexdigest()

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['inventory','verify']);p.add_argument('run',type=Path);p.add_argument('capture',type=Path);p.add_argument('--archive',type=Path);a=p.parse_args()
 manifest=a.run/'settled_manifest.json'
 if a.mode=='inventory':
  files=[]
  for kind,base in [('record',a.run),('artifact',a.capture)]:
   if not base.exists():continue
   for f in sorted(base.rglob('*')):
    if not f.is_file() or f.name in ['settled_manifest.json','preservation.json']:continue
    files.append({'location':kind,'relative_path':str(f.relative_to(base)),'bytes':f.stat().st_size,'sha256':sha(f)})
  data={'run_id':a.run.name,'settled_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'files':files,'remote_records':str(a.run.resolve()),'remote_artifacts':str(a.capture.resolve()),'previous_manifests':'retained historical; this manifest covers final settled record revisions'}
  if a.archive:data['archive']={'name':a.archive.name,'bytes':a.archive.stat().st_size,'sha256':sha(a.archive)}
  manifest.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({'run':a.run.name,'files':len(files),'bytes':sum(f['bytes'] for f in files)}));return
 import numpy as np
 from PIL import Image
 data=json.loads(manifest.read_text());errors=[];decoded={'png':0,'depth':0,'json':0,'jsonl':0};verified=0
 for item in data['files']:
  f=({'record':a.run,'artifact':a.capture}[item['location']])/item['relative_path']
  try:
   assert f.stat().st_size==item['bytes'] and sha(f)==item['sha256'],'destination size/hash mismatch'
   verified+=1
   if f.suffix=='.png':
    with Image.open(f) as im:im.load()
    decoded['png']+=1
   elif f.suffix=='.npy':np.load(f,allow_pickle=False);decoded['depth']+=1
   elif f.suffix=='.json':json.loads(f.read_text());decoded['json']+=1
   elif f.suffix=='.jsonl':
    for line in f.read_text().splitlines():json.loads(line)
    decoded['jsonl']+=1
   elif f.suffix in ['.log','.txt','.patch','.csv']:f.read_text(errors='replace')
  except Exception as exc:errors.append({'path':str(f),'error':str(exc)})
 if data.get('archive'):
  try:
   assert a.archive and a.archive.stat().st_size==data['archive']['bytes'] and sha(a.archive)==data['archive']['sha256'],'archive hash/size mismatch'
   with tarfile.open(a.archive,'r:gz') as tar:
    for member in tar:
     if member.isfile():
      with tar.extractfile(member) as f:
       while f.read(8388608):pass
  except Exception as exc:errors.append({'archive':str(a.archive),'error':str(exc)})
 report={'run_id':a.run.name,'status':'locally_verified' if not errors else 'preservation_failed','verified_files':verified,'decoded':decoded,'errors':errors,'local_records':str(a.run.resolve()),'local_artifacts':str(a.capture.resolve()),'settled_manifest_sha256':sha(manifest),'archive_local':str(a.archive.resolve()) if a.archive else None,'checked_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
 # Store beside the ignored capture, then commit a copy separately; no circular manifest.
 a.capture.mkdir(parents=True,exist_ok=True);(a.capture/'destination-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
 if errors:raise SystemExit(1)
if __name__=='__main__':main()
