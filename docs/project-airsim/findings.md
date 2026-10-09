# Project AirSim v1.0.1 bounded audit for Real4Real

Run date: 2026-10-09 UTC. Candidate branch: `eval/project-airsim`. Packaged Blocks was run on the supplied A5000 host. The five conclusions below are intentionally separate. Numerical targets are audit choices, not AirLab acceptance criteria or real-world validation.

## Decision by research question

| Question | Status | Evidence and limit |
| --- | --- | --- |
| 1. Native controller, dynamics and sensor integration | **Partly demonstrated; fails full route criteria** | Two Simple Flight + Fast Physics route runs captured RGB, raw depth and actual vehicle pose; horizontal tasks returned true and ended 0.053/0.035 m from target. Takeoff returned false in both; vertical returned false in both; return returned false once. Stock Blocks dynamics are uncalibrated to the real drone. |
| 2. Pose-setting capture, calibrated replay, synchronized replay | **Pose capture demonstrated; calibration and synchronization partial** | Two original non-physics A sequences set all five poses with 0 m reported translation error and <0.000003° quaternion orientation difference after normalization. A separate corrected downward-camera sequence did the same. All 20 RGB/depth records per sequence advanced in timestamp after the achieved pose. Native K, configured mount and direct image camera poses were exported. There was no independent camera calibration or atomic cross-camera capture. |
| 3. Dynamics/control host with external Gaussian renderer | **Plausible architecture, not demonstrated integration** | Native control/state and timestamped camera-pose interfaces were observed. External observation substitution, clock coupling, common geometry/collisions and an observation-consuming controller were not implemented. |
| 4. Reconstruction and held-out real-image fidelity | **Blocked** | No approved real captures, calibration, reconstruction asset, train/test split, held-out horizontal/vertical images or evaluation thresholds. Stock Blocks cannot answer altitude extrapolation (15 m capture to 50 m render) or real-image fidelity. Perception usefulness additionally needs a selected model/task, labels or reference outputs and metrics. |
| 5. Learned-policy/perception-driven navigation | **Blocked** | No selected navigation task and compatible policy/perception pipeline or usable weights. The waypoint controller did not consume RGB. No policy was trained or evaluated; policy latency is N/A. |

**Recommendation:** use Project AirSim as a **conditional dynamics/control host** for a separately specified Gaussian-renderer experiment. Keep packaged Blocks as a **native visual and API baseline**. **Defer** renderer selection for held-out Real4Real fidelity, altitude extrapolation and downstream perception until the missing real-scene inputs exist. Do not treat the stock simulator as a reconstruction renderer or a learned-policy result.

## Scope and inputs

