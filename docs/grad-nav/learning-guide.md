# Human supervision guide

Read `utils/gs_local.py` first: distinguish the Nx10 xyzw active renderer interface from the alternate matrix path, understand hardcoded K/mount/origin offsets and one-camera loop. Check `render.py` for the audit's direct-versus-author adapter, config relocation and explicit numerical poses. Current tests establish algebra, not rendered calibration.

Read `envs/assets/quadrotor_dynamics_advanced.py` and `probe.py`: wxyz, total normalized thrust, world Z-up gravity,200Hz inner integration and20Hz feedback. Understand kp2/kd0.8 height PD, -0.25m perturbation, force balance versus recovery, overshoot and diagnostic error bands. These component results do not calibrate a real drone.

Read `envs/drone_long_traj.py` observation/action/termination sections and `utils/point_cloud_util.py`: privileged and actor fields differ, observations detach visual features, native actions add clamp/delay/filter, FOV point distance omits unseen/unsampled geometry, and the body-rate termination currently reads quaternion fields.

Read `models/squeeze_net.py`, `models/vae.py`, `models/actor.py`, `algorithms/gradnav.py` and `examples/train_gradnav.py`: six-object checkpoint coverage and explicit --play are essential. Learned visual projection/history/normalizer must match the model/config/map. A Gaussian checkpoint is scene data. Short-horizon differentiable training and online inference are distinct.

For Real4Real, learn calibrated capture poses, distortion, data normalization and physical scale; verify split exclusion across reconstruction/fitting. Depth ED and background replacement need independent geometric checks. Hold-out images, altitude coverage and a downstream task determine fidelity/usefulness, not a demonstration video. Inspect repair-history.json before supervising any future host compiler repair.
