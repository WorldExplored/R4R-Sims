# Project AirSim bounded audit

Pinned native Blocks release: v1.0.1, source commit `09755454b8d82b0231af7e59fd1ab8f980ff32c5`, Blocks Linux SHA256 `4a0c7b6de27ed32bdf4de1c31c222c19b796500108b654382b5d76b4ba000040`, client `projectairsim==1.0.2`. The released source package labels itself 1.0.1 while the release prescribes client 1.0.2; record the server hash and verify observed APIs. Do not infer incompatibility from the labels.

The four configs derive from the pinned upstream `scene_basic_drone.jsonc`, `robot_quadrotor_fastphysics.jsonc`, and `robot_quadrotor_nonphysics.jsonc`. They retain the stock Blocks map and native quadrotor definitions, enable a 400×225 RGB Scene and Depth Planar pair on downward and forward cameras, set capture interval to 0.1 simulator seconds, disable the chase camera, and use manual exposure and zero motion blur for RGB. Actual exposure and projection behavior remain subject to the packaged renderer. No Unreal Editor or plugin build is involved.

## Host sequence

On Ubuntu 22.04 with NVIDIA Vulkan and Python 3.11, from this directory:

```bash
bash setup_linux.sh
bash preflight_linux.sh
bash launch_linux.sh 1
bash run_one.sh pose 20261009T010000Z-pose-1
bash run_one.sh pose 20261009T010500Z-pose-2
bash run_one.sh smoke 20261009T011000Z-smoke-1
# Review RGB, depth and route clearance before measured flights.
bash run_one.sh flight 20261009T012000Z-flight-1
bash run_one.sh flight 20261009T012500Z-flight-2
bash collect_linux.sh <each-run-id>
```

Use fresh UTC IDs; example IDs are placeholders. The simulator launches once and each run reloads a scene. A root-run packaged Unreal process fails; `setup_linux.sh` copies the verified package to a directory owned by the existing unprivileged `nobody` user, and `launch_linux.sh` runs that copy. The source ZIP and isolated venv remain outside Git at `/root/r4r-airsim-deps`. Launches have a 120 second readiness limit and at most three manual attempts. Stop only a recorded audit launch with `stop_linux.sh <attempt>` when finished.

`run_one.sh` caps A at 120 wall seconds and B at 180, preserves exit status through `tee`, records source/config hashes, host details and 1 Hz sampled GPU data, and writes raw frames under ignored `artifacts/project-airsim/<id>`. Small results go under `results/project-airsim/<id>`. Its Python client sets a 10 second ordinary request timeout. Flight tasks cap at 30 seconds. The runner does not retry failures. Any diagnosed repair must use a new run ID and be described in results.

A uses the upstream non-physics mode and direct `set_pose` with a five-pose route. Each pose gets achieved vehicle pose and direct native camera pose from image message fields `pos_x/y/z` and `rot_w/x/y/z`, plus next-capture timestamps for RGB and planar depth. Its freshness check requires increasing per-camera timestamps; it does not claim clock synchronization across cameras. The camera-info topic carries the native intrinsic matrix.

B uses Simple Flight + Fast Physics. The smoke moves 1 m after takeoff. A measured flight moves 2.5 m horizontally, 1 m upward in NED, rotates to -15° world yaw, hovers, returns and lands. The two measured attempts use the same config and route definition; absolute vertical waypoints depend on achieved takeoff altitude, recorded before execution. RGB/depth are observed; the waypoint controller does not consume the images.

The audit does not train a scene or policy. C is an availability/compatibility search and has no inference run. Native Blocks cannot measure reconstruction quality on held-out real imagery.
