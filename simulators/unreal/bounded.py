#!/usr/bin/env python3
"""Independent wall-clock supervisor for one owned AirSim audit process group."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, value):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temp, path)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=("a", "b"), required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument("--asset-zip", type=Path, required=True)
    p.add_argument("--exe", type=Path, required=True)
    p.add_argument("--deadline-s", type=int, default=190)
    args = p.parse_args()
    root = Path(__file__).resolve().parents[2]
    run_dir = root / "artifacts" / "unreal" / args.run_id
    if run_dir.exists():
        raise SystemExit("Run ID already exists: " + args.run_id)
    command = [sys.executable, str(Path(__file__).with_name("audit.py")), "run",
               "--root", str(root), "--asset-zip", str(args.asset_zip),
               "--exe", str(args.exe), "--mode", args.mode,
               "--run-id", args.run_id, "--max-wall-s", "180"]
    supervisor_log = Path("/tmp") / (args.run_id + "-supervisor.log")
    with supervisor_log.open("w", encoding="utf-8", buffering=1) as log:
        log.write(now() + " argv=" + json.dumps(command) + "\n")
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                 start_new_session=True)
        try:
            status = child.wait(timeout=args.deadline_s)
        except subprocess.TimeoutExpired:
            log.write(now() + " independent watchdog timeout; terminate owned process group\n")
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
            owned = run_dir / "owned-process.json"
            if owned.is_file():
                game_pid = json.loads(owned.read_text(encoding="utf-8"))["pid"]
                try:
                    if os.getpgid(game_pid) == game_pid:
                        os.killpg(game_pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            status = 124
        log.write(now() + " exit_status=" + str(status) + "\n")
    if run_dir.exists():
        with (run_dir / "console.log").open("a", encoding="utf-8") as out:
            out.write(supervisor_log.read_text(encoding="utf-8"))
        run_json = run_dir / "run.json"
        if run_json.is_file():
            run = json.loads(run_json.read_text(encoding="utf-8"))
            if status != 0 and run.get("status") in ("starting", "running"):
                run["status"] = "timed_out" if status == 124 else "failed"
                run.setdefault("errors", []).append({"wall_utc": now(), "error": "supervisor terminated child", "exit_status": status})
                run["exit_status"] = status
                atomic_json(run_json, run)
        with (run_dir / "commands.log").open("a", encoding="utf-8") as out:
            out.write(json.dumps({"wall_utc": now(), "command": command, "supervisor_exit_status": status}) + "\n")
    print(json.dumps({"run_id": args.run_id, "run_dir": str(run_dir),
                      "exit_status": status, "supervisor_log": str(supervisor_log)}), flush=True)
    return status


if __name__ == "__main__":
    sys.exit(main())
