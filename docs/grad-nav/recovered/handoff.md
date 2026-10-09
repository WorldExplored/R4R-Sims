# GRaD-Nav simulator audit — phase 1 handoff

Prepared 2026-10-04. Candidate: authors' GRaD-Nav (`Qianzhong-Chen/grad_nav`), not the R2R benchmark. “GrandNav” in Air Labs notes is treated as GRaD-Nav pending confirmation. No GPU experiment or real-world transfer was measured here.

## Status and smallest useful reproduction

**A — prepared, unexecuted:** load the released `gate_mid` Nerfstudio/Splatfacto scene; render five known camera poses derived from the first evaluation camera (offsets 0, ±0.10 transformed scene units horizontally and vertically), RGB plus depth. This checks scene load and novel views near a known camera, not navigation or broad novel-view fidelity.

**B — prepared, unexecuted:** 20 control ticks at 0.05 simulated seconds each using the authors' `QuadrotorSimulator`, a fixed hover target and a simple height feedback law. Logs proprioceptive observation, requested body rates and thrust, and resulting state. This is a dynamics interface smoke test, not the published full visual-navigation environment and not a learned policy.

**C — blocked:** published GRaD-Nav `--play` path for `drone_long_traj.yaml` requires a compatible serialized checkpoint. README gives `examples/logs/.../best_policy.pt` as a developer output path; no public policy-weight download was verified. A scene archive cannot satisfy this. Do not train or invent weights. If authors supply verified weights, run the exact config and map named with them; keep GRaD-Nav++ checkpoints and configs separate.

Input → output: Splatfacto `config.yml` + checkpoint + data parser → `eval_setup` → fixed-intrinsics camera → per-camera `get_outputs_for_camera` → RGB/depth. Native loop: vehicle state + 4-action command → delay/clamp → differentiable quadrotor dynamics → next state; pose → Gaussian RGB/depth → SqueezeNet feature; state/features/history → CENet + actor → next action. Point-cloud distance and waypoints feed reward. The training method is a SHAC-like differentiable actor-critic, not online MPC. Visual features are detached in the environment, so do not infer every operation backpropagates through rendering. See [source trace](sources.md).

## Provision and effort

Provision **Ubuntu 22.04 x86_64, NVIDIA RTX 4090 24 GB, modern 12–24 core CPU, 64 GB RAM, and 1 TB local NVMe** for the first run. This is a conservative machine class, not a proven minimum: the paper reports an i9-13900K, RTX 4090 and 48 GB RAM for 128 drones in a ~1.5 GB Gaussian scene, 0.05 s simulated tick and ~0.07 s wall tick. The paper's training throughput is no guarantee of single-camera online latency or a larger outdoor scene. A cheaper **Ubuntu 22.04 x86_64, RTX 3090 24 GB, 32–64 GB RAM, 500 GB NVMe** is a plausible A/B attempt; compatibility and speed remain to be measured. A 12 GB card may render a smaller scene, but no minimum for these released assets is established. NVIDIA CUDA/Linux is the practical target because the stack invokes gsplat CUDA and PyTorch CUDA; this Mac is for static checks only. GUI is not needed for the scripted render, but CUDA is.

Budget roughly 0.5 day to secure/download and inspect assets and dependencies, 0.5–1 day to establish the frozen environment and repair path/version issues, then 1–2 hours for A/B and evidence verification. C needs a checkpoint first. Download and expanded sizes for the author's two Drive ZIPs are **unknown until accessible**; inspect both before extracting. Paper's ~1.5 GB scene model is a reported example, not the ZIP size. Reserve at least 100 GB free for the initial scene, extracted assets, environment and outputs pending inventory; stop if the measured expanded sizes do not fit. Current local disk reported 689 GiB free, but assets were not downloaded.

## Bounded Ubuntu execution

Run under a fresh directory on the provisioned host. The scripts live beside this handoff. They never install a system package or modify upstream. All commands below are **unexecuted on GPU host**.

```bash
export AUDIT="$HOME/Documents/AirLab/Real4Real/sim-audit/grad-nav"
cd "$AUDIT"
git clone https://github.com/Qianzhong-Chen/grad_nav.git upstream
git -C upstream checkout d9b00e16107338e49071c65f44582c013e522633
git -C upstream status --short
df -h .
nvidia-smi
python3 -m venv .venv
. .venv/bin/activate
```