Real4Real targets outdoor residential, suburban and campus views below 100 m, including held-out horizontal and vertical trajectories. Indoor, sparse physical scenes and racing remain separate applicability questions. Sparse training-image coverage differs from sparse scene content. Blocks is an indoor synthetic stock scene. The release lists Neighborhood (closer in content to residential areas) and LandscapeMountains (outdoor landscape, unlike the target housing/campus distribution). Neither is reconstructed from Real4Real imagery. [Release](https://github.com/iamaisim/ProjectAirSim/releases/tag/v1.0.1).

The host was Ubuntu 22.04.5, Intel Xeon Gold 6342 (96 reported logical CPUs), 503 GiB RAM, 120 GiB overlay disk and RTX A5000 24,564 MiB. NVIDIA proprietary driver 580.178.04, Vulkan loader and NVIDIA ICD/device were verified. CUDA alone was not used as evidence of graphics access. Full-instance billing including storage/other charges was **not available**; no hourly cost is claimed. An initial root launch was rejected by UE; the packaged executable then ran offscreen under the existing unprivileged `nobody` account. The second launch later crashed with SIGSEGV after A2. The third launch served B and the corrected A sequence. This exhausted the three-launch cap. LandscapeMountains acquisition was feasible by listed size (593,115,486 bytes; published SHA256 `b008c48e0a6f864073968fb2ef44f9937dea6bba04488655796e3f8155defc06`) but a separate packaged environment could not be launched within the remaining launch budget. No outdoor flight is claimed.

Pinned source commit `09755454b8d82b0231af7e59fd1ab8f980ff32c5`; official `Blocks-Linux-1.0.1.zip` SHA256 `4a0c7b6de27ed32bdf4de1c31c222c19b796500108b654382b5d76b4ba000040`, matching the release digest. The unpacked archive launched `Blocks.sh`, UE 5.2.1. The isolated Python client was `projectairsim==1.0.2`, prescribed by the v1.0.1 release. The packaged server reported build hash `deff6aa11dd8961ae5de05ea64630995a12bbf67`, distinct from the release source commit; observed APIs worked. [Source investigation](source-investigation.md) gives pinned paths. No editor, rebuild, renderer injection, training or large policy download occurred.

## A: pose control and replay

The original two sequences are `20261009T002738Z-pose-1` and `20261009T002820Z-pose-2`, both at runner commit `8911bf8`. The separate camera-mount repair is `20261009T003933Z-pose-corrected` at `768ab92`. All used the documented `non-physics` mode and the same absolute vehicle poses: base (-1, 8, -4) m, +2 m in NED X, 1 m upward (NED Z=-5), yaw -45° to -15°, then base. Set-pose returned true at all 15 steps. Ground-truth vehicle pose agreed at every step: maximum position error 0 m and normalized-quaternion angle error <0.000003°. Targets were ≤0.01 m and ≤0.1°.

Each sequence saved 10 PNG RGB and 10 `.npy` float16 planar-depth frames across two cameras. Within a camera, RGB/depth shared a timestamp. For the corrected sequence, image timestamps were at least 31 ms of **simulator time** after its achieved pose timestamp; the two original sequences had minima of 71 ms and 3 ms. All 20 per-run freshness checks increased relative to the preceding request on that camera/type. Direct image camera pose metadata shows the 2 m translation, 1 m vertical translation and 30° rotation. The corrected camera’s reported position equals the vehicle position because its native mount translation is zero. These checks demonstrate fresh pose-controlled capture, not atomic synchronization of both cameras or exact repeat pixels. The two original sequences showed RGB variation at identical poses; several forward depth pixels saturated at 65504.

Median `get_images` request round trip, measured at the client wall clock, was 254 ms, 278 ms and 289 ms for A1, A2 and corrected A respectively (20 image records per sequence, with RGB/depth from one request assigned the same interval). This is not one-way sensor latency or pure renderer time.

The first two A sequences mistakenly had the nominal `DownCamera` at mount `(0,0,0.5) m`, pitch -11.46°, so those are **not downward-view calibration evidence**. The separately hashed repair uses mount `(0,0,0) m`, pitch -90°, as in B. It was run once under the permitted diagnosed repair, without a repeat at that corrected configuration. Compare camera poses only within a configuration. The camera named `ForwardCamera` is at frame origin; its first corrected A depth contained about 32.9% `65504` saturated pixels and near-field values down to 0.1 m. This mounting can see the vehicle, limiting its use as an unobstructed forward view.

**Achieved levels:** pose-setting capture: demonstrated on stock Blocks. Native-config calibrated replay: partial (K, mounting and direct camera pose exported; no independent real-camera calibration or distortion validation). Synchronized replay: partial (RGB/depth per camera share timestamps; separate camera requests and no atomic step/trigger across cameras). `get_images` returned images with timestamps later than pose setting in these runs; the test did not identify an old buffered image. A fixed sleep was not used as sole evidence.

## B: controller, dynamics and sensor integration

Path: absolute waypoint commands → Simple Flight → Fast Physics → `actual_pose` and native camera messages. RGB was recorded concurrently, **never fed to the waypoint controller**. Initial smoke `20261009T002844Z-smoke-1` was blocked by the server crash. Smoke `20261009T002933Z-smoke-2` and one diagnosed retry `20261009T003251Z-smoke-repair` both had false takeoff and horizontal results; landing timed out at the client's 10 s NNG receive timeout. The async client creates a request context before returning its task; the first timeout edit happened after that creation and did not repair it. The measured-run code set a 30 s receive timeout before context creation, retaining a 10 s ordinary request timeout. No smoke pass is claimed.

The frozen [route](frozen-route.md) used spawn (-1,8,-4) m and yaw -45°; gravity settled the vehicle on a Blocks surface near Z=-2.693 m. Its absolute horizontal target was (1.5,8,-4), vertical target (1.5,8,-5), yaw -15° absolute (-0.261799 rad), return (-1,8,-4), with 3 s wall holds and native land. Both measured runs reloaded the same scene/config without teleports during the measured flight. The route remains a scripted indoor integration test, not obstacle avoidance or visual navigation.

| Metric | Flight 1 `20261009T003453Z` | Flight 2 `20261009T003606Z` | Audit target |
| --- | ---: | ---: | --- |
| Takeoff task | false | false | true within timeout |
| Horizontal task; endpoint error | true; 0.053 m | true; 0.035 m | true; ≤0.5 m |
| Vertical task; endpoint error | false; 0.445 m | false; 0.444 m | true; ≤0.5 m |
| Yaw task; heading error | true; 1.65° | true; 2.30° | true; ≤10° |
| Return task; endpoint error | false; 0.488 m | true; 0.504 m | true; ≤0.5 m |
| Hover 1 max displacement; median 100 ms finite-difference speed | 0.046 m; 0.012 m/s | 0.046 m; 0.012 m/s | ≤0.5 m displacement |
| Hover 2 max displacement; median speed | 0.005 m; 0.002 m/s | 0.006 m; 0.003 m/s | ≤0.5 m displacement |
| Land task/native landed state | true / 1 | true / 1 | landed, motion and ground check |
| Native collision events | 2 (spawn, landing) | 2 (spawn, landing) | record actual events |

Endpoint position is the nearest native pose sample at command completion (within 1.3 ms wall); a later command may begin immediately, so five-second settling was not separately measurable for every segment. Return flight 2 exceeded 0.5 m by 0.004 m. Hover speeds are approximate finite differences from position over 100 ms wall intervals, not native velocity topic readings. Both land states were 1, with final Z≈-2.693 m and collision/ground contact evidence. This does not establish a safe outdoor route or calibrated dynamics.

The [horizontal plot](../../artifacts/project-airsim/20261009T003453Z-flight-1/analysis/trajectory_horizontal.png) and [vertical plot](../../artifacts/project-airsim/20261009T003453Z-flight-1/analysis/trajectory_vertical.png) show requested steps and achieved native vehicle positions. Their source traces are `actual_vehicle.jsonl`, `reference_route.jsonl` and `actions.jsonl` in each ignored local artifact directory. Data for both outcomes remains available even where thresholds fail.

## Camera, timing and resources

Configured RGB: 400×225, horizontal 90° FOV, type 0, 8-bit decoded PNG; configured transfer compression true. Planar depth: type 1, raw `16FC1` float16 arrays in meters, not colorized depth. `K=[200,0,200;0,200,112.5;0,0,1]` was reported for both cameras, consistent with horizontal FOV and square pixels. The implied vertical FOV is about 58.7° under a pinhole/no-distortion assumption. Native camera mounting transforms, directly reported image poses, vehicle poses and exact per-run configs are preserved. Quaternion fields are `w,x,y,z`; NED meters are used for commands and recorded positions. Rendering projection beyond the reported K, antialiasing and effective exposure/gamma were not independently measured; config requests gamma 2.5, manual exposure method 3 and motion blur 0. Pixel-identical replay is not promised.

The release documentation defines Depth Planar as distance from the camera plane; it is not ray distance (Depth Perspective). The received arrays had shape 225×400, dtype float16. Some forward images used 65504, maximum finite float16, as a saturated/no-return-like value; it was masked in previews and remains raw in `.npy`. No conversion to float32 was made in storage. Colorized depth is only a preview.

| Timing/resource observation | Flight 1 | Flight 2 | Meaning |
| --- | ---: | ---: | --- |
| State span, wall / simulator | 43.106 / 31.392 s | 43.123 / 31.536 s | Distinct clocks; no synchronized one-way latency inference |
| Saved RGB / depth, both cameras | 608 / 607 | 610 / 611 | Received = saved; queue drops 0 |
| RGB saved per wall second, combined | 14.10 | 14.15 | Delivery/save rate, not renderer FPS |
| Forward RGB frames / simulator span | 304 / 31.191 s | 305 / 31.461 s | Median timestamp gap 0.102 s; no duplicate timestamps |
| Forward max timestamp gap | 0.117 s | 0.204 s | Observable capture gap only |
| Median callback-to-save interval | 30.8 ms | 34.6 ms | Client-side processing/storage, not sensor latency |
| Sampled GPU memory peak / utilization peak | 992 MiB / 49% | 984 MiB / 60% | `nvidia-smi` ~1 s samples, may miss peaks |

The RGB [video](../../artifacts/project-airsim/20261009T003453Z-flight-1/analysis/forward_rgb_10fps.mp4) uses ordered ForwardCamera PNGs at constant 10 frames/s for playback, with one padded row for H.264's even-height requirement. Native frames are 400×225; the encoded video is 400×226. It does not preserve variable wall delivery timing. [RGB preview](../../artifacts/project-airsim/20261009T003453Z-flight-1/analysis/rgb_preview.png) and [labeled depth preview](../../artifacts/project-airsim/20261009T003453Z-flight-1/analysis/depth_preview.png) are derived; the PNG and `.npy` sequences remain authoritative. The configured interval was 0.1 simulator seconds; expected theoretical captures, actual received messages and saved frames should not be equated without exposure of the engine's dropped-capture count. No renderer-process GPU synchronization or pure render-time instrumentation was available. Cold startup and a formal 10 s warm-up were not instrumented; setup/downloading completed under the 45 min attempt bound, with a roughly 7 s logged Blocks download, but an exact end-to-end setup duration is unavailable.

## C: policy availability

The v1.0.1 release assets, pinned example scripts and model paths were inspected within the 15 min bound. No checkpoint with a compatible selected navigation task, license, model interface and observation contract was verified. ONNX-related runtime libraries alone do not establish a supplied navigation policy. This result means **weights none for this audit**, not that Project AirSim universally lacks policy support. Scripted route, built-in Simple Flight controller, pretrained learned policy and new training are different objects. No training or policy inference occurred.

## Gaussian host assessment

| Component | Evidence class | Assessment |
| --- | --- | --- |
| Native state, Simple Flight, Fast Physics | Demonstrated | Vehicle state and route control worked with failures documented above. |
| Native image camera pose and K | Demonstrated | Direct metadata, timestamps and configured mount support pose export. |
| External Gaussian observation rendering | Missing | No renderer was connected; no common-scene image comparison. |
| Observation substitution into controller/policy | Missing | The waypoint controller does not consume images. A learned controller would need an explicit adapter. |
| Clock synchronization | Documented interface, untested coupling | Simulator timestamps exist. External render scheduling and latency/step semantics need a dedicated experiment. |
| Geometry/collisions | Native collisions demonstrated; cross-renderer equivalence missing | Native Blocks geometry produced spawn/landing collision events. A Gaussian view alone does not provide physical collision geometry. |
| Depth semantics | Demonstrated native planar depth; external unknown | A Gaussian renderer's depth must be declared planar/ray and validated in the same camera frame. |

The smallest next experiment is a single approved real outdoor scene with calibrated camera poses and a fixed train/test split including horizontal and vertical held-out images. Freeze thresholds and a downstream perception model/task with labels or reference outputs before comparing a Gaussian renderer and a native camera baseline. A separate host test should feed externally rendered observations to a specified controller under explicit clock and collision rules. None of these steps was executed here.

## Reproduction and preservation

Local worktree: `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-worktrees/project-airsim`. Remote checkout: `/root/R4R-Sims-project-airsim`. Dependencies were isolated under `/root/r4r-airsim-deps`, outside tracked source. The canonical checkout and its unrelated modifications were left untouched. Remote GitHub authentication was unavailable; local authenticated Git pushed the branch, and incremental Git bundles fast-forwarded the same branch on the remote. No personal credentials were copied to the VM. The private SSH key is not in any results artifact.

Run command shape (from the remote checkout, after `setup_linux.sh` and packaged launch):

```bash
simulators/project-airsim/preflight_linux.sh
simulators/project-airsim/run_one.sh pose 20261009T003933Z-pose-corrected
simulators/project-airsim/run_one.sh flight 20261009T003453Z-flight-1
simulators/project-airsim/collect_linux.sh 20261009T003453Z-flight-1
/root/r4r-airsim-deps/venv/bin/python simulators/project-airsim/analyze.py artifacts/project-airsim/20261009T003453Z-flight-1 artifacts/project-airsim/20261009T003453Z-flight-1/analysis
```

The literal historical commands, code revisions, Python package freeze, configs/hashes, native records, GPU samples, failure logs, per-file SHA256 and artifact sizes are in the [results index](../../results/project-airsim/README.md) and its run directories. Replay uses new UTC run IDs; the IDs above are historical identifiers, not commands to overwrite them. Each raw directory was copied via resumable rsync to the isolated local artifacts path and its manifest checked locally. All large capture sequences and videos are ignored by ordinary Git.

## Common comparison table

| Capability | Project AirSim finding | Run status | Evidence strength | Source/run reference |
| --- | --- | --- | --- | --- |
| Capture import | Native stock cameras; no real capture import tested | Partial | Direct native capture | A/B runs; `images.jsonl` |
| Scene representation | Packaged UE Blocks mesh/physics; no reconstructed scene | Demonstrated stock only | Direct package/config | Release; configs |
| Pose replay | Non-physics `set_pose` sequence | Pass for vehicle pose | Direct repeated state | A1/A2; corrected A |
| Calibration | Native K and mounts, direct image camera pose; no independent real calibration | Partial | Direct metadata + config | `camera_info.jsonl`; image records |
| Dynamics/control | Simple Flight + Fast Physics; mixed false task outcomes | Partial/fail criteria | Direct two-route trace | B1/B2 actions and plots |
| Sensors | RGB PNG + planar float16 depth; saturation observed | Pass for interface | Direct payloads | A/B raw captures |
| Policy availability | No compatible task-matched weights verified | Blocked | Bounded asset inspection | v1.0.1 release/examples |
| Indoor/outdoor/racing | Indoor Blocks integration only; no outdoor/racing run | Indoor only | Direct run; outdoor docs only | B1/B2; release |
| Setup burden | Pinned binary/client installed; root launch failure, crash, unprivileged repair | Completed with failures | Direct logs | setup/launch logs |
| Measured resources | A5000 ~1 GiB sampled VRAM; 49–60% sampled GPU peak | Measured stock run | 1 s samples | B1/B2 GPU CSV |
| Preservation | Local checksummed raw and small result records; branch pushed | Verified for listed runs | SHA256/Git | results index |
