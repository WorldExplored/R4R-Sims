# Follow-up for the Unreal audit already running

Prepared October 8, 2026 from the user's pasted terminal progress. Native results below are reported by that Codex session and must be verified from its actual run records. This follow-up takes precedence over the earlier provisional A4500 recommendation and stage-1-only instruction for this already supplied host.

```text
Continue the current Unreal audit from its actual state. Do not restart preparation, switch GPU, discard existing work, or repeat successful native tests unless verification exposes a concrete problem.

CURRENT STATE
The supplied host is Ubuntu 22.04 with RTX A5000 24 GB, driver 580.178.04 and about 112 GB free when inspected. Its host fingerprint was confirmed and the repository deploy key was explicitly approved. Preserve established access; do not repeat those approval requests. A missing EGL loader was reportedly fixed, NVIDIA Vulkan was detected, and packaged Linux Blocks rendered with a responding AirSim RPC. The actual v1.8.1 Linux ZIP reportedly passed integrity checks at 142,533,463 bytes. These host/archive observations override earlier provisional warnings after you verify the records. Do not downgrade the release because of a historical 22-byte issue report, and do not reject this user-supplied A5000 because an older availability list omitted it. The earlier 200 GB estimate was a planning target, not a mandatory minimum.

A reportedly produced eight RGB/depth pairs. B reportedly finished the square and landed with no NEW collision, after an earlier attempt exposed a spawn collision with Ground_6. Preserve every attempt and its failure details. A completed native flight does not establish the Gaussian-splat path.

R4R CONTEXT AND SCOPE
The lab's central goal is to collect a small real outdoor capture once, reconstruct the scene, then generate realistic observations for NEW drone camera trajectories. Targets include residential/suburban/campus scenes below 100 m. The example of capture at 15 m and rendering at 50 m is an unresolved research goal. Indoor navigation, outdoor navigation including sparse scenes, and racing are additional applicability questions.

Evaluate whether this candidate contributes a renderer, dynamics/control host, sensor interface or conventional visual baseline. A stock Blocks replay/square flight demonstrates integration only. It cannot establish outdoor reconstruction fidelity, accurate altitude extrapolation, racing competence or real-drone transfer. No new policy or scene training is authorized. A released compatible learned policy may be evaluated; otherwise report it blocked. Do not call the proportional script/SimpleFlight a learned policy.

VALIDATE EXISTING A/B BEFORE ADDING WORK
Check actual logs/configs rather than assuming the summary proves correctness:
- Confirm A's no-dynamics replay mode; requested versus actual rig pose; actual capture-time camera pose; intrinsics, units, axes, handedness and quaternion representation. Open all eight images/depth arrays and check dimensions, scene changes and plausible known-surface depth. Document any pose/depth checks that remain unperformed.
- Verify RGB/depth timestamps and capture-pose alignment. If only RGB timing was recorded, declare that limitation. Perform only a small targeted additional capture if needed; do not rerun the full audit without reason.
- For B, verify estimated state, ground truth, actual trajectory, waypoint tolerance/deadlines, achieved action intervals, landing state and collision records. Retain the spawn collision baseline and evidence for distinguishing subsequent impacts. Disclose any limitation of timestamp-based collision detection. Keep failed attempts separate from the successful retry.
- Measure rates from records. A >=2 s image interval means at most about 0.5 Hz before overhead, not 2 Hz. Report achieved cadence honestly; do not rewrite the run as meeting a target it missed. Separate RPC acquisition latency, renderer throughput, control rate, policy latency, wall/simulation time, sampled VRAM and playback FPS. Unsupported measurements stay unmeasured.
- Record actual archive URL/hash and engine/client/build versions. Separate verified binary provenance from an unverified source-commit association. Keep environment fixes/patches and commands. Do not modify completed-run records to erase errors.

RESOLVE THE SPLAT BLOCKER CONCRETELY
The UE5 editor download requires Epic access. Record the exact supported Linux editor version, compatible plugin commit, authorized download route and input needed. Do not buy access, train a scene, or begin a large source-engine build merely to bypass the sign-in wall. Continue source/interface inspection and finish independent A/B deliverables.

If authorized editor access becomes available during this session, use one lawful pretrained Gaussian scene and the smallest camera-only UE project. Verify imported splats appear in exported SceneCapture/sensor images, not just an editor viewport. Record pose/calibration/scale conversion and plugin LOD/color settings. Assess RGB, splat depth, mesh occlusion and collision support separately. A plugin's capture-depth tool for reconstruction does not prove imported splats provide correct sensor depth. Inventory download/extracted/project space before installation; 112 GB may or may not fit.

If access remains unavailable, mark the UE splat runtime test BLOCKED, preserve exact runnable preparation and report the single next user action. This must not block collecting native results, finishing sources/handoff/slides, or committing work. Do not claim the complete native-plus-splat evaluation succeeded.

ANSWER THE THREE ARCHITECTURES
Explain separately (1) splats rendered inside UE, (2) external splat observations with the existing dynamics/control host retained, and (3) UE removed with named components owning dynamics, sensors, collisions and time. State what each replaces, what already exists, and what remains an unbuilt adapter. Camera replay through an external renderer is distinct from synchronized closed-loop sensor replacement.

Only compare images quantitatively if representations of the SAME world exist with matched camera poses, intrinsics, resolution and documented appearance assumptions. Do not compare Blocks against an unrelated splat scene as a fidelity benchmark. Held-out real-image evaluation needs approved AirLab images, calibration, train/test split and a compatible reconstruction. Without these, give the exact missing inputs and leave fidelity/altitude-transfer conclusions pending.

DELIVERY AND PARALLEL WORK
Canonical repository: WorldExplored/R4R-Sims.
Local checkout: ~/Downloads/AL/R4R-Sims/.
Keep code/configs in simulators/unreal/, notes in docs/unreal/, small evidence in results/unreal/<run-id>/ and large artifacts in ignored artifacts/unreal/<run-id>/ or verified durable storage. Inspect current README/AGENTS and new docs/r4r-audit-context.md if available. Current host measurements supersede older provisional setup assumptions.

Other simulator work is concurrent. Use an isolated candidate branch/worktree; commit only owned files. Preserve newer commits, uncommitted changes and existing approvals. Do not reset/force-push or modify shared planning files casually. Push task commits and pull the same branch locally. Report actual branch/commit URLs.

Collection verification must compare the destination with a SOURCE file-size/SHA-256 manifest made for completed files. Hashing the destination and comparing it with itself does not verify transfer. Copy configs/patches, trajectories, logs, frames/depth/videos, essential scene/checkpoint inputs and edited UE project assets. Open representative copied outputs and parse records. Preserve failed runs too. Inventory free local space. Document verifiable retrieval/version/hash/access for reproducible dependencies instead of copying full engine/cache trees. Git does not preserve ignored artifacts.

Collect completed evidence now and periodically during further work. Do not leave the only copy on this host or terminate it before verified preservation. Report any local/durable collection blocker honestly. Kill only owned processes; do not shut down the instance yourself.

Finish handoff.md, sources.md, assets.md and the actual result deck from measured native evidence, with splat/real-data/policy blockers clearly labelled. Include reference versus actual trajectory plots, RGB contact sheet, depth visualization, measured cadence/resource use, failures, limitations, architecture comparison and a short supervision guide. Use the same evidence categories and R4R dimensions as the other candidates; do not fabricate their results or rank unlike tasks as simulator performance.

Return a test-by-test demonstrated/failed/blocked/not-tested table; exact local artifact paths; source/destination checksum status; pushed commits; what the existing results let us conclude for R4R; what remains untested; and the exact action needed to unblock the splat test. Do not stop at a progress summary while independent authorized work remains.
```
