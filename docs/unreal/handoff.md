# Unreal / Real4Real execution handoff

**Audit date:** 2026-10-08. **Execution host:** user-supplied RunPod Ubuntu 22.04.5 instance, NVIDIA RTX A5000 24 GB, driver 580.178.04, 50 GB RAM cgroup, 9 advertised vCPU (7.65 cgroup effective), 120 GB root disk and separate 112 GB `/workspace` volume. The provider UI displayed $0.30/hour; billing and storage charges were not independently checked. `vulkaninfo` found the NVIDIA Vulkan device and the packaged game log selected VulkanRHI. This supports hardware rendering, not a minimum-hardware claim. Epic recommends Ubuntu 22.04, 32 GB RAM, at least 8 GB graphics memory and NVIDIA driver 570+ for Linux UE development [1].

**Latest focused session:** [focused-validation.md](focused-validation.md) records yaw sanity, the landing-state failure reproduced without route/images, and a corrected final-color mesh plus one dark splat frame. It supersedes the earlier S final-color blocker below; all original runs remain retained.

**Closeout:** further Unreal GPU experiments are stopped. This audit did **not** demonstrate a complete R4R workflow. Camera sanity passed. **B remains partial and fails end-to-end acceptance**: takeoff returned False despite airborne movement; land returned True despite LandedState remaining Flying after ground contact. A usable mesh capture and one visible splat frame demonstrate narrow integration, while appearance remains unvalidated. The importer loses higher-order SH coefficients when present; that loss does **not** establish the cause of the dark red frame. The next renderer comparison needs the **same PLY**, matched cameras, retained-attribute checks and color/exposure analysis before another dataset. The updated presentation is `Unreal_R4R_Audit_2026-10-08_v3.pptx`; v2, [the earlier handoff](archive/handoff-d981d5a.md) and all raw attempts remain preserved.

**Recovery and shared-host check:** [recovery.json](../../results/unreal/closeout-20261008/recovery.json) reverified **18 run folders / 360 files / 69,923,660 B**, all three input ZIPs against VM-source hashes, the 128-file compiled plugin, and the imported project/map/point-cloud assets. It reopened 70 PNGs and 37 depth arrays; macOS produced previews for all three copied videos. All Unreal scientific inputs and essential edited project assets are recoverable locally. [instance-dependencies.json](../../results/unreal/closeout-20261008/instance-dependencies.json) records no simulator/GPU process on this A5000 and no dependency among the inspected audits. `TRAVELUAV` uses separate A6000 host `209.137.198.205`; `RFLY SIM`, `GRADNAV` and `AIRSIM` are idle phase-1 tasks. This is a documented observation, not a provider-wide guarantee. The instance remains running and was not terminated.

**A5000 cleared for reuse at the user's request:** Unreal installations, scientific asset copies, ignored run outputs and known temporary audit files have been removed from `63.141.33.148:22134` after local source-hash verification and GitHub publication. [Cleanup result](../../results/unreal/a5000-cleanup-20261008/result.json) and [postcheck](../../results/unreal/a5000-cleanup-20261008/postcheck.json) retain the exact paths and disk/access checks. The residual 98-file / 6,338,480-byte setup/script/project backup is local at `/Users/srreyanshsethi/Downloads/AL/R4R-Sims/artifacts/unreal/unreal-final-backup-20261008/`, verified against its VM-created source manifest. Automatic approval review rejected deleting whole checkouts, so both source-only repositories and all non-Unreal simulator files remain. The running instance, SSH access, NVIDIA driver and system packages were preserved. No connection or change was made to the A6000. Historical execution commands below now require restoring the locally preserved archives/project first.

## Decision and experiment levels

The central R4R question is whether a small **real** capture of a residential, suburban or campus site below 100 m can supply trustworthy camera views along **new** drone trajectories. Capture at 15 m and rendering at 50 m remains a research goal. No AirLab captured scene, calibrated holdout, or trained scene was supplied. Native Blocks verifies integration only.