Before package installation, capture `python --version`, driver/CUDA, inspect upstream `AGENTS.md` if present, and lock compatible PyTorch/Nerfstudio/gsplat versions in `runs/<id>/environment.txt`. The upstream README does **not** pin these versions. The official Nerfstudio installation page lists a **trial baseline**, PyTorch 2.1.2 + CUDA 11.8 and torchvision 0.16.2, with the matching CUDA toolkit needed to build extensions. On an Ubuntu host with CUDA 11.8 toolkit and compatible driver, the bounded isolated trial is `python -m pip install 'torch==2.1.2+cu118' 'torchvision==0.16.2+cu118' --extra-index-url https://download.pytorch.org/whl/cu118` followed by `python -m pip install 'nerfstudio==1.1.3' 'gym' 'transformers'`; install gsplat only at the version required by that resolved Nerfstudio distribution after checking `pip show nerfstudio gsplat`. This is **not an author-verified lockfile**; stop and document an incompatibility rather than silently upgrade. Do not assume latest Nerfstudio can load an older pickle/config. Record exact `pip freeze`. Keep compatibility fixes as `patches/*.patch`; never silently edit the checkout.

Acquire `point_cloud.zip` (Drive ID `1xIDb1-HFkniBagvMbWDgfy4okKTckwra`) and `gs_data.zip` (ID `1skbXqg__Ew3ytNmqe_xiaqHpexZnsfdw`) through the author's folder. Before extraction run `ls -lh`, `sha256sum`, `unzip -l` and `df -h`; put the extracted files under `upstream/envs/assets/{point_cloud,gs_data}` as expected by code. Check `gate_mid` resolves to `sv_1007_gate_mid`, `config.yml`, referenced Nerfstudio checkpoint, transforms, and the corresponding point cloud; record all hashes in `asset-inventory.csv`. The Drive page was inaccessible from this environment; availability, terms and sizes require host verification.

Use a unique ID and an isolated run directory (never reuse):

```bash
RID="$(date -u +%Y%m%dT%H%M%SZ)-gradnav-gatemid-a"
mkdir -p "runs/$RID"
AUDIT_RUN="$(pwd)/runs/$RID" AUDIT_UPSTREAM="$(pwd)/upstream" AUDIT_TIMEOUT=180s bash ./capture.sh python ./run_a.py --out "$(pwd)/runs/$RID"
RID="$(date -u +%Y%m%dT%H%M%SZ)-gradnav-dynamics-b"
mkdir -p "runs/$RID"
AUDIT_RUN="$(pwd)/runs/$RID" AUDIT_UPSTREAM="$(pwd)/upstream" AUDIT_TIMEOUT=90s bash ./capture.sh python ./run_b.py --out "$(pwd)/runs/$RID"
```

`capture.sh` applies the timeout to the child and preserves its exit status through `tee`; it writes `run.json` even when the child times out. External termination of the capture shell itself may interrupt that write, so check for `run.json` after any host failure. For C, only after weights are verified, freeze a copy of the compatible YAML with `episode_length` and `games_num` bounded; then use `capture.sh` with the authors' `python examples/train_gradnav.py --cfg <frozen-yaml> --checkpoint <absolute-verified-pt> --play --render --device cuda:0 --seed 0 --no-time-stamp --logdir <run>/upstream-logs`. Run from `upstream/` because relative asset/output paths are used. The published play path has no frame-by-frame evidence guarantee; instrument the evaluation loop to write state/action/pose records before accepting C. Preserve that patch.

## Evidence contract and acceptance

Each `runs/<run-id>/` contains `run.json`, `commands.log`, `console.log`, `environment.txt`, `assets.sha256`, `config/`, `patches/`, `reference_route.jsonl`, `state.jsonl`, `actions.jsonl`, `camera_poses.jsonl`, `frames/` and optional `video/`, `metrics.json`. A writes camera poses and frames every pose (five total), while state/actions explicitly say `not applicable`. B records state and actions every 0.05 simulated second for 20 ticks; camera and scene fields say `not applicable`. C should log each 0.05 s control step, each actual camera pose, each render, and any dropped interval with a reason; reference route, realized vehicle trajectory and realized camera poses are separate files.

