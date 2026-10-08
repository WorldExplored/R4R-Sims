# Unreal execution plan and Codex prompt

Updated 2026-10-08. No runtime reproduction has been performed here. A4500 x1 is the lowest-price candidate in the user-supplied list; host specifications, full-instance price and actual rendering compatibility require verification. This preserves native camera replay, scripted flight, conditional policy evaluation, Unreal splat replay, conditional fidelity comparisons, evidence collection and the final presentation.

## Copy-paste prompt

```text
Continue the Unreal / Real4Real evaluation. This is an execution task, including the agreed camera, flight, splat-rendering, evidence-preservation and presentation work. Installation and a smoke test alone are not completion. Do not train policies.

REPOSITORY AND WORKSPACE
Use https://github.com/WorldExplored/R4R-Sims.git.
Local checkout: ~/Downloads/AL/R4R-Sims/
Remote checkout: ~/R4R-Sims/
Simulator folder: simulators/unreal/
Plans and sources: docs/unreal/
Small run evidence: results/unreal/<unique-run-id>/
Large outputs: ignored artifacts/unreal/<unique-run-id>/
Downloads/dependencies/builds: ignored third_party/unreal/ on the remote instance.

Reuse an existing checkout after inspecting its origin and git status. Otherwise create the parent directory and authenticate, then git clone into the exact path. Preserve unrelated files, repositories and uncommitted changes. Read README.md, AGENTS.md, docs/gpu-options.md, docs/chat-update.md, applicable nested instructions and all existing Unreal plans first. Explicit current instructions override stale repository names/paths. Use simulators/unreal as the Unreal Testing folder; do not create an independent unsynchronized project beside the repository.

Create simulator-specific scripts, configs and setup instructions under simulators/unreal. Use root configs/ and scripts/ only for genuinely shared code. Inspect for prior audit.py and source files; none is guaranteed to exist. Recover/import them if available, otherwise implement the agreed runner. Do not invent prior measurements.

MACHINE
Selected candidate: A4500 x1, 20 GB VRAM, displayed $0.28/hour in the October 8 availability list. Intended OS: Ubuntu 22.04 x86-64. Planning target: at least 8 vCPUs, 32 GB RAM, 200 GB free SSD for a prebuilt editor plus small assets; allow about 500 GB free if a source-engine build proves necessary, after inventorying download/build sizes. These are planning targets, not measured minimum requirements.

Before recommending launch, verify the provider's actual SKU, whole-instance hourly price, storage charges, CPU/RAM/disk, GPU exposure and Ubuntu image. The list does not verify these. Lambda's public documented catalog does not list A4500, so confirm the provider/account listing rather than silently assuming its host specifications. No fixed budget cap applies; avoid unnecessary spending. Do not launch resources yourself. If A4500 fails a concrete requirement, explain it before changing hardware. A6000 x1 (48 GB, displayed $0.54/hour) is the next-cheapest listed candidate if additional memory/host capacity is genuinely needed, subject to verifying its full price.

Validate nvidia-smi and vulkaninfo, actual hardware Vulkan rendering and a supported graphics driver. Use the selected UE version's driver requirements; current Epic Linux guidance lists NVIDIA 570+. CUDA alone is insufficient. Retain a working provider driver when compatible. Use verified offscreen rendering or a GPU-backed display session. Xvfb alone does not demonstrate hardware rendering. Never use -nullrhi for image tests.

GIT AND SSH
Verify authenticated repository read and write access independently on both machines. Keep credentials outside the repository. Prefer a repository-scoped remote credential; do not copy the private SSH key onto the instance. If authentication requires user action, state the exact action and keep preparing independent work.

Use the supplied SSH command, host, username, port and local private-key path. Never request or print key contents. Verify the server host key normally. Authenticate local and remote clones. Use git pull --ff-only after inspecting status, commit/push only this task's authored files, and pull on the other machine. Handle divergence without force-push or overwriting work. Coordinate a single writer per branch at a time. Git is for authored code and small results, not bulk artifact transfer.

INSTALLATION
Download large reproducible dependencies directly on the instance. Record upstream URL, release/tag, commit, license, checksum, archive validation, executable path and required setup changes. Do not commit engine installations, downloaded third-party repositories, datasets, checkpoints or caches.

For native tests, use original Microsoft AirSim packaged Linux Blocks. Inspect release metadata and archive contents before extraction. Linux v1.8.1 uses tag v1.8.1, not v1.8.1-linux, and has an upstream report of an empty 22-byte Blocks.zip. Reject empty/incomplete archives. Inspect v1.8.0-linux or v1.7.0-linux for a valid Blocks package and record any version change. Inspect launch scripts/binary dependencies and establish a working GPU-rendered launch. Do not execute Windows .exe/run.bat instructions on Ubuntu. Do not silently replace Blocks with a different scene. If no packaged Blocks release works, investigate a Linux source build, report its concrete requirements, and preserve the blocker if unavailable.

Create an isolated Python environment compatible with the selected AirSim client/server; do not modify system Python. The earlier proposed dependency set was Python 3.9, numpy 1.23.5, opencv-contrib-python 4.7.0.72, msgpack-rpc-python 0.4.1 and airsim 1.8.1. Treat it as an unexecuted starting point, verify compatibility with the selected release and record actual resolved packages. Resolve AirSim installation prerequisites explicitly. Do not claim the packaged UE version without build evidence.

For splat tests, use a separate editable UE5 project. Obtain a lawful Linux prebuilt editor through authorized Epic access, or its source/toolchain if necessary. Pin the version to the chosen plugin. YaGS currently documents Windows runtime platforms; do not assume Ubuntu support from Vulkan references. Inspect Linux-capable candidates such as Italink/GaussianSplattingForUnrealEngine (its descriptor lists Linux and README requires UE5.5+). Verify actual Linux compilation and camera capture before claiming support. Use pretrained scene import only; avoid its optional reconstruction/training workflow. Record plugin rendering limitations. A matching polygonal scene and UE5 drone integration are not prerequisites for a camera-only splat run.

AGREED TESTS
A. Native camera replay:
Eight explicit poses near spawn, 0–1 m horizontal displacement and about 2 m above origin, initially allowing 0.25 s settling. Use ComputerVision mode and simSetVehiclePose; label this as moving a camera rig, not flying. Warm up with three image pulls, then capture all eight 640x480 RGB PNGs and floating-point DepthPlanar arrays. Record target pose, actual camera pose, vehicle/rig pose, FOV/intrinsics and sensor/request timestamps. Verify dimensions, decoding, nonempty images, expected scene changes, depth units, RGB/depth alignment and plausible depth on a known surface. DepthPlanar is camera-plane depth, not pixel-ray distance.

B. Native closed-loop scripted flight:
Inspect clearance, take off, track the agreed 1 m square at roughly 2–3 m altitude, land. The outer proportional position controller observes estimated position, targets 5 Hz, bounds NED velocity to 0.7 m/s, and issues 0.2 s velocity commands; SimpleFlight is the inner controller. Define and record gain, yaw/drivetrain mode, waypoint tolerance and deadlines before execution. Capture RGB/depth up to 2 Hz; GPU observations at 1 Hz. Measure achieved rates, waypoint completion, tracking error and collisions. Separate estimated state, ground truth, reference waypoints, achieved vehicle trajectory and actual camera trajectory. Stop on collision/timeout; record failures.

C. Released learned-policy evaluation:
Retain this test as conditional. It requires named compatible weights, inference code, scene/task, preprocessing, action scaling/rate and success criteria. Blocks supplies none in the prior handoff. If no released compatible artifact is found, report blocked with evidence. Do not train substitutes, run random weights or call the scripted controller a learned policy.

S. Actual Unreal Gaussian-splat camera replay:
Acquire one lawful compatible pretrained Gaussian scene, verifying Gaussian attributes rather than assuming any PLY is a splat model. Import it into the editable Linux UE project, execute an explicit camera trajectory and save RGB plus poses/intrinsics. Confirm splats appear in exported sensor/SceneCapture images, not only the editor viewport. Test available depth and mesh/splat occlusion with documented semantics. Keep collision proxies separate from visual depth; a convex hull does not establish usable scene collision.

Do not compare unrelated Blocks and splat scenes as a fidelity benchmark. Preserve the common-scene UE-versus-splat comparison as conditional on matching representations, scale, axes, camera calibration and exposure. Preserve the held-out real-image test as conditional on approved calibrated AirLab captures: training-only reconstruction split, held-out real viewpoints/trajectories, paired renders and defined masks/exposure for PSNR/SSIM/LPIPS. Without these inputs, identify the missing assets and exact next action. Do not claim sparse outdoor fidelity or the 15 m capture -> accurate 50 m view requirement is established.

IMPLEMENTATION AND MEASUREMENTS
Use unique IDs for every attempt, finite startup/RPC/takeoff/waypoint/landing deadlines and an independent watchdog that survives blocked RPCs. Validate timeout/failure collection offline before renting. Initial A/B wall deadlines are 180 seconds each; record any justified changes. Kill only owned processes.

Document NED metres, quaternion order, camera mount, UE coordinates and validated conversions to splat coordinates. For A, supported pause-based diagnostics may synchronize poses/images. For B, record sensor times, query times and offsets; do not silently pause and claim real-time performance. Check timestamp units. Blocking image calls or async joins may lower controller frequency, so measure actual action intervals.

Keep setup, warmup, execution, capture RPC latency, simulation time, wall time, GPU utilization/VRAM and any actual renderer profiling separate. RPC latency is not renderer FPS. Missing samples remain missing.

PRESERVATION
Log exact commands, exit codes, exceptions, environment, revisions/patches, settings, asset hashes, policy/controller provenance, routes, actions, states, camera records, timings and outputs. Flush logs and write completed frames atomically where practical. Use tmux or equivalent so SSH loss does not erase the run.

Push code/configs/notes/small results, then pull locally. Keep large captures out of ordinary Git. Pull them to local artifacts/unreal/<run-id>/ with resumable rsync over SSH, using --partial and --append-verify only for suitable immutable files. Preserve originals. No recursive SCP of engine/dataset trees. Periodically copy completed evidence during long runs; another directory on the same VM is not durable storage.

Generate a final file-size/SHA-256 manifest after writers stop. Verify it at the local/durable destination and open representative copied RGB, depth and video. Push artifact locations and verification status to results/unreal/<run-id>/. Preserve non-reproducible edited UE project assets even when ignored. Reproducible dependencies may remain remote only if retrieval/version instructions are recorded. Do not terminate the instance until every essential item has a verified local/durable copy and all small results/code are pushed. Report readiness; do not terminate unrelated resources.

DELIVERABLES
Produce measured findings, contact sheets, depth visualizations, reference/achieved trajectory plots, and a labeled replay video when enough frames exist. A's eight images can be a contact sheet. Distinguish video playback FPS from measured capture rate.

Generate the agreed slideshow from actual results, including failures and blockers. Cover feasibility, architecture, scene/data, inputs, controller/policy, exact trajectories, asset/config provenance, outputs, runtime/memory, hardware, limitations, R4R relevance, pros/cons, indoor/outdoor/racing applicability and discussion questions. Include detailed evidence in an appendix and notes where useful. Save the actual deck and figures locally, link them from results, and synchronize them through an appropriate small-file Git or large-artifact route.

Include the supervision/learning guide: packaged project versus editor, API/component boundaries, observation/action interfaces, camera coordinates, planned versus achieved paths, and what each measurement demonstrates. Explain splats inside UE, external splat rendering while retaining simulator dynamics, and removing UE as separate architectures, without claiming unbuilt adapters exist.

Finish with test-by-test demonstrated/failed/blocked status, exact viewed/copied output paths, pushed commit IDs, checksum verification and genuinely missing prerequisites. Keep independent preparation moving if access/assets are absent; do not fabricate execution.

CONNECTION:
SSH command: [PASTE COMPLETE COMMAND]
Host / username / port: [FROM PROVIDER]
Local private-key path: [ABSOLUTE PATH OUTSIDE REPOSITORY]
Launch details: [SKU, CPU, RAM, DISK, UBUNTU IMAGE, FULL-INSTANCE PRICE]
Epic access if needed: [AVAILABLE / NEED USER SIGN-IN]
```
