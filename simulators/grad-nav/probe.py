"""Direct component diagnostics. This never constructs a learned policy or trainer."""
import argparse
import ast
import hashlib
import importlib.util
import json
import os
import time
from pathlib import Path


def load_functions(path, names, namespace):
    tree = ast.parse(path.read_text())
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    if {n.name for n in nodes} != set(names):
        raise RuntimeError("requested upstream definitions missing")
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["baseline-none", "force", "smoke", "recovery", "conversion"])
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    import torch
    import numpy as np
    torch.manual_seed(0)
    torch.set_num_threads(1)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    source = args.upstream / "envs/assets/quadrotor_dynamics_advanced.py"
    spec = importlib.util.spec_from_file_location("audit_quadrotor", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if args.mode == "conversion":
        ns = load_functions(args.upstream / "utils/gs_local.py",
            ["quaternion_to_rotation_matrix", "pose2nerf_transform"], {"torch": torch})
        pose_fn = ns["pose2nerf_transform"]
        quat_fn = ns["quaternion_to_rotation_matrix"]
        identity = torch.tensor([[0., 0., 0., 1.]], device=device)
        yaw90 = torch.tensor([[0., 0., 2**-0.5, 2**-0.5]], device=device)
        p0 = torch.zeros((1, 3), device=device)
        p1 = torch.tensor([[1., 2., 3.]], device=device)
        t0 = pose_fn(p0, identity, device)
        t1 = pose_fn(p1, identity, device)
        expected_yaw = torch.tensor([[[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]]], device=device)
        assert torch.allclose(quat_fn(identity), torch.eye(3, device=device)[None], atol=1e-6)
        assert torch.allclose(quat_fn(yaw90), expected_yaw, atol=1e-6)
        assert torch.allclose(t1[0, :3, 3] - t0[0, :3, 3], torch.tensor([1., -2., -3.], device=device), atol=1e-6)
        # Environment flips Y/Z before the helper. Combined translation has positive derivative.
        t_env = pose_fn(p1 * torch.tensor([1., -1., -1.], device=device), identity, device)
        assert torch.allclose(t_env[0, :3, 3] - t0[0, :3, 3], p1[0], atol=1e-6)
        camera_ns = {"identity_body_camera_c2w": t0[0].cpu().tolist(),
            "yaw90_body_camera_c2w": pose_fn(p0, yaw90, device)[0].cpu().tolist(),
            "quaternion_order_actual": "xyzw", "dynamics_order": "wxyz",
            "origin_offset_body_before_flip": [-6., 0., 0.],
            "mount_orthonormal_residual": float(torch.linalg.norm(t0[0,:3,:3].T @ t0[0,:3,:3] - torch.eye(3,device=device)).item()),
            "normalization": "helper render path applies no dataparser transform or scale",
            "scope": "algebraic checks only; native scene alignment and scale blocked"}
        collision = load_functions(args.upstream / "utils/point_cloud_util.py", ["ObstacleDistanceCalculator"], {"torch": torch})
        cls = collision["ObstacleDistanceCalculator"]
        obj = cls.__new__(cls)
        obj.device, obj.fov_degrees = device, 90.
        results = []
        for label, points in [("rear_point_only", [[-0.01,0.,0.]]), ("front_point", [[0.1,0.,0.]]), ("coincident_point", [[0.,0.,0.]])]:
            obj.points = torch.tensor(points, device=device)
            value = obj.compute_nearest_distances(p0, torch.tensor([[1.,0.,0.,0.]],device=device)).item()
            results.append({"diagnostic":label, "nearest_distance": value if np.isfinite(value) else None,
                            "nonfinite":not np.isfinite(value), "synthetic_geometry":True})
        camera_ns["obstacle_diagnostics"] = results
        (out / "conversion.json").write_text(json.dumps(camera_ns, indent=2)+"\n")
        print(json.dumps(camera_ns))
        return
    config = {"mode":args.mode, "seed":0, "mass_kg":1., "max_total_thrust_N":24.,
        "inertia_kg_m2":[0.01,0.012,0.025], "inner_hz":200., "outer_dt_s":0.05,
        "inner_substeps":10, "quaternion_order":"wxyz", "world_axes":"x,y,z up in dynamics",
        "noise_std":None if args.mode=="baseline-none" else 0., "policy_weights":"none",
        "height_target_m":1.25, "gains_kp_kd":[2.,0.8], "body_rates_rad_s":[0.,0.,0.],
        "ticks":100 if args.mode=="recovery" else 20,
        "perturbation_m":-0.25 if args.mode!="force" else 0.,
        "diagnostic_band_m":0.02, "band_is_lab_acceptance_threshold":False,
        "termination":"fixed ticks, or error on nonfinite state; no native scene contacts",
        "bypasses":["DroneLongTrajEnv", "GS", "CNN", "VAE", "actor", "normalization", "native action delay/filter"],
        "interface":"SI desired body rates and normalized total thrust directly to run_simulation"}
    (out/"config.json").write_text(json.dumps(config,indent=2)+"\n")
    cls = module.QuadrotorSimulator
    def simulator(noise):
        return cls(mass=torch.tensor([1.],device=device),
            inertia=torch.diag(torch.tensor(config["inertia_kg_m2"],device=device))[None],
            link_length=0.15, Kp=torch.tensor([[1.,1.2,2.5]],device=device),
            Kd=torch.tensor([[0.001,0.001,0.002]],device=device), freq=200.,
            max_thrust=torch.tensor([24.],device=device),total_time=0.05,
            rotor_noise_std=noise,br_noise_std=noise)
    # Warmup uses a disposable simulator and cannot alter the measured starting state.
    if args.mode!="baseline-none":
        warm=simulator(0.)
        for _ in range(5):
            warm.run_simulation(torch.tensor([[0.,0.,1.25]],device=device),torch.zeros((1,3),device=device),
                torch.tensor([[1.,0.,0.,0.]],device=device),torch.zeros((1,3),device=device),
                (torch.zeros((1,3),device=device),torch.tensor([9.81/24.],device=device)))
        if device.type=="cuda": torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
    sim=simulator(config["noise_std"])
    z0=1.25+config["perturbation_m"]
    pos=torch.tensor([[0.,0.,z0]],device=device);vel=torch.zeros((1,3),device=device)
    quat=torch.tensor([[1.,0.,0.,0.]],device=device);omega=torch.zeros((1,3),device=device)
    (out/"reference_route.jsonl").write_text(json.dumps({"target_height_m":1.25,"ticks":config["ticks"],"dt_s":0.05})+"\n")
    records=[]; timing=[]; saturations=0
    wall0=time.perf_counter()
    with (out/"state.jsonl").open("w") as states,(out/"actions.jsonl").open("w") as actions:
        states.write(json.dumps({"step":0,"sim_time_s":0.,"position_m":pos[0].cpu().tolist(),"velocity_m_s":vel[0].cpu().tolist(),"quaternion_wxyz":quat[0].cpu().tolist()})+"\n")
        for i in range(config["ticks"]):
            z=float(pos[0,2]); vz=float(vel[0,2])
            requested_N=9.81 if args.mode=="force" else 9.81+2.*(1.25-z)-0.8*vz
            requested=requested_N/24.;applied=max(0.,min(1.,requested)); saturations+=int(applied!=requested)
            actions.write(json.dumps({"step":i,"sim_time_s":i*0.05,"wall_since_start_s":time.perf_counter()-wall0,
                "observation_z_vz":[z,vz],"requested_body_rates_rad_s":[0.,0.,0.],"applied_body_rates_rad_s":[0.,0.,0.],
                "requested_normalized_thrust":requested,"applied_normalized_thrust":applied,"applied_total_thrust_N":applied*24.})+"\n");actions.flush()
            if device.type=="cuda": torch.cuda.synchronize()
            tick=time.perf_counter()
            pos,vel,omega,quat,acc,alpha=sim.run_simulation(pos,vel,quat,omega,
                (torch.zeros((1,3),device=device),torch.tensor([applied],device=device)))
            if device.type=="cuda": torch.cuda.synchronize()
            latency=time.perf_counter()-tick;timing.append(latency)
            if not all(torch.isfinite(x).all().item() for x in (pos,vel,omega,quat,acc,alpha)): raise ValueError("nonfinite state")
            row={"step":i+1,"sim_time_s":(i+1)*0.05,"wall_since_start_s":time.perf_counter()-wall0,
                "position_m":pos[0].cpu().tolist(),"velocity_m_s":vel[0].cpu().tolist(),
                "quaternion_wxyz":quat[0].cpu().tolist(),"angular_velocity_rad_s":omega[0].cpu().tolist(),"dynamics_wall_s":latency}
            states.write(json.dumps(row)+"\n");states.flush(); records.append(row)
    errors=[1.25-r["position_m"][2] for r in records]
    in_band=[r["sim_time_s"] for r,e in zip(records,errors) if abs(e)<=0.02]
    metrics={"sim_duration_s":config["ticks"]*0.05,"measured_wall_s":time.perf_counter()-wall0,
        "initial_z_m":z0,"final_z_m":records[-1]["position_m"][2],"final_error_m":errors[-1],
        "drift_m":records[-1]["position_m"][2]-z0,"rmse_height_error_m":float(np.sqrt(np.mean(np.square(errors)))),
        "overshoot_above_setpoint_m":max(0.,max(r["position_m"][2] for r in records)-1.25),
        "first_entry_0.02m_band_s":in_band[0] if in_band else None,"saturated_ticks":saturations,
        "dynamics_median_s":float(np.median(timing)),"dynamics_p95_s":float(np.percentile(timing,95)),
        "peak_torch_allocated_bytes":torch.cuda.max_memory_allocated() if device.type=="cuda" else None,
        "render_throughput":None,"policy_latency":None,"video_playback_fps":None,"sampling_dt_sim_s":0.05,
        "missing_samples":0,"timing_scope":"five disposable warmup steps, synchronized dynamics only, transfers/logging excluded",
        "force_balance_scope":"no displaced-altitude recovery claim" if args.mode=="force" else "adapter height feedback, no native learned controller"}
    (out/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")
    print(json.dumps(metrics))


if __name__=="__main__": main()
