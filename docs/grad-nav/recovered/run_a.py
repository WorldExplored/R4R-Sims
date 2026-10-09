"""Five known camera poses through the authors' Splatfacto loader. GPU host only."""
import argparse
import json
import sys
import time
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    out = args.out.resolve()
    (out / "frames").mkdir(parents=True, exist_ok=True)
    upstream = Path(__import__("os").environ["AUDIT_UPSTREAM"]).resolve()
    sys.path.insert(0, str(upstream))
    import numpy as np
    import torch
    from PIL import Image
    from utils.gs_local import get_gs

    torch.manual_seed(0)
    gs = get_gs("gate_mid", None, 0.4)
    camera = gs.camera_out
    base = camera.camera_to_worlds.clone()
    with torch.inference_mode():
        for _ in range(5):
            gs.pipeline.model.get_outputs_for_camera(camera, obb_box=None)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
    # Offsets are in Nerfstudio transformed scene coordinates, not claimed meters.
    offsets = [(0, 0, 0), (0.1, 0, 0), (-0.1, 0, 0), (0, 0.1, 0), (0, -0.1, 0)]
    route = out / "reference_route.jsonl"
    poses = out / "camera_poses.jsonl"
    metrics = []
    with route.open("w") as rf, poses.open("w") as pf, torch.inference_mode():
        for i, xyz in enumerate(offsets):
            pose = base.clone()
            pose[0, :, 3] += torch.tensor(xyz, device=pose.device, dtype=pose.dtype)
            row = {"index": i, "offset_scene_units": xyz,
                   "camera_to_world_3x4": pose[0].detach().cpu().tolist(),
                   "frame": "Nerfstudio transformed", "scale_m_per_unit": None}
            rf.write(json.dumps(row) + "\n")
            camera.camera_to_worlds = pose
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            start = time.perf_counter()
            output = gs.pipeline.model.get_outputs_for_camera(camera, obb_box=None)
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            elapsed = time.perf_counter() - start
            rgb = output["rgb"].detach().cpu().numpy()
            depth = output["depth"].detach().cpu().numpy()
            if not np.isfinite(rgb).all() or not np.isfinite(depth).all():
                raise ValueError(f"nonfinite render at pose {i}")
            Image.fromarray((np.clip(rgb, 0, 1) * 255).astype("uint8")).save(out / "frames" / f"rgb_{i:03d}.png")
            np.save(out / "frames" / f"depth_{i:03d}.npy", depth)
            pf.write(json.dumps({**row, "rgb_shape": list(rgb.shape), "depth_shape": list(depth.shape)}) + "\n")
            metrics.append({"index": i, "render_wall_s": elapsed, "warmup": False})
    (out / "state.jsonl").write_text('{"applicable":false,"reason":"known camera route only"}\n')
    (out / "actions.jsonl").write_text('{"applicable":false,"reason":"known camera route only"}\n')
    (out / "metrics.json").write_text(json.dumps({"render": metrics, "playback_fps": None,
        "note": "five warmup renders at reference pose; five synchronized timed renders; small sample"}, indent=2) + "\n")
    (out / "run_detail.json").write_text(json.dumps({"level": "A", "map": "gate_mid", "policy": "none",
        "seed": 0, "camera_fx_fy_cx_cy_original": [462.956, 463.002, 323.076, 181.184],
        "resolution_scale": 0.4, "scene_scale_m_per_unit": None,
        "missing": ["actual vehicle trajectory", "control actions", "metric scene scale"]}, indent=2) + "\n")


if __name__ == "__main__":
    main()
