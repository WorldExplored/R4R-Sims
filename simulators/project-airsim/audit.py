#!/usr/bin/env python3
"""Bounded v1.0.1 Blocks A/B capture. Raw output belongs in ignored artifacts."""
import argparse
import asyncio
import hashlib
import json
import math
import os
import queue
import sys
import threading
import time
import traceback
from pathlib import Path

SOURCE_COMMIT = "09755454b8d82b0231af7e59fd1ab8f980ff32c5"
IMAGE_KEYS = ("time_stamp", "height", "width", "encoding", "big_endian", "step",
              "pos_x", "pos_y", "pos_z", "rot_w", "rot_x", "rot_y", "rot_z")

def now():
    return {"wall_unix_s": time.time(), "wall_monotonic_ns": time.monotonic_ns()}

def write_json(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")
    tmp.replace(path)

def append(path, value):
    with path.open("a", encoding="utf8") as out:
        out.write(json.dumps(value, sort_keys=True, default=str) + "\n")
        out.flush()

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as src:
        for chunk in iter(lambda: src.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()

def pose_dict(pose):
    return json.loads(json.dumps(pose, default=lambda x: dict(x)))

def xyz(pose):
    p = pose.get("translation", pose.get("position", {}))
    return [p.get(k) for k in ("x", "y", "z")]

def qdict(yaw_deg, x, y, z):
    from projectairsim.types import Pose
    rad = math.radians(yaw_deg) / 2
    return Pose({"frame_id": "DEFAULT_FRAME", "translation": {"x": x, "y": y, "z": z},
                 "rotation": {"w": math.cos(rad), "x": 0.0, "y": 0.0, "z": math.sin(rad)}})

class Recorder:
    def __init__(self, root, max_frames=700):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=False)
        (root / "rgb").mkdir()
        (root / "depth_planar").mkdir()
        self.q = queue.Queue(maxsize=200)
        self.stop = threading.Event()
        self.count = {"received_rgb": 0, "received_depth": 0, "saved_rgb": 0,
                      "saved_depth": 0, "dropped_queue": 0, "state": 0, "collision": 0}
        self.lock = threading.Lock()
        self.max_frames = max_frames
        self.worker = threading.Thread(target=self._write, daemon=True)
        self.worker.start()

    def callback(self, kind, camera=None):
        def receive(_, msg):
            stamp = now()
            with self.lock:
                if kind in ("rgb", "depth"):
                    self.count["received_" + kind] += 1
            try:
                self.q.put_nowait((kind, camera, msg, stamp))
            except queue.Full:
                with self.lock:
                    self.count["dropped_queue"] += 1
        return receive

    def _write(self):
        import cv2
        import numpy as np
        from projectairsim.utils import unpack_image
        while not self.stop.is_set() or not self.q.empty():
            try:
                kind, camera, msg, stamp = self.q.get(timeout=0.2)
            except queue.Empty:
                continue
            try:
                if kind in ("rgb", "depth"):
                    idx = self.count["saved_" + kind]
                    if idx >= self.max_frames:
                        append(self.root / "drops.jsonl", {**stamp, "reason": "max_frames", "kind": kind})
                        continue
                    meta = {k: msg.get(k) for k in IMAGE_KEYS}
                    meta.update(stamp)
                    meta["camera"] = camera
                    meta["image_type"] = 0 if kind == "rgb" else 1
                    arr = unpack_image(msg)
                    if kind == "depth":
                        if arr.ndim != 2:
                            raise ValueError(f"depth shape {arr.shape}")
                        file = self.root / "depth_planar" / f"{camera}_{idx:04d}.npy"
                        np.save(file, arr, allow_pickle=False)
                        meta["dtype"] = str(arr.dtype)
                        meta["finite_fraction"] = float(np.isfinite(arr).mean())
                        meta["nonfinite_count"] = int((~np.isfinite(arr)).sum())
                    else:
                        if arr.ndim != 3:
                            raise ValueError(f"RGB shape {arr.shape}")
                        file = self.root / "rgb" / f"{camera}_{idx:04d}.png"
                        if not cv2.imwrite(str(file), arr):
                            raise IOError(f"PNG write failed: {file}")
                        meta["dtype"] = str(arr.dtype)
                    meta["path"] = str(file.relative_to(self.root))
                    meta["sha256"] = digest(file)
                    meta["saved_wall_monotonic_ns"] = time.monotonic_ns()
                    meta["callback_to_save_ms"] = (meta["saved_wall_monotonic_ns"] - stamp["wall_monotonic_ns"]) / 1e6
                    append(self.root / "images.jsonl", meta)
                    with self.lock:
                        self.count["saved_" + kind] += 1
                elif kind == "state":
                    append(self.root / "actual_vehicle.jsonl", {**stamp, "native": msg})
                    with self.lock:
                        self.count["state"] += 1
                elif kind == "collision":
                    append(self.root / "collisions.jsonl", {**stamp, "native": msg})
                    with self.lock:
                        self.count["collision"] += 1
                elif kind == "camera_info":
                    append(self.root / "camera_info.jsonl", {**stamp, "camera": camera, "native": msg})
            except Exception as exc:
                append(self.root / "errors.jsonl", {**stamp, "kind": kind, "error": repr(exc)})
            finally:
                self.q.task_done()

    def direct_image(self, kind, camera, image, request_timing):
        self.callback(kind, camera)(None, image)
        append(self.root / "requests.jsonl", {"kind": kind, "camera": camera, **request_timing})

    def close(self):
        self.q.join()
        self.stop.set()
        self.worker.join(timeout=5)
        write_json(self.root / "counts.json", self.count)

def subscribe_capture(client, drone, rec):
    for camera in ("DownCamera", "ForwardCamera"):
        for kind, topic in (("rgb", "scene_camera"), ("depth", "depth_planar_camera"),
                            ("camera_info", "scene_camera_info")):
            if topic not in drone.sensors.get(camera, {}):
                append(rec.root / "errors.jsonl", {"missing_topic": [camera, topic]})
                continue
            client.subscribe(drone.sensors[camera][topic], rec.callback(kind, camera))
    client.subscribe(drone.robot_info["actual_pose"], rec.callback("state"))
    client.subscribe(drone.robot_info["collision_info"], rec.callback("collision"))

async def task_done(rec, drone, label, started_task, limit=30):
    append(rec.root / "actions.jsonl", {"phase": label, "event": "start", **now()})
    try:
        result = await asyncio.wait_for(started_task, limit)
        append(rec.root / "actions.jsonl", {"phase": label, "event": "complete", "result": result, **now()})
        return result
    except Exception as exc:
        append(rec.root / "actions.jsonl", {"phase": label, "event": "failed", "error": repr(exc), **now()})
        try:
            drone.cancel_last_task()
        except Exception:
            pass
        raise

async def flight(args, client, world, drone, rec):
    subscribe_capture(client, drone, rec)
    await asyncio.sleep(2)
    drone.enable_api_control()
    if not drone.arm():
        raise RuntimeError("arm returned false")
    start = pose_dict(drone.get_ground_truth_pose())
    append(rec.root / "reference_route.jsonl", {"phase": "spawn", "pose": start, **now()})
    try:
        await task_done(rec, drone, "takeoff", await drone.takeoff_async(timeout_sec=25))
        hover_pose = pose_dict(drone.get_ground_truth_pose())
        append(rec.root / "reference_route.jsonl", {"phase": "hover_1", "pose": hover_pose, "duration_wall_s": 3, **now()})
        await task_done(rec, drone, "hover_1", await drone.hover_async(), 5)
        await asyncio.sleep(3)
        p = xyz(hover_pose)
        if any(v is None for v in p):
            raise RuntimeError(f"unknown hover position: {hover_pose}")
        if args.mode == "smoke":
            route = [{"phase": "short_horizontal", "ned_m": [p[0]+1, p[1], p[2]], "speed_m_s": 1.0}]
        else:
            route = [
                {"phase": "horizontal", "ned_m": [p[0]+2.5, p[1], p[2]], "speed_m_s": 1.0},
                {"phase": "vertical_up", "ned_m": [p[0]+2.5, p[1], p[2]-1.0], "speed_m_s": 1.0},
            ]
        for segment in route:
            append(rec.root / "reference_route.jsonl", {**segment, **now()})
            target=segment["ned_m"]
            await task_done(rec, drone, segment["phase"],
                await drone.move_to_position_async(*target, velocity=segment["speed_m_s"], timeout_sec=25))
        if args.mode == "flight":
            append(rec.root / "reference_route.jsonl", {"phase": "yaw_plus_30", "degrees_from_spawn": -15, **now()})
            await task_done(rec, drone, "yaw_plus_30",
                            await drone.rotate_to_yaw_async(math.radians(-15), timeout_sec=25))
            await task_done(rec, drone, "hover_2", await drone.hover_async(), 5)
            await asyncio.sleep(3)
            return_pt = [p[0],p[1],p[2]]
            append(rec.root / "reference_route.jsonl", {"phase": "return", "ned_m": return_pt, "speed_m_s": 1.0, **now()})
            await task_done(rec, drone, "return",
                await drone.move_to_position_async(*return_pt, velocity=1.0, timeout_sec=25))
        await task_done(rec, drone, "land", await drone.land_async(timeout_sec=25))
        append(rec.root / "actions.jsonl", {"phase": "landed_check", "landed_state": drone.get_landed_state(),
                                           "ground_truth": pose_dict(drone.get_ground_truth_pose()), **now()})
    finally:
        try:
            drone.disarm()
            drone.disable_api_control()
        except Exception as exc:
            append(rec.root / "errors.jsonl", {"cleanup": repr(exc), **now()})

def pose_sequence():
    return [
        ("base", -1.0, 8.0, -4.0, -45.0),
        ("horizontal_plus_2m", 1.0, 8.0, -4.0, -45.0),
        ("vertical_up_1m", 1.0, 8.0, -5.0, -45.0),
        ("heading_plus_30deg", 1.0, 8.0, -5.0, -15.0),
        ("return_base", -1.0, 8.0, -4.0, -45.0),
    ]

def pose_capture(args, client, world, drone, rec):
    # Capture info through published topic; get_images service promises a next-capture timestamp.
    for camera in ("DownCamera", "ForwardCamera"):
        topic = drone.sensors.get(camera, {}).get("scene_camera_info")
        if topic:
            client.subscribe(topic, rec.callback("camera_info", camera))
    prior = {}
    for label, x, y, z, yaw in pose_sequence():
        requested=qdict(yaw,x,y,z)
        append(rec.root / "reference_route.jsonl", {"phase": label, "requested": pose_dict(requested), **now()})
        set_result=drone.set_pose(requested)
        achieved=pose_dict(drone.get_ground_truth_pose())
        append(rec.root / "actual_vehicle.jsonl",
               {"phase": label, "set_pose_result": set_result, "achieved": achieved,
                "sim_ns": world.get_sim_time(), **now()})
        if not set_result:
            raise RuntimeError(f"set_pose failed at {label}")
        for camera in ("DownCamera", "ForwardCamera"):
            start=now()
            images=drone.get_images(camera,[0,1])
            end=now()
            for kind, image_type in (("rgb",0),("depth",1)):
                img=images[image_type]
                ts=img.get("time_stamp")
                last=prior.get((camera,kind))
                fresh=ts is not None and (last is None or ts>last)
                append(rec.root / "freshness.jsonl",
                       {"phase": label, "camera": camera, "kind": kind, "time_stamp": ts,
                        "previous": last, "fresh": fresh, "request_start": start, "request_end": end})
                prior[(camera,kind)]=ts
                if not fresh:
                    raise RuntimeError(f"stale {camera}/{kind} at {label}: {ts} <= {last}")
                rec.direct_image(kind,camera,img,{"phase":label,"request_start":start,"request_end":end})
    return 0

async def run(args):
    import projectairsim
    from projectairsim import ProjectAirSimClient, World, Drone
    root=Path(args.output).resolve()
    rec=Recorder(root)
    meta={"status":"running","mode":args.mode,"run_id":root.name,
          "source_commit":SOURCE_COMMIT,"client_version":projectairsim.__version__,
          "config_dir":str(Path(args.config_dir).resolve()),"scene":args.scene,
          "policy_weights":"none","split":"official Blocks native scene, no dataset split",
          "started":now(),"command":sys.argv,"request_timeout_ms":10000}
    write_json(root/"run.json",meta)
    client=ProjectAirSimClient()
    try:
        client.connect()
        client.socket_services.recv_timeout=10000
        meta["server_commit"]=client.get_build_commit_hash()
        # A packaged server may report a different build; retain the value and test API behavior.
        world=World(client,args.scene,delay_after_load_sec=2,sim_config_path=str(Path(args.config_dir).resolve())+"/")
        drone=Drone(client,world,"Drone1")
        write_json(root/"resolved_config.json",world.get_configuration())
        meta["scene_config_path"]=str(world.scene_config_path)
        meta["robot_config_paths"]=[str(x) for x in world.robot_config_paths]
        write_json(root/"run.json",meta)
        if args.mode=="pose":
            pose_capture(args,client,world,drone,rec)
        else:
            await flight(args,client,world,drone,rec)
        meta["status"]="completed"
        return 0
    except Exception as exc:
        meta["status"]="failed"
        meta["error"]=repr(exc)
        append(root/"errors.jsonl",{"error":repr(exc),"traceback":traceback.format_exc(),**now()})
        return 1
    finally:
        meta["finished"]=now()
        try:
            client.disconnect()
        except Exception as exc:
            append(root/"errors.jsonl",{"disconnect":repr(exc),**now()})
        rec.close()
        write_json(root/"run.json",meta)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("pose","smoke","flight"),required=True)
    p.add_argument("--scene",required=True)
    p.add_argument("--config-dir",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    raise SystemExit(asyncio.run(run(a)))
