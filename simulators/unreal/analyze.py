#!/usr/bin/env python3
"""Validate a completed Blocks run and make measured evidence figures."""
import argparse
import json
from pathlib import Path
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw


def rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []


def median(values):
    return float(statistics.median(values)) if values else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    cameras = rows(run_dir / "camera.jsonl")
    states = rows(run_dir / "state.jsonl")
    actions = rows(run_dir / "actions.jsonl")
    gpu = rows(run_dir / "gpu.jsonl")
    if run["status"] != "completed" or not cameras:
        raise SystemExit("Analysis needs a completed run with camera records")
    figures = run_dir / "figures"
    figures.mkdir(exist_ok=True)
    rgb_arrays, depth_arrays, frame_stats = [], [], []
    for row in cameras:
        rgb = Path(row["rgb"])
        depth = Path(row["depth"])
        # Run paths are remote absolutes; transferred runs use the same basenames.
        rgb = run_dir / "frames" / rgb.name
        depth = run_dir / "depth" / depth.name
        with Image.open(rgb) as opened:
            opened.load()
            if opened.size != (640, 480):
                raise ValueError(f"Unexpected RGB dimensions: {rgb}")
            arr = np.asarray(opened.convert("RGB"))
        z = np.load(depth, allow_pickle=False)
        if z.shape != (480, 640):
            raise ValueError(f"Unexpected depth dimensions: {depth}")
        positive = z[np.isfinite(z) & (z > 0)]
        frame_stats.append({
            "index": row["index"], "rgb": str(rgb), "depth": str(depth),
            "rgb_mean": float(arr.mean()), "rgb_std": float(arr.std()),
            "positive_finite_depth_fraction": float(positive.size / z.size),
            "depth_median_m": float(np.median(positive)) if positive.size else None,
            "depth_p05_m": float(np.percentile(positive, 5)) if positive.size else None,
            "depth_p95_m": float(np.percentile(positive, 95)) if positive.size else None,
        })
        rgb_arrays.append(arr)
        depth_arrays.append(z)
    differences = [float(np.abs(a.astype(np.int16) - b.astype(np.int16)).mean())
                   for a, b in zip(rgb_arrays, rgb_arrays[1:])]
    contact = Image.new("RGB", (4 * 320, 2 * 264), "white")
    draw = ImageDraw.Draw(contact)
    for n, arr in enumerate(rgb_arrays[:8]):
        tile = Image.fromarray(arr).resize((320, 240))
        x, y = (n % 4) * 320, (n // 4) * 264
        contact.paste(tile, (x, y + 24))
        draw.text((x + 8, y + 5), f"frame {cameras[n]['index']}", fill="black")
    contact.save(figures / "rgb-contact.png")
    fig, axes = plt.subplots(2, 4, figsize=(16, 7), constrained_layout=True)
    for n, ax in enumerate(axes.flat):
        if n < len(depth_arrays):
            z = depth_arrays[n]
            bounded = np.where(np.isfinite(z) & (z > 0), z, np.nan)
            ax.imshow(bounded, cmap="viridis", vmin=0, vmax=10)
            ax.set_title(f"frame {cameras[n]['index']} · DepthPlanar m")
        ax.axis("off")
    fig.savefig(figures / "depth-grid.png", dpi=140)
    plt.close(fig)
    actual = [r.get("actual_vehicle_pose_ned", {}).get("position_ned_m")
              for r in rows(run_dir / "vehicle_trajectory.jsonl")]
    actual = [p for p in actual if p]
    route = json.loads((run_dir / "reference_route.json").read_text(encoding="utf-8"))
    targets = route.get("poses_xyz") or route.get("waypoints_xyz")
    fig, ax = plt.subplots(figsize=(7, 6), constrained_layout=True)
    if targets:
        ax.plot([x[0] for x in targets], [x[1] for x in targets],
                "o--", label="reference", color="#d95f02")
    if actual:
        ax.plot([p["x"] for p in actual], [p["y"] for p in actual],
                ".-", label="actual rig/vehicle", color="#1b9e77")
    ax.set(xlabel="NED x (m)", ylabel="NED y (m)", title="Reference and achieved XY path")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, alpha=.3)
    ax.legend()
    fig.savefig(figures / "trajectory-xy.png", dpi=170)
    plt.close(fig)
    velocity_commands = [r for r in actions if r.get("type") == "moveByVelocityAsync"]
    action_times = [r["wall_elapsed_s"] for r in velocity_commands]
    intervals = [b-a for a, b in zip(action_times, action_times[1:]) if b > a]
    capture_times = [r["wall_elapsed_s"] for r in cameras]
    capture_intervals = [b-a for a, b in zip(capture_times, capture_times[1:]) if b > a]
    vram = []
    for r in gpu:
        output = r.get("stdout", "")
        parts = [x.strip() for x in output.split(",")]
        if r.get("exit_code") == 0 and len(parts) >= 4:
            try:
                vram.append(float(parts[2]))
            except ValueError:
                pass
    errors_to_waypoint = []
    if run["mode"] == "b":
        for target in targets:
            errors_to_waypoint.append(min(
                (sum((p[k]-target[i])**2 for i, k in enumerate(("x","y","z"))))**.5
                for p in actual) if actual else None)
    summary = {
        "run_id": run["run_id"], "status": run["status"],
        "frames_checked": len(cameras), "states": len(states), "velocity_commands": len(velocity_commands),
        "rgb_adjacent_mean_abs_difference": differences,
        "frame_stats": frame_stats,
        "capture_rpc_wall_s_median": median([r["capture_rpc_wall_s"] for r in cameras]),
        "capture_interval_wall_s_median": median(capture_intervals),
        "command_interval_wall_s_median": median(intervals),
        "command_rate_hz_from_median_interval": 1 / median(intervals) if intervals else None,
        "command_rate_hz_over_action_span": (len(action_times)-1) / (action_times[-1]-action_times[0]) if len(action_times)>1 else None,
        "command_interval_wall_s_p95": float(np.percentile(intervals, 95)) if intervals else None,
        "camera_capture_rate_hz_over_span": (len(capture_times)-1)/(capture_times[-1]-capture_times[0]) if len(capture_times)>1 else None,
        "simulation_elapsed_s_first_to_last_state": (states[-1]["state_timestamp_raw"] - states[0]["state_timestamp_raw"]) / 1e9 if len(states)>1 and "state_timestamp_raw" in states[-1] and "state_timestamp_raw" in states[0] else None,
        "peak_gpu_memory_used_mib_samples": max(vram) if vram else None,
        "waypoint_nearest_recorded_state_error_m": errors_to_waypoint,
        "new_collision_recorded": any(
            s.get("collision") and s.get("collision_timestamp_raw", 0) >
            json.loads((run_dir / "collision_baseline.json").read_text())["time_stamp_raw"]
            for s in states) if (run_dir / "collision_baseline.json").exists() else None,
        "timing_note": "RPC and sampling intervals are not renderer FPS; no synchronized GPU render timing",
    }
    (run_dir / "analysis.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: summary[k] for k in ("run_id", "frames_checked", "states",
          "velocity_commands", "capture_rpc_wall_s_median", "capture_interval_wall_s_median",
          "command_rate_hz_from_median_interval", "peak_gpu_memory_used_mib_samples",
          "waypoint_nearest_recorded_state_error_m", "new_collision_recorded")}, indent=2))


if __name__ == "__main__":
    main()
