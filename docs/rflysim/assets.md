> **10 October 2026 update:** [Current execution readiness](current-execution.md) supersedes the historical host/installer/access-permission assumptions below. Execution is authorized on the selected AirGPU host; guest access and complete installer remain blocked. Numerical pending tests are preserved.

# Asset and access inventory

| Input | Source / exact revision | Known size / retention / blocker |
|---|---|---|
| Installer | official download page / language content names `RflySimToolchain-v5.01-20260831.iso` | ISO bytes/SHA/URL/EULA missing; contact form not submitted. Retain durable ISO or tested stable retrievable URL/hash, not solely an expiring email link. |
| Expanded toolchain | official FAQ guidance | 80–100 GB documented full install; selected component/WSL/cache sizes unmeasured. 500 GB total /300 GB free remains provisional. |
| CopterSim source | `0d14487f8dc3086ad29387ed40e068e301905343` | Public Simulink model; not installed binary revision or visual toolchain. Root tree has no LICENSE. Source terms unresolved. |
| RflyExpCode | `7dbec4d8796d6e23ee86c523e4ba5712203b1519` | Instructional files; public root license not identified. Some design exercises incomplete/teacher access; not needed for stock run. |
| Public camera source | RflySimVision `49d60c0907e67cef9c768ac28d89f9c3232f07a7`, `sensor_pkg/VisionCaptureApi.py` | 90,339 bytes retrieved/hashed locally; installed equivalence unknown; no root license asserted. Retained ignored source evidence, not redistributed as task code. |
| Startup/controller source | RflyArena `c43421ed5ccc46d4d049d94ac3af8ebbe8b80137` | Startup 5,695 bytes; RL node 33,066 bytes; repo MIT with nested package licenses. Not used as stock launcher/model. |
| Released policy candidate | RflyArena `src/rl_control/model/exported/policy.onnx` | Tree reports 424,701 bytes; not downloaded/executed. State-feedback controller; no compatible R4R visual policy/task/adapter established. |
| Stock scene/model/PX4/config | supplied by selected ISO | Installed names/bytes/hashes/license/build/params unresolved. Need inventory before capture. |
| AirLab photos/poses/calibration | not supplied | Missing imagery, metric origin/scale, camera calibration and train/test split. |
| Held-out horizontal/vertical views | not supplied | Fidelity and altitude extrapolation blocked. |
| Reconstruction/Gaussian assets | not supplied | No scene training or reconstruction permitted; import path eligibility unresolved. |
| Downstream model/thresholds | not supplied | No dataset/checkpoint or lab fidelity criterion fabricated. |

Budget uncompressed RGB at 640×480×3×10 Hz = 9,216,000 bytes/s. Two 21 s A sequences + 30 s rate test + at most 75 s B capture = 147 s, about 1.35 GB raw RGB before metadata/warmup/duplicates; PNG compression varies. Allocate a provisional 5 GB capture/transfer buffer only after measuring the installed scene and receiver; logs/source media/deck are separate. Inventory local free space and destination space. Dependency/data retention must preserve the scientific inputs actually used, configs, patches, firmware parameters and camera transform. Large media in ignored artifacts, small index/deck/PDF in Git. No live full-instance price verified.
