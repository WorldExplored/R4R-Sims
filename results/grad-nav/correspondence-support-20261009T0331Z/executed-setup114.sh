#!/usr/bin/env bash
set -euo pipefail
BASE=/home/ubuntu/grad-nav-deps
NEW="$BASE/env-render114-20261009T0337Z"
LOG="$BASE/diagnostics/ns114-20261009T0337Z"
mkdir -p "$LOG"
exec > >(tee "$LOG/setup.log") 2>&1
trap 'rc=$?; printf "%s\n" "$rc" > "$LOG/exit-status.txt"' EXIT
test ! -e "$NEW"
"$BASE/env-render/bin/python" -m pip freeze > "$LOG/baseline-freeze.txt"
python3 -m venv "$NEW"
printf '%s\n' "$BASE/env-render/lib/python3.10/site-packages" > "$NEW/lib/python3.10/site-packages/gradnav-readonly-baseline.pth"
"$NEW/bin/python" -m pip install --no-deps 'nerfstudio==1.1.4'
"$NEW/bin/python" - <<'PY'
import importlib.metadata as m,json
from packaging.requirements import Requirement
from pathlib import Path
rows=[];needs=[]
for text in m.requires('nerfstudio'):
 r=Requirement(text)
 if r.marker and not r.marker.evaluate():continue
 try:v=m.version(r.name)
 except m.PackageNotFoundError:v=None
 ok=v is not None and (not r.specifier or r.specifier.contains(v,prereleases=True))
 rows.append({'requirement':text,'installed':v,'satisfied':ok})
 if not ok:needs.append(str(r).split(';')[0])
p=Path('/home/ubuntu/grad-nav-deps/diagnostics/ns114-20261009T0337Z')
(p/'initial-dependency-check.json').write_text(json.dumps(rows,indent=2)+'\n')
(p/'required-adjustments.txt').write_text('\n'.join(needs)+'\n')
print(json.dumps({'needs':needs,'torch':m.version('torch'),'gsplat':m.version('gsplat')},indent=2))
PY
"$NEW/bin/python" -m pip freeze > "$LOG/initial-freeze.txt"
printf 'NS114_ENV=%s\n' "$NEW"
