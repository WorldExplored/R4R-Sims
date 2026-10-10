> **10 October 2026 update:** [Current execution readiness](current-execution.md) supersedes the historical host/installer/access-permission assumptions below. Execution is authorized on the selected AirGPU host; guest access and complete installer remain blocked. Numerical pending tests are preserved.

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


## Bounded follow-up sources — October 8 local / October 9 UTC

Retained official artifact bytes/hashes in [new source manifest](../../results/rflysim/local-20261009T020939Z/source-manifest.json). [Release asset inventory](../../results/rflysim/local-20261009T020939Z/release-assets.json) records checked API output: CopterSim/RflySimVision/doc/Docs no releases; RflyExpCode v1.0 example ZIP 19,964,088 bytes, other release tags no assets. This limited artifact search does not prove no private/email-distributed Linux package exists.

[Docker running-location table](https://rflysim.com/doc/en/3.Soft/docker.html#integration-with-rflysim-simulation) explicitly locates CopterSim/RflySim3D on native Windows; [Free resource index](https://rflysim.com/doc/en/4.DevRef/3d-res.html#i-3d-models) limits Free to UE4; [sensor document](https://rflysim.com/doc/en/4.DevRef/vis-cfg.html#version-restriction-overview) warns binary licensing wins over inconsistent documentation. [Docs README at 608bf7f47e4f61bc38b75b7353a7e469c75e4b95](https://github.com/RflySim/Docs/blob/608bf7f47e4f61bc38b75b7353a7e469c75e4b95/README.md#L20), lines20–24, describes enterprise Linux cloud deployment (historical, not current license). Download language snapshot lines420–427/522 contains form fields and current filename; line650 contains old OneDrive folder/version2.54 links, both inaccessible through web lookup. Access failure remains a blocker. No form submitted or emails sent; no installer downloaded. See `readiness.md` for the complete-path conclusion and exact acquisition action.
