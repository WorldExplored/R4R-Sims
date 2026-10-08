# TravelUAV / OpenUAV simulator audit — phase 1 handoff

**Status, 2026-10-04:** source and release metadata investigated; syntax and light logic checked locally; **no UE scene, GPU policy, benchmark episode, or Gaussian reconstruction executed**. The source checkout is pinned to `5cc26e9a4a55b9c788e918f7c3bb2dc5076a85e6`. This candidate is separate from other R4R audits. The local Mac did not receive large assets. All findings below are preliminary until phase 2. See [source ledger](sources.md), [asset inventory](asset_inventory.md), and [slide outline](slides.md).

## What this system is

The authors' **OpenUAV** is a UE4/AirSim scene and flight platform. **TravelUAV / UAV-Need-Help** is the outdoor target-search navigation dataset and evaluation task on that platform. **LLaMA-UAV** is the released learned policy; it is not a second simulator. The old `buaa-colalab/TravelUAV` repository is an author-associated earlier version of the same code. The ground navigation R2R benchmark is unrelated. The code and paper provide no released indoor or drone-racing benchmark for this stack.

```text
UE4 Linux scene executable + AirSim settings
  → AirSim RGB/depth/IMU/state camera rig (five directions)
  → [A] known reference poses → RGB/depth/camera records
  → [B] prescribed world-frame waypoints → SimpleFlight moveOnPathAsync
        → actual state + sensor stream (controller/physics loop)
  → [C] target description + assistant notice + image/state history
        → Vicuna-7B/LLaMA-UAV/EVA/QFormer → coarse target
        → trajectory-completion model → 3-D world waypoints
        → SimpleFlight loop → new observations
        → Grounding DINO stop decision → per-episode outcome
```

The A route calls `simSetKinematics` for each pose and **does not demonstrate control or physics**. B and C reset state with `simSetKinematics`, then command `moveOnPathAsync` at 1 m/s; achieved poses must be measured. The C assistant with `always_help=True,use_gt=True` uses reference-route information. Keep that condition visible in any comparison. No random weights, scripted substitute policy, DAgger, or training are part of this audit.

## Selected reproduction and acceptance

Use the authors' Linux `ModernCityMap` scene from the `closeloop_envs` archive and one official `seen_valset` episode, `ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f`. It has 33 index rows in the released split; those rows point to **one** `merged_data.json`. This is a deterministic smoke test, not the paper's 1,410-episode Test Seen score. The first six reference states form A's known camera route and B's prescribed path; C receives the unmodified instruction and reference episode, with at most ten learned decisions.

| Level | Acceptance | What remains unproved |
| --- | --- | --- |
| A | Six 5-view RGB/depth captures open, nonempty camera poses and FOV are logged, actual camera times/poses and reference states are separate, and all files hash. | Navigation, collision handling, sparse-view fidelity, real-world transfer. |
| B | `moveOnPathAsync` returns state/IMU/image observations and a nonempty achieved trajectory; at least one measured state differs from requested route; timeout/collision/termination is explicit. | Learned policy or paper score. |
| C | Only released weights load; `policy_trace.jsonl` contains instruction, coarse and refined waypoints, stop decision, latency; output images/logs open; official metric code can score this one episode with denominator one. | Full Test Seen/UO/UM performance or performance on an R4R Gaussian scene. |

If the selected episode proves malformed or incompatible, record the failure and select the next lexicographic `ModernCityMap` episode from the pinned split. Give the replacement a new run ID and preserve the original failure. Do not silently choose a different map, checkpoint, or model.

## Machine to provision

