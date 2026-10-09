#!/usr/bin/env python3
"""Make small, reproducible flight summaries and empirical media from one run."""
import argparse
import json
import math
import statistics
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def records(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def nearest(states, tick):
    return min(states, key=lambda s: abs(s["wall_monotonic_ns"] - tick))


def position(state):
    p = state["native"]["position"]
    return np.array([p["x"], p["y"], p["z"]], dtype=float)


def make(run_root, result_root):
    result_root.mkdir(parents=True, exist_ok=True)
    states = records(run_root / "actual_vehicle.jsonl")
    actions = records(run_root / "actions.jsonl")
    route = records(run_root / "reference_route.jsonl")
    images = records(run_root / "images.jsonl")
    t0 = states[0]["wall_monotonic_ns"]
    t = np.array([(s["wall_monotonic_ns"] - t0) / 1e9 for s in states])
    xyz = np.array([position(s) for s in states])
    tasks = {}
    for a in actions:
        if a.get("event") == "complete":
            phase = a["phase"]
            s = nearest(states, a["wall_monotonic_ns"])
            target = next((r["ned_m"] for r in route if r["phase"] == phase and "ned_m" in r), None)
            tasks[phase] = {"returned": a["result"], "achieved_ned_m": position(s).tolist(),
                            "requested_ned_m": target,
                            "endpoint_error_m": float(np.linalg.norm(position(s) - target)) if target else None,
                            "state_time_offset_ms": (s["wall_monotonic_ns"] - a["wall_monotonic_ns"]) / 1e6}
    for hover, next_phase in (("hover_1", "horizontal"), ("hover_2", "return")):
        start = next((a["wall_monotonic_ns"] for a in actions if a.get("phase") == hover and a.get("event") == "complete"), None)
        stop = next((a["wall_monotonic_ns"] for a in actions if a.get("phase") == next_phase and a.get("event") == "start"), None)
        if start and stop:
            segment = xyz[(t0 + t * 1e9 >= start) & (t0 + t * 1e9 <= stop)]
            ref = position(nearest(states, start))
            tasks[hover]["hold_max_displacement_m"] = float(np.linalg.norm(segment - ref, axis=1).max()) if len(segment) else None
    for axis, title, component in (("horizontal", "Horizontal X in NED", 0), ("vertical", "Vertical Z in NED", 2)):
        fig, ax = plt.subplots(figsize=(9.6, 4.8))
        ax.plot(t, xyz[:, component], color="#18759b", lw=1.8, label="Achieved vehicle pose")
        target_times = [0.0]
        target_values = [xyz[0, component]]
        for r in route:
            if "ned_m" in r:
                target_times.append((r["wall_monotonic_ns"] - t0) / 1e9)
                target_values.append(r["ned_m"][component])
        target_times.append(t[-1]); target_values.append(target_values[-1])
        ax.step(target_times, target_values, where="post", color="#c55035", lw=1.7, label="Requested waypoint")
        ax.set(xlabel="Wall time since first state (s)", ylabel="NED position (m)", title=title)
        ax.grid(alpha=.2); ax.legend(frameon=False); fig.tight_layout()
        fig.savefig(result_root / f"trajectory_{axis}.png", dpi=170)
        plt.close(fig)
    rgb = sorted((run_root / "rgb").glob("ForwardCamera_*.png"))
    depth = sorted((run_root / "depth_planar").glob("DownCamera_*.npy"))
    if rgb:
        Image.open(rgb[len(rgb)//2]).save(result_root / "rgb_preview.png")
        command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-framerate", "10",
                   "-pattern_type", "glob", "-i", str(run_root / "rgb" / "ForwardCamera_*.png"),
                   "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-c:v", "libx264",
                   "-pix_fmt", "yuv420p", str(result_root / "forward_rgb_10fps.mp4")]
        subprocess.run(command, check=True, timeout=120)
    if depth:
        z = np.load(depth[len(depth)//2]).astype("float32")
        valid = np.isfinite(z) & (z < 65504)
        fig, ax = plt.subplots(figsize=(8, 4.5))
        plot = ax.imshow(np.ma.masked_where(~valid, z), cmap="viridis", vmin=0, vmax=20)
        fig.colorbar(plot, ax=ax, label="Depth Planar (m), 0–20 m preview")
        ax.set_title("DownCamera raw float16 depth; 65504 masked as saturated")
        ax.set_axis_off(); fig.tight_layout()
        fig.savefig(result_root / "depth_preview.png", dpi=150)
        plt.close(fig)
    duration = (states[-1]["wall_monotonic_ns"] - t0) / 1e9
    sim_duration = (states[-1]["native"]["time_stamp"] - states[0]["native"]["time_stamp"]) / 1e9
    summary = {"run_id": run_root.name, "wall_state_span_s": duration, "sim_state_span_s": sim_duration,
               "state_count": len(states), "tasks": tasks,
               "image_counts": {kind: sum(x["image_type"] == k for x in images) for kind, k in (("rgb", 0), ("depth", 1))},
               "rgb_saved_per_wall_s": sum(x["image_type"] == 0 for x in images)/duration,
               "depth_saved_per_wall_s": sum(x["image_type"] == 1 for x in images)/duration,
               "callback_to_save_ms_median": statistics.median(x["callback_to_save_ms"] for x in images),
               "collision_event_count": len(records(run_root / "collisions.jsonl")) if (run_root / "collisions.jsonl").exists() else 0,
               "video_playback_fps": 10, "video_timing": "constant 10 fps from ordered saved ForwardCamera RGB; one padded row for H.264; not native wall/simulator timing"}
    (result_root / "analysis.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("output", type=Path)
    opts = parser.parse_args()
    make(opts.raw, opts.output)
