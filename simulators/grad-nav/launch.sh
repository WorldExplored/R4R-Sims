#!/usr/bin/env bash
set -euo pipefail
MODE=${1:?a or d}
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
DEPS="$HOME/grad-nav-deps"
export CUDA_HOME=/workspace/R4R-Sims/artifacts/traveluav-openuav/dependencies/cuda-11.8
export PATH="$DEPS/env-render/bin:$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"
export MAX_JOBS=2
export MPLCONFIGDIR="$DEPS/cache/matplotlib"
export TORCH_EXTENSIONS_DIR="$DEPS/cache/torch-extensions"
cd "$ROOT"
python simulators/grad-nav/run.py "$MODE" --root "$ROOT" --upstream "$DEPS/upstream" --timeout 900
