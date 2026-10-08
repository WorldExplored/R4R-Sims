# Reviewed Unreal / Gaussian-splatting audit prompt

Reviewed 2026-10-08. **Ready for phase-1 investigation; GPU execution remains conditional on artifact and host readiness.** This prompt replaces the pasted prompt's old workspace and supplements `execution-prompt.md` with lab context, explicit stage selection, fair comparisons and runner checks. Existing code and plans are preserved. No simulator was executed during this review. The user subsequently supplied progress from an active A5000 run, including native A/B results. Use `in-progress-followup.md` for that ongoing session rather than restarting with this stage-1 prompt.

## Review verdict

The pasted prompt is scientifically careful about camera replay, control, policies and splat collision limits. It is not a complete hardware-execution instruction: it explicitly ends at phase 1, uses an obsolete workspace, lacks the actual R4R brief, does not require pushing the shared repository, and cannot by itself give parallel candidates a fair comparison protocol.

The newer `docs/unreal/execution-prompt.md` fixes many execution/storage details. Preserve its native A/B tests and conditional C/splat/fidelity tests, but treat its implementation choices as provisional. In particular, original Microsoft AirSim Blocks is a proposed UE/control baseline, not Unreal itself, IAMAI Project AirSim, or a UE5-compatible splat/drone stack. Do not build an unnecessary second simulator merely to fill every test cell.

**Do not rent four GPUs before phase-1 readiness checks.** Independent source audits can run locally. Start one bounded reproduction on the cheapest compatible host, verify rendering and collection, then parallelize ready candidates. This is a cost recommendation, not a prohibition on user-authorized parallel runs.

## Copy-paste prompt

