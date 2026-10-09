# GRaD-Nav execution handoff

Read findings.md, artifact-index.md, preservation.json and repair-history.json first. Compiler repair succeeded with existing GCC11. A renders but capture alignment remains unresolved; D demonstrates native coordinate coupling. C and fidelity remain blocked. Read render-results.md. The new bounded debugging session is complete; instance stays running.

Local candidate: `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav`, branch `audit/grad-nav`. Remote: `/home/ubuntu/R4R-Sims-grad-nav`. Dependency root `/home/ubuntu/grad-nav-deps`, baseline source `d9b00e16107338e49071c65f44582c013e522633`; current inspected `95218abe9a5d355519cdaab78d915365303066fe`. Authenticated publishing is on the Mac; remote GitHub credentials were unavailable. Git bundles preserve object identities and fast-forward the remote branch. No personal credential was transferred.

## Reproduction

Completed B exact invocation shape, from the remote candidate:
```bash
/home/ubuntu/grad-nav-deps/env-dynamics/bin/python simulators/grad-nav/run.py force --root /home/ubuntu/R4R-Sims-grad-nav --upstream /home/ubuntu/grad-nav-deps/upstream --timeout 90
/home/ubuntu/grad-nav-deps/env-dynamics/bin/python simulators/grad-nav/run.py smoke --root /home/ubuntu/R4R-Sims-grad-nav --upstream /home/ubuntu/grad-nav-deps/upstream --timeout 90
/home/ubuntu/grad-nav-deps/env-dynamics/bin/python simulators/grad-nav/run.py recovery --root /home/ubuntu/R4R-Sims-grad-nav --upstream /home/ubuntu/grad-nav-deps/upstream --timeout 90
```
Each generates a new run ID, configs, command/status/error logs, every0.05s achieved state/actions and1s GPU samples. Conversion checks use mode `conversion`. Exact numeric definitions are in plan.md and each config.json. Direct SI normalized-thrust interface bypasses native env/learned observations.

Executed rendering commands are `bash simulators/grad-nav/launch.sh a` or `d`. These ran successfully on this host after explicit GCC11 selection; capture alignment remains a separate blocker. Do not rerun completed B to tune its outcome. `setup-render.sh` shows installation/extraction commands but refuses overwriting extracted inputs, so it is not an existing-host rerun command. Original configs remain preserved; path relocation is in render.py. No upstream source patches or training run.

Actual host is Ubuntu22.04.5, A6000 48GB class,6vCPU,47GiB RAM/251GiB disk. CUDA driver580.126.09 reports13.0 capability; actual toolkit11.8.89 is separately recorded. Rendering Python3.10.12, Torch2.1.2+cu118, TV0.16.2+cu118, NS1.1.3, gsplat1.0.0, NumPy1.26.4. B uses isolated Torch2.0.1+cu118, NumPy1.26.3. Complete freezes and commands are preserved. Actual inference/render minimum VRAM is unmeasured. Paper's4090/48GB training baseline is a reference, not a minimum. Retain this existing A6000 host; no extra rental is needed. A cheaper24GB NVIDIA Linux host is only a future conditional renderer candidate, not verified here.

## Collection

The five-minute resumable Mac collector was launched into a separate live folder without delete flags, but only its initial cycle was logged and the background process did not persist. Sustained periodic cadence was not verified. Explicit incremental and final rsync collected the completed/failure groups. Finalized files were separately copied and SHA256 checked after settlement. Full scientifically used gate_mid data, checkpoint, config and point cloud are under ignored `artifacts/grad-nav/scientific-inputs/`. Full unused ZIP archives remain on the host and at replacement URLs verified from the Mac, with hashes; selected used bytes are locally preserved. Environments/toolkit are reproducible dependencies, not the sole scientific input copy. Do not terminate the instance or remove remote files in this session.


## Continuation reproduction and dependency ownership

`bash simulators/grad-nav/launch.sh a` uses the frozen historical route with an assertion against numerical drift. `bash simulators/grad-nav/launch.sh d` uses unchanged native mount and existing named controller. `bash simulators/grad-nav/launch.sh scene-diagnostic` records exact COLMAP/source pose, released camera-path pose with hardcoded K, and an explicit no-hit camera separately. All bounded at900s with exit status preserved. GPU-dependent commands were executed only on the existing host.

CUDA_HOME borrows `/workspace/R4R-Sims/artifacts/traveluav-openuav/dependencies/cuda-11.8` read-only. Keep it in place. Exact NVIDIA11.8 redistribution component URLs/bytes/SHA256 are in `results/grad-nav/20261009T020316Z-compiler-preflight/borrowed-cuda-components.json`; compiler/runtime/CCCL11.8.89, cuBLAS11.11.3.6, cuSPARSE11.7.5.86, cuSOLVER11.4.1.48, cuRAND10.3.0.86. Reacquire those exact archives from NVIDIA redistrib11.8.0, verify hashes, expand into a new GRaD-Nav-owned toolkit root, merge compiler/runtime bin/include/lib/nvvm plus library headers and lib64→lib if absent. Do not run TravelUAV compile_cuda.py in its checkout because it mutates that candidate. No new toolkit installation occurred here. CC=/usr/bin/gcc-11,CXX=/usr/bin/g++-11; do not change system alternatives or bypass nvcc checks. Existing driver580.126.09 stayed unchanged.

Next needed: author-confirmed relationship between scene checkpoint and released capture poses/physical scale; compatible original six-object learned checkpoint; trustworthy held-out capture split for fidelity. The diagnostic route is not calibrated flight or a common-scene R4R comparison.

Compiler preflight source and emitted build commands are in results/grad-nav/20261009T020316Z-compiler-preflight. For a fresh authorized host, run that preflight under `timeout 120s bash executed-preflight.sh` after verifying its isolated dependency root. All seven exact borrowed-toolkit URLs returned HTTP200 with matching Content-Length from the receiving Mac; no archive body was downloaded in the continuation. Original CUDA component archive hashes came from the earlier toolkit acquisition, not these HEAD requests.
