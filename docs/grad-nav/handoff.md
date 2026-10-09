# GRaD-Nav execution handoff

Read findings.md, artifact-index.md, preservation.json and repair-history.json first. A/D rendering is blocked by host compiler selection, C by original policy components, fidelity by provenance/calibration/reference inputs. Do not repeat the setup or fix compiler/packages in this session. Instance stays running.

Local candidate: `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav`, branch `audit/grad-nav`. Remote: `/home/ubuntu/R4R-Sims-grad-nav`. Dependency root `/home/ubuntu/grad-nav-deps`, baseline source `d9b00e16107338e49071c65f44582c013e522633`; current inspected `95218abe9a5d355519cdaab78d915365303066fe`. Authenticated publishing is on the Mac; remote GitHub credentials were unavailable. Git bundles preserve object identities and fast-forward the remote branch. No personal credential was transferred.

## Reproduction

Completed B exact invocation shape, from the remote candidate:
```bash
/home/ubuntu/grad-nav-deps/env-dynamics/bin/python simulators/grad-nav/run.py force --root /home/ubuntu/R4R-Sims-grad-nav --upstream /home/ubuntu/grad-nav-deps/upstream --timeout 90
/home/ubuntu/grad-nav-deps/env-dynamics/bin/python simulators/grad-nav/run.py smoke --root /home/ubuntu/R4R-Sims-grad-nav --upstream /home/ubuntu/grad-nav-deps/upstream --timeout 90
/home/ubuntu/grad-nav-deps/env-dynamics/bin/python simulators/grad-nav/run.py recovery --root /home/ubuntu/R4R-Sims-grad-nav --upstream /home/ubuntu/grad-nav-deps/upstream --timeout 90
```
Each generates a new run ID, configs, command/status/error logs, every0.05s achieved state/actions and1s GPU samples. Conversion checks use mode `conversion`. Exact numeric definitions are in plan.md and each config.json. Direct SI normalized-thrust interface bypasses native env/learned observations.

Rendering command for a future separately authorized attempt is `bash simulators/grad-nav/launch.sh a` or `d`. These are currently blocked. `setup-render.sh` shows installation/extraction commands but refuses overwriting extracted inputs, so it is not an existing-host rerun command. Original configs remain preserved; path relocation is in render.py. No source patches or training run.

Actual host is Ubuntu22.04.5, A6000 48GB class,6vCPU,47GiB RAM/251GiB disk. CUDA driver580.126.09 reports13.0 capability; actual toolkit11.8.89 is separately recorded. Rendering Python3.10.12, Torch2.1.2+cu118, TV0.16.2+cu118, NS1.1.3, gsplat1.0.0, NumPy1.26.4. B uses isolated Torch2.0.1+cu118, NumPy1.26.3. Complete freezes and commands are preserved. Actual inference/render minimum VRAM is unmeasured. Paper's4090/48GB training baseline is a reference, not a minimum. Retain this existing A6000 host; no extra rental is needed. A cheaper24GB NVIDIA Linux host is only a future conditional renderer candidate, not verified here.

## Collection

The five-minute resumable Mac collector was launched into a separate live folder without delete flags, but only its initial cycle was logged and the background process did not persist. Sustained periodic cadence was not verified. Explicit incremental and final rsync collected the completed/failure groups. Finalized files were separately copied and SHA256 checked after settlement. Full scientifically used gate_mid data, checkpoint, config and point cloud are under ignored `artifacts/grad-nav/scientific-inputs/`. Full unused ZIP archives remain on the host and at replacement URLs verified from the Mac, with hashes; selected used bytes are locally preserved. Environments/toolkit are reproducible dependencies, not the sole scientific input copy. Do not terminate the instance or remove remote files in this session.

Follow-up prompt: “Read docs/grad-nav/findings.md, artifact-index.md, preservation.json and repair-history.json on audit/grad-nav. Preserve all historical failures. With a new explicitly bounded repair budget, inspect nvcc's host-compiler choice and GCC11 cc1plus before any package install. Reattempt A/D only after that targeted preflight, and verify camera transforms through actual rendered observations. Keep C blocked until the original six-object checkpoint and matching interfaces are supplied. Keep fidelity blocked until trustworthy held-out capture provenance and an existing reconstruction are supplied. Do not train, rent or terminate hardware.”
