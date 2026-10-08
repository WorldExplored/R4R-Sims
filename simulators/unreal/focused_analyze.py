#!/usr/bin/env python3
"""Summarize source-manifested focused validation without changing raw evidence."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import manifest

IDS=["ue-20261008T232215Z-yaw-6b9a9962", "ue-20261008T232324Z-land-isolated-a3227c9a",
     "ue-20261008T232549Z-land-settled-04b41479", "ue-20261008T232723Z-land-observed-c1f84706",
     "ue-20261008T232449Z-s-light-1f298556", "ue-20261008T232833Z-s-light-573e44a0"]

def jsonl(path): return [json.loads(line) for line in path.read_text().splitlines()]

def angle_error(a,b):
    qa=np.array([a[k] for k in ("w","x","y","z")]);qb=np.array([b[k] for k in ("w","x","y","z")])
    dot=abs(float(np.dot(qa/np.linalg.norm(qa),qb/np.linalg.norm(qb))))
    return math.degrees(2*math.acos(min(1,dot)))

def main():
    p=argparse.ArgumentParser();p.add_argument("--artifacts-root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--local-artifacts-root",type=Path);args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    report={"audit_date":"2026-10-08","session_start_utc":"2026-10-08T23:20:00Z",
        "session_deadline_utc":"2026-10-08T23:50:00Z","runs":[],"preservation":{"source_manifests_verified":True}}
    for rid in IDS:
        run=args.artifacts_root/rid;manifest.verify(run)
        m=json.loads((run/"source-manifest.json").read_text())
        row={"run_id":rid,"local_path":str((args.local_artifacts_root/rid).resolve()) if args.local_artifacts_root else str(run.resolve()),"source_manifest_sha256":manifest.digest(run/"source-manifest.json"),
            "verified_files":len(m["files"]),"verified_bytes":sum(x["bytes"] for x in m["files"])}
        meta=json.loads((run/"run.json").read_text());row["raw_runner_status"]=meta.get("status",meta.get("render_exit_status"))
        if "yaw" in rid:
            cameras=jsonl(run/"camera.jsonl")
            row["audited_status"]="demonstrated_yaw_and_visually_confirmed"
            row["max_requested_rgb_orientation_error_deg"]=max(angle_error(c["requested_pose_ned"]["orientation_xyzw_ned"],c["rgb_capture_pose_ned"]["orientation_wxyz"]) for c in cameras)
            row["max_requested_rgb_position_error_m"]=max(math.sqrt(sum((c["requested_pose_ned"]["position_ned_m"][k]-c["rgb_capture_pose_ned"]["position_ned_m"][k])**2 for k in ("x","y","z"))) for c in cameras)
            row["rgb_depth_timestamp_difference_ms"]=[(c["depth_timestamp_raw_ns"]-c["rgb_timestamp_raw_ns"])/1e6 for c in cameras]
            row["max_rgb_depth_capture_orientation_error_deg"]=max(angle_error(c["depth_capture_pose_ned"]["orientation_wxyz"],c["rgb_capture_pose_ned"]["orientation_wxyz"]) for c in cameras)
            row["pixel_comparisons"]=json.loads((run/"validation.json").read_text())["pixel_comparisons"]
        elif "land" in rid:
            states=jsonl(run/"descent.jsonl")
            if "isolated" in rid:
                row["audited_status"]="rejected_never_airborne_despite_raw_pass"
            elif "settled" in rid: row["audited_status"]="failed_takeoff_rpc_false_descent_not_run"
            else:
                row["audited_status"]="reproduced_flying_after_ground_contact"
                v=json.loads((run/"validation.json").read_text())
                row["validation"]=v
                descent=[s for s in states if s["phase"]=="landAsync"]
                row["descent_poll_rate_hz_median"]=1/statistics.median(b["wall_elapsed_s"]-a["wall_elapsed_s"] for a,b in zip(descent,descent[1:]))
                row["descent_peak_downward_speed_mps"]=max(s["vertical_velocity_ned_down_mps"] for s in descent)
                row["first_new_floor_contact"]=next(s for s in descent if s["new_collision_after_spawn_baseline"])
                fig,axes=plt.subplots(3,1,figsize=(10,8),sharex=True)
                t=[s["wall_elapsed_s"] for s in states]
                axes[0].plot(t,[np.nan if s["altitude_above_settled_spawn_ground_m"] is None else s["altitude_above_settled_spawn_ground_m"] for s in states]);axes[0].set_ylabel("Height above settled\nspawn ground (m)")
                axes[1].plot(t,[s["vertical_velocity_ned_down_mps"] for s in states]);axes[1].set_ylabel("NED vertical velocity\n+down (m/s)")
                axes[2].step(t,[s["landed_state"] for s in states],where="post");axes[2].set_yticks([0,1],["Landed","Flying"]);axes[2].set_ylabel("Reported state")
                contact=row["first_new_floor_contact"]["wall_elapsed_s"]
                for ax in axes:
                    ax.axvline(contact,color="red",linestyle=":",label="new Ground_6 contact")
                    ax.axvline(v["land_rpc"]["rpc_completion_wall_elapsed_s"],color="black",linestyle="--",label="land RPC true")
                    ax.grid(alpha=.25)
                axes[0].legend(loc="best");axes[-1].set_xlabel("Wall seconds since run start")
                fig.suptitle("Isolated takeoff, hold and landing — LandedState failure reproduced")
                fig.tight_layout();fig.savefig(args.output/"isolated-descent.png",dpi=150);plt.close(fig)
        else:
            d=json.loads((run/"diagnostics.json").read_text());row["diagnostics"]=d;row["decoded_images"]={}
            for name in d["frames"]:
                rgb=np.array(Image.open(run/name))[...,:3]
                row["decoded_images"][name]={"shape":list(rgb.shape),"min":int(rgb.min()),"max":int(rgb.max()),
                    "mean":float(rgb.mean()),"pixel_fraction_any_channel_gt10":float((rgb.max(2)>10).mean()),
                    "pixel_fraction_any_channel_ge250":float((rgb.max(2)>=250).mean())}
            row["audited_status"]="saturated_mesh_control_rejected" if "1f298556" in rid else "finalcolor_mesh_and_dark_splat_frame_exported_fidelity_unvalidated"
        report["runs"].append(row)
    report["preservation"].update(verified_files=sum(r["verified_files"] for r in report["runs"]),
        verified_bytes=sum(r["verified_bytes"] for r in report["runs"]))
    (args.output/"summary.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")

if __name__=="__main__":main()
