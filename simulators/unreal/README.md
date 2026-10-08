# Unreal testing

`audit.py` runs AirSim's packaged Linux Blocks camera replay (A) and scripted multirotor square (B); `bounded.py` applies an independent 190 s watchdog to one owned run. `analyze.py` validates frames/depth and plots measured evidence. `manifest.py create` hashes completed **source** run files; after `rsync`, `manifest.py verify` compares the local copy to that source manifest. Keep unique `ue-...` IDs and preserve failures.

The current user-supplied host is Ubuntu 22.04 with RTX A5000 24 GB and NVIDIA Vulkan driver 580.178.04. Exact commands, asset hashes, measured A/B results, known landing failure and the UE5 Gaussian-splat gate are in [the handoff](../../docs/unreal/handoff.md). Code/configuration belongs here, small result summaries in `results/unreal/`, and ignored raw captures and dependencies in `artifacts/unreal/` and `third_party/unreal/`. No weights or scene training are part of this runner.
