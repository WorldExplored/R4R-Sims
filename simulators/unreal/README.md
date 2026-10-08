# Unreal Testing

Simulator-specific authored scripts, configurations and setup instructions belong here. No simulator, engine, dataset, checkpoint or runner is installed by this folder scaffold.

Read [the execution plan and complete Codex prompt](../../docs/unreal/execution-prompt.md) before implementation. The intended local checkout is `~/Downloads/AL/R4R-Sims/`; the intended remote checkout is `~/R4R-Sims/` on Ubuntu. Use `results/unreal/<run-id>/` for small records and ignored `artifacts/unreal/<run-id>/` for large captures. Download large reproducible dependencies into ignored `third_party/unreal/` remotely when local copies are unnecessary.

Selected hardware candidate: A4500 x1, 20 GB VRAM, user-supplied displayed price $0.28/hour. Verify actual host specifications, full price and hardware Vulkan rendering before use. Never treat a CUDA check as renderer validation.
