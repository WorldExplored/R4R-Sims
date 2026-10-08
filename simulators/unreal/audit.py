#!/usr/bin/env python3
"""Packaged Linux Blocks camera and scripted-flight evidence runner."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import signal
import socket
import statistics
import subprocess
import sys
import threading
import time
import traceback
import uuid
from datetime import datetime, timezone

AIRSIM_COMMIT = "96235148a332fe7cb3d3525a0720e26faaca99e0"
ASSET_URL = "https://github.com/microsoft/AirSim/releases/download/v1.8.1/Blocks.zip"
ASSET_BYTES = 142533463
ASSET_SHA256 = "563e1da1b5d7303b9405c8736243ea92ab0a011b96a561f26f17563d105a404f"
SETTINGS = {
    "SettingsVersion": 1.2,
    "SimMode": "Multirotor",
    "PhysicsEngineName": "FastPhysicsEngine",
    "ApiServerPort": 41451,
    "Vehicles": {"Drone1": {"VehicleType": "SimpleFlight", "AutoCreate": True}},
    "CameraDefaults": {"CaptureSettings": [
        {"ImageType": 0, "Width": 640, "Height": 480, "FOV_Degrees": 90,
         "AutoExposureSpeed": 100, "MotionBlurAmount": 0},
        {"ImageType": 1, "Width": 640, "Height": 480, "FOV_Degrees": 90}
    ]}
}


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, obj):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, path)


def record(path, obj):
    with open(path, "a", encoding="utf-8", buffering=1) as f:
        f.write(json.dumps(obj, sort_keys=True) + "\n")


def cmd_output(args):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=10, check=False)
        return {"command": args, "exit_code": p.returncode,
                "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"command": args, "error": str(e)}


def png_ok(path):
    with open(path, "rb") as f:
        data = f.read(24)
    return data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) == 24


def port_free():
    with socket.socket() as sock:
        return sock.connect_ex(("127.0.0.1", 41451)) != 0


def preflight(args):
    z = args.asset_zip.resolve()
    exe = args.exe.resolve()
    checks = {
        "time_utc": utc(), "os": platform.platform(), "python": sys.version,
        "asset_zip": str(z), "asset_url": ASSET_URL,
        "asset_exists": z.is_file(), "expected_compressed_bytes": ASSET_BYTES,
        "exe": str(exe), "exe_exists": exe.is_file(),
        "port_41451_free": port_free(),
        "disk_free_bytes": shutil.disk_usage(args.root).free,
        "gpu": cmd_output(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"]),
        "vulkan": cmd_output(["vulkaninfo", "--summary"]),
    }
    if z.is_file():
        checks["asset_bytes"] = z.stat().st_size
        checks["asset_sha256"] = sha256(z)
    if exe.is_file():
        checks["exe_sha256"] = sha256(exe)
    print(json.dumps(checks, indent=2))
    return 0 if (checks["asset_exists"] and checks.get("asset_bytes") == ASSET_BYTES
                 and checks.get("asset_sha256") == ASSET_SHA256
                 and checks["exe_exists"] and checks["port_41451_free"]
                 and checks["disk_free_bytes"] >= 3_000_000_000
                 and checks["gpu"].get("exit_code") == 0
                 and checks["vulkan"].get("exit_code") == 0) else 2


def vec(v):
    return {"x": float(v.x_val), "y": float(v.y_val), "z": float(v.z_val)}


def quat(q):
    return {"w": float(q.w_val), "x": float(q.x_val),
            "y": float(q.y_val), "z": float(q.z_val)}


def pose(p):
    return {"position_ned_m": vec(p.position), "orientation_xyzw_ned": quat(p.orientation)}


def pump(stream, path, prefix):
    with open(path, "a", encoding="utf-8", errors="replace", buffering=1) as out:
        for line in iter(stream.readline, ""):
            out.write(utc() + " " + prefix + " " + line)


def gpu_samples(stop, path):
    while not stop.wait(1.0):
        r = cmd_output(["nvidia-smi", "--query-gpu=timestamp,name,memory.used,memory.total,utilization.gpu,driver_version", "--format=csv,noheader,nounits"])
        record(path, {"wall_utc": utc(), **r})


def capture(client, run_dir, index, kind, t0, first_stamp):
    import airsim
    import numpy as np
    begin = time.perf_counter()
    responses = client.simGetImages([
        airsim.ImageRequest("front_center", airsim.ImageType.Scene, False, True),
        airsim.ImageRequest("front_center", airsim.ImageType.DepthPlanar, True, False),
    ], vehicle_name="Drone1")
    latency = time.perf_counter() - begin
    if len(responses) != 2:
        raise RuntimeError("Expected two image responses")
    rgb, depth = responses
    if rgb.width != 640 or rgb.height != 480 or not rgb.image_data_uint8:
        raise RuntimeError("Missing or wrong-sized RGB image")
    if depth.width != 640 or depth.height != 480 or len(depth.image_data_float) != 640 * 480:
        raise RuntimeError("Missing or wrong-sized depth image")
    rgb_path = run_dir / "frames" / ("%04d.png" % index)
    rgb_tmp = rgb_path.with_suffix(".png.tmp")
    rgb_tmp.write_bytes(bytes(rgb.image_data_uint8))
    os.replace(rgb_tmp, rgb_path)
    if not png_ok(rgb_path):
        raise RuntimeError("RGB PNG signature invalid")
    depth_path = run_dir / "depth" / ("%04d.npy" % index)
    depth_tmp = depth_path.with_suffix(".npy.tmp")
    with open(depth_tmp, "wb") as out:
        np.save(out, np.asarray(depth.image_data_float, dtype=np.float32).reshape(480, 640))
    os.replace(depth_tmp, depth_path)
    info = client.simGetCameraInfo("front_center", "Drone1")
    fov = float(info.fov)
    fx = 640 / (2 * math.tan(math.radians(fov) / 2))
    stamp = int(rgb.time_stamp)
    record(run_dir / "camera.jsonl", {
        "index": index, "kind": kind, "wall_utc": utc(), "wall_elapsed_s": time.perf_counter() - t0,
        "image_timestamp_raw": stamp, "sim_elapsed_s_from_first_image":
        (stamp - first_stamp) / 1e9 if first_stamp is not None else 0.0,
        "camera_pose_response_ned": {"position_ned_m": vec(rgb.camera_position),
                                      "orientation_xyzw_ned": quat(rgb.camera_orientation)},
        "camera_info_pose_ned": pose(info.pose),
        "intrinsics": {"width": 640, "height": 480, "hfov_deg": fov,
                       "fx_px": fx, "fy_px_assuming_square_pixels": fx, "cx_px": 320, "cy_px": 240},
        "rgb": str(rgb_path.resolve()), "depth": str(depth_path.resolve()),
        "capture_rpc_wall_s": latency, "rgb_sha256": sha256(rgb_path), "depth_sha256": sha256(depth_path),
    })
    return stamp


def state_sample(client, run_dir, index, t0, first_state_stamp):
    s = client.getMultirotorState("Drone1")
    gt = client.simGetGroundTruthKinematics("Drone1")
    vp = client.simGetVehiclePose("Drone1")
    collision = client.simGetCollisionInfo("Drone1")
    stamp = int(s.timestamp)
    record(run_dir / "state.jsonl", {
        "index": index, "wall_utc": utc(), "wall_elapsed_s": time.perf_counter() - t0,
        "state_timestamp_raw": stamp, "sim_elapsed_s_from_first_state":
        (stamp - first_state_stamp) / 1e9 if first_state_stamp is not None else 0.0,
        "estimated_position_ned_m": vec(s.kinematics_estimated.position),
        "estimated_velocity_ned_mps": vec(s.kinematics_estimated.linear_velocity),
        "ground_truth_position_ned_m": vec(gt.position), "ground_truth_velocity_ned_mps": vec(gt.linear_velocity),
        "ground_truth_orientation_xyzw_ned": quat(gt.orientation),
        "vehicle_pose_ned": pose(vp), "collision": bool(collision.has_collided),
        "collision_timestamp_raw": int(collision.time_stamp),
        "collision_object": str(collision.object_name), "landed_state": int(s.landed_state)
    })
    record(run_dir / "vehicle_trajectory.jsonl", {
        "index": index, "wall_utc": utc(), "wall_elapsed_s": time.perf_counter() - t0,
        "state_timestamp_raw": stamp, "actual_vehicle_pose_ned": pose(vp),
        "ground_truth_position_ned_m": vec(gt.position)
    })
    return s, collision, stamp


def main_run(args):
    import airsim
    import numpy as np
    if preflight(args) != 0:
        raise RuntimeError("Preflight failed")
    run_id = args.run_id or datetime.now(timezone.utc).strftime("ue-%Y%m%dT%H%M%SZ") + "-" + args.mode + "-" + uuid.uuid4().hex[:8]
    run_dir = (args.root / "artifacts" / "unreal" / run_id).resolve()
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "frames").mkdir()
    (run_dir / "depth").mkdir()
    (run_dir / "assets").mkdir()
    shutil.copy2(Path(__file__), run_dir / "audit.py")
    lock = args.root / "dependency-lock.txt"
    if lock.is_file():
        shutil.copy2(lock, run_dir / "dependency-lock.txt")
    write_json(run_dir / "assets" / "Blocks.json", {"url": ASSET_URL, "sha256": ASSET_SHA256, "bytes": ASSET_BYTES, "remote_path": str(args.asset_zip.resolve()), "preservation": "verified retrievable release URL and SHA-256; archive retained on instance"})
    settings = json.loads(json.dumps(SETTINGS))
    if args.mode == "a":
        settings["SimMode"] = "ComputerVision"
        settings.pop("PhysicsEngineName")
        settings["Vehicles"]["Drone1"]["VehicleType"] = "ComputerVision"
    settings_path = run_dir / "settings.json"
    write_json(settings_path, settings)
    metadata = {
        "run_id": run_id, "mode": args.mode, "experiment_level": args.mode.upper(),
        "status": "starting", "started_utc": utc(), "repo": "microsoft/AirSim",
        "repo_commit": AIRSIM_COMMIT,
        "repo_modifications": "none applied by audit; packaged binary not source-diffed",
        "audit_repo_commit": cmd_output(["git", "-C", str(args.root), "rev-parse", "HEAD"]),
        "audit_repo_worktree": cmd_output(["git", "-C", str(args.root), "status", "--porcelain"]),
        "scene": "v1.8.1 Linux Blocks/FlyingExampleMap; packaged scene assets",
        "scene_split": "stock release; no train/test split", "policy_weights": "none",
        "controller": "none (A)" if args.mode == "a" else "outer bounded proportional velocity script plus SimpleFlight inner controller",
        "input_asset_url": ASSET_URL, "input_asset_zip": str(args.asset_zip.resolve()),
        "input_asset_sha256": sha256(args.asset_zip), "input_asset_bytes": args.asset_zip.stat().st_size,
        "game_exe": str(args.exe.resolve()), "game_exe_sha256": sha256(args.exe),
        "runner_sha256": sha256(run_dir / "audit.py"),
        "dependency_lock_sha256": sha256(run_dir / "dependency-lock.txt") if (run_dir / "dependency-lock.txt").is_file() else None,
        "settings": str(settings_path), "settings_sha256": sha256(settings_path),
        "output_dir": str(run_dir), "seed": None, "randomness": "no scripted randomness; engine seed not exposed",
        "max_wall_s": args.max_wall_s, "rpc_timeout_s": 5, "connection_timeout_s": 60,
        "os": platform.platform(), "python": sys.version, "airsim_version": airsim.__version__,
        "numpy_version": np.__version__, "gpu_preflight": cmd_output(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"]),
        "camera": "front_center, 640x480, 90 deg HFOV; NED metres; camera response extrinsic recorded per frame",
        "sampling": "B target 5 Hz state/actions, up to 2 Hz RGB/depth; A 8 poses; 1 Hz GPU; first 3 frames warmup discarded",
        "timing": "capture RPC wall latency only; no synchronized GPU render timing, policy latency, or video FPS",
        "exit_status": None, "errors": []
    }
    write_json(run_dir / "run.json", metadata)
    commands = run_dir / "commands.log"
    console = run_dir / "console.log"
    record(commands, {"wall_utc": utc(), "argv": sys.argv, "command": "audit.py run", "status": "start"})
    game_home = Path("/tmp/r4r-ue-home")
    game_settings = game_home / "Documents" / "AirSim" / "settings.json"
    game_settings.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(settings_path, game_settings)
    import pwd
    nobody = pwd.getpwnam("nobody")
    for owned in (game_home, game_home / "Documents", game_settings.parent, game_settings):
        os.chown(owned, nobody.pw_uid, nobody.pw_gid)
    exe_cmd = [str(args.exe.resolve()), "Blocks", "-RenderOffscreen", "-vulkan",
               "-windowed", "-ResX=640", "-ResY=480", "-nosound", "-log"]
    game_env = os.environ.copy()
    game_env.update({"HOME": str(game_home), "XDG_RUNTIME_DIR": str(game_home)})
    record(commands, {"wall_utc": utc(), "argv": exe_cmd, "command": "Unreal packaged executable", "status": "start"})
    game = None
    stop = threading.Event()
    client = None
    t0 = time.perf_counter()
    deadline = t0 + args.max_wall_s
    exit_code = 1
    try:
        with open(console, "a", encoding="utf-8", buffering=1) as log:
            log.write(utc() + " run start " + run_id + "\n")
        game = subprocess.Popen(exe_cmd, cwd=str(args.exe.resolve().parents[3]),
                                env=game_env, user=nobody.pw_uid, group=nobody.pw_gid,
                                start_new_session=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, errors="replace")
        write_json(run_dir / "owned-process.json", {"pid": game.pid, "argv": exe_cmd})
        threading.Thread(target=pump, args=(game.stdout, console, "UE"), daemon=True).start()
        threading.Thread(target=gpu_samples, args=(stop, run_dir / "gpu.jsonl"), daemon=True).start()
        while time.perf_counter() < min(deadline, t0 + 60):
            if game.poll() is not None:
                raise RuntimeError("Packaged game exited before RPC connection: " + str(game.returncode))
            if not port_free():
                break
            time.sleep(0.25)
        else:
            raise TimeoutError("AirSim RPC socket did not open in 60 s")
        client = airsim.MultirotorClient(timeout_value=5)
        if not client.ping():
            raise RuntimeError("AirSim RPC ping failed after socket opened")
        metadata["server_version"] = client.getServerVersion()
        metadata["status"] = "running"
        write_json(run_dir / "run.json", metadata)
        first_stamp = None
        for i in range(3):
            warm = client.simGetImage("front_center", airsim.ImageType.Scene, "Drone1")
            record(run_dir / "warmup.jsonl", {"index": i, "wall_utc": utc(), "received": bool(warm)})
        if args.mode == "a":
            # NED metre offsets relative to the stock scene start; fixed yaw and short bounded path.
            route = [(0, 0, -2), (0.5, 0, -2), (1, 0, -2), (1, 0.5, -2),
                     (1, 1, -2), (0.5, 1, -2), (0, 1, -2), (0, 0, -2)]
            write_json(run_dir / "reference_route.json", {"frame": "AirSim NED metres, relative to start", "poses_xyz": route})
            for i, xyz in enumerate(route):
                if time.perf_counter() >= deadline:
                    raise TimeoutError("run wall timeout")
                target = airsim.Pose(airsim.Vector3r(*xyz), airsim.Quaternionr(0, 0, 0, 1))
                record(run_dir / "actions.jsonl", {"index": i, "wall_utc": utc(), "type": "simSetVehiclePose", "target_ned_m": xyz, "ignore_collision": True})
                client.simSetVehiclePose(target, True, "Drone1")
                time.sleep(0.25)
                actual = client.simGetVehiclePose("Drone1")
                record(run_dir / "vehicle_trajectory.jsonl", {"index": i, "wall_utc": utc(), "actual_vehicle_pose_ned": pose(actual)})
                gt = client.simGetGroundTruthKinematics("Drone1")
                record(run_dir / "state.jsonl", {"index": i, "wall_utc": utc(),
                                                 "wall_elapsed_s": time.perf_counter() - t0,
                                                 "ground_truth_position_ned_m": vec(gt.position),
                                                 "vehicle_pose_ned": pose(actual)})
                stamp = capture(client, run_dir, i, "A", t0, first_stamp)
                if first_stamp is None:
                    first_stamp = stamp
        else:
            baseline = client.simGetCollisionInfo("Drone1")
            write_json(run_dir / "collision_baseline.json", {
                "wall_utc": utc(), "has_collided": bool(baseline.has_collided),
                "time_stamp_raw": int(baseline.time_stamp),
                "object_name": str(baseline.object_name)})
            first_stamp = capture(client, run_dir, 0, "B_pre_takeoff", t0, first_stamp)
            client.enableApiControl(True, "Drone1")
            if not client.armDisarm(True, "Drone1"):
                raise RuntimeError("SimpleFlight arm failed")
            record(run_dir / "actions.jsonl", {"wall_utc": utc(), "type": "takeoffAsync", "timeout_s": 15})
            client.takeoffAsync(timeout_sec=15, vehicle_name="Drone1").join()
            start = client.simGetVehiclePose("Drone1").position
            route = [(float(start.x_val + dx), float(start.y_val + dy), -2.0)
                     for dx, dy in [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]]
            write_json(run_dir / "reference_route.json", {"frame": "AirSim NED metres", "waypoints_xyz": route,
                                                        "controller_hz_target": 5, "speed_limit_mps": 0.7})
            index = 1
            last_capture = time.perf_counter()
            first_state_stamp = None
            for waypoint in route:
                wp_start = time.perf_counter()
                while time.perf_counter() < min(deadline, wp_start + 15):
                    s, collision, state_stamp = state_sample(client, run_dir, index, t0, first_state_stamp)
                    if first_state_stamp is None:
                        first_state_stamp = state_stamp
                    if collision.has_collided and int(collision.time_stamp) > int(baseline.time_stamp):
                        raise RuntimeError("New collision after baseline; stopped")
                    p = s.kinematics_estimated.position
                    error = [waypoint[0] - p.x_val, waypoint[1] - p.y_val, waypoint[2] - p.z_val]
                    if math.sqrt(sum(e * e for e in error)) < 0.25:
                        break
                    velocity = [max(-0.7, min(0.7, 0.7 * e)) for e in error]
                    record(run_dir / "actions.jsonl", {"index": index, "wall_utc": utc(), "type": "moveByVelocityAsync",
                                                       "wall_elapsed_s": time.perf_counter() - t0,
                                                       "velocity_ned_mps": velocity, "duration_s": 0.2,
                                                       "target_ned_m": waypoint, "error_ned_m": error})
                    client.moveByVelocityAsync(*velocity, duration=0.2, vehicle_name="Drone1").join()
                    if time.perf_counter() - last_capture >= 2.0:
                        stamp = capture(client, run_dir, index, "B", t0, first_stamp)
                        if first_stamp is None:
                            first_stamp = stamp
                        last_capture = time.perf_counter()
                    index += 1
                else:
                    raise TimeoutError("Waypoint or run timeout at " + str(waypoint))
                record(run_dir / "actions.jsonl", {"wall_utc": utc(), "type": "waypoint_reached",
                                                   "target_ned_m": waypoint, "error_norm_m": math.sqrt(sum(e * e for e in error)),
                                                   "wall_elapsed_s": time.perf_counter() - t0})
            record(run_dir / "actions.jsonl", {"wall_utc": utc(), "type": "landAsync", "timeout_s": 20})
            client.landAsync(timeout_sec=20, vehicle_name="Drone1").join()
            state_sample(client, run_dir, index + 1, t0, first_state_stamp)
            capture(client, run_dir, index + 1, "B_post_land", t0, first_stamp)
        if not list((run_dir / "frames").glob("*.png")) or not (run_dir / "state.jsonl").is_file():
            raise RuntimeError("No usable image/state evidence")
        metadata["status"] = "completed"
        exit_code = 0
    except Exception as e:
        metadata["status"] = "failed"
        metadata["errors"].append({"wall_utc": utc(), "error": str(e), "traceback": traceback.format_exc()})
        with open(console, "a", encoding="utf-8", buffering=1) as log:
            log.write(utc() + " ERROR " + traceback.format_exc() + "\n")
    finally:
        if client and args.mode == "b":
            try:
                client.armDisarm(False, "Drone1")
                client.enableApiControl(False, "Drone1")
            except Exception as e:
                metadata["errors"].append({"cleanup_error": str(e)})
        stop.set()
        if game and game.poll() is None:
            os.killpg(game.pid, signal.SIGTERM)  # dedicated group owned by this run
            try:
                game.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(game.pid, signal.SIGKILL)
                game.wait(timeout=5)
        if game:
            record(commands, {"wall_utc": utc(), "command": "Unreal packaged executable", "pid": game.pid, "exit_code": game.returncode})
        metadata["finished_utc"] = utc()
        metadata["wall_elapsed_s"] = time.perf_counter() - t0
        metadata["sample_counts"] = {
            name: sum(1 for _ in open(run_dir / name, encoding="utf-8")) if (run_dir / name).is_file() else 0
            for name in ("actions.jsonl", "state.jsonl", "vehicle_trajectory.jsonl", "camera.jsonl", "gpu.jsonl")
        }
        metadata["missing_data"] = [name for name, count in metadata["sample_counts"].items() if count == 0]
        if (run_dir / "actions.jsonl").is_file():
            times = [item["wall_elapsed_s"] for item in map(json.loads, (run_dir / "actions.jsonl").read_text(encoding="utf-8").splitlines())
                     if item.get("type") == "moveByVelocityAsync" and "wall_elapsed_s" in item]
            intervals = [b - a for a, b in zip(times, times[1:]) if b > a]
            metadata["achieved_outer_command_rate_hz_median"] = 1 / statistics.median(intervals) if intervals else None
        metadata["exit_status"] = exit_code
        metadata["game_exit_status_after_cleanup"] = game.returncode if game else None
        write_json(run_dir / "run.json", metadata)
        record(commands, {"wall_utc": utc(), "command": "audit.py run", "exit_code": exit_code})
        print("RUN_DIR=" + str(run_dir), flush=True)
    return exit_code


def collect(args):
    source = args.run_dir.resolve()
    if not (source / "run.json").is_file():
        raise RuntimeError("Not a run directory")
    dest = args.dest.resolve()
    dest.mkdir(parents=True, exist_ok=False)
    shutil.copytree(source, dest / source.name)
    copied = dest / source.name
    if args.asset_zip:
        if sha256(args.asset_zip) != ASSET_SHA256:
            raise RuntimeError("Asset hash mismatch")
    else:
        raise RuntimeError("Asset zip required for verification")
    hashes = {}
    for path in sorted(copied.rglob("*")):
        if path.is_file():
            hashes[str(path.relative_to(copied))] = sha256(path)
    write_json(dest / "sha256-manifest.json", hashes)
    for relative, digest in hashes.items():
        if sha256(copied / relative) != digest:
            raise RuntimeError("Transfer hash mismatch: " + relative)
    import cv2
    for path in (copied / "frames").glob("*.png"):
        if not png_ok(path) or cv2.imread(str(path)) is None:
            raise RuntimeError("PNG cannot open: " + str(path))
    import numpy as np
    for path in (copied / "depth").glob("*.npy"):
        if np.load(path, allow_pickle=False).shape != (480, 640):
            raise RuntimeError("Depth cannot open: " + str(path))
    for path in copied.glob("*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            json.loads(line)
    print(json.dumps({"snapshot": str(dest), "files_verified": len(hashes), "asset_sha256": ASSET_SHA256}, indent=2))
    return 0


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("preflight", "run"):
        q = sub.add_parser(name)
        q.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
        q.add_argument("--asset-zip", type=Path, required=True)
        q.add_argument("--exe", type=Path, required=True)
        if name == "run":
            q.add_argument("--mode", choices=("a", "b"), required=True)
            q.add_argument("--run-id")
            q.add_argument("--max-wall-s", type=int, default=180)
    q = sub.add_parser("collect")
    q.add_argument("--run-dir", type=Path, required=True)
    q.add_argument("--asset-zip", type=Path, required=True)
    q.add_argument("--dest", type=Path, required=True)
    args = p.parse_args()
    if args.command == "preflight":
        return preflight(args)
    if args.command == "run":
        return main_run(args)
    return collect(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
