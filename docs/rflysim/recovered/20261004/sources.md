# Sources and evidence ledger — accessed 2026-10-04

Claims are tagged **D** documented, **I** inferred, **S** statically checked here, **E** locally executed, **M** remotely measured. No M claims exist in phase 1. Documentation HTML line numbers below are the source page's rendered line positions; installed-source line numbers must be captured in phase 2.

| Evidence | URL and precise location | Status / limit |
|---|---|---|
| Architecture: CopterSim model DLL, PX4, UE4/UE5 visual/collision/sensors; Windows vs Ubuntu/WSL | <https://rflysim.com/doc/en/4.DevRef/frame.html> lines 348–359, 367–376, 395–401, 433–444 | D; no native Linux visual claim |
| Download center ISO and MATLAB Runtime | <https://rflysim.com/doc/en/5.HW/dl.html> lines 319–350 | D; official <https://rflysim.com/download.html> names `RflySimToolchain-v5.01-20260831.iso`; link is emailed after contact form; URL/size/hash pending |
| Free vs Full/Custom edition | <https://rflysim.com/doc/en/> version table; <https://rflysim.com/doc/en/4.DevRef/3d-res.html> version note | D; Free UE4, Full UE5; verify installed build |
| Free RGB/sensor count and target limits | <https://rflysim.com/doc/en/4.DevRef/vis-cfg.html> version restriction table | D; page itself notes inconsistent attribution, verify binary |
| Windows install, fast `OnekeyScript.exe`, optional WSL/reboot, full MATLAB route | <https://rflysim.com/doc/en/1/InstallLearn.html> Core Installation in 3 Steps | D; no install performed |
| CPU/OS/RAM/disk baseline | <https://rflysim.com/doc/en/HowToInstall.pdf> section 1.1.1 | D; generic demo guidance |
| RTX 2060 and >16 GB for closed loop | <https://rflysim.com/doc/en/2.Course/ch2/index.html> section 2.2.2 | D; basis for cheaper option |
| Expanded disk 80–100 GB, 300 GB free recommendation, startup shortcut | <https://rflysim.com/doc/en/3/FAQ.html> disk and first-simulation questions | D |
| SITLRun prompts/SimMode=2/iris, LowGPU and NoUI alternatives | <https://rflysim.com/doc/en/4.DevRef/bat.html> Basic Simulation Scripts and script comparison | D; exact installed BAT must be inspected |
| SDK offboard/local NED control and state | <https://rflysim.com/doc/en/4.DevRef/pysdk/ctrl/px4mav.html> lines 562–590 and method index lines 138–200 | D; runner mirrors documented methods, actual source unverified |
| Vision request/capture uses UE and `VisSensor`, `hasData`, `Img` | <https://rflysim.com/doc/en/4.DevRef/pysdk/vision/viscap.html> lines 459–487, 1020–1029, 1066–1072 | D; frame pose API needs inspection |
| CopterSim public model repository | <https://github.com/RflySim/CopterSim> and `Init.m`, `Multicopter_vPC.slx`, `MathModelDocEn.pdf` tree (page lines 140–157) | D; Simulink source is not full UE visual source; no LICENSE identified in page. GitHub HEAD `0d14487f8dc3086ad29387ed40e068e301905343` at <https://github.com/RflySim/CopterSim/commit/0d14487f8dc3086ad29387ed40e068e301905343>. |
| Experiment repository | <https://github.com/RflySim/RflyExpCode> tree lines 140–158; <https://github.com/RflySim/RflyExpCode/blob/master/code/e0/1.SoftwareSimExps/icon/Init.m> lines 1–151 | D; Init.m defines quad mass, gains, initial state; no current binary/version inferred. GitHub HEAD `7dbec4d8796d6e23ee86c523e4ba5712203b1519` at <https://github.com/RflySim/RflyExpCode/commit/7dbec4d8796d6e23ee86c523e4ba5712203b1519>; license pending. |
| Older v3 edition history | <https://rflysim.com/doc/en/RflysimVersions.pdf> section 3 | D; historical description, not current installer proof |

**Static local checks:** target absent before work; no applicable parent `AGENTS.md`; local Air Labs repo had unrelated untracked `FalconGym/` and `reproduction/`, untouched. `git ls-remote` to both GitHub repos failed with DNS resolution, but GitHub browser commit links resolved both HEADs. `run.py` syntax and dry-run logic were checked on macOS; that is not a Windows SDK execution.

**Licenses/access:** The official site calls its base edition free/open-source while distributing an ISO and separately selling Full/Custom tiers. This does not prove rights to redistribute UE binaries, scenes, or downloaded packs. The visible GitHub repository pages did not expose a license, so treat source reuse terms as unresolved until `LICENSE`/EULA are captured. Full UE5 and select sensors/scenes require a higher edition. No authenticated or paid artifact was fetched here.
