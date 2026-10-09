#!/usr/bin/env python3
"""Bounded RflySim Free Edition SITL audit. Phase-1 static draft; verify installed SDK first."""
import argparse
import csv
import hashlib
import importlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone


def utc():
    return datetime.now(timezone.utc).isoformat()


def dump(path, data):
    path.write_text(json.dumps(data, indent=2, default=str) + "\n", encoding="utf-8")


def line(path, data):
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, default=str) + "\n")


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sdk_root(toolchain):
    matches = list(toolchain.rglob("RflySimSDK/ctrl/PX4MavCtrlV4.py"))
    return matches[0].parents[2] if len(matches) == 1 else None


def preflight(args, out):
    root = sdk_root(args.toolchain) if args.toolchain.exists() else None
    free = shutil.disk_usage(args.runs.parent if args.runs.parent.exists() else Path.cwd()).free
    data = {
        "utc": utc(), "os": platform.platform(), "python": sys.version,
        "toolchain": str(args.toolchain.resolve()), "sdk_root": str(root) if root else None,
        "camera_config": str(args.camera_config.resolve()) if args.camera_config else None,
        "camera_config_exists": bool(args.camera_config and args.camera_config.is_file()),
        "free_bytes": free, "gpu": None, "driver": None,
        "checks": {"toolchain_exists": args.toolchain.is_dir(), "sdk_unique": root is not None,
                   "free_20gb_for_run": free >= 20 * 1024**3},
        "unverified": ["installed version", "PX4 build/params", "ports", "camera poses", "scene ID", "licenses"]
    }
    if root:
        p = root / "RflySimSDK" / "ctrl" / "PX4MavCtrlV4.py"
        data["sdk_controller_sha256"] = sha(p)
        v = root / "RflySimSDK" / "vision" / "VisionCaptureApi.py"
        if v.is_file():
            data["sdk_vision_sha256"] = sha(v)
        for name in ("SITLRun.bat", "RflySim3D.exe", "CopterSim.exe"):
            hits = list(args.toolchain.rglob(name))
            data[name] = [str(x) for x in hits[:10]]
    if out:
        dump(out, data)
    return data