`run.json` must name source SHA and dirty diff hash; OS, CPU, RAM, GPU, driver, CUDA, Python and all package versions; absolute input/output paths; scene/data split; asset URLs and SHA-256; config hash; seed; policy path/hash or `none`; camera intrinsics/extrinsics, axes/quaternion order and scale; start state, goals/gates and termination; UTC start/end, wall and simulated duration; timeout, process exit and errors. A's camera route is in Nerfstudio transformed coordinates and must not be called metric until dataparser scale is verified. For native GRaD-Nav route use author `gate_mid` bounds and inspect planner output, with a hover-start to waypoint sequence; log start, gate geometry and termination from frozen config/code.

Sample GPU memory (`nvidia-smi --query-compute-apps=pid,used_gpu_memory` plus GPU total) every 1 s during any GPU run, including failures. Time after at least five warmup renders/control steps and `torch.cuda.synchronize()` around GPU intervals. Report render images/s separately from actor inference latency, control Hz and encoded video playback FPS. A pass: five finite, openable PNGs and depth arrays with logged poses and dimensions. B pass: 20 finite states and 20 bounded commands, nonzero simulated duration, no exception. C pass: valid matching checkpoint and one fully logged episode with explicit outcome; no success claim merely from process exit.

Collect evidence during long runs every 5 min and on error, not only at completion. From a separate terminal, use `while kill -0 <audit-pid> 2>/dev/null; do rsync -a --partial "$AUDIT/runs/$RID/" "$DURABLE/grad-nav/$RID/"; sleep 300; done; rsync -a --partial "$AUDIT/runs/$RID/" "$DURABLE/grad-nav/$RID/"` with `DURABLE` set to a non-ephemeral mounted disk. Also run the final `rsync` after failure. Copy configs, patches, trajectories, frames/videos, logs and small assets. Large scene archives may remain at a verified retrievable URL only after SHA-256 and access are independently confirmed; otherwise copy them too. After transfer, run `(cd "$DURABLE/grad-nav/$RID" && sha256sum -c manifest.sha256)`, open sample PNGs with Pillow and check video with `ffprobe`, and parse every JSONL line. Do not delete host data before verification or stop unrelated processes.

## R4R decision frame and learning guide

Indoor obstacle and gate navigation are relevant as visual-control and sim-to-real research examples, with photorealistic appearance and differentiable dynamics. Limits: the released maps are small indoor/gate scenes; obstacle reward uses forward-FOV point distance, not swept body-volume collision; camera/scale/lighting assumptions may not match R4R. Outdoor navigation, sparse capture, unseen views, open sky and high-speed racing are **research questions**. Racing needs gate timing, vehicle aero/control limits and motion blur validation. Replacing Unreal visuals with splats is feasible to test for RGB appearance, but does not replace collision geometry, physics, dynamics, sensor effects, mission logic or reliable novel views. Keep native scene reproduction separate from a later common-scene comparison: one measured outdoor scene, known metric scale and calibrated route/camera, render matched camera poses in Unreal and 3DGS, inspect held-out views and geometry, then only assess closed-loop outcomes.

The human should read, in order: `utils/gs_local.py` (scene loader, camera and per-camera render); `envs/assets/quadrotor_dynamics_advanced.py` (dynamics and quaternion convention); `envs/drone_long_traj.py` (observations, actions, reward, bounds); `utils/point_cloud_util.py` (FOV obstacle distance); `algorithms/gradnav.py` and `models/actor.py` (training versus play, checkpoint schema); `examples/train_gradnav.py` and `examples/cfg/gradnav/drone_long_traj.yaml` (entry point/config). Learn coordinate frames, metric scale, camera calibration, Gaussian artifacts, reward/termination and time versus throughput before supervising claims.

## Current blockers

Shell GitHub DNS and `gh` API failed locally; source was inspected through web pages. Exact commit SHA is visible in GitHub history but has not been cloned or independently checked. Drive assets, their hashes/sizes/licenses, actual configs/checkpoints, compatibility versions and pretrained policy weights remain unverified. First Mate executable was not on PATH; no backend was assumed or changed. Hardware-dependent scripts have not run. Review [sources.md](sources.md) and [asset-inventory.csv](asset-inventory.csv) before phase 2.
