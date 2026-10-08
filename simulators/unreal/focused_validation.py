#!/usr/bin/env python3
"""Bounded yaw-camera or takeoff/hover/landing validation on existing Blocks."""
import argparse
import json
import math
import os
from pathlib import Path
import pwd
import shutil
import signal
import subprocess
import threading
import time
import traceback

import audit


def validate_camera(client, run, t0):
    import airsim
    import cv2
    import numpy as np
    images = []
    rows = []
    position = [0.0, 0.0, -2.0]
    yaws = [0, 90, 180, -90, 0]
    audit.write_json(run / "reference_route.json", {
        "position_ned_m": position, "yaw_degrees": yaws,
        "frame": "right-handed NED metres; quaternion fields w,x,y,z",
        "purpose": "four distinct yaw directions plus repeat-zero stale-frame check"})
    for index, yaw in enumerate(yaws):
        target = airsim.Pose(airsim.Vector3r(*position),
                            airsim.to_quaternion(0, 0, math.radians(yaw)))
        audit.record(run / "actions.jsonl", {"wall_utc": audit.utc(),
            "type": "simSetVehiclePose", "index": index, "yaw_deg": yaw,
            "requested_pose_ned": audit.pose(target)})
        client.simSetVehiclePose(target, True, "Drone1")
        time.sleep(0.5)
        requested_at = time.time()
        start = time.perf_counter()
        responses = client.simGetImages([
            airsim.ImageRequest("front_center", airsim.ImageType.Scene, False, True),
            airsim.ImageRequest("front_center", airsim.ImageType.DepthPlanar, True, False)], "Drone1")
        latency = time.perf_counter() - start
        rgb, depth = responses
        output = run / "frames" / f"{index:04d}.png"
        output.write_bytes(bytes(rgb.image_data_uint8))
        pixels = cv2.imread(str(output), cv2.IMREAD_COLOR)
        if pixels is None or pixels.shape != (480, 640, 3):
            raise RuntimeError("RGB decode/dimensions failed")
        depth_path = run / "depth" / f"{index:04d}.npy"
        np.save(depth_path, np.asarray(depth.image_data_float, dtype=np.float32).reshape(480, 640))
        info = client.simGetCameraInfo("front_center", "Drone1")
        actual = client.simGetVehiclePose("Drone1")
        row = {"index": index, "yaw_deg": yaw, "wall_elapsed_s": time.perf_counter()-t0,
            "capture_request_wall_unix_s": requested_at, "capture_return_wall_unix_s": time.time(),
            "rpc_latency_wall_s": latency, "requested_pose_ned": audit.pose(target),
            "actual_rig_pose_ned": audit.pose(actual), "camera_info_pose_ned": audit.pose(info.pose),
            "rgb_capture_pose_ned": {"position_ned_m": audit.vec(rgb.camera_position),
                                     "orientation_wxyz": audit.quat(rgb.camera_orientation)},
            "depth_capture_pose_ned": {"position_ned_m": audit.vec(depth.camera_position),
                                       "orientation_wxyz": audit.quat(depth.camera_orientation)},
            "rgb_timestamp_raw_ns": int(rgb.time_stamp), "depth_timestamp_raw_ns": int(depth.time_stamp),
            "intrinsics": {"width": 640, "height": 480, "hfov_deg": float(info.fov),
                "fx_fy_assumed_px": 640/(2*math.tan(math.radians(info.fov)/2)), "cx": 320, "cy": 240},
            "image": str(output), "sha256": audit.sha256(output), "depth_sha256": audit.sha256(depth_path),
            "rgb_min_max": [int(pixels.min()), int(pixels.max())]}
        audit.record(run / "camera.jsonl", row)
        audit.record(run / "vehicle_trajectory.jsonl", {"index": index, "actual_pose_ned": audit.pose(actual)})
        rows.append(row)
        images.append(pixels)
    comparisons = []
    for i, j in [(0,1), (1,2), (2,3), (3,4), (0,4)]:
        delta = np.abs(images[i].astype(np.int16)-images[j].astype(np.int16))
        comparisons.append({"indices": [i,j], "mean_absolute_rgb_difference": float(delta.mean()),
            "different_pixel_fraction": float(np.any(delta>0, axis=2).mean()),
            "pixel_fraction_any_channel_difference_gt10": float(np.any(delta>10, axis=2).mean())})
    canvas = np.zeros((2*280, 3*360, 3), np.uint8)
    for i, pixels in enumerate(images):
        x,y=(i%3)*360,(i//3)*280
        canvas[y+25:y+265,x:x+320] = cv2.resize(pixels,(320,240))
        cv2.putText(canvas,f"yaw {yaws[i]} deg",(x+4,y+20),cv2.FONT_HERSHEY_SIMPLEX,.5,(255,255,255),1)
    cv2.imwrite(str(run / "yaw-contact.png"), canvas)
    if len({r["sha256"] for r in rows[:4]}) != 4:
        raise RuntimeError("Distinct yaw views produced duplicate image hashes")
    return {"status": "captured_pending_visual_confirmation", "frames": 5, "pixel_comparisons": comparisons}


def validate_landing(client, run, t0):
    import airsim
    events = []
    phase = "spawn_settling"
    first_stamp = None
    baseline = client.simGetCollisionInfo("Drone1")
    ground_z = None
    def sample():
        nonlocal first_stamp
        s,c,stamp = audit.state_sample(client, run, len(events), t0, first_stamp)
        if first_stamp is None:
            first_stamp = stamp
        row = {"phase": phase, "wall_elapsed_s": time.perf_counter()-t0,
            "state_timestamp_raw_ns": stamp, "altitude_above_ned_origin_m": -float(s.kinematics_estimated.position.z_val),
            "altitude_above_settled_spawn_ground_m": ground_z-float(s.kinematics_estimated.position.z_val) if ground_z is not None else None,
            "vertical_velocity_ned_down_mps": float(s.kinematics_estimated.linear_velocity.z_val),
            "landed_state": int(s.landed_state), "collision": bool(c.has_collided),
            "collision_timestamp_raw_ns": int(c.time_stamp), "collision_object": c.object_name,
            "new_collision_after_spawn_baseline": bool(c.has_collided and int(c.time_stamp)>int(baseline.time_stamp))}
        events.append(row)
        audit.record(run / "descent.jsonl", row)
        return row
    def command(name, timeout_s, observe_s):
        nonlocal phase
        phase = name
        finished = threading.Event()
        result = {}
        def rpc():
            try:
                other = airsim.MultirotorClient(timeout_value=timeout_s+5)
                future = getattr(other, name)(timeout_sec=timeout_s, vehicle_name="Drone1")
                result["server_return_value"] = future.get()
            except Exception:
                result["error"] = traceback.format_exc()
            finally:
                result["rpc_completion_wall_elapsed_s"] = time.perf_counter()-t0
                finished.set()
                audit.record(run / "actions.jsonl", {"type": name+"_rpc_completed", **result})
        audit.record(run / "actions.jsonl", {"type": name, "wall_elapsed_s": time.perf_counter()-t0,
            "timeout_s": timeout_s, "observation_window_s": observe_s})
        threading.Thread(target=rpc, daemon=True).start()
        end = time.perf_counter()+observe_s
        post_complete_end = None
        while time.perf_counter()<end:
            sample()
            if finished.is_set() and post_complete_end is None:
                post_complete_end = time.perf_counter()+(10 if name=="landAsync" else 1)
            if post_complete_end is not None and time.perf_counter()>=post_complete_end:
                break
            time.sleep(.2)
        if not finished.is_set():
            raise RuntimeError(name+" RPC did not complete within observation window")
        if "error" in result:
            raise RuntimeError(result["error"])
        return result
    settle_start=time.perf_counter()
    stable_since=None
    while time.perf_counter()-settle_start<15:
        row=sample()
        stable=abs(row["vertical_velocity_ned_down_mps"])<.05 and row["landed_state"]==0
        if stable and stable_since is None: stable_since=time.perf_counter()
        if not stable: stable_since=None
        if time.perf_counter()-settle_start>=5 and stable_since and time.perf_counter()-stable_since>=1:
            break
        time.sleep(.2)
    else: raise RuntimeError("Spawn did not settle before arming")
    ground_z=-events[-1]["altitude_above_ned_origin_m"]
    baseline=client.simGetCollisionInfo("Drone1")
    audit.write_json(run / "collision_baseline.json", {
        "has_collided":bool(baseline.has_collided),"timestamp_raw":int(baseline.time_stamp),
        "object_name":baseline.object_name,"settled_ground_z_ned_m":ground_z})
    client.enableApiControl(True, "Drone1")
    if not client.armDisarm(True, "Drone1"):
        raise RuntimeError("Arm failed")
    takeoff = command("takeoffAsync", 15, 20)
    if events[-1]["landed_state"]!=int(airsim.LandedState.Flying) or events[-1]["altitude_above_settled_spawn_ground_m"]<.5:
        raise RuntimeError("Takeoff RPC completed without verified airborne state and >0.5 m clearance")
    phase = "hover"
    for _ in range(40): sample(); time.sleep(.2)
    land = command("landAsync", 20, 35)
    landed = len(events)>=5 and all(e["landed_state"]==int(airsim.LandedState.Landed) for e in events[-5:])
    accepted = landed and takeoff.get("server_return_value") is True and land.get("server_return_value") is True
    summary = {"status": "passed" if accepted else "failed_rpc_or_landed_state", "landed_confirmed": landed,
        "acceptance": "verified airborne hover; takeoff/land RPC true; last five polls all Landed; no relaxation",
        "settled_ground_z_ned_m":ground_z,"takeoff_airborne_verified":True,
        "takeoff_rpc": takeoff, "land_rpc": land, "samples": len(events),
        "no_images_acquired": True, "new_collisions": [e for e in events if e["new_collision_after_spawn_baseline"]],
        "last_state": events[-1], "max_altitude_above_ned_origin_m": max(e["altitude_above_ned_origin_m"] for e in events)}
    audit.write_json(run / "validation.json", summary)
    if not accepted:
        raise RuntimeError("RPC boolean or five-consecutive-Landed acceptance failed; see validation.json")
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode", choices=["camera", "landing"])
    p.add_argument("--run-id", required=True)
    args=p.parse_args()
    root=Path(__file__).resolve().parents[2]
    run=root/"artifacts/unreal"/args.run_id
    run.mkdir(parents=True, exist_ok=False)
    for name in ("frames", "depth"): (run/name).mkdir()
    shutil.copy2(__file__,run/"focused_validation.py")
    shutil.copy2(audit.__file__,run/"audit_helpers.py")
    settings=json.loads(json.dumps(audit.SETTINGS))
    if args.mode=="camera": settings["SimMode"]="ComputerVision"; settings["Vehicles"]["Drone1"]["VehicleType"]="ComputerVision"
    audit.write_json(run/"settings.json",settings)
    home=Path("/tmp")/("r4r-validation-home-"+args.run_id)
    cfg=home/"Documents/AirSim/settings.json"
    cfg.parent.mkdir(parents=True)
    shutil.copy2(run/"settings.json",cfg)
    user=pwd.getpwnam("nobody")
    for f in [home,home/"Documents",cfg.parent,cfg]: os.chown(f,user.pw_uid,user.pw_gid)
    exe=Path("/tmp/r4r-ue-assets/LinuxBlocks1.8.1/LinuxNoEditor/Blocks/Binaries/Linux/Blocks")
    argv=[str(exe),"Blocks","-RenderOffscreen","-vulkan","-windowed","-ResX=640","-ResY=480","-nosound","-log"]
    t0=time.perf_counter(); game=None; stop=threading.Event(); client=None; code=1
    meta={"run_id":args.run_id,"experiment":args.mode,"started_utc":audit.utc(),"policy_weights":"none",
        "source_asset_url":audit.ASSET_URL,"asset_sha256":audit.ASSET_SHA256,"binary_sha256":audit.sha256(exe),
        "runner_sha256":audit.sha256(Path(__file__)),"helper_sha256":audit.sha256(Path(audit.__file__)),
        "git_commit":audit.cmd_output(["git","-C",str(root),"rev-parse","HEAD"]),
        "git_status":audit.cmd_output(["git","-C",str(root),"status","--short"]),
        "environment":audit.cmd_output(["/root/R4R-Sims/third_party/unreal/venv/bin/python","-m","pip","freeze"]),
        "host":audit.cmd_output(["uname","-a"]),"gpu":audit.cmd_output(["nvidia-smi"]),
        "output_dir":str(run),"seed":None,"sampling_target_state_hz":5,"gpu_sampling_target_hz":1,
        "scene_split":"stock Blocks; none","warmup":"camera 3 discarded RGB calls; landing no camera calls",
        "render_throughput":"unmeasured","policy_latency":"none","errors":[]}
    audit.write_json(run/"run.json",meta)
    audit.record(run/"commands.log",{"argv":argv,"wall_utc":audit.utc()})
    def timeout_signal(*_): raise TimeoutError("Independent watchdog signal")
    signal.signal(signal.SIGTERM,timeout_signal)
    try:
        if not audit.port_free(): raise RuntimeError("RPC port owned by another process; no process stopped")
        env=os.environ.copy(); env.update(HOME=str(home),XDG_RUNTIME_DIR=str(home))
        game=subprocess.Popen(argv,cwd=str(exe.parents[3]),env=env,user=user.pw_uid,group=user.pw_gid,
            start_new_session=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors="replace")
        audit.write_json(run/"owned-process.json",{"pid":game.pid,"argv":argv})
        threading.Thread(target=audit.pump,args=(game.stdout,run/"console.log","UE"),daemon=True).start()
        threading.Thread(target=audit.gpu_samples,args=(stop,run/"gpu.jsonl"),daemon=True).start()
        import airsim
        deadline=time.perf_counter()+60
        while time.perf_counter()<deadline:
            try:
                client=airsim.MultirotorClient(timeout_value=3)
                if client.ping(): break
            except Exception: pass
            time.sleep(.5)
        else: raise TimeoutError("RPC startup")
        if args.mode=="camera":
            for _ in range(3): client.simGetImages([airsim.ImageRequest("front_center",airsim.ImageType.Scene,False,True)],"Drone1")
            result=validate_camera(client,run,t0)
        else: result=validate_landing(client,run,t0)
        audit.write_json(run/"validation.json",result)
        meta["status"]=result["status"]; code=0
    except Exception:
        meta["status"]="failed"; meta["errors"].append(traceback.format_exc())
    finally:
        stop.set()
        if client and args.mode=="landing":
            try: client.armDisarm(False,"Drone1"); client.enableApiControl(False,"Drone1")
            except Exception: meta["errors"].append(traceback.format_exc())
        if game and game.poll() is None:
            os.killpg(game.pid,signal.SIGTERM)
            try: game.wait(timeout=10)
            except subprocess.TimeoutExpired: os.killpg(game.pid,signal.SIGKILL); game.wait()
        meta.update(finished_utc=audit.utc(),wall_elapsed_s=time.perf_counter()-t0,exit_status=code,
                    game_exit_status=game.returncode if game else None)
        audit.write_json(run/"run.json",meta)
        audit.record(run/"commands.log",{"exit_status":code,"wall_utc":audit.utc()})
        print(json.dumps({"run_id":args.run_id,"status":meta["status"],"exit_status":code}),flush=True)
    return code


if __name__=="__main__": raise SystemExit(main())
