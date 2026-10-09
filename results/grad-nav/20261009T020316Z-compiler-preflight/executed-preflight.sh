#!/usr/bin/env bash
set -euo pipefail
BASE=/home/ubuntu/grad-nav-deps
RID=$(date -u +%Y%m%dT%H%M%SZ)-compiler-preflight
OUT="$BASE/diagnostics/$RID"
mkdir -p "$OUT"
exec > >(tee "$OUT/console.log") 2>&1
trap 'code=$?; printf "%s\n" "$code" > "$OUT/exit-status.txt"' EXIT
date -u
env | sort > "$OUT/environment-before.txt"
git -C /home/ubuntu/R4R-Sims-grad-nav rev-parse HEAD
git -C /workspace/R4R-Sims status --short --branch
cp "$BASE/cache/torch-extensions/gsplat_cuda/build.ninja" "$OUT/historical-build.ninja"
cat "$OUT/historical-build.ninja"
for c in gcc gcc-11 g++ g++-11; do
  command -v "$c"
  "$c" --version | head -1
  "$c" -print-prog-name=cc1plus
done
ls -l /usr/lib/gcc/x86_64-linux-gnu/11/cc1plus
cat > "$OUT/minimal.cpp" <<'EOF'
#include <iostream>
int main(){std::cout << "cxx11-ok " << (2+3) << std::endl;return 0;}
EOF
set -x
/usr/bin/g++-11 -std=c++17 "$OUT/minimal.cpp" -o "$OUT/minimal-cxx"
"$OUT/minimal-cxx"
set +x
cat > "$OUT/minimal.cu" <<'EOF'
#include <cuda_runtime.h>
#include <cstdio>
__global__ void add(int* x){*x=2+3;}
int main(){int* d; int h=0; if(cudaMalloc(&d,sizeof(int))!=cudaSuccess)return 1;add<<<1,1>>>(d);if(cudaDeviceSynchronize()!=cudaSuccess)return 2;if(cudaMemcpy(&h,d,sizeof(int),cudaMemcpyDeviceToHost)!=cudaSuccess)return 3;cudaFree(d);printf("cuda11-ok %d\n",h);return h==5?0:4;}
EOF
export CUDA_HOME=/workspace/R4R-Sims/artifacts/traveluav-openuav/dependencies/cuda-11.8
set -x
"$CUDA_HOME/bin/nvcc" -v -ccbin /usr/bin/g++-11 -std=c++17 "$OUT/minimal.cu" -o "$OUT/minimal-cuda"
"$OUT/minimal-cuda"
set +x
env | sort > "$OUT/environment-after.txt"
printf 'DIAGNOSTIC_PATH=%s\n' "$OUT"
