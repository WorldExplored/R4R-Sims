# Sources and executable trace

Read 2026-10-08 local date (remote records use UTC October9). Authors' upstream baseline is **d9b00e16107338e49071c65f44582c013e522633**, current inspected is **95218abe9a5d355519cdaab78d915365303066fe**. Both are actual cloned Git objects. No baseline upstream modifications were made. Current adds CUSTOM_SCENE.md and tools/validate_scene.py, absent at baseline, plus planner and environment changes. Their diff is preserved in preflight.

The old recovered sources.md used web-page line numbers, not Python source lines. Use the exact pinned source links below and code-index.json for source-line references.

| File/symbol | Exact source lines |
|---|---|
| utils/gs_local.py `GS` | [L18–131](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/utils/gs_local.py#L18) |
| utils/gs_local.py `get_gs` | [L134–165](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/utils/gs_local.py#L134) |
| utils/gs_local.py `quaternion_to_rotation_matrix` | [L168–200](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/utils/gs_local.py#L168) |
| utils/gs_local.py `pose2nerf_transform` | [L202–247](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/utils/gs_local.py#L202) |
| utils/gs_local.py `render` | [L98–131](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/utils/gs_local.py#L98) |
| envs/assets/quadrotor_dynamics_advanced.py `QuadrotorSimulator` | [L3–182](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/envs/assets/quadrotor_dynamics_advanced.py#L3) |
| envs/assets/quadrotor_dynamics_advanced.py `quaternion_to_rotation_matrix` | [L65–86](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/envs/assets/quadrotor_dynamics_advanced.py#L65) |
| envs/assets/quadrotor_dynamics_advanced.py `update` | [L112–148](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/envs/assets/quadrotor_dynamics_advanced.py#L112) |
| envs/assets/quadrotor_dynamics_advanced.py `run_simulation` | [L150–182](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/envs/assets/quadrotor_dynamics_advanced.py#L150) |
| envs/drone_long_traj.py `step` | [L374–461](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/envs/drone_long_traj.py#L374) |
| envs/drone_long_traj.py `process_GS_data` | [L580–589](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/envs/drone_long_traj.py#L580) |
| envs/drone_long_traj.py `calculateObservations` | [L592–684](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/envs/drone_long_traj.py#L592) |
| envs/drone_long_traj.py `calculateReward` | [L687–794](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/envs/drone_long_traj.py#L687) |
| utils/point_cloud_util.py `filter_points_in_fov` | [L53–75](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/utils/point_cloud_util.py#L53) |
| utils/point_cloud_util.py `compute_nearest_distances` | [L101–117](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/utils/point_cloud_util.py#L101) |
| models/squeeze_net.py `VisualPerceptionNet` | [L6–24](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/models/squeeze_net.py#L6) |
| algorithms/gradnav.py `evaluate_policy` | [L426–482](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/algorithms/gradnav.py#L426) |
| algorithms/gradnav.py `train` | [L517–737](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/algorithms/gradnav.py#L517) |
| algorithms/gradnav.py `play` | [L739–743](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/algorithms/gradnav.py#L739) |
| algorithms/gradnav.py `save` | [L745–748](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/algorithms/gradnav.py#L745) |
| algorithms/gradnav.py `load` | [L750–759](https://github.com/Qianzhong-Chen/grad_nav/blob/d9b00e16107338e49071c65f44582c013e522633/algorithms/gradnav.py#L750) |

## Algorithm and interfaces

`train_gradnav.py` selects `algorithms.gradnav.GradNav`; explicit --play selects load/run rather than train. `GradNav` is a short-horizon differentiable actor-critic method, described by [GRaD-Nav v3](https://arxiv.org/html/2503.03984v3), not online MPC. B and D invoke dynamics directly and use the named adapter PD controller. No actor, critic or VAE is constructed. No optimization or training occurs. Current VLA/MoE GRaD-Nav++ is a separate variant. R2R is unrelated.

`GS` loads Splatfacto through `eval_setup(test_mode='inference')`. `render` accepts Nx10, takes xyz at0:3 and xyzw at6:10, computes camera transform and loops one camera at a time. Its output is a stacked tensor, not a genuinely batched rasterization call. The unused `render_quad_poses` documents Nx3x4 but passes that into the Nx10 renderer and references unset dataparser fields. Use the active env step path instead.

The active environment stores vehicle quaternion xyzw, converts to dynamics wxyz and back. It adds [-6,0,0], flips Y/Z and invokes `pose2nerf_transform` with matrices F, rounded mount M and camera-basis C. The helper comment says wxyz but destructures xyzw. Numerical diagnostics exercise exact AST functions and establish the actual convention. The rounded mount has an orthonormality residual, preserved rather than silently fixed. The active renderer does not apply dataparser transform/scale; apply normalization exactly once for new data and preserve original/applied conventions.

Native observations have57 dimensions in the selected current baseline config: height/Zvelocity/quaternion, two action histories, linear velocity,16 visual features,24 CENet latent values. Privileged obs67 are separate. Native action is tanh-limited4D, then body rate clamp/scale0.5, body delay0.8, thrust delay0.7 and thrust scale0.25. Dynamics integrates ten0.005s substeps per 0.05 s outer tick, with total thrust in N as normalized scalar times max_thrust. The max_thrust doc calls it per-rotor, but code applies it once as total body-Z force. B/D direct adapter bypasses native delay/filter/noise observations, which is logged.

`VisualPerceptionNet` begins from torchvision SqueezeNet, replaces its first convolution and creates a projection FC. Stock backbone weights alone cannot establish the actual learned visual observation. `GradNav.load` expects a six-object serialized list: actor, critic, target critic, observation RMS, VAE and trained visual_net. The author Drive archives contain Gaussian ckpt and some mocap pose tensors, no best_policy.pt/final_policy.pt. No releases are listed by GitHub API. README paths under examples/logs are developer outputs. C and complete learned-observation latency are blocked.

## Collision and import limits

`ObstacleDistanceCalculator` reads XYZ via Open3D and applies a forward angular cone, then nearest-point distance. There is no swept body-volume/contact response. Synthetic diagnostics show a near rear point and a coincident point can return infinity. `calculateReward` adds distance reward only below0.5, while termination uses bounds/height/horizon/finite checks. `condition_body_rate` selects privileged10:13, within quaternion9:13, rather than rates13:16. The unused collision-limit scalar does not establish contact checking.

Current `CUSTOM_SCENE.md` suggests `ns-export pointcloud` after Splatfacto. [Official Splatfacto docs](https://docs.nerf.studio/nerfology/methods/splat.html) instead specify `ns-export gaussian-splat` for Gaussian PLY and state generic pointcloud/mesh export is unsupported. A Gaussian PLY is also not automatically compatible with the repository's config/checkpoint loader or collision geometry. Current validate_scene.py only checks discrete nearest-point clearance; its printed free-space/metric claims exceed what it establishes. No diagnostic backport or training instruction was executed.

## Downloads, dependencies and licenses

The [author-linked Drive folder](https://drive.google.com/drive/folders/1XEoJU3PVTMx782MMfSFNm5D0zTawKrbJ) contains replacement IDs1f-ohG0KLkIVXtiRVqvHmqduWRh4hDVQn for gs_data.zip and1FS0hF7aufFsd6OH0Xcca9fGgbcMGqkOf for point_cloud.zip. The old README IDs return404. Folder metadata identifies December8,2025 modifications. Selected gate_mid config uses no auto-scale, center none, orientation none, train-split fraction0.9 and3D points, but earlier reconstruction/fitting exclusion is not attested. Record scales and views without a verified held-out fidelity claim.

[GRaD-Nav paper](https://arxiv.org/html/2503.03984v3) documents a4090/i9/48GB training/simulation baseline; these are not inference minimums. [Nerfstudio1.1.3](https://github.com/nerfstudio-project/nerfstudio/tree/9b3cbc79bf239eb3c69e7c288632aab02c4f0bb1) pins gsplat1.0.0, unlike the GRaD-Nav README. Actual package freeze and compiler are recorded per run. Rendering initially uses Torch2.1.2/cu118/TV0.16.2, NS1.1.3/gsplat1.0.0, NumPy1.26.4. Dynamics uses isolated Torch2.0.1/cu118/NumPy1.26.3. The CUDA11.8 toolkit from TravelUAV is reused read-only; no system driver or authentication was changed.

Repository LICENSE.md is NVIDIA DiffRL with noncommercial research/evaluation restrictions and notice obligations. Nerfstudio/gsplat licenses are separately recorded by their distributions. The Drive archives do not supply clear scene/policy reuse terms in the inspected listing. Public download is access evidence, not a blanket license. Paper's own publication license does not establish asset redistribution terms. Scientific input copies remain ignored/local.

## Continuation sources (accessed 2026-10-08 local / October9UTC)

- [CUDA11.8 Linux installation guide](https://docs.nvidia.com/cuda/archive/11.8.0/cuda-installation-guide-linux/index.html): supported Linux compiler toolchain and redistribution tarball workflow.
- [CUDA11.8 release archive](https://developer.nvidia.com/cuda-11-8-0-download-archive). Exact borrowed component URLs/hashes preserved in compiler-preflight/borrowed-cuda-components.json. No toolkit or driver installation performed.
- Pinned Nerfstudio `nerfstudio/models/splatfacto.py:749` RGB+ED selection,788–805 RGBbackground/clamp and depthfallback;690–705 inference camera path does not apply training camera optimizer. `nerfstudio/process_data/colmap_utils.py:446` scalar-first COLMAP→OpenGL and worldaxes conversion,475applied_transform provenance. `nerfstudio/data/dataparsers/nerfstudio_dataparser.py:319` distinguishes already saved versus original coordinate metadata. Exact source9b3cbc79bf239eb3c69e7c288632aab02c4f0bb1.
- Local execution: A20261009T020714Z-a-1004f1, D20261009T020926Z-d-748818, scene diagnostic20261009T021154Z-scene-diagnostic-64cb11, compiler20261009T020316Z-compiler-preflight. Logs/configs/source/records in results/grad-nav; raw data locally preserved in artifact index. No source-image fidelity metric.

## Controlled training-camera diagnostic (2026-10-08 local / October9UTC)

- Actual installed NS1.1.3/1.1.4 model, datamanager and camera-optimizer module paths/SHA256 are in correspondence-support/runtime-profiles.txt. Original config and checkpoint remain the author gate_mid archive inputs; no weights or upstream source were edited.
- NS1.1.3 pipeline base_pipeline.py:101–126 separates strict model loading from non-model pipeline state. splatfacto.py:318–331 resizes/restores Gaussian arrays and sets model step30000;254 constructs indexed camera optimizer;699–707 uses corrections only in model training mode. Evaluation diagnostic explicitly calls the saved correction implementation without changing training mode.
- CameraOptimizer.apply_to_camera camera_optimizers.py:153–177 applies world rotation and independent translation using cam_idx. FullImageDatamanager cached_train full_images_datamanager.py:181–262 and next_train:337–355 supply canonical preprocessed source/K and correctly indexed camera. _undistort_image:380–431 gives distortion, half-pixel shift and ROI crop.
- NerfstudioDataparser nerfstudio_dataparser.py:124–131 sorts filenames;210–228 forms fraction split;237–258 applies orientation/center/scale and selects poses. dataparser_utils.get_train_eval_split_fraction uses evenly spaced training indices. The270-row mapping is exact for this released dataset/loader; the original training filename list is not embedded in the checkpoint.
- [NS1.1.4 dependency declaration](https://raw.githubusercontent.com/nerfstudio-project/nerfstudio/v1.1.4/pyproject.toml) pins gsplat1.0.0,viser0.2.3,opencv-python-headless4.10.0.84. Actual installed dependency checks and pixel equivalence are preserved separately; a Git tag alone is not treated as proof of wheel code identity.