```text
Perform the Unreal Engine / Gaussian-splatting candidate audit for AirLab Real4Real (R4R). This is a task to produce and, when a host is supplied, execute a concrete reproduction. Do not stop at generic advice. Follow the STAGE setting below; do not rent hardware.

STAGE=1
Use 1 now for source/code investigation and execution preparation. When the user supplies hardware, use 2 to finish preparation and run supported experiments. Source investigation, installation and a smoke test are not equivalent to completed scientific evaluation. Missing assets may legitimately block individual tests; preserve independent progress and report each blocker precisely.

R4R BRIEF
R4R aims to reduce repeated outdoor drone flights by turning a small real capture into realistic camera observations for new trajectories. The lab's pipeline is real images + camera poses -> reconstruction -> scene representation -> new trajectory -> rendered observations -> downstream evaluation. Its target is residential/suburban/campus scenes below 100 m. Capture at 15 m and rendering at 50 m is a proposed research goal, not proven extrapolation. The lab plans an outdoor train/test dataset with horizontal and vertical routes and image/downstream metrics. Do not assume those data are available here. Indoor navigation, outdoor navigation including sparse scenes, and racing are additional applicability questions, not established test tasks.

Read docs/r4r-audit-context.md and identify any difference from the current lab plan. Do not confuse R4R with the R2R benchmark. Do not treat a stock-scene video or scripted flight as evidence of fidelity in the real captured environment. No new policy training or scene training is authorized in this audit. Released pretrained models may be used when compatible. The broader lab reconstruction/training work is a separate task.

REPOSITORY, PATHS AND PARALLEL WORK
Repository: https://github.com/WorldExplored/R4R-Sims.git
User's local checkout: ~/Downloads/AL/R4R-Sims/
Remote checkout: ~/R4R-Sims/ unless a supplied existing checkout is selected.
Candidate code/setup/configs: simulators/unreal/
Candidate plans/sources/handoff/slides outline: docs/unreal/
Small evidence: results/unreal/<unique-run-id>/
Large outputs: ignored artifacts/unreal/<unique-run-id>/ or verified durable storage.
Reproducible downloads/builds: ignored third_party/unreal/.

Resolve absolute paths on the actual machine. A Linux scratch checkout is not the user's Mac checkout. Never claim a file was collected to the Mac unless verified there. Inspect origin and git status; reuse only the correct repository. Preserve unrelated files, histories and uncommitted changes. Read README.md, AGENTS.md, docs/gpu-options.md, docs/chat-update.md, applicable nested instructions, existing Unreal notes and runner code before editing. Recover prior evidence only with provenance; do not invent missing results.

Use a candidate branch such as audit/unreal-<timestamp> and an isolated worktree or checkout. Concurrent candidate agents must not share one mutable Git checkout, port, settings directory or engine project. Own simulators/unreal/, docs/unreal/ and results/unreal/. Coordinate shared-file edits. Do not force-push, discard changes, automatically stash others' work, or merge another candidate's experiments into this candidate. Push task commits, pull the same branch on the other machine, and report branch/commit URLs. Integrate without overwriting parallel changes.

Verify repository read/write access and local/remote synchronization before claiming delivery. Credentials and the local private SSH key stay outside Git. Use supplied SSH command/host/user/port/key path; never request key contents or bypass host-key checks. If access is absent, state the exact user action needed and continue independent work. Do not install/reconfigure orchestration. If First Mate is already installed, inspect version/backend and use only if helpful; direct Codex is acceptable.

SCIENTIFIC AND ARCHITECTURE QUESTIONS
Answer separately:
1. Import/render splats inside UE. What visual component changes? Does the selected plugin support the chosen UE version and Linux build? Do splats appear in the actual sensor/SceneCapture output? What happens to depth, occlusion, exposure, collisions and packaging?
2. Keep an existing dynamics/control host and obtain camera observations from an external splat renderer. Trace timestamped vehicle state -> camera mount/extrinsic -> renderer pose/intrinsics -> RGB/depth -> consumer. Distinguish logged replay from synchronized closed-loop observations. State who owns time, collision geometry, sensor publication and stale-frame behavior. An existing render function is not a working adapter.
3. Remove UE entirely. Name the existing replacement for dynamics, control, sensors, collision queries and time. Mark missing components explicitly. Do not invent a drone stack to make UE seem complete.

Prefer the smallest lawful released scene/build and existing interfaces. Audit a native UE/control baseline and a splat path as separate versioned stacks if necessary. Original Microsoft AirSim, IAMAI Project AirSim and TravelUAV's AirSim APIs are different dependencies. Avoid duplicating Project AirSim evaluation already owned by another candidate. Static visual splats alone provide neither physical dynamics nor validated collision geometry.

SOURCES AND ASSET READINESS
Use Epic documentation for the exact chosen UE version, authors' repositories/papers, release metadata and licenses. Pin commits and provide file/line permalinks for executable paths. Record access date and classify claims as documented, inferred, statically checked, locally executed or remotely measured. Historical issue reports are warnings, not proof of current asset failure. Inaccessible downloads remain blockers.

For each required asset record role, URL, tag/commit/version, license/access restrictions, expected/observed SHA-256, compressed/expanded sizes, local/remote paths and preservation decision. Never label a locally computed hash as an upstream-published checksum. Inspect archive integrity and contents to distinguish Linux executables from Windows packages. Derive binary provenance from release/build evidence; do not assert a packaged binary exactly matches a source commit when unverified.

Existing native baseline proposal: a valid original Microsoft AirSim Linux Blocks package. The runner currently pins v1.8.1; the prompt names older Linux fallback releases. Verify a real Linux archive and compatible client before committing to one. If fallback changes version/hash, make the runner asset-driven rather than retaining conflicting constants. Do not substitute a different scene silently. Prefer investigating a verified packaged route over compiling a large engine from source. If an editor/source build is necessary, report its concrete dependency/access/time/space burden.

Existing UE splat candidate: Italink/GaussianSplattingForUnrealEngine. Its README specifies UE5.5+ and its descriptor lists Linux, but these facts do not establish a tested Linux build, sensor export or faithful rendering. Inspect import/runtime modules and dependencies, pin a compatible version, obtain one lawful pretrained Gaussian model and verify its attributes. Do not invoke its optional reconstruction/training workflow. A PLY extension alone does not establish Gaussian attributes. A plugin's capture/depth feature used to train splats does not establish exported depth of imported splats.

MACHINE AND RENTAL GATE
Only use docs/gpu-options.md's user-supplied October 8 candidate list. Cheapest GPU candidate for a small UE pilot: A4500 x1, 20 GB, displayed $0.28/hr. Fallback if measured or documented memory/host requirements demand it: A6000 x1, 48 GB, displayed $0.54/hr. No GPU rental is needed for stage 1; the listed CPU node is not a renderer substitute.

Intended OS: Ubuntu 22.04 x86-64, subject to the chosen package/plugin. Editor pilot planning target: at least 8 vCPUs, 32 GB RAM and 200 GB free SSD. These are planning targets, not measured minima; packaged-only work may need less. Inventory before recommending storage. Source compilation may need substantially more space and time, and requires a separate documented build decision. Do not upgrade because a paper trained on a larger GPU.

Before recommending rental, return a readiness table: exact scene/build, OS/engine/plugin compatibility, download access, released policy status, graphics requirements, ordinary non-root execution, CPU/RAM/storage and whole-instance price. Unknown host specifications or login/download access are explicit gaps. Do not infer provider identity from GPU names. Recommend the cheapest compatible listed SKU and explain uncertainty.

On the actual host verify OS, driver, GPU visibility, Vulkan device/extensions and actual hardware-backed offscreen rendering. CUDA/nvidia-smi alone is insufficient; a successful vulkaninfo exit alone does not show UE selected the NVIDIA GPU. Never use -nullrhi for image tests. Xvfb is not evidence of hardware rendering. Use version-specific driver guidance. Do not alter authentication/security settings, create privileged users or replace working drivers blindly. Use an existing ordinary user; if the host only provides an unsuitable root execution path, report the required host prerequisite.

EXPERIMENTS AND ACCEPTANCE
Keep each test's purpose, prerequisites, exact config and acceptance written before execution. Classify A (camera replay), B (closed-loop controller), C (released learned policy) explicitly. Retain all tests below as executable or clearly blocked; do not mark an installation-only result complete.

A: native camera replay. Retain the proposed eight near-spawn poses covering 0–1 m horizontal displacement at about 2 m height, 640x480 RGB and float DepthPlanar, with three initial image pulls for warmup and initially 0.25 s settling. Use ComputerVision mode or an equivalent verified no-dynamics replay path. Define all poses/orientations and camera mount before capture. Record requested pose, actual vehicle/rig pose, capture-time camera pose, intrinsics and timestamps. Verify every expected image decodes at the intended size, the camera changed as commanded, depth semantics/units and RGB/depth alignment. Validate transforms with an analytic/known-surface check. Merely receiving eight PNGs is insufficient.

B: native closed-loop scripted flight, conditional on a supported control layer. Preserve takeoff, a 1 m square at roughly 2–3 m altitude, and landing. Existing proposal: bounded proportional outer position controller over estimated state, target 5 Hz commands, componentwise velocity bounds of 0.7 m/s, 0.2 s command duration, SimpleFlight inner control; initially gain 0.7 and 0.25 m waypoint tolerance. These are engineering defaults, not lab accuracy targets. Check route clearance and explicitly set gain, speed-norm versus per-axis limits, yaw/drivetrain, tolerance and deadlines. RGB/depth target up to 2 Hz and GPU samples 1 Hz; report actual intervals and dropped samples. Initial A/B wall deadline 180 s each plus a bounded cleanup allowance. Independent watchdog must survive blocked RPCs. Success requires all waypoints met within tolerance/deadlines, recorded actual trajectory, no new collision and completed landing. Include tracking error and command/sensor rates. This tests integration, not broad navigation or racing competence.

C: released pretrained learned-policy evaluation only when a named compatible checkpoint, task/scene, preprocessing, observation/action schema, action scaling/rate and success condition are available. Trace inference all the way to actions and task outcomes. If missing or incompatible, give the exact artifact/interface blocker. No new policy generation/training, random weights or relabelled scripted controller. Different native policies/tasks cannot form a fair simulator leaderboard.

S: actual UE Gaussian-splat camera replay. Import a lawful pretrained model into a compatible editable project. Export images along an explicit calibrated route using the actual intended capture path, not only editor screenshots. Record source-model normalization, scale, conversion, plugin settings and any Gaussian clipping/LOD/color differences. Verify splats appear in captures; check mesh/splat occlusion and available depth separately, with documented semantics. Missing splat depth or collisions must not be silently replaced with polygonal ground truth. No drone policy is required for this A-level experiment.

F: matched-world renderer comparison, conditional on compatible representations of the SAME scene. Match camera-to-world/world-to-camera conventions, mount, handedness, axes, quaternion order, units, scale, intrinsics, distortion, resolution and lighting/exposure assumptions. Document unavoidable differences including baked appearance, tone mapping, LOD and transparency sorting. Never compute a fidelity comparison between unrelated Blocks and splat scenes. A renderer comparison without real reference images is not proof of real-world fidelity.

R: held-out-real-image evaluation, conditional on approved calibrated AirLab data and a fixed training/test split. Use existing reconstruction trained only on the training split; no fitting on held-out images. Replay held-out real poses with matched calibration. Report PSNR/SSIM/LPIPS, masking and exposure rules, plus per-route/altitude/coverage strata rather than a single average. Separate interpolation from altitude/viewpoint extrapolation, sparse captured coverage from sparse physical content, vegetation, moving objects, depth consistency and collision support. A held-out lower-altitude route cannot establish 50 m performance. Downstream usefulness needs a named real-data perception/task baseline and its metric; otherwise mark that conclusion pending. Do not invent a numerical fidelity pass bar or a downstream model.

CODE CHECKS BEFORE HOST EXECUTION
Inspect and reuse simulators/unreal/audit.py and bounded.py; they are provisional, not validated runtime tools. Recheck the current version because concurrent chats may have changed it. Resolve asset-specific preflight constants and provenance, privileged nobody/chown launch assumptions, shared /tmp settings paths, the current >=2 s capture interval versus the 2 Hz proposal, missing depth capture timestamp/pose alignment evidence, and verification based only on destination hashes. A real transfer check compares a source manifest against the destination, not the destination against itself. Preserve mode A's existing ComputerVision switch.

Create run.json and command/failure logs before preflight so download/preflight/launch failures leave evidence too. Only retain changes needed for selected tests. Check syntax/help and meaningful offline behavior where possible: corrupt/wrong-platform archive rejection, ordinary-user launch paths, timeout exit/logging, interrupted transfers and detection of a changed destination file. Do not install large dependencies locally just to test source syntax. Report exactly what was and was not checked. GPU/GUI-dependent commands stay unexecuted until tested on the target.

RECORDS, TIMING AND COLLECTION
Record each attempt in results/unreal/<run-id>/ with run.json, commands.log, console.log, task status and small manifests/metrics. Large frame/depth/video/project outputs go under ignored artifacts/unreal/<run-id>/. Link exact paths from the run record. Capture revisions and authored patches, environment/OS/GPU/driver, settings/seeds, input/output paths, asset URLs/hashes, split, scene scale/frame conventions, camera intrinsics/extrinsics, controller/policy provenance or none, timeouts, exit codes and missing data. Reference route, actual vehicle trajectory and actual capture-time camera poses are separate records. Store commands as executed and retain failures even when piped through tee.

Separate setup, warmup, wall time and simulation time; verify timestamp units and clocks. Do not treat acquisition RPC latency as renderer FPS or image timestamp differences as guaranteed simulation steps. Measure steady-state rendering throughput with defined workload/warmup/synchronization when supported, policy latency only if C runs, achieved control/sensor rates, and sampled GPU memory. Label sampled GPU-memory maximum as sampled, not an exact allocation peak. Exported video playback FPS is presentation metadata. Paused replay cannot establish real-time closed-loop performance.

During long runs, collect completed immutable files and flushed logs periodically from a LOCAL collector. Use resumable rsync over SSH or user-approved durable storage. Do not describe another directory on the VM as backup. Capture failures immediately. Never delete remote evidence before verification; only stop processes owned by this run.

Inventory local free space and every essential asset: configs/patches, trajectories, images/depth/videos, logs, scene/checkpoint inputs actually used, and non-reproducible edited UE project content. Preserve each by verified local/durable copy or a tested retrievable versioned URL plus SHA-256 and access instructions. Reproducible engine installs/caches need not be copied wholesale. Licensed artifacts must follow redistribution terms. Expiring signed URLs alone do not preserve inputs.

Freeze completed files, create a SOURCE size/SHA-256 manifest, transfer, and compare the destination against it. Open representative copied RGB/depth/video and parse records. Commit/push small results and artifact/verification links; pull locally and verify the same commits. Git alone does not copy ignored artifacts. If the Mac/durable destination is unavailable, collection remains blocked and the host must retain evidence. Do not claim a local copy or shutdown readiness. Report completion only after verified preservation; do not terminate resources yourself.

DELIVERABLES AND COMPARISON
Stage 1: docs/unreal/handoff.md, sources.md, assets.md, slides.md, and only necessary runners/configs. Handoff includes input-to-output path, exact bounded setup/preflight/run/collect commands, controller/policy and observation/action interfaces, scene provenance, trajectories, hardware/cost/storage/install-effort estimates with evidence/uncertainty, outputs, acceptance, blockers, pros/cons and learning guide. Explain editor versus packaged build, camera conventions, selected splat interface and relevant code files. slides.md proposes figures and evidence needed; all findings pending execution are labelled.

Stage 2: complete supported tests and provide a test-by-test demonstrated/failed/blocked/not-tested table. Save real contact sheets, depth views, reference/actual trajectory plots and a replay video when enough frames exist. Produce the result presentation using available presentation tooling, with actual evidence and failures, not fabricated placeholders. Synchronize figures/deck as small Git files or verified artifacts as appropriate.

Use the dimensions in docs/r4r-audit-context.md for cross-candidate comparability. Summarize whether to reuse UE as visual baseline, retain its host with external rendering, use a splat plugin, defer, or reject it for R4R. Explain how each experiment affects that decision. Compare peers only using retrieved evidence; do not invent their measurements. Report performance hardware/workload differences and missing common scenes/tasks explicitly.

Finish with a concise outcome, created paths and branch/commit URLs, what was actually checked, exact provision recommendation or runtime host used, missing inputs, verified collection paths, and next command/prompt. A partial successful test does not erase other failures or blockers.

STAGE-2 CONNECTION INPUTS (only needed once a host exists):
SSH command: [complete command, no private-key contents]
Host / existing ordinary username / port: [provider details]
Local private-key path: [absolute path outside repository]
Host details: [GPU count/SKU, CPU, RAM, free SSD, OS, graphics driver, total hourly price]
Local collection path: ~/Downloads/AL/R4R-Sims/artifacts/unreal/
Epic download access if necessary: [available or exact sign-in prerequisite]
Approved AirLab dataset/calibration/split and pretrained scene: [actual paths, or unavailable]
```

