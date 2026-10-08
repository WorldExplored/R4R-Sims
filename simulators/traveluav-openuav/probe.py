#!/usr/bin/env python3
"""Bounded AirSim camera and path probe. Requires the released Linux scene."""
import argparse
import json
import math
import time
from pathlib import Path

import airsim
import numpy as np
from PIL import Image

CAMERAS = ("FrontCamera", "LeftCamera", "RightCamera", "RearCamera", "DownCamera")


def values(v):
    return [float(v.x_val), float(v.y_val), float(v.z_val)]


def quat(q):
    return [float(q.x_val), float(q.y_val), float(q.z_val), float(q.w_val)]


def write_jsonl(path, item):
    with path.open("a", encoding="utf-8") as out:
        out.write(json.dumps(item, sort_keys=True) + "\n")


def record(client, out, frames, index, mode, command, wall_start):
    state = client.getMultirotorState()
    imu = client.getImuData()
    collision = client.simGetCollisionInfo()
    ground_truth = client.simGetGroundTruthKinematics()
    pose = state.kinematics_estimated
    record = {
        "index": index, "mode": mode, "wall_s": time.monotonic() - wall_start,
        "sim_timestamp_ns": int(state.timestamp),
        "position_ned_m": values(ground_truth.position), "estimated_position_ned_m": values(pose.position),
        "orientation_xyzw": quat(pose.orientation),
        "linear_velocity_ned_mps": values(pose.linear_velocity),
        "angular_velocity_radps": values(pose.angular_velocity),
        "collision": bool(collision.has_collided), "contact_object": collision.object_name, "contact_timestamp_ns": int(collision.time_stamp), "command": command,
        "imu_timestamp_ns": int(imu.time_stamp), "imu_orientation_xyzw": quat(imu.orientation),
        "imu_angular_velocity_radps": values(imu.angular_velocity),
        "imu_linear_acceleration_mps2": values(imu.linear_acceleration),
    }
    write_jsonl(out / "actual_vehicle.jsonl", record)
    requests = []
    for name in CAMERAS:
        requests += [airsim.ImageRequest(name, airsim.ImageType.Scene, False, False),
                     airsim.ImageRequest(name, airsim.ImageType.DepthPerspective, True, False)]
    start = time.perf_counter()
    responses = client.simGetImages(requests)
    render_rpc_s = time.perf_counter() - start
    if len(responses) != len(requests):
        raise RuntimeError(f"received {len(responses)} of {len(requests)} camera responses")
    for cam_index, name in enumerate(CAMERAS):
        rgb, depth = responses[2 * cam_index:2 * cam_index + 2]
        if rgb.width <= 0 or rgb.height <= 0 or depth.width <= 0 or depth.height <= 0:
            raise RuntimeError(f"empty image for {name}")
        pixels = np.frombuffer(rgb.image_data_uint8, dtype=np.uint8).reshape(rgb.height, rgb.width, 3)
        depth_pixels = np.asarray(depth.image_data_float, dtype=np.float32).reshape(depth.height, depth.width)
        frame_dir = frames / name
        frame_dir.mkdir(parents=True, exist_ok=True)
        rgb_file = frame_dir / f"{index:04d}.png"
        depth_file = frame_dir / f"{index:04d}_depth_m.npy"
        Image.fromarray(pixels).save(rgb_file)
        np.save(depth_file, depth_pixels)
        info = client.simGetCameraInfo(name)
        write_jsonl(out / "actual_camera.jsonl", {
            "index": index, "camera": name, "wall_s": time.monotonic() - wall_start,
            "image_timestamp_ns": int(rgb.time_stamp), "depth_timestamp_ns": int(depth.time_stamp),
            "position_ned_m": values(rgb.camera_position), "orientation_xyzw": quat(rgb.camera_orientation),
            "fov_deg": float(info.fov), "width": int(rgb.width), "height": int(rgb.height),
            "rgb_path": str(rgb_file), "depth_path": str(depth_file),
            "render_rpc_s": render_rpc_s, "warmup": index == 0,
            "intrinsics_pinhole": {"fx": rgb.width/(2*math.tan(math.radians(info.fov)/2)),
                                   "fy": rgb.width/(2*math.tan(math.radians(info.fov)/2)),
                                   "cx": rgb.width/2, "cy": rgb.height/2,
                                   "source": "derived from horizontal FOV, square pixels; validate projection"},
            "projection_matrix": info.proj_mat.matrix,
            "camera_rgb_depth_timestamp_spread_ns": max(r.time_stamp for r in responses)-min(r.time_stamp for r in responses), "depth_unit": "meters", "frame": "AirSim NED",
        })
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("a", "b"))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--frames-dir", required=True, type=Path)
    parser.add_argument("--episode", required=True, type=Path)
    parser.add_argument("--port", type=int, default=41451)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    episode = json.loads(args.episode.read_text())
    route = episode["trajectory_raw_detailed"]
    if len(route) < 6:
        raise ValueError("reference route needs at least six states")
    # Keep one short, reproducible segment. Reference poses and achieved states stay separate.
    route = route[:6]
    for i, item in enumerate(route):
        write_jsonl(out / "reference_route.jsonl", {"index": i, "pose": item})
    client = airsim.MultirotorClient(ip="127.0.0.1", port=args.port, timeout_value=10)
    client.confirmConnection()
    wall_start = time.monotonic()
    initial = route[0]
    state = airsim.KinematicsState()
    state.position = airsim.Vector3r(*initial["position"])
    state.orientation = airsim.Quaternionr(*initial["orientation"])
    client.simSetKinematics(state, ignore_collision=True)
    write_jsonl(out/"events.jsonl", {"event":"initial_reset", "wall_s":time.monotonic()-wall_start,"target":initial})
    if args.mode == "a":
        for i, target in enumerate(route):
            state.position = airsim.Vector3r(*target["position"])
            state.orientation = airsim.Quaternionr(*target["orientation"])
            write_jsonl(out/"events.jsonl", {"event":"pose_reset", "index":i, "wall_s":time.monotonic()-wall_start,"target":target})
            client.simSetKinematics(state, ignore_collision=True)
            client.simContinueForFrames(1)
            client.simPause(True)
            write_jsonl(out / "actions.jsonl", {"index": i, "type": "set_kinematics", "target": target})
            record(client, out, args.frames_dir, i, "a", "set_kinematics", wall_start)
    else:
        client.enableApiControl(True)
        client.armDisarm(True)
        client.simPause(False)
        path = [airsim.Vector3r(*item["position"]) for item in route[1:]]
        write_jsonl(out / "actions.jsonl", {"index": 0, "type": "moveOnPathAsync", "velocity_mps": 1,
                                              "waypoints_ned_m": [item["position"] for item in route[1:]]})
        future = client.moveOnPathAsync(path, velocity=1, drivetrain=airsim.DrivetrainType.ForwardOnly,
                                        yaw_mode=airsim.YawMode(is_rate=False), lookahead=3, adaptive_lookahead=1)
        try:
            for i in range(31):
                current = record(client, out, args.frames_dir, i, "b", "moveOnPathAsync", wall_start)
                if math.dist(current["position_ned_m"], route[-1]["position"]) < 2:
                    break
                time.sleep(0.2)
        finally:
            client.simPause(True)
        write_jsonl(out/"events.jsonl", {"event":"pause", "wall_s":time.monotonic()-wall_start})
        # The pinned msgpack Future completes while subsequent RPC calls pump its loop.
        # Inspect its flag without an unbounded join or a second loop-driving thread.
        future_completed = bool(future._set_flag)
        write_jsonl(out/"events.jsonl", {"event":"async_status", "completed":future_completed,
            "result":future.result if future_completed else None,
            "error":str(future.error) if future.error else None})
    ending = {"reason": "pose_replay_complete" if args.mode == "a" else ("endpoint_within_2m" if math.dist(current["position_ned_m"],route[-1]["position"]) < 2 else "sample_budget"),
              "samples": i+1, "wall_s": time.monotonic()-wall_start,
              "async_completion_observed": future_completed if args.mode == "b" else None}
    (out/"termination.json").write_text(json.dumps(ending,indent=2)+"\n")
    print(json.dumps({"mode": args.mode, "samples": i + 1, "output": str(out)}))


if __name__ == "__main__":
    main()
