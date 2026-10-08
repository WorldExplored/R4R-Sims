#!/usr/bin/env python3
"""Install only NVIDIA 11.8 compiler/runtime headers needed by Grounding DINO."""
import hashlib,json,shutil,tarfile,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[2]/'artifacts/traveluav-openuav/dependencies'
base='https://developer.download.nvidia.com/compute/cuda/redist/'
meta=json.load(urllib.request.urlopen(base+'redistrib_11.8.0.json',timeout=30))
target=root/'cuda-11.8';target.mkdir(parents=True,exist_ok=True);records=[]
for package in ['cuda_nvcc','cuda_cudart','cuda_cccl']:
 item=meta[package]['linux-x86_64'];url=base+item['relative_path'];archive=root/Path(item['relative_path']).name
 if not archive.exists():
  with urllib.request.urlopen(url,timeout=60) as r,archive.open('wb') as f:shutil.copyfileobj(r,f)
 actual=hashlib.sha256(archive.read_bytes()).hexdigest()
 if actual!=item['sha256']:raise RuntimeError('CUDA object hash mismatch: '+str(archive))
 with tarfile.open(archive) as t:
  unpack=root/'cuda-packages';unpack.mkdir(exist_ok=True)
  t.extractall(unpack)
  name=Path(t.getnames()[0]).parts[0]
 shutil.copytree(unpack/name,target,dirs_exist_ok=True)
 records.append({'package':package,'url':url,'bytes':archive.stat().st_size,'sha256':actual,'expected_sha256':item['sha256']})
if not (target/'lib64').exists():(target/'lib64').symlink_to('lib')
(root/'cuda-components.json').write_text(json.dumps(records,indent=2)+'\n')
print(target)