```text
A  8 target NED poses → AirSim ComputerVision pose RPC → packaged UE Blocks
   → RGB + DepthPlanar + actual rig/camera poses (no flight dynamics)
B  estimated position → scripted P velocity action → SimpleFlight/FastPhysicsEngine
   → vehicle state + UE collision → camera RGB/DepthPlanar (closed loop)
C  released policy observations → learned actions → task outcome: no compatible artifact
S  author Gaussian PLY → UE 5.5.4 + Italink plugin → one SceneCapture export; appearance unresolved
```

| Level | Current result | Valid inference |
| --- | --- | --- |
| A | **Demonstrated.** `ue-20261008T215319Z-a-5fe9b7c3`, exit 0, eight opened 640×480 RGB/depth pairs, eight requested and actual poses. | Pose-driven stock scene rendering works. |
| B | **Partial; end-to-end acceptance failed.** Original square flight reached five waypoints; focused isolation reproduced Flying after floor contact despite True land RPC. Takeoff returned False despite achieved airborne height. | Airborne movement and control/state plumbing work. Complete B success and the cause of RPC/state discrepancies remain unproven. |
| C | **Blocked.** Blocks release has no identified compatible pretrained weights, inference/preprocessing, task interface or success protocol. | No policy outcome. The P controller is not a learned policy. |
| S | **Build/import and one-frame final-color export demonstrated.** The initial eight images failed; a later corrected light direction/intensity produced a visible final-color cube and one very dark splat image in `...573e44a0`. | Appearance/coverage, useful observations, depth and fidelity remain unvalidated. See focused session. |
| Common-scene comparison | **Not tested.** No matching mesh/splat representation of one scene. | Blocks and a different splat scene cannot form a fidelity benchmark. |
| Held-out real scene | **Blocked on lab data.** No approved AirLab calibrated capture or train/test split. | No conclusion about sparse outdoor coverage, altitude extrapolation, or real-drone transfer. |

## Native input, control and observations

`audit.py` uses AirSim client 1.8.1 with packaged Linux Blocks v1.8.1. AirSim source tag `v1.8.1` resolves to `96235148a332fe7cb3d3525a0720e26faaca99e0`; the separately released binary is verified by its own ZIP and executable hashes, **not** by a source-to-binary attestation. Blocks loads `FlyingExampleMap` under the AirSim game mode. Its packaged scene assets carry separate terms from the MIT AirSim source. No scene train/test split exists.

A sends `simSetVehiclePose` to a ComputerVision rig at `(0,0,-2), (0.5,0,-2), (1,0,-2), (1,0.5,-2), (1,1,-2), (0.5,1,-2), (0,1,-2), (0,0,-2)` in AirSim NED metres, identity quaternion. Eight `simGetVehiclePose` and image-response camera centers matched these targets exactly to recorded precision; camera and rig offsets were zero in this configuration. Three warmup image calls were discarded. Captures started after 0.25 s settling. This does not exercise a drone controller.

B uses `getMultirotorState().kinematics_estimated.position` as the outer controller observation. For each of five waypoints on a 1 m square at `z=-2 m`, it computes `v_i=clip(0.7*(target_i-estimate_i), -0.7, 0.7)` m/s and sends `moveByVelocityAsync(vx,vy,vz,duration=0.2)` with AirSim default drivetrain/yaw settings. Target cadence 5 Hz, 0.25 m waypoint tolerance, 15 s each waypoint, 15 s takeoff, 20 s landing, 180 s total run, independent 190 s watchdog. SimpleFlight supplies the inner controller; AirSim's FastPhysicsEngine supplies multirotor state while UE contributes rendered images and scene collision. B logs estimated state, `simGetGroundTruthKinematics`, `simGetVehiclePose`, `simGetCollisionInfo`, image-response camera pose and requested actions separately. GPU samples target 1 Hz. API calls are sequential, so B RGB/depth and state are **not synchronized pairs**. No engine seed API was set.