def jsonable(value):
    if value is None:
        return None
    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, (int, float, str, bool, list, dict)):
        return value
    return str(value)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["preflight", "run", "manifest", "verify"])
    ap.add_argument("--toolchain", type=Path, required=True)
    ap.add_argument("--runs", type=Path, required=True)
    ap.add_argument("--camera-config", type=Path)
    ap.add_argument("--duration", type=int, default=75)
    ap.add_argument("--run-id")
    ap.add_argument("--verify-dir", type=Path)
    args = ap.parse_args()
    if args.mode == "preflight":
        args.runs.mkdir(parents=True, exist_ok=True)
        d = preflight(args, args.runs / "preflight.json")
        print(json.dumps(d, indent=2))
        return 0 if all(d["checks"].values()) else 2
    if args.mode == "verify":
        if not args.run_id or not args.verify_dir:
            ap.error("verify requires --run-id and --verify-dir")
        manifest = args.runs / args.run_id / "sha256.json"
        if not manifest.is_file():
            ap.error("source manifest absent")
        entries = json.loads(manifest.read_text(encoding="utf-8"))
        failures = []
        for rel, expected in entries.items():
            dest = args.verify_dir / rel
            if not dest.is_file() or dest.stat().st_size != expected["bytes"] or sha(dest) != expected["sha256"]:
                failures.append(rel)
        for path in args.verify_dir.glob("frames/*.png"):
            try:
                import cv2
                if cv2.imread(str(path)) is None:
                    failures.append(str(path))
            except ImportError:
                failures.append("OpenCV absent; image decoding unverified")
                break
        print(json.dumps({"verified_files": len(entries) - len(failures), "failures": failures}, indent=2))
        return 0 if not failures else 3
    if args.mode == "manifest":
        if not args.run_id:
            ap.error("manifest requires --run-id")
        folder = args.runs / args.run_id
        if not folder.is_dir():
            ap.error("run folder absent")
        files = {str(p.relative_to(folder)): {"bytes": p.stat().st_size, "sha256": sha(p)}
                 for p in folder.rglob("*") if p.is_file() and p.name != "sha256.json"}
        dump(folder / "sha256.json", files)
        print(f"manifested {len(files)} files in {folder}")
        return 0
    if not 60 <= args.duration <= 120:
        ap.error("duration must be 60..120 seconds")
    args.runs.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + os.urandom(4).hex()
    folder = args.runs / run_id
    folder.mkdir(exist_ok=False)
    (folder / "frames").mkdir()
    (folder / "configs").mkdir()
    pf = preflight(args, folder / "preflight.json")
    dump(folder / "environment.json", {"utc": utc(), "platform": platform.platform(),
         "python": sys.version, "executable": sys.executable, "cwd": os.getcwd(),
         "gpu_driver": "unmeasured", "toolchain_version": "pending host inspection"})
    dump(folder / "assets.json", {"toolchain": str(args.toolchain.resolve()),
         "camera_config": str(args.camera_config.resolve()) if args.camera_config else None,
         "iso_url": "pending", "iso_sha256": "pending", "scene": "pending installed inspection",
         "vehicle_model": "pending installed inspection", "px4_build": "pending installed inspection",
         "policy_weights": "none"})
    if args.camera_config and args.camera_config.is_file():
        shutil.copy2(args.camera_config, folder / "configs" / args.camera_config.name)
    route = [{"t_s": t, "ned_m": pos, "yaw_rad": 0.0} for t, pos in
             [(0, [0, 0, -2]), (12, [0, 0, -2]), (22, [2, 0, -2]),
              (32, [2, 2, -2]), (42, [0, 0, -2])]]
    dump(folder / "reference_route.json", {"frame": "local NED, metres; initial origin pending", "route": route})
    cmd = " ".join(sys.argv)
    (folder / "commands.log").write_text(f"{utc()} {cmd}\n", encoding="utf-8")
    run = {"id": run_id, "started_utc": utc(), "status": "starting", "exit_status": None,
           "command": cmd, "input_paths": [str(args.toolchain), str(args.camera_config)],
           "output_path": str(folder.resolve()), "duration_limit_s": args.duration,
           "state_target_hz": 10, "camera_target_hz": 1, "gpu_poll_hz": 1,
           "time_conventions": "UTC wall clock and monotonic seconds; simulation time not available until verified",
           "control_mode": "PX4 offboard position", "seed": "none; deterministic route",
           "camera_intrinsics_extrinsics": "pending Config.json parsing and actual-pose API verification",
           "scale": "NED metres; UE conversion pending", "scene_split": "stock demo; none",
           "policy_weights": "none", "errors": []}
    dump(folder / "run.json", run)
    for name in ("actions.jsonl", "vehicle_state.jsonl", "camera_poses.jsonl"):
        (folder / name).touch()
    console = (folder / "console.log").open("a", encoding="utf-8")
    def log(message):
        s = f"{utc()} {message}"
        print(s, flush=True)
        console.write(s + "\n")
        console.flush()
    mav = None
    vis = None
    status = 1
    start = time.monotonic()
    try:
        if not all(pf["checks"].values()):
            raise RuntimeError("preflight failed")
        sys.path.insert(0, str(sdk_root(args.toolchain)))
        mod = importlib.import_module("RflySimSDK.ctrl.PX4MavCtrlV4")
        mav = mod.PX4MavCtrler(ID=1)
        mav.InitMavLoop()
        time.sleep(2)
        # Camera is optional: no frames are claimed unless request and data succeed.
        if args.camera_config and args.camera_config.is_file():
            try:
                vm = importlib.import_module("RflySimSDK.vision.VisionCaptureApi")
                vis = vm.VisionCaptureApi()
                vis.jsonLoad(jsonPath=str(args.camera_config))
                if not vis.sendReqToUE4():
                    raise RuntimeError("UE camera request rejected")
                vis.startImgCap()
                log("camera capture started")
            except Exception as exc:
                vis = None
                run["errors"].append(f"camera unavailable: {exc}")
                log(f"camera unavailable: {exc}")
        mav.initOffboard()
        mav.SendPosNED(0, 0, -2, 0)
        mav.SendMavArm(True)
        log("offboard setpoint and arm sent; acknowledgment must be checked in state/flight log")
        start = time.monotonic()
        last_segment = -1
        last_frame = -1
        last_gpu = -1
        with (folder / "gpu.csv").open("w", newline="", encoding="utf-8") as gf:
            gw = csv.writer(gf)
            gw.writerow(["utc", "elapsed_wall_s", "gpu_memory_used_mib", "gpu_util_percent", "query_status"])
            while True:
                elapsed = time.monotonic() - start
                if elapsed >= min(args.duration - 8, 50):
                    break
                segment = max(i for i, item in enumerate(route) if elapsed >= item["t_s"])
                target = route[segment]["ned_m"]
                # Offboard setpoints are renewed at 10 Hz for PX4 keepalive.
                mav.SendPosNED(*target, 0)
                line(folder / "actions.jsonl", {"utc": utc(), "elapsed_wall_s": elapsed,
                     "action": "SendPosNED", "target_ned_m": target, "yaw_rad": 0})
                if segment != last_segment:
                    log(f"segment {segment} target {target}")
                    last_segment = segment
                fields = {key: jsonable(getattr(mav, key, None)) for key in
                          ("uavPosNED", "uavVelNED", "uavAngEular", "uavAngEuler", "truePosNED", "isArmed")}
                line(folder / "vehicle_state.jsonl", {"utc": utc(), "elapsed_wall_s": elapsed,
                     "sim_time_s": None, "source": "RflySimSDK PX4 controller fields; truth unverified", "fields": fields})
                # Never label reference or vehicle position as actual camera pose.
                line(folder / "camera_poses.jsonl", {"utc": utc(), "elapsed_wall_s": elapsed,
                     "actual_pose": None, "reason": "camera pose API and extrinsics not yet verified"})
                second = int(elapsed)
                if vis is not None and second != last_frame:
                    last_frame = second
                    try:
                        if vis.hasData and vis.hasData[0]:
                            import cv2
                            frame = vis.Img[0]
                            if frame is not None:
                                path = folder / "frames" / f"{second:04d}.png"
                                if cv2.imwrite(str(path), frame):
                                    line(folder / "frames.jsonl", {"utc": utc(), "elapsed_wall_s": elapsed,
                                         "path": str(path), "camera_pose": None})
                                else:
                                    raise RuntimeError("imwrite failed")
                        else:
                            line(folder / "frames_missing.jsonl", {"utc": utc(), "elapsed_wall_s": elapsed,
                                 "reason": "no camera data"})
                    except Exception as exc:
                        line(folder / "frames_missing.jsonl", {"utc": utc(), "elapsed_wall_s": elapsed,
                             "reason": str(exc)})
                if second != last_gpu:
                    last_gpu = second
                    try:
                        q = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,utilization.gpu",
                             "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=2)
                        gw.writerow([utc(), elapsed, *(q.stdout.strip().split(", ") if q.returncode == 0 else ["", ""]), q.returncode])
                    except (OSError, subprocess.TimeoutExpired) as exc:
                        gw.writerow([utc(), elapsed, "", "", str(exc)])
                    gf.flush()
                time.sleep(max(0, 0.1 - (time.monotonic() - start - elapsed)))
        status = 0
    except Exception as exc:
        run["errors"].append(repr(exc))
        log(f"ERROR {exc!r}")
    finally:
        if mav is not None:
            try:
                mav.sendMavLand()
                line(folder / "actions.jsonl", {"utc": utc(), "action": "sendMavLand"})
                log("land sent")
                landing_start = time.monotonic()
                while time.monotonic() - landing_start < 6:
                    line(folder / "vehicle_state.jsonl", {"utc": utc(),
                         "elapsed_wall_s": time.monotonic() - start, "sim_time_s": None,
                         "phase": "landing", "source": "RflySimSDK PX4 controller fields; truth unverified",
                         "fields": {key: jsonable(getattr(mav, key, None)) for key in
                                    ("uavPosNED", "uavVelNED", "isArmed")}})
                    time.sleep(0.1)
            except Exception as exc:
                run["errors"].append(f"landing: {exc!r}")
                status = 1
            try:
                mav.endOffboard()
                mav.endMavLoop()
            except Exception as exc:
                run["errors"].append(f"cleanup: {exc!r}")
        if vis is not None:
            try:
                vis.stopRun()
            except Exception as exc:
                run["errors"].append(f"vision cleanup: {exc!r}")
        run.update({"ended_utc": utc(), "elapsed_wall_s": time.monotonic() - start,
                    "status": "commands_completed_unverified" if status == 0 else "failed", "exit_status": status})
        dump(folder / "run.json", run)
        with (folder / "commands.log").open("a", encoding="utf-8") as f:
            f.write(f"{utc()} exit_status={status}\n")
        console.close()
        files = {str(p.relative_to(folder)): {"bytes": p.stat().st_size, "sha256": sha(p)}
                 for p in folder.rglob("*") if p.is_file() and p.name != "sha256.json"}
        dump(folder / "sha256.json", files)
    return status


if __name__ == "__main__":
    sys.exit(main())
