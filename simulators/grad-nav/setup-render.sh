#!/usr/bin/env bash
set -euo pipefail
DEPS="$HOME/grad-nav-deps"
LOG="$HOME/R4R-Sims-grad-nav/artifacts/grad-nav/preflight"
mkdir -p "$LOG" "$DEPS/scenes"
date -u +%FT%TZ > "$LOG/render-setup-start.txt"
python3 - <<'PY'
import zipfile,pathlib,json,hashlib
r=pathlib.Path.home();deps=r/'grad-nav-deps';log=r/'R4R-Sims-grad-nav/artifacts/grad-nav/preflight'
rows=[]
for name in ['gs_data.zip','point_cloud.zip']:
 p=deps/'downloads'/name;h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 with zipfile.ZipFile(p) as z:
  members=[i for i in z.infolist() if (i.filename.startswith('gs_data/sv_1007_gate_mid/') or i.filename=='point_cloud/sv_1007_gate_mid.ply') and not i.is_dir()]
  size=sum(i.file_size for i in members)
  if __import__('shutil').disk_usage(deps).free<size+10*1024**3:raise RuntimeError('insufficient expansion headroom')
  for i in members:
   target=(deps/'scenes'/i.filename).resolve()
   if not target.is_relative_to((deps/'scenes').resolve()):raise RuntimeError('unsafe archive member')
   if target.exists():raise RuntimeError('refuse to overwrite extracted asset')
   z.extract(i,deps/'scenes')
 rows.append({'archive':str(p),'bytes':p.stat().st_size,'sha256':h.hexdigest(),'selected_expanded_bytes':size,'selected_members':len(members)})
(log/'download-hashes.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows))
PY
python3 -m venv "$DEPS/env-render"
export CUDA_HOME=/workspace/R4R-Sims/artifacts/traveluav-openuav/dependencies/cuda-11.8
export PATH="$CUDA_HOME/bin:$DEPS/env-render/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"
export MAX_JOBS=2
nvcc --version
python -m pip install 'torch==2.1.2+cu118' 'torchvision==0.16.2+cu118' --extra-index-url https://download.pytorch.org/whl/cu118
python -m pip install 'numpy==1.26.4' 'nerfstudio==1.1.3' 'gsplat==1.0.0' 'setuptools<81'
python -m pip freeze > "$LOG/render-freeze.txt"
python -c 'import torch; import nerfstudio; import gsplat; print(torch.__version__,torch.cuda.is_available(),gsplat.__version__)'
date -u +%FT%TZ > "$LOG/render-setup-end.txt"