Coordinates: AirSim reports right-handed NED metres (+X north, +Y east, +Z down); UE uses left-handed Z-up centimetres. Each quaternion JSON object has named `w`, `x`, `y`, `z` fields despite a historical `orientation_xyzw_ned` key in raw records. The `front_center` camera FOV response was 89.903625°, giving estimated `fx=fy=320.5387 px`, `cx=320`, `cy=240` for 640×480 under a square-pixel pinhole assumption. Response camera pose is recorded per RGB frame. A response pose and immediately queried camera-info pose matched exactly; B differed by up to 0.0646 m because these are sequential RPCs while the vehicle moves. RGB and planar depth are requested together, but only the RGB response timestamp is retained; depth-specific timestamp/extrinsic agreement is **unmeasured**. `DepthPlanar` means optical-axis plane distance in metres, not ray length. A representative first-frame wall center returned 23.09375 m, ground sample 6.0195 m and sky/far sample 13,456 m; the visualized depth plot clips at 50 m. A targeted first-frame registration check found the depth sky/wall boundary at rows 75, 75, 77, 75, 75 for image columns 100, 200, 300, 400, 500; the strongest local RGB edge within ±5 rows matched each row exactly. This is a five-column spatial check, not a whole-image or temporal calibration.

## Measured A/B findings and failures

| Measure | A replay | B waypoint run `...33710b89` | B landing-check run `...a3d4be49` |
| --- | ---: | ---: | ---: |
| Wall elapsed | 33.50 s | 60.78 s | 64.75 s |
| RGB/depth pairs | 8 | 7 | 8 (including pre-takeoff and post-contact) |
| Median image RPC wall latency | 3.129 s | 3.159 s | 3.210 s |
| Median image interval | 3.389 s | 5.280 s | 5.355 s |
| In-flight image cadence from median interval | n/a | 0.189 Hz | 0.187 Hz |
| Median inter-command rate | n/a | 4.695 Hz | 4.696 Hz |
| Command rate over action span | n/a | see `analysis.json` | 2.007 Hz; camera waits create gaps |
| Sampled peak GPU memory used | 862 MiB | 863 MiB | 769 MiB |
| State samples / velocity commands | 8 / 0 | 74 / 69 | 94 / 69 |
| Simulation first-to-last state | not logged for A | 33.61 s | 48.83 s |
| Waypoint errors | n/a | nearest-recorded-state: 0.156–0.232 m | five explicit `waypoint_reached`: 0.228–0.248 m |
| New collision relative to spawn timestamp | n/a | none observed during route | `Ground_6` on descent at 58.57 s |
| Final `LandedState` | n/a | `Flying` at end of route | `Flying` after 10 s polling; exit 1 |

Image RPC latency includes render, transport and encoding, so it **cannot be called renderer frame time or throughput**. The B image cadence is much lower than the intended “up to 2 Hz.” No synchronized GPU timer, renderer throughput, learned-policy latency or real-time playback measurement exists. Replay videos are deliberately encoded at **2 playback FPS**, separate from acquisition cadence. GPU memory is 1 Hz `nvidia-smi` whole-GPU sampling, not isolated process peak; a single live snapshot found UE RSS about 709 MiB and cgroup memory 2.50 GB, not a peak RAM requirement. The A run had 28 GPU samples and the B landing-check run 59.

The initial A attempt `...f0246d36` failed on an RPC startup race; `...5fe9b7c3` corrected it. A B preflight attempt `...e868ec1c` had no run directory because an earlier game process still held the port; only its local supervisor output survives, so it has no source manifest. Process ownership was fixed. `...d415e2e7` stopped on a pre-existing `Ground_6` spawn collision. The later runs recorded that baseline timestamp and stopped only on a newer collision. The floor contact in the final run is a **new** collision, not the spawn baseline. `...eddeea80` recorded five waypoint events and an immediate post-land observation but no confirmed `LandedState`. These attempts have separate IDs and retained errors. Landing remains a concrete simulator/control-path defect to investigate before navigation benchmark claims.

## Gaussian runtime result and next gate