## Evidence and unresolved implementation issues

Repository snapshot inspected: tree `71ed7bc1f96b6ff77df5da8b43693e6563e249e4`, read October 8. File contents should be rechecked before modification because other chats can update the repository.

| Observed issue | Evidence in snapshot | Consequence |
| --- | --- | --- |
| Pasted prompt ends after phase 1 | User-supplied prompt | It cannot authorize/require the later hardware run by itself |
| Asset version cannot vary | `audit.py` lines 22–25, 83–107, 222, 235, 428–432 | A valid fallback release fails hardcoded size/hash checks and carries wrong provenance |
| Privileged launch assumptions | `audit.py` lines 257–282 | `chown`/switching to `nobody` generally needs privilege; it may fail on an ordinary SSH account before the guarded launch |
| Shared settings directory | `audit.py` lines 257–264 | Concurrent runs share `/tmp/r4r-ue-home` and can overwrite settings |
| Capture-rate mismatch | `audit.py` line 364 versus line 249 | A >=2 s interval yields at most about 0.5 Hz before RPC overhead, not the stated up-to-2 Hz target |
| Incomplete RGB/depth alignment record | `audit.py` lines 135–177 | Only RGB response timestamp/pose is retained; pairwise capture alignment cannot be verified from the saved metadata |
| Destination self-check | `audit.py` lines 420–440 | Manifest is generated after copying and checked against that same destination, not the original source |
| Preflight failures lack per-run record | `audit.py` lines 207–214 | Preflight occurs before the run directory and manifest are created |
| Claimed binary/source correspondence unverified | `audit.py` lines 22, 232–235 | A pinned source commit does not establish how a downloaded binary was built |

