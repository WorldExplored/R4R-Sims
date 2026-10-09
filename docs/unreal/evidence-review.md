# Unreal preserved-evidence review

Reviewed **8 October 2026 Indianapolis / 9 October UTC** from local immutable evidence and pinned GitHub source. No SSH, remote inspection, installation, simulator execution, GPU experiment or deletion occurred. This review starts at audit commit `bc14c24ad7288848019a4aea541853980fa2d7bb`; the dirty canonical `main` checkout's `simulators/unreal/analyze.py` was preserved. Authored review files use the existing `unreal-a5000-audit` worktree.

**Conclusion:** native camera replay and yaw sanity are demonstrated. Scripted flight is demonstrated but **B fails end-to-end acceptance**. UE5 exported a final-color cube and one dark splat frame; useful splat appearance is unvalidated. No learned policy or complete R4R workflow was demonstrated. Outdoor reconstruction, 15 m capture→50 m novel views and real-drone transfer remain research questions.

## 1. Evidence availability and provenance

Canonical preserved root: `/Users/srreyanshsethi/Downloads/AL/R4R-Sims/`. Below, **RAW** means `artifacts/unreal/`; **INPUTS** means `third_party/unreal/assets/`. Historical `/root`, `/tmp` and `/workspace` paths inside records are execution provenance, not currently available remote paths.

Fresh [verification.json](../../results/unreal/evidence-review-20261008/verification.json) compares actual local size/SHA-256 to VM-created manifests, then anchors those manifests against committed [recovery.json](../../results/unreal/closeout-20261008/recovery.json) and [residual-source-manifest.json](../../results/unreal/a5000-cleanup-20261008/residual-source-manifest.json):

- **18 run directories: 360 files / 69,923,660 B**, no missing or changed manifested file.
- **Residual backup: 98 files / 6,338,480 B** under `RAW/unreal-final-backup-20261008/`; includes setup traces, script variants and essential saved projects.
- **Compiled plugin: 128 files / 45,291,029 B**, no mismatch. Total **586 source-manifested files** checked; 92 PNGs (including plugin resources) and 37 depth arrays decoded. Depth arrays are finite 480×640; finite values alone do not establish physical validity.
- All three ZIPs freshly hashed; no duplication or expansion. Imported map, point-cloud `.uasset`, `.uproject` and configs match the S run manifest. These inputs are locally recoverable without depending on the cleared host.
- The preflight-only log `RAW/ue-20261008T215415Z-b-e868ec1c/supervisor.log` SHA `c38e191da2494e78784b46e5b7d080b49507feaafe4a316c0c1a1bbadc051fdf` matches the **source-manifested residual copy** `tmp/ue-20261008T215415Z-b-e868ec1c-supervisor.log`. This improves the earlier recovery record's stated provenance exception; it does not invent a missing preflight run directory.
- Three preserved MP4s match their source manifests. Prior closeout generated local macOS thumbnails; this review makes no new full-video decode or playback-rate performance claim.

