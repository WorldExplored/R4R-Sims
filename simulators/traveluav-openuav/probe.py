#!/usr/bin/env python3
"""Bounded AirSim camera and path probe. Requires the released Linux scene."""
import argparse
import json
import math
import time
import threading
import signal
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


def record_state(client, out, index, mode, command, wall_start):
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
    return record


def record_images(client, out, frames, index, wall_start):
    requests = []
    for name in CAMERAS:
        requests += [airsim.ImageRequest(name, airsim.ImageType.Scene, False, False),
                     airsim.ImageRequest(name, airsim.ImageType.DepthPerspective, True, False)]
    # Capture the active socket's bytes: Tornado bound on_read when connecting.
    client.ping()
    chunks=[]
    socket=client.client._transport._sockets[0]
    original=socket._unpacker
    class ObservedUnpacker:
        def feed(self,data):
            chunks.append(data)
            return original.feed(data)
        def __iter__(self):return iter(original)
    socket._unpacker=ObservedUnpacker()
    start=time.perf_counter()
    try:
        responses=client.simGetImages(requests)
    finally:
        render_rpc_s=time.perf_counter()-start
        socket._unpacker=original
    if chunks:(frames.parent/f"image_rpc_payload_{index:04d}.msgpack").write_bytes(b"".join(chunks))
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
            "depth_position_ned_m": values(depth.camera_position), "depth_orientation_xyzw": quat(depth.camera_orientation),
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
    if args.mode == "a": client.simPause(True)
    client.simSetKinematics(state, ignore_collision=True)
    write_jsonl(out/"events.jsonl", {"event":"initial_reset", "wall_s":time.monotonic()-wall_start,"target":initial})
    if args.mode == "a":
        for i, target in enumerate(route):
            state.position = airsim.Vector3r(*target["position"])
            state.orientation = airsim.Quaternionr(*target["orientation"])
            write_jsonl(out/"events.jsonl", {"event":"pose_reset", "index":i, "wall_s":time.monotonic()-wall_start,"target":target})
            client.simSetKinematics(state, ignore_collision=True)
            client.simContinueForFrames(1)
            deadline=time.monotonic()+2
            while not client.simIsPause() and time.monotonic()<deadline:
                time.sleep(0.01)
            client.simPause(True)
            # Reapply reference kinematics while paused, after the startup physics tick.
            client.simSetKinematics(state, ignore_collision=True)
            write_jsonl(out / "actions.jsonl", {"index": i, "type": "set_kinematics", "target": target})
            record_state(client, out, i, "a", "set_kinematics", wall_start)
            record_images(client, out, args.frames_dir, i, wall_start)
    else:
        client.enableApiControl(True)
        client.armDisarm(True)
        client.simPause(False)
        path = [airsim.Vector3r(*item["position"]) for item in route[1:]]
        write_jsonl(out / "actions.jsonl", {"index": 0, "type": "moveOnPathAsync", "velocity_mps": 1,
                                              "waypoints_ned_m": [item["position"] for item in route[1:]]})
        done = threading.Event()
        sampling_stop = threading.Event()
        outcome = {"completed": False, "result": None, "error": None}
        counts = {"states": 0, "images": 0, "missed_deadlines": 0}
        def interrupted(signum, frame):
            outcome["error"] = "outer probe timeout signal " + str(signum)
            done.set()
        signal.signal(signal.SIGTERM, interrupted)
        def fly():
            control = airsim.MultirotorClient(ip="127.0.0.1", port=args.port, timeout_value=90)
            try:
                future = control.moveOnPathAsync(path, velocity=1, drivetrain=airsim.DrivetrainType.ForwardOnly,
                    yaw_mode=airsim.YawMode(is_rate=False), lookahead=3, adaptive_lookahead=1)
                outcome["result"] = future.get()
                outcome["completed"] = True
            except Exception as exc:
                outcome["error"] = repr(exc)
            finally:
                write_jsonl(out/"events.jsonl", dict(event="async_status", wall_s=time.monotonic()-wall_start, **outcome))
                done.set()
        def sample_states():
            sensors = airsim.MultirotorClient(ip="127.0.0.1", port=args.port, timeout_value=2)
            deadline = time.monotonic()
            while not sampling_stop.is_set():
                try:
                    record_state(sensors, out, counts["states"], "b", "moveOnPathAsync", wall_start)
                    counts["states"] += 1
                except Exception as exc:
                    write_jsonl(out/"events.jsonl", {"event":"state_sampling_error", "error":repr(exc), "wall_s":time.monotonic()-wall_start})
                deadline += 0.2
                if deadline < time.monotonic():
                    missed = int((time.monotonic()-deadline)//0.2)+1
                    counts["missed_deadlines"] += missed
                    deadline += missed*0.2
                sampling_stop.wait(max(0,deadline-time.monotonic()))
        def sample_images():
            images = airsim.MultirotorClient(ip="127.0.0.1", port=args.port, timeout_value=10)
            while not sampling_stop.is_set():
                try:
                    record_images(images, out, args.frames_dir, counts["images"], wall_start)
                    counts["images"] += 1
                except Exception as exc:
                    write_jsonl(out/"events.jsonl", {"event":"image_sampling_error", "error":repr(exc), "wall_s":time.monotonic()-wall_start})
                sampling_stop.wait(1.0)
        workers = [threading.Thread(target=fn, daemon=True) for fn in (sample_states,sample_images,fly)]
        for worker in workers: worker.start()
        done.wait()
        sampling_stop.set()
        workers[0].join(3)
        # Final measured state precedes pause, even if the path RPC failed/timed out.
        current = record_state(client, out, counts["states"], "b", "final_before_pause", wall_start)
        client.simPause(True)
        write_jsonl(out/"events.jsonl", {"event":"pause_after_final_state", "wall_s":time.monotonic()-wall_start})
        workers[1].join(12)
        future_completed = outcome["completed"]
        i = counts["states"]
        write_jsonl(out/"events.jsonl", {"event":"sampling_summary", "requested_state_cadence_s":0.2,
            "image_wait_after_batch_s":1.0, "missed_state_deadlines":counts["missed_deadlines"],
            "separate_clients":True, "state_samples":counts["states"]+1, "image_batches":counts["images"]})
    ending = {"reason": "pose_replay_complete" if args.mode == "a" else ("rpc_completed" if future_completed else "rpc_error_or_timeout"),
              "samples": i+1, "wall_s": time.monotonic()-wall_start,
              "async_completion_observed": future_completed if args.mode == "b" else None}
    (out/"termination.json").write_text(json.dumps(ending,indent=2)+"\n")
    print(json.dumps({"mode": args.mode, "samples": i + 1, "output": str(out)}))
    if args.mode == "b" and (not future_completed or outcome["error"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