The official UE 5.5.4 installed archive extracted with exit 0 and supplied Vulkan 580.178.04 on the existing A5000. `RunUAT.sh BuildPlugin -TargetPlatforms=Linux` built Italink commit `411f879985719ce69eaaf15d58152c551e2719b1` in **1 min 46 s**; the compiled 45,291,029-byte plugin file set is independently source-manifested and copied locally. The author `chinese_vase.ply` imported to `/Game/Gaussians/chinese_vase` and saved as a `.uasset` with `/Game/Maps/VaseSmoke.umap`. The data interface in the saved actor points to that imported asset. This is a real Linux compile/import result, not a camera-success claim.

| S run ID | What happened | Acceptance |
| --- | --- | --- |
| `ue-20261008T222943Z-s-8434c18c` | Build and import passed. Python used nonexistent `SceneCapture2D.get_capture_component2d`; UE process still exited 0. | **Failed export.** Traceback and project asset retained. |
| `ue-20261008T223559Z-s-8c7e26a7` | Python property fixed. One valid 640×480 PNG byte stream exported under an extensionless filename; script rejected the missing `.png`. Its RGB extrema were 0–1. | **Failed export naming and image content.** |
| `ue-20261008T224031Z-s-fe9a3ea3` | Literal `.png` name and Niagara warmup; eight requested/actual centers and eight PNGs logged. All RGB channels stayed 0–1; Niagara was inactive immediately after warmup. Median inter-export wall interval 0.912 s is **not** valid scene-render throughput. The positional Python `Rotator` call also gave unintended rotations, so these are not a validated route. | **Failed usable RGB and pose orientation.** No depth. |
| `ue-20261008T224552Z-s-control-10f8cdbd` | Saved map control: imported asset bound to Niagara, component active after one tick; immediate capture of a lit UE cube and splat was black. | **Failed immediate capture control.** |
| `ue-20261008T224847Z-s-control-83b490d9` | Correct named yaw and 32 real editor ticks. Cube base-color capture had RGB max 26; final-color cube and splat stayed 0–1. | **Base-color geometry only.** No valid final-color observation. |
| `ue-20261008T225105Z-s-control-e488bef0` | With 40 editor ticks and stronger light, cube base-color reached RGB max 228. Cube scene-color was 0; splat base-color and scene-color were 0, final color 0–1. | **Failed splat RGB.** The final-color path also fails a mesh control, so isolate that path before attributing cause to the plugin. |

All six S directories have a **VM-created** size/SHA-256 manifest, matched local copies, and decoded images where produced. The first three runs sampled whole-GPU memory at 1 Hz; the largest observed value was **765 MiB**, not a per-process or minimum VRAM measurement. The eight-image S run took 169.3 s wall including editor startup; these black frames cannot measure useful rendering throughput. No synchronized GPU render timer, splat depth, collision, policy latency or simulation time was measured. The original S script logged a post-export wall timestamp, not the exposure instant. The corrected future script now uses named `Rotator(roll=..., pitch=..., yaw=...)`, target and actual poses, FOV-derived pinhole intrinsics and separate capture-request/export-completion times; this correction is syntax checked but **has not produced a validated splat image**.

**Current next gate on the same A5000:** the focused session corrected the mesh final-color gate by reversing the light toward the visible face and reducing its saturating intensity. One dark splat frame exported; do not replay a route yet. Inspect its material, exposure and imported color against a reference for the same PLY/camera. The selected importer validates higher-order SH fields but does not retain them in its point/color structure. Useful appearance and view-dependent fidelity therefore remain open. The project and control scripts are preserved; no engine build or GPU change is needed. See [focused-validation.md](focused-validation.md) for measured results, exact preserved launchers and source references.

## Assets, install effort and host choice