Mode A already changes settings to ComputerVision at lines 223–227. It should be retained, not incorrectly flagged as still running multirotor physics. No GPU, dependency install or runtime test was performed in this review. These are static observations, not observed host failures.

Primary upstream resources checked October 8:

- [Epic Linux Development Quickstart](https://dev.epicgames.com/documentation/en-us/unreal-engine/linux-development-quickstart-for-unreal-engine): supports installed Linux builds and recommends Ubuntu 22.04, 32 GB RAM and dedicated Vulkan graphics. Use version-specific requirements rather than latest-version requirements for an older package.
- [NVIDIA Vulkan driver support](https://developer.nvidia.com/vulkan-driver): RTX A4500 and A6000 are listed graphics devices. This does not establish graphics exposure on a rental VM.
- [Italink plugin README at inspected commit](https://github.com/Italink/GaussianSplattingForUnrealEngine/blob/411f879985719ce69eaaf15d58152c551e2719b1/README.md): UE5.5+, Gaussian PLY import, GPU-particle/static-mesh rendering, capture and optional training tools. Latest commit metadata returned July 6, 2026; maintenance quality and Linux runtime reliability remain unmeasured.
- [Plugin descriptor](https://github.com/Italink/GaussianSplattingForUnrealEngine/blob/411f879985719ce69eaaf15d58152c551e2719b1/GaussianSplattingForUnrealEngine.uplugin): Linux is declared in supported target platforms; runtime and editor modules are distinct.
- [AirSim v1.8.1 release](https://github.com/microsoft/AirSim/releases/tag/v1.8.1): current metadata lists Blocks.zip at 142,533,463 bytes; the body gives Windows-style run.bat instructions. Archive contents were not downloaded, so its Linux suitability is unverified.
- [AirSim issue 4637](https://github.com/microsoft/AirSim/issues/4637): historical report of a 22-byte Linux Blocks archive. It must not be treated as a verified current archive measurement.
- [AirSim v1.8.0-linux release](https://github.com/microsoft/AirSim/releases/tag/v1.8.0-linux): lists Blocks.zip at 188,508,816 compressed bytes. Extraction size, executable validity and host execution were not measured.

The actual R4R primary briefing and its missing inputs are recorded in `docs/r4r-audit-context.md`. Host CPU/RAM/disk, provider identity, total billing and current availability were not independently obtained. A4500 is a conditional pilot recommendation, not a certified full-workload minimum.
