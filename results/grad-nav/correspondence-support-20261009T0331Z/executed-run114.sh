#!/usr/bin/env bash
set -euo pipefail
BASE=/home/ubuntu/grad-nav-deps
NEW="$BASE/env-render114-20261009T0337Z"
LOG="$BASE/diagnostics/ns114-20261009T0337Z"
exec > >(tee -a "$LOG/setup.log") 2>&1
"$NEW/bin/python" -m pip install --no-deps 'opencv-python-headless==4.10.0.84' 'viser==0.2.3' 'tensorly==0.9.0'
"$NEW/bin/python" - <<'PY'
import importlib.metadata as m,json,cv2,torch,gsplat,nerfstudio
from packaging.requirements import Requirement
from pathlib import Path
rows=[]
for text in m.requires('nerfstudio'):
 r=Requirement(text)
 if r.marker and not r.marker.evaluate():continue
 try:v=m.version(r.name)
 except m.PackageNotFoundError:v=None
 rows.append({'requirement':text,'installed':v,'satisfied':v is not None and (not r.specifier or r.specifier.contains(v,prereleases=True))})
p=Path('/home/ubuntu/grad-nav-deps/diagnostics/ns114-20261009T0337Z')
(p/'resolved-dependencies.json').write_text(json.dumps(rows,indent=2)+'\n')
assert all(x['satisfied'] for x in rows)
assert torch.__version__=='2.1.2+cu118' and gsplat.__version__=='1.0.0' and m.version('nerfstudio')=='1.1.4'
print('Resolved versions',torch.__version__,gsplat.__version__,cv2.__version__,nerfstudio.__file__)
PY
"$NEW/bin/python" -m pip freeze > "$LOG/resolved-freeze.txt"
"$NEW/bin/python" -m pip check > "$LOG/pip-check.txt" 2>&1 || true
export CUDA_HOME=/workspace/R4R-Sims/artifacts/traveluav-openuav/dependencies/cuda-11.8
export PATH="$NEW/bin:$BASE/env-render/bin:$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"
export CC=/usr/bin/gcc-11 CXX=/usr/bin/g++-11 MAX_JOBS=2
export MPLCONFIGDIR="$BASE/cache/matplotlib" TORCH_EXTENSIONS_DIR="$BASE/cache/torch-extensions"
cd /home/ubuntu/R4R-Sims-grad-nav
"$NEW/bin/python" simulators/grad-nav/run.py correspondence --root /home/ubuntu/R4R-Sims-grad-nav --upstream "$BASE/upstream" --timeout 300