**Recommended:** x86-64 Ubuntu 22.04 LTS workstation or GPU VM with **one NVIDIA RTX 6000 Ada 48 GB**, **16 vCPU, 64 GB RAM, 300 GB SSD**, installed NVIDIA driver compatible with CUDA 11.8 (NVIDIA's 11.8 release notes list Linux 520.61.05 as the toolkit minimum). A single host avoids the code's multi-host RPC assumptions. The 48 GB choice leaves capacity for a UE scene and the 7B policy/DINO/trajectory models on one GPU; it is an engineering margin, **not a measured minimum**. GPU allocation and render/ML memory remain to measure independently with `nvidia-smi`. CUDA-enabled PyTorch 2.0.1 cu118 is the author's installation target. No desktop GUI is assumed; `-RenderOffscreen` still needs a working NVIDIA graphics driver and must be tested. Native builds shown by the author use Linux shell launchers; do not provision macOS for execution.

**Cheaper trial for A/B:** Ubuntu 22.04 with one RTX 4090 24 GB, 8 vCPU, 32 GB RAM, 200 GB SSD, with free-space and VRAM gates before download/run. The 24 GB card is a plausible single-scene renderer test, not verified for C on the same GPU; stop if GPU memory or disk headroom is insufficient. No 8×A100 cluster is indicated for this smoke run. The paper's 8×A100 report describes training/parallel throughput, not inference VRAM, single-scene FPS, or render requirements.

Estimated hands-on installation: 2–4 h for a prepared Ubuntu host plus network transfer; transfer/extraction may take many hours depending on bandwidth and archive expansion. A/B probe is capped at 90 s after scene startup; scene startup is capped at 60 s. C evaluation is capped at 600 s after server startup; server lifetime is 900 s. Those are **budgets**, not measured runtimes. Allow 1–2 h to inspect and verify outputs. CPU load, RAM peak, scene VRAM, policy VRAM, total storage, and throughput are pending measurement.

## Exact host setup and asset commands (unexecuted; Ubuntu host only)

Copy this directory intact to `/workspace/traveluav-openuav`. Preserve `upstream/.git`, `eval_observe.patch`, and the local metadata. Run in Bash. Commands below install only into the host's conda environment; no system security/authentication change is needed. `p7zip-full` and a working NVIDIA driver must already be available or be installed by the host owner.

```bash
AUDIT=/workspace/traveluav-openuav
cd "$AUDIT"
git -C upstream rev-parse HEAD
git -C upstream status --short
git -C upstream diff > phase2-before.patch
git -C upstream diff --staged > phase2-before-staged.patch
df -h "$AUDIT"; free -h; nvidia-smi
command -v 7z; command -v timeout; command -v ss
conda create -y -p "$AUDIT/.conda-ab" python=3.10
conda activate "$AUDIT/.conda-ab"
python -m pip install --upgrade pip
python -m pip install airsim==1.8.1 numpy==1.26.3 Pillow==10.2.0 huggingface_hub==0.27.1
mkdir -p assets/downloads/env assets/downloads/data assets/envs assets/dataset assets/models
```

Download **only** these scene and navigation partitions; do not clone the entire 83.7 GB scene or 483 GB data repository. HF revisions and per-object SHA-256 are pinned in `asset_inventory.md` and `expected-sha256.txt`. Each download is resumable in HF's cache, but treat network errors as blockers. Use `timeout 3h` per bounded call if the host scheduler requires a hard cap.

```bash
huggingface-cli download wangxiangyu0814/TravelUAV_env --repo-type dataset --revision 44de5739a95a2f6a88767446421cddada9606642 --include 'closeloop_envs.*' --local-dir "$AUDIT/assets/downloads/env"
huggingface-cli download wangxiangyu0814/TravelUAV --repo-type dataset --revision faa8f2514156455ea7423464cc1295e6f92575cb --include 'ModernCityMap.*' --local-dir "$AUDIT/assets/downloads/data"
cd "$AUDIT" && head -n 8 expected-sha256.txt | sha256sum -c - > assets/download-hash-check.log
cat assets/download-hash-check.log
7z l -slt assets/downloads/env/closeloop_envs.zip > assets/env-expanded-list.txt
7z l -slt assets/downloads/data/ModernCityMap.zip > assets/data-expanded-list.txt
7z t assets/downloads/env/closeloop_envs.zip
7z t assets/downloads/data/ModernCityMap.zip
7z x -y assets/downloads/env/closeloop_envs.zip -oassets/envs
7z x -y assets/downloads/data/ModernCityMap.zip -oassets/dataset
du -sh assets/downloads assets/envs assets/dataset
find assets/envs -name 'ModernCityMap.sh' -o -name 'ModularPark.sh'
find assets/dataset -path '*/00ac4ad3-1b8b-410d-9abc-43b65186571f/*' -type f
```

Check the extraction layout before running. The host scripts require `assets/envs/closeloop_envs/ModernCityMap.sh` and `assets/dataset/ModernCityMap/<episode-id>/merged_data.json` plus `mark.json`. If the archive adds a wrapper directory, move that wrapper under the expected asset root and record the move in `commands.log`; do not edit upstream code. `chmod +x` the scene shell launcher if archive permissions lost. Expanded sizes are measured from `7z l` and `du`, never guessed from the compressed total. Retain all eight compressed partitions until their pinned HF URL/hash has been verified retrievable from a second machine or a durable copy is made.

For C, create a **separate** conda environment so A/B remains usable if the legacy model requirements conflict. The author advertises the following checkpoints, all required; local availability is pending. Check base-model and scene-use terms before redistribution.

```bash
conda create -y -p "$AUDIT/.conda-c" python=3.10
conda activate "$AUDIT/.conda-c"
python -m pip install --upgrade pip
python -m pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
python -m pip install -e "$AUDIT/upstream/Model/LLaMA-UAV"
python -m pip install -r "$AUDIT/upstream/requirement.txt"
huggingface-cli download wangxiangyu0814/llama-uav-7b --revision 6cd1a273ba26338a1be4eb93b43489ee0099fbce --local-dir "$AUDIT/assets/models/llama-uav-7b"
huggingface-cli download wangxiangyu0814/traveluav-traj-model --revision 583a3f6b9111fd80e76d6905eaa0f1793f3fd03f --local-dir "$AUDIT/assets/models/traj"
huggingface-cli download lmsys/vicuna-7b-v1.5 --revision 3321f76e3f527bd14065daf69dad9344000a201d --local-dir "$AUDIT/assets/models/vicuna-7b-v1.5"
mkdir -p "$AUDIT/assets/models/LAVIS"
curl -fL --retry 3 --connect-timeout 30 -o "$AUDIT/assets/models/LAVIS/eva_vit_g.pth" 'https://storage.googleapis.com/sfr-vision-language-research/LAVIS/models/BLIP2/eva_vit_g.pth'
curl -fL --retry 3 --connect-timeout 30 -o "$AUDIT/assets/models/LAVIS/instruct_blip_vicuna7b_trimmed.pth" 'https://storage.googleapis.com/sfr-vision-language-research/LAVIS/models/InstructBLIP/instruct_blip_vicuna7b_trimmed.pth'
curl -fL --retry 3 --connect-timeout 30 -o "$AUDIT/assets/models/groundingdino_swint_ogc.pth" 'https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/groundingdino_swint_ogc.pth'
cd "$AUDIT" && tail -n 6 expected-sha256.txt | sha256sum -c - >> assets/download-hash-check.log
cat assets/download-hash-check.log
sha256sum assets/models/LAVIS/*.pth assets/models/groundingdino_swint_ogc.pth > assets/external-model-sha256.txt
cp assets/download-hash-check.log assets/verified-sha256.txt
cat assets/external-model-sha256.txt >> assets/verified-sha256.txt
```

The pinned author adapter is ~1.74 GB; trajectory checkpoint ~1.98 GB; Vicuna base ~13.48 GB. EVA, QFormer and DINO sizes are pending headers/download; record actual byte counts. The first 8 expected hashes cover 28.50 GB of scene/data archives. Total known compressed/weight bytes are ~45.70 GB before expanded data, packages, output, and any backup. On an inaccessible URL, record HTTP status/time and stop C; do not substitute a similarly named model. The author's nested processor directory supplies preprocessing config, **not** EVA weights or a tokenizer. Vicuna supplies tokenizer files.

## Exact preflight, run, and collection (unexecuted until Ubuntu GPU host)

Use **fresh run IDs** generated by each runner. They refuse occupied ports and kill only their own scene process/group. `host.sh` runs direct AirSim for A/B without the upstream scene server. C uses the author server and released eval pipeline, with the isolated logging patch already in this checkout. If re-cloning a clean commit, run `git apply --check "$AUDIT/eval_observe.patch"` then `git apply "$AUDIT/eval_observe.patch"` exactly once. This patch logs coarse/refined actions, intermediate episode observations, camera poses and policy latency; it does not alter predicted actions or stop thresholds. It adds RPC and disk overhead to measured control throughput. Inspect `upstream.patch` in every run.

```bash
cd "$AUDIT"
conda activate "$AUDIT/.conda-ab"
./host.sh preflight
./host.sh a
./host.sh b
conda activate "$AUDIT/.conda-c"
./policy_smoke.sh
./collect.sh "$AUDIT/runs/<actual-run-id>" "$AUDIT/collections"
```

Do A, inspect results, then B; run C only after all required checkpoints pass the hash checks. `policy_smoke.sh` uses one GPU and one scene, `--batchSize 1`, `--maxWaypoints 10`, Test Seen L1 assistant, seed 100. Its server is port 30000, AirSim scene port 30001, DDP port 20001. The unmodified `scripts/eval.sh` uses 25000 and 80005 and must **not** be used. The upstream C scene server launches child graphics processes and suppresses their stdout; the wrapper stores the server log and kills its own process group at exit. Do not stop any unrelated process. Before a retry, check `ss -ltnp` and `ps` and use a new run ID.

While long downloads or runs proceed, collect a snapshot every 5–10 min and immediately after failure, not only at completion. The run folder contains `run.json`, `commands.log`, `console.log`, server/scene logs, hardware/version files, `reference_route.jsonl`, `actual_vehicle.jsonl`, `actual_camera.jsonl` or C `camera_poses.jsonl`, `actions.jsonl` or C `policy_trace.jsonl`, raw frames/depth and official eval output. A/B sample all five cameras every known route pose or every 0.2 wall seconds during B; C traces each learned action and writes the current episode per step. Missing entries are missing data, not interpolated measurements. `run.json` records expected timeouts and status; file hashes and artifact validation are added by `collect.sh`. Commands piped to `tee` record `${PIPESTATUS[0]}` rather than `tee` status. A failed run folder is still evidence.

```bash
# Snapshot without interrupting the run; replace RUN with the active path.
RUN="$AUDIT/runs/<actual-run-id>"
mkdir -p "$AUDIT/collections/live-$(basename "$RUN")"
rsync -a --partial "$RUN/" "$AUDIT/collections/live-$(basename "$RUN")/"
# After completion or failure, archive and validate. Transfer the archive to durable storage.
./collect.sh "$RUN" "$AUDIT/collections"
sha256sum -c "$AUDIT/collections/$(basename "$RUN").tar.gz.sha256"
tar -tzf "$AUDIT/collections/$(basename "$RUN").tar.gz" >/dev/null
```

Transfer each run archive plus the scripts/config, `eval_observe.patch`, split/episode metadata, asset inventory, verified hashes, and selected scientific assets to durable storage. For large author assets, either copy the verified bytes or retain the exact revision URL plus SHA-256 **and verify retrieval from a separate machine/account** before terminating a rented host. Keep original zip partitions when retrieval cannot be confirmed. Check archive hash **after transfer**, `tar -tzf`, `validation.json`, and open sampled PNG/JSON/depth arrays. No cleanup or host deletion until this succeeds.

## Measurement and interpretation

Report four independent rates: scene RGB/depth render/RPC throughput (`simGetImages` wall time, with dimensions and camera count), learned model latency (CUDA synchronized and excluding first warmup decision), achieved control/update rate (state timestamps and wall intervals), and encoded-video playback FPS if a video is made. Never call playback FPS simulation FPS. Sample `nvidia-smi` at 1 s and log scene-only A/B memory separately from C policy+scene memory. Use `run.json` and timestamped `actual_vehicle`/camera records to distinguish wall time from simulation time (`ClockSpeed` and pauses can differ). The upstream policy path clips metric depth to 8-bit; A/B saves raw float depth in metres for future Gaussian comparison. Measure intrinsics from 256×256 and 90° only after confirming scene `simGetCameraInfo`; record camera offsets/FOV and AirSim NED, quaternions xyzw, metres. Do not assume the reference vehicle trajectory equals actual camera poses.

Official Test Seen has 1,410 episodes; this smoke has denominator **one**. In the released evaluator, stop within 20 m is success; crossing within 20 m can yield oracle success. Easy paths are ≤250 m, hard >250 m. `utils/metric.py` computes SR/OSR as successful/oracle episode directories divided by all selected result directories, NE as final-to-reference-end Euclidean distance, and SPL with zero on failure and a reference length reduced by 20 m. Save the raw per-episode outcome and stop/collision/timeout reason before any aggregate. Published results are only comparison context, never locally measured results.

## R4R fit and Gaussian replacement

| Use case | Preliminary fit | Limits / decision gate |
| --- | --- | --- |
| Outdoor urban navigation | Strongest native match: long 3-D object search with multi-view RGB/depth, human trajectories, language and a released policy. | Scene art and target objects differ from R4R; assistant can use GT route; no real-drone transfer measured. |
| Outdoor sparse/natural scenes | Platform lists island, desert, roads and forest, but sparse-view reconstruction robustness is open. | Choose one exact natural scene, measure view coverage and held-out camera views; do not infer fidelity from a UE demo. |
| Indoor navigation | AirSim can render/control indoors in principle, but this release has no verified indoor executable, episodes or metrics. | Requires a separately licensed/validated scene and task; cannot claim TravelUAV indoor benchmark support. |
| Racing | Dynamics APIs may support waypoint flight; TravelUAV has no racing gates, timing, penalties, track split or racing policy. | A separate racing benchmark such as AirSim Drone Racing Lab would be another candidate, not evidence for this model. |
| Real drone research | Useful for perception/action interface, failure logging and sim-to-real hypotheses. | Sensor noise, latency, dynamics, weather, safety envelope and real-world validation are missing. |

For Gaussian splats, first compare **native UE scene rendering** with **an R4R reconstruction** on a common metric camera route: calibrated multi-view intrinsics/extrinsics, NED↔reconstruction transform and scale, fixed exposure/time, held-out viewpoints including sparse/occluded regions. Then test whether the splat renderer supplies **five synchronized RGB views and depth with the same semantics/range** as the learned model input. A plain RGB splat renderer does not establish metric depth, collision mesh, dynamic object behavior, controllable object placement, or physically coupled camera motion. A wrapper must keep the AirSim state/controller and replace camera observations at corresponding poses/timestamps, or explicitly replace physics too. Report per-view image/depth quality, navigation task outcome, render latency and failure regions separately. Native-scene policy success does **not** establish policy performance on a Gaussian reconstruction. No scene training or novel-view fidelity claim is made in phase 1.

## Blockers and what the human should learn

Current blockers: no Linux NVIDIA host; scene/data compressed archives and all policy weights absent locally; expanded sizes unmeasured; external EVA/QFormer/DINO sizes/hash/access not verified; base-model terms and third-party UE asset rights need factual review; upstream scene server and AirSim graphics behavior remain unexecuted. The local shell initially lacked GitHub DNS, but an escalated read-only Git query and source-only clone succeeded. Firstmate was found as a checkout at commit `260c4f089449c33f08c31df714ca9cfe2a25b50a`; its own `docs/codex-app-backend.md` says Codex App is not a selectable runtime backend. Direct Codex execution was used; no orchestration installation or reconfiguration occurred.

Learning guide (read in order): `airsim_plugin/AirVLNSimulatorServerTool.py` for scene spawning/ports/camera rig; `AirVLNSimulatorClientTool.py` for controller versus state setting and sensor calls; `src/vlnce_src/env_uav.py` for episode schema, instruction and target placement; `src/model_wrapper/travel_llm.py` plus `src/model_wrapper/utils/travel_util.py` for observation/action contract and preprocessing; `src/vlnce_src/eval.py`, `closeloop_util.py`, and `utils/metric.py` for stop and denominator; `utils/env_vector_uav.py` and `utils/closeloop_util.py` for observation assembly and saved trajectories. Plot reference route, actual vehicle path, and actual camera frusta in one NED 3-D view, with collision/stop markers and image timestamps. The human should be able to identify an episode's instruction, explain each coordinate transform, distinguish commanded/achieved pose, and read the raw failure log before interpreting any metric.

**Follow-up prompt once hardware exists:** “Use `/workspace/traveluav-openuav/handoff.md` on the provisioned Ubuntu 22.04 RTX 6000 Ada host. Execute the pinned A and B probes, then the one-episode released-weight C smoke if all assets validate. Collect and transfer every run and verify hashes. Report measured scene VRAM, policy VRAM, render throughput, synchronized policy latency, control rate, output integrity, failures, and any deviations from the handoff. Do not run DAgger/training or claim Gaussian/real-world transfer.”