The [Linux Blocks release ZIP](https://github.com/microsoft/AirSim/releases/download/v1.8.1/Blocks.zip) is **142,533,463 bytes**, SHA-256 `563e1da1b5d7303b9405c8736243ea92ab0a011b96a561f26f17563d105a404f`, ZIP integrity checked and expanded content **281,273,935 bytes**. The binary at `/tmp/r4r-ue-assets/LinuxBlocks1.8.1/LinuxNoEditor/Blocks/Binaries/Linux/Blocks` has SHA-256 in each `run.json`; the ZIP stays `/workspace/r4r_assets/Blocks_v1.8.1.zip`. An isolated Python environment at `third_party/unreal/venv` contains AirSim 1.8.1 and pinned NumPy/OpenCV/msgpack; the separate `analysis-venv` contains plotting dependencies. `libegl1` and `vulkan-tools` were needed for the host image. Installing packages, archive transfer, unpacking and RPC setup took multiple short iterations; budget **1–2 h human setup** for a fresh comparable host, plus 1–2 min each native run and collection. This is a planning estimate, not a measured fresh-install benchmark.

**Tested suitable machine class:** **Ubuntu 22.04 RTX A5000 24 GB graphics VM** with NVIDIA 570+ driver, at least 8 vCPU, 32 GB RAM and 120 GB root; a future provision should favor **150 GB root/scratch** around the 65.34 GB editor tree and 27.09 GB archive. Further experiments are stopped, and no active Unreal job requires keeping this instance. The actual host proved Vulkan/Blocks at 640×480 and has 50 GB RAM; 24 GB VRAM is headroom, not a minimum. For a cheaper packaged-Blocks-only repetition, an Ubuntu 22.04 NVIDIA Vulkan graphics VM with **8 GB VRAM, 4 core CPU, 32 GB RAM and 30 GB free disk** is consistent with Epic's editor recommendation but **unmeasured for this binary**; require a `vulkaninfo`/RGB smoke test before assuming compatibility. A future justified UE 5.5.4 project test can use the tested A5000 class with 60+ GB extraction/project headroom. Original 3DGS training hardware does not set runtime VRAM needs here; no scene or policy is trained.

The signed-in Epic page listed official `Linux_Unreal_Engine_5.5.4.zip` at 25.23 GiB (27,085,247,533 bytes from HTTP Content-Range), and recommends about 60 GB free for extraction. Its SHA-256 is `e20acd77e6caad42ee1bf0df1cb4c5077ceb1350817cfdacb554f4a594710383`; ZIP entries sum to 65,296,010,542 B, and the extracted tree measured 65,338,684,416 apparent bytes including directories. `unzip` exited 0. The ZIP was copied to local `third_party/unreal/assets/` and independently matched the **VM source** size/hash. The signed URL expires, so retain the verified local ZIP and [Epic Linux page](https://www.unrealengine.com/linux); no source-engine build was needed. Italink's sample `PlyExamples.zip` is 123,484,316 bytes compressed and 143,389,803 expanded; `chinese_vase.ply` is 22,798,434 bytes, 91,923 Gaussians with all required float attributes. Sample scene rights are not stated in the plugin MIT license; keep this private and do not redistribute it as a licensed dataset. See [assets.md](assets.md).

## Three splat architectures

1. **Inside UE:** the Italink plugin imports a Gaussian PLY and renders it through UE/Niagara. It replaces appearance for chosen objects; UE remains the editor/world renderer, scheduler, collision host and compositor. A drone B test would still need a UE5-compatible drone/control layer and an independently validated collision mesh. The UE4.27 packaged Blocks binary is not an editable UE5 project, so copying the plugin into it is not an integration route. The plugin descriptor lists Linux and README says UE5.5+; compilation and PLY import passed, while actual SceneCapture final-color imagery failed validation.
2. **External renderer, dynamics retained:** keep AirSim/UE or another simulator for time, drone dynamics, SimpleFlight, collision and non-camera sensors; feed actual timestamped camera poses/intrinsics to a splat renderer and return its RGB/depth to the controller. Only camera observation supply changes. A time/coordinate/exposure adapter and deadline-aware sensor replacement remain **unbuilt**. Offline pose replay through a standalone splat viewer would be level A, not closed-loop B.
3. **Remove UE:** another named component must own dynamics, control, sensor timing, collision geometry, task evaluation and logging. A visual splat renderer supplies appearance only. No complete replacement stack or validated adapter is identified by this audit.

Italink's importer converts PLY `(X,Y,Z)` metres to UE `100*(X,-Z,-Y)` centimetres, with quaternion `(X,-Z,-Y,W)`. This must be inverted when comparing camera paths. The scene's original coordinate frame and metric calibration are not documented by the sample ZIP, so object-only S is a rendering interface test. Depth of a splat, mesh/splat occlusion, translucent sorting and collision must be checked separately; a Gaussian point cloud is not an accurate physical surface by itself.

## R4R applicability and next scientific tests

| Use case | What this evidence supports | Required next evidence |
| --- | --- | --- |
| Indoor navigation | Native camera, state, velocity and collision APIs in a tiny stock map. | Realistic doors/obstacles, calibrated sensors, task/success definition, robust landing. |
| Outdoor navigation, including sparse scenes | UE can host a world and camera; this run has no outdoor reconstruction. | AirLab approved capture, scale/calibration, coverage below 100 m, vegetation and missing-surface tests, held-out views. |
| Racing | Timed action/state plumbing only. | Gates, racing course, high-rate camera/control, task metrics and compatible policy/controller. Current 0.187 Hz images are inadequate for a meaningful vision racing claim. |

Separate **sparse captured viewpoints** from **physically sparse vegetation**. Test view coverage, unseen altitude/angle, disocclusion, tree branches/leaves, moving objects, depth consistency and independently authored collision geometry. A stock Blocks scene answers none of these. Later, train reconstruction only on approved training captures, render calibrated held-out real camera poses at 15 m and higher altitudes including the proposed 50 m trajectory, compare paired images with specified masks/exposure and PSNR/SSIM/LPIPS, and report failure regions and downstream controller behavior. Training this scene is a later research phase, outside this audit. A native UE mesh-versus-splat comparison additionally needs the **same world representation** in both, matching poses, intrinsics, resolution, scale and lighting assumptions; UE materials and splat view-dependent color may still differ.

## Exact continuation and preservation commands

Current native commands, executed on the supplied Ubuntu host from `/root/R4R-Sims`, use the **working** binary and isolated Python. Use a fresh run ID; do not rerun A/B without a concrete validation reason. `bounded.py` owns only its game/process group. The supervisor writes a separate log and preserves the underlying exit status, even when shell output is piped through `tee` (use `set -o pipefail`).

```bash
cd /root/R4R-Sims
PY=third_party/unreal/venv/bin/python
ZIP=/workspace/r4r_assets/Blocks_v1.8.1.zip
EXE=/tmp/r4r-ue-assets/LinuxBlocks1.8.1/LinuxNoEditor/Blocks/Binaries/Linux/Blocks
$PY simulators/unreal/audit.py preflight --asset-zip "$ZIP" --exe "$EXE"
RID="ue-$(date -u +%Y%m%dT%H%M%SZ)-b-$(python3 -c 'import uuid;print(uuid.uuid4().hex[:8])')"
set -o pipefail
$PY simulators/unreal/bounded.py --mode b --run-id "$RID" --asset-zip "$ZIP" --exe "$EXE" 2>&1 | tee "/tmp/$RID-terminal.log"
status=${PIPESTATUS[0]}; echo "audit_exit=$status"; test "$status" -eq 0
```

For A, change `--mode b` to `--mode a` and use a new `-a-` ID. The existing run paths are in `results/unreal/`. The UE5 editor and S tests were executed; their exact commands, runner copies, statuses and errors are retained under the six S run IDs above. Do not call a zero `UnrealEditor-Cmd` exit an accepted image without decoded-pixel validation. To collect any finished run, create its **source** manifest after all writers stop, then transfer with `rsync --partial`, verify it locally and decode outputs:

```bash
python3 simulators/unreal/manifest.py create "artifacts/unreal/$RID"
# On the Mac, from the audit worktree:
rsync -az --partial -e 'ssh -i ~/Downloads/private_key.pem -p 22134 -o BatchMode=yes' \
  root@63.141.33.148:/root/R4R-Sims/artifacts/unreal/$RID/ \
  ~/Downloads/AL/R4R-Sims/artifacts/unreal/$RID/
python3 simulators/unreal/manifest.py verify ~/Downloads/AL/R4R-Sims/artifacts/unreal/$RID
```

The **historical S control** command and imported project are preserved. Its script and Python trace live in `ue-20261008T225105Z-s-control-e488bef0`; the imported `.uasset`/`.umap` live in `ue-20261008T224031Z-s-fe9a3ea3`. The newer focused controls supersede this configuration. Use the following only as provenance; future execution needs the concrete material/color hypothesis in the focused report and a fresh unique ID:

```bash
cd /root/R4R-Sims-unreal-audit
BASE=artifacts/unreal/ue-20261008T225105Z-s-control-e488bef0
cp "$BASE/control-script.py" /tmp/r4r-splat-channel-control.py
# Apply and record the specific SceneCapture lighting/render-path correction here.
set -o pipefail
bash "$BASE/launch-runner.sh" 2>&1 | tee /tmp/r4r-splat-followup-terminal.log
status=${PIPESTATUS[0]}; echo "control_exit=$status"
RID=$(cat /tmp/r4r-splat-channel-active-id)
python3 simulators/unreal/manifest.py create "artifacts/unreal/$RID"
```

The launcher has a 600 s `timeout -k 30`, runs UE as `nobody`, records the underlying command exit in `render.exit`, and returns nonzero if expected diagnostics are missing. The **scientific acceptance gate** is a decoded visibly nonblack final-color control mesh followed by visibly nonblack Gaussian output, matching requested/actual camera poses and asset binding; process exit 0 alone is insufficient. For transfer, change the remote `rsync` source above to `/root/R4R-Sims-unreal-audit/artifacts/unreal/$RID/`, then verify the VM-created manifest and open all copied images. Fresh-host reconstruction uses the locally verified UE ZIP, compiled plugin package, author sample ZIP and copied `captured-project/` in the S evidence; no signed URL or engine source build is required.

The transfer copies raw configs, source runner, routes, actions, state, actual vehicle/camera trajectories, RGB/depth, GPU and console logs, figures and video. All six native and six S remote run directories were source-hashed and local copies verified; the one preflight-only supervisor log is local without a remote source manifest. The Blocks ZIP is retrievable at its versioned public URL/hash. The sample ZIP, full official editor ZIP and built plugin package have separate locally verified source hashes; S project `.uasset`/`.umap` are in the source-manifested run folders. No remote evidence or unrelated VM process was deleted/stopped. During the long editor work, the official archive was copied with `rsync --partial`; S run folders were collected after each failure and at completion, then source-manifest verified and opened locally.

## Supervision guide

Read [sources.md](sources.md) alongside these files. First learn UE's distinction between a **packaged** UE4.27 game (Blocks) and an **editable** UE5.5 project (required for splat import), plus cooking/maps and asset license boundaries. Then inspect `simulators/unreal/audit.py` and AirSim `client.py`/`types.py`: identify which RPC requested a pose, which response gave the capture-time camera pose, and why RGB/depth timestamps are not fully aligned. Trace the B observation → proportional velocity → SimpleFlight/FastPhysicsEngine → collision/ground-truth loop. Practice NED/UE/PLY axis and centimetre conversions before replaying a route. Finally inspect the plugin PLY reader, import factory and renderer; check SceneCapture output rather than only its viewport. A supervisor should be able to explain each failure ID, waypoint/collision baseline, actual image cadence, manifest verification and what the held-out real image split would test.

**Primary sources:** [1] [Epic Linux requirements](https://dev.epicgames.com/documentation/en-us/unreal-engine/linux-development-requirements-for-unreal-engine); exact source file/line and release links in [sources.md](sources.md). Findings reflect these run records and remain subject to the stated capture/asset limits.
