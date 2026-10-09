# Sources checked 2026-10-08

Tags: **documented**, **source-inspected**, **inferred**, **blocked**, **not tested**. Nothing is demonstrated by a simulator run. Exact dated upstream artifact hashes and local retention paths are in the preparation result `source-manifest.json`; the installed ISO revision remains separate.

| Source | Location / finding |
|---|---|
| [Official install](https://rflysim.com/doc/en/1.Start/install.html) | Core installation steps: Windows mounted ISO, fast OnekeyScript.exe without MATLAB; install claims are documentation, not local execution. |
| [CopterSim](https://rflysim.com/doc/en/3.Soft/coptersim.html) | Supported Platforms, Version System, CLI, model loading, custom channels: Windows/Linux, default/DLL/SO/XML model; Free SITL/8 vehicles; collision input from visual engine. |
| [WinWSL](https://rflysim.com/doc/en/3.Soft/winwsl.html#wsl1-vs-wsl2) | WSL1 default; WSL2 optional for Docker/GPU; distribution RflySim-20.04. |
| [Microsoft WSL comparison](https://learn.microsoft.com/en-us/windows/wsl/compare-versions) | WSL2 VM architecture; establish virtualization requirements if changing from WSL1. |
| [Visual engine](https://rflysim.com/doc/en/3.Soft/3d-eng.html) | UE scene/sensor/collision component, separate from CopterSim. |
| [Sensor configuration](https://rflysim.com/doc/en/4.DevRef/vis-cfg.html) | Version/mount/Type1 sections: one RGB vehicle1 fits documented Free restrictions (≤3 sensors); world-fixed mode2 and mounted mode0, dimensions/FOV/pose fields; SDK BGR appendix. Actual edition eligibility unexecuted. |
| [Vision capture](https://rflysim.com/doc/en/4.DevRef/pysdk/vision/viscap.html) | Request and capture APIs; concrete pinned camera code below is stronger for reviewed implementation. |
| [UE SDK](https://rflysim.com/doc/en/4.DevRef/pysdk/ue/ue4ctrl.html) | initUE4MsgRec, UE4MsgRecLoop, reqCam, getCamCoptObj: CameraData and collision return documented; installed exact fields and timestamps unresolved. |
| [Protocol](https://rflysim.com/doc/en/4.DevRef/protocol.html) | Main port table: ID1 control20100, estimated20101, truth30101, model control30100, visual20008/9/10, QGC14550, CameraData20006 from UE SDK. Installed configuration wins. |
| [Model import XML](https://rflysim.com/doc/en/4.DevRef/3d-import.html) | MeshPath lookup /Game and /Rfly3DSimPlugin; UE-baked assets + XML, not direct calibrated imagery/Gaussian ingestion. Free import eligibility not established here. |
| [Course 3](https://rflysim.com/doc/en/3/CoreExp.html) | Free-marked teaching examples are not proof of arbitrary map/loader availability in current binary. |
| [Download form](https://rflysim.com/download.html), [language content](https://rflysim.com/js/langData.js?v=20260715_course) lines 519–522 | Installer filename v5.01-20260831, email delivery; no form submitted or ISO obtained. |
| [Official vision course](https://rflysim.com/doc/en/RflySimAPIs/8.RflySimVision/PPT.pdf) slide28 | Windows simulator with shared-memory relay for Free and direct UDP for Full; Linux image consumers do not establish Linux renderer release. |
| [FAQ](https://rflysim.com/doc/en/3/FAQ.html) | Full install 80–100 GB, 300 GB free recommendation; provisional capacity basis. |
| [Pinned camera source](https://github.com/RflySim/RflySimVision/blob/49d60c0907e67cef9c768ac28d89f9c3232f07a7/sensor_pkg/VisionCaptureApi.py#L1340) | lines 612–700 update, 702–851 request, 1340–1455 mmap/time fallback, 1672–1750 thread startup, 1779 jsonLoad. `stopRun` not defined in inspected file. Not asserted installed. |
| [Pinned startup](https://github.com/RflySim/RflyArena/blob/c43421ed5ccc46d4d049d94ac3af8ebbe8b80137/windows/rflysim/SITLRun.bat#L1) | Elevation, custom FX150 model, WSL/PX4 compilation and broad taskkill; evidence only. Exact reviewed lines in runner-review. |
| [Pinned RL interface](https://github.com/RflySim/RflyArena/blob/c43421ed5ccc46d4d049d94ac3af8ebbe8b80137/src/rl_control/scripts/control_rl_node.py#L485) | `_build_obs` lines485–531 is25D state/error/reference input; `_publish_action`536 onward throttle + body rates. Tree contains weights; no RGB/navigation/racing adapter established. |
| [CopterSim HEAD](https://github.com/RflySim/CopterSim/commit/0d14487f8dc3086ad29387ed40e068e301905343), [RflyExpCode HEAD](https://github.com/RflySim/RflyExpCode/commit/7dbec4d8796d6e23ee86c523e4ba5712203b1519) | Rechecked gh commits API; model/examples public, not complete rebuildable visual stack. Root licenses not identified. |

Repository context is from current GitHub main `2cd4f7145486854f9c84a4ae2f6aedf197e963d4`; `docs/r4r-audit-context.md` original context commit `7fd458f9b431b47a9dc909599c98cacea2eb99bb`. Source claims about the internal R4R PDF are inherited from that briefing, not a newly supplied dataset. Local GitHub pull/push capability was checked with gh API permissions; no remote host access tested. No orchestration installed; First Mate absent from prior inspected executable/app paths.
