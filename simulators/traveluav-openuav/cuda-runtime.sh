#!/usr/bin/env bash
# Export only this task's verified CUDA runtime directories; no profile/driver edits.
source "$(dirname "$0")/layout.sh"
export CUDA_HOME="$ARTIFACTS/dependencies/cuda-11.8"
cuda_libs="$($ENV_C/bin/python - "$ARTIFACTS/dependencies" <<'INNER'
from pathlib import Path
import sys
root=Path(sys.argv[1]);dirs=[root/'cuda-11.8/lib']
for library in ['libcublas.so.11','libcusparse.so.11','libcusolver.so.11','libcurand.so.10']:
 found=sorted(p for p in (root/'cuda-packages').rglob(library) if p.parent.name=='lib')
 if not found:raise SystemExit('Missing runtime library '+library)
 dirs.append(found[-1].parent)
print(':'.join(dict.fromkeys(str(d) for d in dirs)))
INNER
)"
export LD_LIBRARY_PATH="$cuda_libs:$ENV_C/lib/python3.10/site-packages/torch/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