| Input | Exact source identity; bytes; SHA-256 |
| --- | --- |
| `INPUTS/Blocks_v1.8.1.zip` | [Microsoft release](https://github.com/microsoft/AirSim/releases/download/v1.8.1/Blocks.zip); 142,533,463 B; `563e1da1b5d7303b9405c8736243ea92ab0a011b96a561f26f17563d105a404f` |
| `INPUTS/Linux_Unreal_Engine_5.5.4.zip` | Official Epic authorized Linux installed build; 27,085,247,533 B; `e20acd77e6caad42ee1bf0df1cb4c5077ceb1350817cfdacb554f4a594710383` |
| `INPUTS/PlyExamples.zip` | Author's linked example archive, provenance/access in [assets.md](assets.md); 123,484,316 B; `ff13af1728c26095bb4e2b51b1f27ee5470acb805e0ad16360fe28876ec03b1e` |
| ZIP member `chinese_vase.ply` | 22,798,434 B; `59b33386c8f0509df11ffd6314284d67895bf20a15b17c5f7e5b6e58d6416506`; no recorded real capture/calibration/split |
| Native entry points | `Blocks.sh` is a **238 B launcher**, SHA `e74e0dd7bad0c33b3ecdd8628290f84e9632ac4c64d840ffc5a8ee62021ebe8e`; actual 165,504,360 B ELF SHA `97e9b0671024454ec29336209843bf72af5cb788af9e27882d77409de4677654`. Both match the same retained ZIP: differing A/B metadata hashes are launcher versus ELF, not a binary patch. |

GitHub holds scripts, small summaries/figures, decks v2/v3, source/asset ledgers, recovery manifests and historical cleanup records. Ignored raw logs, frames/depth/videos, proprietary editor ZIP, sample ZIP, compiled plugin and essential imported project are **local artifacts**, not preserved by Git. Do not mistake a Git push for off-device backup of those large assets. Existing licenses/access limits in assets.md still apply; no Epic archive or author sample redistribution permission is inferred here. Cleanup records show earlier removal; no current instance state or other-host dependency was inspected this turn.

## 2. Exact tested pipelines

[Pipeline records](../../results/unreal/evidence-review-20261008/pipelines.json) retain selected `run.json`, settings, routes, camera rows, waypoint completions and previous analysis. **The copied per-run scripts are the executed versions**; current Git scripts contain subsequent fixes. Native launch flags were `-RenderOffscreen -vulkan -windowed -ResX=640 -ResY=480 -nosound -log`; S used `UnrealEditor-Cmd -RenderOffscreen -vulkan -ExecutePythonScript=...` under `runuser nobody`, with saved per-run launch scripts/watchdogs and `render.exit`. These are historical commands, not permission to rerun. All experiments used weights **none**, no scene/policy training, no exposed engine seed, and no real train/test split.

### A: pose replay → native RGB/planar depth

`Blocks.zip + ComputerVision settings.json + reference_route.json → copied audit.py → AirSim RPC simSetVehiclePose(ignore_collision=True) → packaged UE4.27.2 / Vulkan / FlyingExampleMap → simGetImages(Scene PNG, DepthPlanar float) → frames/*.png, depth/*.npy, camera.jsonl, vehicle_trajectory.jsonl, state.jsonl`.

Definitive run **`ue-20261008T215319Z-a-5fe9b7c3`**. Release/source association AirSim v1.8.1 commit `96235148a332fe7cb3d3525a0720e26faaca99e0`; engine log says **4.27.2-18319896**. This association is not source-to-packaged-binary attestation. Client AirSim1.8.1, Python3.11.11, NumPy1.23.5; full package freezes preserved. Ubuntu22.04.5/kernel6.8.0-146, RTX A5000 24564 MiB, driver580.178.04.

Requested NED metre centers: `(0,0,-2),(.5,0,-2),(1,0,-2),(1,.5,-2),(1,1,-2),(.5,1,-2),(0,1,-2),(0,0,-2)`, identity rotation. Three discarded warmup calls; 0.25 s settle per pose. Actual rig and RGB capture centers match those eight targets exactly to recorded precision. This teleports a rig and exercises no flight controller.

Camera `front_center`: 640×480, response HFOV **89.903625°**; pinhole assumption `fx=fy=320.538710`, `cx=320,cy=240`, square pixels, no distortion calibration. AirSim NED is right-handed, +Z down, metres; UE is left-handed +Z up, centimetres. Named quaternion components `w,x,y,z` govern interpretation despite the misleading historical key `orientation_xyzw_ned`. AirSim's origin/heading is scene-relative; no geospatial calibration exists. RGB response pose is the capture pose; later camera-info/rig calls are distinct records.

Fresh [camera/depth review](../../results/unreal/evidence-review-20261008/camera-depth-review.json): all retained native arrays are positive finite, but include >10 km sky/far values. First A RGB/depth boundary check is within **one pixel at five columns**; this limited test does not establish full registration. Original A/B depth timestamps and depth response poses were **never recorded** and cannot be recovered from later tests.

Separate camera sanity **`ue-20261008T232215Z-yaw-6b9a9962`** holds `(0,0,-2)` and yaw `0,90,180,-90,0°`, 0.5 s settle. Fresh decode reproduces distinct-view RGB mean differences **31.29–43.08/255** and **94.1–99.0%** changed pixels; return-to-zero difference0.968/255. Requested→RGB position error0, quaternion error≤0.0000137°. RGB/depth timestamps differ **5.249–8.051 ms**, with orientation agreement to rounding. Static rig removes movement during this offset; moving acquisition synchronization remains unproven. [Original local yaw sheet](/Users/srreyanshsethi/Downloads/AL/R4R-Sims/artifacts/unreal/ue-20261008T232215Z-yaw-6b9a9962/yaw-contact.png) was reopened and visually confirmed. Original eight-frame A is retained unchanged.

### B: estimated state → scripted velocity → dynamics → observations

`same Blocks ZIP + Multirotor/SimpleFlight/FastPhysicsEngine settings + five square waypoints → copied audit.py position feedback → moveByVelocityAsync → SimpleFlight inner controller + AirSim dynamics + UE collision/native camera → actions/state/actual vehicle/capture pose/collision/RGB/depth records`.

Final route run **`ue-20261008T220451Z-b-a3d4be49`**, audit source commit `a082b6044fed4ee4b41881dd2002cc7c8ff7adfa`. After takeoff, five requested points are a 1 m square returning to start at NED z=−2; exact start-offset coordinates are in its route file. Outer observation is estimated XYZ; action is NED velocity `clip(0.7*(target−estimate),±0.7)` **per axis**, duration0.2 s, default drivetrain/yaw. This is not a scalar norm speed cap or learned policy. Target5 Hz, waypoint tolerance0.25 m, each waypoint15 s, takeoff15 s/land20 s, wall cap180 s plus independent190 s supervisor. No inner-controller gain override recorded; released defaults are source-associated, not instrumented binary measurements.

All five waypoint completion records exist, with errors **0.228–0.248 m**. Actual vehicle path and actual camera path are distinct; later camera-info position differs from capture response by up to **0.06456 m** in moving B. Collision baseline is retained, and the fixed guard rejects only **new timestamps**; it does not suppress later collisions. Eight image pairs, 69 velocity commands and94 states were recorded. Land RPC `.join()` discarded its boolean; subsequent explicit polls remained Flying at floor contact, so exit1/end-to-end failure is retained. The later no-camera isolated test reproduces this failure (section4).

### S: released PLY → imported UE5 Niagara → exported final color

`author chinese_vase.ply → pinned Italink PLY factory → saved /Game/Gaussians/chinese_vase + /Game/Maps/VaseSmoke → GaussianSplattingPointCloudActor / Niagara data interface → SceneCapture2D → RGBA8 final-color PNG`.

UE **5.5.4-40574608+++UE5+Release-5.5 Linux installed build**, plugin commit **`411f879985719ce69eaaf15d58152c551e2719b1`**, locally retained BuildPlugin logs record clang18.1.0rc (LLVM461274b81d8641eab64d494accddc81d7db8a09e) and successful plugin build (not engine source build). Import run `ue-20261008T222943Z-s-8434c18c`; final saved project from **`ue-20261008T224031Z-s-fe9a3ea3/captured-project/`**, source-manifested map/point-cloud/config. Import asset SHA `4dddbe3ce2b334c4edb002d5685eb49bde6c9d6ed4f0e66cdb408e981ebea4f0`. S had no drone/control layer, simulated vehicle, policy or collision/depth validation.

Eight requested UE-cm route centers: `(900,0,0),(900,80,0),(900,-80,0),(900,0,80),(900,0,-80),(850,80,60),(850,-80,60),(900,0,0)`. Actual centers match, but positional Rotator arguments produced unwanted roll/pitch (first actual pitch≈0,yaw180,**roll180**). All frames remained RGB0–1; **this route failed**. Corrected current route script was not rerun successfully.

Final fixed-frame run **`ue-20261008T232833Z-s-light-573e44a0`**: requested/actual camera `(900,0,0)` cm, pitch0/yaw180/roll0, local forward−X, 640×480/HFOV60°, assumed `fx=fy=554.256258,cx=320,cy=240`. `RTF_RGBA8`, `SCS_FINAL_COLOR_LDR`, capture-every-frame/movement off; actual Slate editor ticks, Niagara activated and scalability disabled. Stationary directional light at `(0,0,500)` cm, pitch−45/yaw180, intensity10; 3× default cube at origin. Cube capture requested tick20/export22; cube hidden and splat requested24/export26. **Niagara remains active during the mesh control**: the silhouette over the cube is not a clean mesh-only reference.

Project renderer defaults disable auto exposure/motion blur. Explicit per-capture exposure, effective postprocess/pre-exposure, material eye-adaptation value and pixel exposure instant were not recorded. Saved map plus scripts recover temporary actors/settings; no final runtime-edited map was saved. Request/export times are wall events, not synchronized GPU/exposure times.

## 3. Distinct failed attempts and validation gaps

Every ID below maps to `RAW/<run-id>/`. [failure-index.json](../../results/unreal/evidence-review-20261008/failure-index.json) gives exact traceback file/line locations; `commands.log`, copied script, `run.json`, console/render log and diagnostics remain immutable. Routine OpenXR warnings also appear in successful native runs and do not establish the fatal cause.

| Run ID | Exact failure/contradiction; cause status | Correction and retest; remaining unknown |
| --- | --- | --- |
| `ue-20261008T215142Z-a-f0246d36` | `supervisor terminated child`, exit−15 before captures. No preserved fatal RPC traceback; startup/readiness failure is a **hypothesis**. | Connection retry changed; next A exported8 pairs. Original termination cause and exact RPC server ownership are not proved. |
| `ue-20261008T215415Z-b-e868ec1c` | Preflight `port_41451_free:false`, exit1; confirmed occupied socket. | Replaced shell-wrapper launch with direct ELF/dedicated process-group ownership; subsequent B launches connected. Preflight log alone does not identify the socket PID; previous handoff's leftover-child attribution is historical diagnosis. |
| `ue-20261008T215611Z-b-d415e2e7` | `RuntimeError: Collision; stopped`, audit.py346/console948–951. Guard treats spawn contact as route failure. | Recorded spawn timestamp/object baseline and compared newer contacts; subsequent square flight worked. Baseline retained separately. |
| `ue-20261008T215758Z-b-33710b89` | Raw exit0 but no post-land state or server boolean; `.join()` returns None. Completion does not prove landing. | Added waypoint completion and landing observations in later runs. Original server return is irrecoverable. |
| `ue-20261008T220223Z-b-eddeea80` | Raw exit0; last recorded z−0.834705, vz+0.203431 m/s, Flying during descent; `.join()` loses boolean. | Added10 s LandedState check; final route run failed it. Full original post-land timeline absent. |
| `ue-20261008T220451Z-b-a3d4be49` | `RuntimeError: landAsync returned but LandedState remained Flying for 10 s`, audit.py391/console946–949. Final z≈+0.681541, stationary after new floor contact. | Isolated no-camera/no-route reproduction still failed. Failing firmware predicate unknown. |
| `ue-20261008T222943Z-s-8434c18c` | Editor exit0 despite Python `AttributeError: 'SceneCapture2D' object has no attribute 'get_capture_component2d'`, render.log2088;0 frames. | Correct read-only `capture_component2d` property; next run reached export. Import/build success is separate. |
| `ue-20261008T223559Z-s-8c7e26a7` | `RuntimeError: SceneCapture PNG missing .../frame_0000.png`, render.log2096. Export wrote extensionless PNG literally. | Added literal `.png`; eight files exported but decoded black. |
| `ue-20261008T224031Z-s-fe9a3ea3` | Eight PNGs RGB0–1; Niagara inactive after12 warmup steps; actual roll180 and wrong route rotations. | Named Rotator fields + real editor ticks/reactivation controls. No corrected successful route; darkness has several unresolved contributors. |
| `ue-20261008T224552Z-s-control-10f8cdbd` | Immediate cube and splat both RGB0–1 despite active Niagara. | Actual editor tick callback and named rotation; base-color geometry emerged later, final color still black. |
| `ue-20261008T224847Z-s-control-83b490d9` | 32 editor ticks; cube base-color max26 but final-color/splat max1. | Stronger light/channel control; no final-color pass. Tick/pose fixes alone insufficient. |
| `ue-20261008T225105Z-s-control-e488bef0` | 40 ticks/intensity100000; cube base-color max228 but final splat0–1. Light yaw0 leaves viewed cube face unlit; source-supported hypothesis for **mesh**. | Reversed light yaw in focused test; saturated cube, not useful control. Does not diagnose splat's material. |
| `ue-20261008T232324Z-land-isolated-a3227c9a` | Raw `passed`, but never Flying/airborne; arming during spawn settling and `.join()` hides return. | Audit rejects false pass; settle-ground + `.get()` + airborne criteria added. |
| `ue-20261008T232549Z-land-settled-04b41479` | `takeoffAsync server reported failure: False` despite≈1.51 m clearance/Flying; abort before land. | Diagnostic retry retained False failure while continuing descent to observe it; no acceptance relaxation. |
| `ue-20261008T232723Z-land-observed-c1f84706` | `RPC boolean or five-consecutive-Landed acceptance failed`; takeoff False, land True, post-contact Flying. | Definitive reproduction; no fix tested. Requires predicate instrumentation. |
| `ue-20261008T232449Z-s-light-1f298556` | Yaw180/intensity100000: center255/background≈222, visibly saturated. Weak pixel gate allowed one essentially black splat frame. | Intensity10 + stricter control gate produced final cube and dark splat. Initial gate's false acceptance retained. |
| `ue-20261008T232833Z-s-light-573e44a0` | Cube geometry usable; splat visible but mean0.159/255 and only0.322% pixels>10. This is **unvalidated appearance**, not a runtime crash/pass of fidelity. | No further GPU run. Same-PLY reference, connected material/exposure diagnosis missing. |

## 4. Definitive isolated landing timeline and source mapping

Run `ue-20261008T232723Z-land-observed-c1f84706`; [extracted timeline](../../results/unreal/evidence-review-20261008/landing-timeline.json) links to raw `actions.jsonl`, `state.jsonl`, `descent.jsonl`, baseline and validation. Wall seconds below start at runner clock, **not simulation seconds**;177 state records,88 descent records, median descent polling4.912 Hz, no image/route blocking. “Hover” here is observation of position hold, not an explicit hover RPC.

| Wall s | Definitive evidence |
| ---: | --- |
| 8.084849 | Takeoff requested, timeout15 s; ground reference settled spawn NED z=+0.669970870 m, baseline Ground_6 timestamp1791502048321702656. |
| 9.312772 | First sampled Flying with clearance>0.5 m:0.530607 m, vz−0.478892 m/s (+down convention). |
| 11.489092 | Takeoff `.get()` **False**; later verified clearance≈1.51 m. |
| Before20.716824 | 40 hold samples: clearance1.509107–1.535264 m. |
| 20.716824 | Land requested, timeout20 s; peak observed downward velocity0.289866 m/s. |
| 28.068106 | **First observed** new Ground_6 contact; collision timestamp1791502071551198208, state timestamp1791502071692201216. Clearance−0.011101 m relative to settled center reference; vz0; Flying. This is sampled contact observation, not an exact wall collision instant. |
| 28.152457 | Land `.get()` **True**. |
| 38.446236 | Final z+0.681071639, linear velocity0, Flying (1); collision flag nowfalse but same contact timestamp/object. Last five polls fail Landed gate. |

Pinned source retrieved again through GitHub contents API; hashes in [source-checks.json](../../results/unreal/evidence-review-20261008/source-checks.json). Use code line numbers from these exact files, not cached page layouts:

- [MultirotorApiBase.cpp25–76](https://github.com/microsoft/AirSim/blob/96235148a332fe7cb3d3525a0720e26faaca99e0/AirLib/src/vehicles/multirotor/api/MultirotorApiBase.cpp#L25-L76): takeoff rejects initial estimated speed>0.05 m/s, then returns moveToPosition/moveOnPath completion at initial z+getTakeoffZ, speed0.5. Landing repeatedly commands downward velocity0.2 and completes after **>10** checks of estimated vz≤0.05. This is a signed comparison, not absolute velocity, and does not require a collision or LandedState. Constants: [header364–365](https://github.com/microsoft/AirSim/blob/96235148a332fe7cb3d3525a0720e26faaca99e0/AirLib/include/vehicles/multirotor/api/MultirotorApiBase.hpp#L364-L365).
- [OffboardApi.hpp212–257](https://github.com/microsoft/AirSim/blob/96235148a332fe7cb3d3525a0720e26faaca99e0/AirLib/include/vehicles/multirotor/firmwares/simple_flight/firmware/OffboardApi.hpp#L212-L257): firmware Landed requires internal `takenoff_`, average motor output≤minimum armed throttle and **all three angular plus all three linear estimator components** abs<0.08. Taking-off detection uses motor output above threshold and abs(vz)>0.01. [RemoteControl.hpp150–153](https://github.com/microsoft/AirSim/blob/96235148a332fe7cb3d3525a0720e26faaca99e0/AirLib/include/vehicles/multirotor/firmwares/simple_flight/firmware/RemoteControl.hpp#L150-L153) obtains the **board's average motor output**, not an inferred commanded throttle.
- [SimpleFlightApi.hpp167–170](https://github.com/microsoft/AirSim/blob/96235148a332fe7cb3d3525a0720e26faaca99e0/AirLib/include/vehicles/multirotor/firmwares/simple_flight/SimpleFlightApi.hpp#L167-L170) maps firmware state to API enum. [moveOnPath340–449](https://github.com/microsoft/AirSim/blob/96235148a332fe7cb3d3525a0720e26faaca99e0/AirLib/src/vehicles/multirotor/api/MultirotorApiBase.cpp#L340-L449) can returnFalse when its waiter fails; observed height is not proof its completion predicate succeeded.

**Missing predicate inputs:** internal takenoff/landed transitions, actual board average motor output, actual configured minimum armed throttle, all angular estimator velocities, predicate-time rather than 5 Hz polled linear velocities, firmware goal mode/timeouts and takeoff waiter's cancellation/timeout/path-progress reason. None can be inferred from a zero sampled vertical velocity, collision flag, or False/True RPC. Public angular ground-truth logging could improve a future runner without rebuild; definitive diagnosis of the **exact failing internal branch** needs a compatible instrumented source build exposing these values. Released source association alone cannot attest that branch in the historical binary. The original run reproduced z≈0.681541; this isolated run z≈0.681072, so route/camera blocking was not necessary for the mismatch.

## 5. Splat schema, importer, material and appearance

[PLY review](../../results/unreal/evidence-review-20261008/ply-review.json) parses the actual retained ZIP member in memory: **91,923 vertices**, binary little-endian1.0, **62 float32 fields**: xyz, normals,3 DC,45 `f_rest`, opacity,3 log-scales,4 rotations. All finite. Normals zero. **87,215 vertices contain nonzero higher-order SH**,3,636,000 nonzero coefficients: representation loss affects this particular input, not just hypothetical files.

| Quantity | Measured range / selected transform |
| --- | --- |
| Positions | Bounds min(−1.712271,−3.058223,−1.597827), max(1.711851,3.034879,1.587942) in **uncalibrated sample units**. Import100*(X,−Z,−Y) assumes metre→cm; sample's physical scale/frame unproved. |
| Scales | Raw log ranges across axes≈−11.914..−0.718; exp scales≈6.697e−6..0.487571. Import exp, reorder(x,z,y), multiply100. |
| Quaternion | Raw norms0.451850..1.457132, median0.822835; normalize. Producer-style `rot_0..3` is **w,x,y,z**, importer reads1,2,3,0 into UE x,y,z,w and stores(x,−z,−y,w). |
| Opacity | Logit−5.522545..12.814271 → sigmoid0.003980..0.999997; stored in color alpha. |
| DC color | `0.28209479*f_dc+0.5`; RGB medians(0.406197,0.285238,0.240992), total range−0.122882..1.788988. Additional sRGB→linear conversion yields medians(0.137253,0.066141,0.047344), range−0.009511..3.819560; no importer clamp. This differs numerically from decoded DC; it does not establish correct radiometric interpretation or darkness cause. |
| Higher SH | `f_rest_0..44` range≈−0.341253..0.308247. Indices validated but **no retained SH storage/upload/evaluation** in selected point representation. |

Static source: [importer179–270](https://github.com/Italink/GaussianSplattingForUnrealEngine/blob/411f879985719ce69eaaf15d58152c551e2719b1/Source/GaussianSplattingRuntime/Private/GaussianSplattingPointCloud.cpp#L179-L270), [point fields18–55](https://github.com/Italink/GaussianSplattingForUnrealEngine/blob/411f879985719ce69eaaf15d58152c551e2719b1/Source/GaussianSplattingRuntime/Public/GaussianSplattingPointCloud.h#L18-L55), [GPU upload65–73](https://github.com/Italink/GaussianSplattingForUnrealEngine/blob/411f879985719ce69eaaf15d58152c551e2719b1/Source/GaussianSplattingRuntime/Private/GaussianSplattingPointCloudDataInterface.cpp#L65-L73). Only position/quaternion/scale/color float4 buffers survive. No inference about training quality follows.

Canonical 3DGS producer conventions are checked against [save_ply225–255](https://github.com/graphdeco-inria/gaussian-splatting/blob/54c035f7834b564019656c3e3fcc3646292f727d/scene/gaussian_model.py#L225-L255) and [build_rotation78–113](https://github.com/graphdeco-inria/gaussian-splatting/blob/54c035f7834b564019656c3e3fcc3646292f727d/utils/general_utils.py#L78-L113). Ordering/exp/sigmoid match this schema; the **specific sample producer revision, training camera frame and radiometric provenance are not recorded**.

**Basis caveat:** position transform M has determinant−1. Under canonical active R covariance `R diag(s²) Rᵀ`, the importer quaternion conversion plus scale permutation does not reproduce `MΣMᵀ` (CPU conditional median relative error1.086). Standard covariance conjugation would require the axial-vector sign det(M), in addition to the axis permutation. UE5.5.4 `Math/Quat.h1202–1214` confirms its usual active RotateVector cross-product formula. **Niagara's connected orientation/projection convention was not decoded**, so this is a localized verification candidate conditional on that convention, not a confirmed renderer defect or explanation of the image. Resolve the consumer before changing quaternion signs.

[Actor factory262–291](https://github.com/Italink/GaussianSplattingForUnrealEngine/blob/411f879985719ce69eaaf15d58152c551e2719b1/Source/GaussianSplattingEditor/Private/GaussianSplattingEditorLibrary.cpp#L262-L291) binds `NS_GaussianSplattingPointCloud` to the imported data interface. Its retained binary references `M_GaussianSplattingPoint`, whose serialized symbols include **MSM_Unlit, BLEND_Translucent, ParticleColor and EyeAdaptation**. These symbols identify the relevant material and exposure-related expression; they do **not** recover graph connections/effective exposure. The alternate static-mesh `M_GaussianSplatting` path is not the selected actor path. Directional-light correction validated the cube; it does not establish that an unlit splat should respond identically.

[Unaltered local cube](/Users/srreyanshsethi/Downloads/AL/R4R-Sims/artifacts/unreal/ue-20261008T232833Z-s-light-573e44a0/cube_final.png) and [splat](/Users/srreyanshsethi/Downloads/AL/R4R-Sims/artifacts/unreal/ue-20261008T232833Z-s-light-573e44a0/splat_final.png) reopened; [derived contact sheet](../../results/unreal/evidence-review-20261008/mesh-splat-contact.png) preserves native pixels without brightening. [Statistics](../../results/unreal/evidence-review-20261008/image-statistics.json):

| Export | Mean RGB /255 | Max | Any RGB>10 | SHA-256 |
| --- | ---: | ---: | ---: | --- |
| Cube with splat active | 35.546848 | 226 | 16.2861% | `01f4b633ff99ced5ec0797e74ef40b330763857391c50eb77b7779679e5d93c8` |
| Splat only | 0.158831 | 113 | 0.3216% | `4f3be948e71a357deb5848e61602af3b7fe28f07f5dfe265250b102b6c18225c` |

Cube request/export unix1791502158.640479/1791502159.245432; splat1791502159.438662/1791502160.441053. These are acquisition/export wall intervals, not render throughput or exposure time. Very dark red object fragments are visible; nonblack pixels are insufficient for useful observations.

**No existing reference-renderer image with this PLY identity and recorded matching cameras was found** in preserved runs, four-member PLY archive or author repository resources/README. Generic author screenshots are not an asset-hash/camera matched reference. For a future matched reference using CV +X right/+Y down/+Z forward, invert position as `p_PLY=Mᵀ*p_UE/100`. The fixed S camera becomes `(9,0,0)` sample units, camera-to-world columns right/down/forward `[(0,0,1),(0,1,0),(−1,0,0)]`; use transpose and `−Rᵀ*C` for world-to-camera. [Conversion record](../../results/unreal/evidence-review-20261008/reference-camera-conversion.json) checks orthonormality/handedness; reference-renderer conventions still need explicit adapter validation. No reference replacement was rendered. SH loss does not, by itself, explain darkness.

## 6. Rates, architecture and R4R limits

Original A33.50 s wall; median acquisition RPC3.129 s, median image interval3.389 s. Final B64.75 s wall; first→last recorded state simulation span≈48.83 s (not whole-run simulation duration), acquisition3.210 s median, image interval5.355 s (**0.187 Hz median-interval cadence;0.125 Hz over all camera timestamps including landing gap**). Velocity commands4.696 Hz from median interval but **2.007 Hz over their full action span**. The≥2 s wait is at most0.5 Hz before acquisition costs, never2 Hz. GPU 1 Hz samples show whole-device max A862/B769 MiB; these are sampled aggregate allocations, not renderer minimum VRAM or isolated process peaks. MP42 FPS is playback. Three image warmups exist; no GPU fence/synchronization, independent render throughput, policy latency, inner-loop achieved rate or meaningful S throughput was measured.

1. **Splats inside UE:** tested UE5 import/Niagara appearance/export. UE retains editor/render scheduling, world/compositor and potential collision host. No compatible UE5 drone layer or validated collision geometry was connected. Packaged UE4 Blocks cannot acquire the UE5 plugin simply by copying it in.
2. **External splat observations retaining dynamics/control:** only RGB/depth supplier changes; AirSim/UE dynamics, SimpleFlight, collision, other sensors and clock would remain. Timestamp/coordinate/intrinsic/exposure/deadline sensor adapter is **unbuilt**; offline replay would still be A.
3. **Remove UE:** a separate component must own dynamics, sensors, collision, time/control and evaluation. No complete replacement stack was built/validated; visual splats provide none of those guarantees.

For AirLab's below100 m residential/suburban/campus navigation, this is integration evidence only. Sparse vegetation, unseen branches/gaps, coverage/disocclusion, altitude extrapolation15→50 m, moving objects, depth consistency and collision are separate unanswered tests. Indoor task fidelity remains untested; current acquisition cadence and absent race course/policy do not establish racing suitability. **C blocked:** no compatible released learned policy/weights/task interface identified. No random weights/scripted-controller policy claim was substituted. Blocks versus vase is not a fidelity benchmark.

## 7. Fixability and smallest next tests — proposed, not executed

| Class | Issue / smallest next test | Required input/software; GPU / rebuild |
| --- | --- | --- |
| Already fixed | Getter→property, literal filename, named camera rotation, editor ticking/Niagara activation, final cube light direction/intensity. Preserve failed attempts. | Existing scripts show narrow successful fixed-frame retest; no new run needed to establish those facts. |
| Localized fix candidate | Dark appearance: dump connected Niagara/material graph and effective exposure/pre-exposure, verify imported DC/alpha on a few points; then **one matched-camera same-PLY reference/UE pair**, with mesh-only control and documented color/exposure. Change one justified conversion at a time. | Preserved PLY/project/plugin, UE5.5.4 and pinned reference renderer; inspection CPU where supported, image pair needs graphics GPU; plugin rebuild only if importer changes. No new dataset/training. |
| Localized fix candidate | Quaternion basis: decode Niagara orientation/projection consumer, compare one anisotropic Gaussian's transformed covariance and projected ellipse. | Source + tiny analytically specified Gaussian/PLY, not new trained scene; CPU math first, GPU one-frame if needed; importer change needs plugin rebuild, not engine build. |
| Requires runtime diagnosis | B takeoff/landing: repeat only isolated settled takeoff/hold/land while instrumenting internal state, motor output/threshold, six estimator velocities and waiter reason. Keep original strict acceptance. | Compatible instrumented AirSim/UE source project/build and Blocks-equivalent scene; graphics GPU for this retained UE runtime; **source rebuild required** for definitive predicate diagnosis, public angular logging alone insufficient. |
| Requires runtime diagnosis | Moving RGB/depth synchronization and rates: one short bounded motion with both response timestamps/poses, renderer GPU markers/fences, acquisition timing and independent command sampling. | Existing native build/client for timing export; GPU required; renderer-throughput instrumentation may require source rebuild. Original missing timestamps cannot be repaired. |
| Substantial renderer change | Higher SH: preserve/upload coefficients and evaluate view-dependent color, validate with two matched view directions against canonical same-PLY renderer. | PLY has nonzero coefficients; importer/data-interface/Niagara shader change or different faithful renderer; GPU and plugin/shader rebuild, no retraining needed. |
| Missing research input | Novel-view R4R: approved calibrated outdoor images/poses/intrinsics, metric scale, train/held-out split including15 m and50 m views, exposure/masks, independent collision reference; assess depth, coverage, moving objects separately. | AirLab data/permission and existing reconstruction first; GPU for later render/evaluation; no present data permits this conclusion. Training is outside this collection task. |
| Missing research input | Splat depth/collisions and closed-loop adapter: first verify depth on known plane/occluder and collision against independent mesh; then timestamped observation replacement. | Known geometry/calibration + selected compatible dynamics/control layer; GPU for rendering, adapter engineering, likely plugin/stack changes. Visual PLY alone insufficient. |
| Missing research input | C/indoor/racing task result: identify released compatible checkpoint plus preprocessing/action/task definitions before evaluation. | Policy weights/licenses and suitable scene/task; GPU requirement follows identified artifacts, currently unknown; no substitute training. |

Missing forever from these historical runs: original depth response timestamps/poses, discarded `.join()` booleans, failing internal predicate inputs, exact effective S exposure/capture instant and GPU-synchronized rendering times. Missing but obtainable later: same-PLY calibrated reference, approved outdoor data/held-out split and validated depth/collision/policy interfaces. Source, raw acquisition and derived review evidence have separate confidence levels: **documented**, **statically checked**, **locally reverified**, **historically GPU-executed**; conditional hypotheses are labeled and no new runtime measurement is claimed.

## Reviewer navigation / CPU reproduction

Read per-run `commands.log`→copied `audit.py`/`focused_validation.py`/`control-script.py`→`run.json`→`actions/state/camera/descent`→PNG/NPY. Use pinned source conditions above and [sources.md](sources.md). Human supervision requires understanding packaged UE4 versus editable UE5, source-associated binary limits, NED/camera quaternion conventions, PLY basis/metric scale and SH/opacity/color decoding, SceneCapture postprocess/tick timing, async future return values, and source-manifest preservation. Current Git scripts alone do not reconstruct prior failures.

Only CPU review commands (Pillow/NumPy environment already available); output outside RAW:

```bash
PY=/Users/srreyanshsethi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
ROOT=/Users/srreyanshsethi/Downloads/AL/R4R-Sims
AUDIT=/Users/srreyanshsethi/Downloads/AL/R4R-Sims-unreal-audit
OUT="$AUDIT/results/unreal/evidence-review-$(date -u +%Y%m%dT%H%M%SZ)"
"$PY" "$AUDIT/simulators/unreal/verify_preserved.py" --root "$ROOT" --records "$AUDIT" --output "$OUT"
"$PY" "$AUDIT/simulators/unreal/review_preserved.py" --root "$ROOT" --output "$OUT"
```

The report's fresh verification and derived files are in `results/unreal/evidence-review-20261008/`. Prior summaries/decks and raw evidence remain intact. Scientific completion is pending; local preservation is verified.
