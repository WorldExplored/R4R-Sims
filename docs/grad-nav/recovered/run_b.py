"""Short proprioceptive closed-loop dynamics smoke test; no learned policy."""
import argparse
import json
import os
import sys
import time
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(Path(os.environ["AUDIT_UPSTREAM"]).resolve()))
    import torch
    from envs.assets.quadrotor_dynamics_advanced import QuadrotorSimulator

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(0)
    mass = torch.tensor([1.0], device=device)
    max_thrust = torch.tensor([24.0], device=device)
    sim = QuadrotorSimulator(mass=mass, inertia=torch.diag(torch.tensor([0.01, 0.012, 0.025], device=device)).unsqueeze(0),
        link_length=0.15, Kp=torch.tensor([[1.0, 1.2, 2.5]], device=device),
        Kd=torch.tensor([[0.001, 0.001, 0.002]], device=device), freq=200.0,
        max_thrust=max_thrust, total_time=0.05, rotor_noise_std=None, br_noise_std=None)
    pos = torch.tensor([[0.0, 0.0, 1.0]], device=device)
    vel = torch.zeros((1, 3), device=device)
    quat = torch.tensor([[1.0, 0.0, 0.0, 0.0]], device=device)  # dynamics uses w,x,y,z
    omega = torch.zeros((1, 3), device=device)
    (out / "reference_route.jsonl").write_text('{"target_height_m":1.25,"scene":"none"}\n')
    (out / "camera_poses.jsonl").write_text('{"applicable":false,"reason":"dynamics-only smoke"}\n')
    with (out / "state.jsonl").open("w") as states, (out / "actions.jsonl").open("w") as actions:
        for step in range(20):
            # State/velocity are the proprioceptive observation in this smoke test.
            observed_z = float(pos[0, 2].item())
            observed_vz = float(vel[0, 2].item())
            desired_force = 9.81 + 2.0 * (1.25 - observed_z) - 0.8 * observed_vz
            thrust = torch.tensor([max(0.0, min(1.0, desired_force / 24.0))], device=device)
            body_rates = torch.zeros((1, 3), device=device)
            actions.write(json.dumps({"step": step, "sim_time_s": step * 0.05,
                "policy": "none; scripted height feedback", "body_rates_rad_s": [0, 0, 0],
                "normalized_thrust": float(thrust.item()), "observed_z_m": observed_z,
                "observed_vz_m_s": observed_vz}) + "\n")
            start = time.perf_counter()
            pos, vel, omega, quat, lin_acc, ang_acc = sim.run_simulation(pos, vel, quat, omega, (body_rates, thrust))
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            wall = time.perf_counter() - start
            if not all(torch.isfinite(x).all().item() for x in (pos, vel, omega, quat, lin_acc, ang_acc)):
                raise ValueError(f"nonfinite dynamics state at {step}")
            states.write(json.dumps({"step": step + 1, "sim_time_s": (step + 1) * 0.05,
                "position_m": pos[0].detach().cpu().tolist(), "velocity_m_s": vel[0].detach().cpu().tolist(),
                "quaternion_wxyz": quat[0].detach().cpu().tolist(), "angular_velocity_rad_s": omega[0].detach().cpu().tolist(),
                "wall_step_s": wall}) + "\n")
    (out / "run_detail.json").write_text(json.dumps({"level": "B dynamics-only", "scene": "none",
        "policy": "none; scripted height feedback", "seed": 0, "ticks": 20, "sim_duration_s": 1.0,
        "missing": ["Gaussian camera", "visual observation", "collision", "task outcome"]}, indent=2) + "\n")


if __name__ == "__main__":
    main()
