set -Eeuo pipefail
cd /workspace/R4R-Sims
source simulators/traveluav-openuav/layout.sh
run="$RESULTS/$(date -u +%Y%m%dT%H%M%SZ)-setup-c-extension"
mkdir -p "$run"
exec > >(tee -a "$run/console.log") 2>&1
trap 'rc=$?; printf "{\"kind\":\"c-extension\",\"exit_status\":%s}\n" "$rc" > "$run/run.json"' EXIT
printf '%s\n' 'python compile_cuda.py; nvcc --version; MAX_JOBS=2 pip install --no-deps --no-build-isolation -e pinned GroundingDINO' > "$run/commands.log"
if [[ ! -x "$ARTIFACTS/dependencies/cuda-11.8/bin/nvcc" || ! -f "$ARTIFACTS/dependencies/cuda-11.8/include/cusparse.h" ]]; then "$ENV_C/bin/python" "$ROOT/compile_cuda.py"; fi
cp "$ARTIFACTS/dependencies/cuda-components.json" "$run/cuda-components.json"
export CUDA_HOME="$ARTIFACTS/dependencies/cuda-11.8" PATH="$ARTIFACTS/dependencies/cuda-11.8/bin:$ENV_C/bin:$PATH" MAX_JOBS=2 TORCH_CUDA_ARCH_LIST=8.6
export CC=/usr/bin/gcc-11 CXX=/usr/bin/g++-11 CUDAHOSTCXX=/usr/bin/g++-11
nvcc --version
"$CC" --version
"$CXX" --version
python -m pip install --no-deps --no-build-isolation -e "$UPSTREAM/src/model_wrapper/utils/GroundingDINO"
python -c 'from groundingdino import _C; import torch; print("DINO CUDA extension OK",torch.__version__,torch.version.cuda,torch.cuda.get_device_name())'
python -m pip freeze > "$run/pip-freeze.txt"
