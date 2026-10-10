# RflySim installation continuation — 10 October 2026

**Installation completed; renderer startup failed; no A/B/coupled experiment ran.** This is installation/startup evidence, not simulator validation. Baseline `0810be8`; previous 20 synthetic tests retain their original provenance.

## Observed path and outcome

Verified Free ISO (23,151,480,832 bytes, SHA-256 `ed5f41add2e97469c900f4ccff87f615eae4e7cfbedcc7d99211afd4d5dc7973`) → Microsoft-signed bundled WSL 2.7.8 runtime MSI → explicit WSL1 → OnekeyScript → stock launcher → PX4 SITL → CopterSim heartbeat. RflySim3D stopped before rendering with **“DirectX Runtime” required**. No state-to-camera-to-frame trace exists yet.

- Runtime MSI: exit0, 9.523 s, 600 s deadline. Actual `RflySim-20.04` distribution mode1; distro name does not establish its Ubuntu version. VirtualMachinePlatform remained disabled.
- RflySim installer: corrected first-install flags, exit0, 916.380 s, 1800 s deadline. Installation at `C:\Users\user\Documents\RflySim`. Overall success includes a helper warning: `RflySimUI/scan_infos.py:283` raises a cp1252 UnicodeEncodeError. The warning was not repaired.
- CopterSim GUI: Free v5.0.1, PX4 1.12.3dev, TCP4560/SITL heartbeat connected; stock `10016_iris`, Grasslands, one quad. QGroundControl launched. Scene clearance, ground origin, precise model/scene hashes and simulation clocks remain unverified.
- Renderer bootstrap offered DirectX Runtime installation. Selected No and preserved the error; no additional platform repair attempted. NVIDIA renderer selection, RGB, depth, collisions and rendering throughput remain not tested.
- No flight/arming commands issued. A/B/coupled **not run**; minimum integration and full-route B **not measured**. C remains blocked. Numerical acceptance criteria and pending configurations unchanged.

## Failures and corrections

| Classification | Symptom / cause / repair / retest |
| --- | --- |
| Authored installer flags | `--psp no` caused first-install PSP prerequisite exit1 (14.025 s). Changed to vendor first-install `--psp yes`; retest exit0. This does not establish a MATLAB license requirement. |
| Authored launcher | Incorrect regex escaping corrupted the copied batch file; exit255. Preserved failed copy; literal replacements produced the working stock startup. Installed upstream launcher unchanged. |
| Authored collection | Copying the entire SDK encountered long-path errors. Cancelled collection; four canonical SDK/launcher files copied, hashed, transferred and parsed locally. |
| Upstream helper | cp1252 encoding traceback in `scan_infos.py`; overall installer exit0. No retest/fix. |
| Platform prerequisite | RflySim3D missing DirectX Runtime modal. Confirmed missing prerequisite, exact dependency version not established. No engine launch or repair retest. |
| SDK uncertainties | Installed APIs copied; adapter/freeze incomplete. Autoarming/failsafe changes in `initOffboard`, raw ACK/landed freshness, truth clocks and camera association require verification. |
| Missing research assets | AirLab images/poses/calibration/reconstruction/split/held-out views/downstream model/thresholds absent; independent of stock startup. |

Authored launcher removed broad taskkill and realtime priority, chose one vehicle and preserved original/failed/corrected copies. Its stale “Kill all CopterSims” echo is not an executed kill. Stock launcher parent exited0 while child components remained; this does not mean complete startup success. Startup was observed manually; the requested independent 120 s startup watchdog was not implemented for this invocation. No deadline-compliance claim is made.

## Installed interface inspection (static, not SDK validation)

Verified local SDK snapshot: `artifacts/rflysim/extension-20261010T204353Z/final/sdk-small/`; hashes in [manifest](installed-sdk-manifest.json).

- `PX4MavCtrlV4.py:1095` InitMavLoop; `:3113` blocking recv_match; `:3137` estimated NED state; `:3198` armed heartbeat. Handler has no verified COMMAND_ACK/EXTENDED_SYS_STATE cache. `:2285` initOffboard autoarms and changes failsafe parameters; do not call blindly. `:2005` SendPosNED; `:863` truth receiver. Timestamp semantics unverified.
- `UE4CtrlAPI.py:369` CameraData defines pose/FOV/image dimensions/timestamp fields; acquisition semantics unverified.
- `VisionCaptureApi.py:3339` jsonLoad, `:3207` startImgCap, `:1278` sendReqToUE4, `:1123` sendUpdateUEImage, `:3308` sendImgBuffer. Transport sending alone is not proof of external observations entering a visual controller.

Gaussian trajectory replay remains a conditional small-adapter candidate after clocks/transforms are verified. Native renderer replacement is substantial integration; controller observation injection and collision/depth ownership remain unresolved. No external renderer implemented. Existing [interface findings](../../../docs/rflysim/interfaces.md) retain source/edition boundaries.

## Preservation and shutdown

[Verification](preservation.json): private Drive → Mac ZIP, exact 371,022 bytes/SHA-256, CRC pass, all 52 manifested file bytes/hashes pass; representative raw logs opened. Archive/extraction are ignored bulk artifacts. No frame/video exists to open. Full ISO remains on the instance disk (Stop accepted; Off not yet verified) plus recorded official source/hash; no complete local ISO copy is claimed. Console archive is a post-install snapshot; original transcript closed afterward.

CopterSim closed normally. QGroundControl did not close within 5 s; only owned PID10176 was terminated. No survivors in [cleanup](cleanup-final.json). Audit-owned WSL distribution terminated successfully within 15 s. No landing confirmation is claimed. Stop requested after Mac verification before the fixed 60-minute deadline; see [dashboard](instance-stop.png). No Delete action.

Previous time ledger unchanged; [extension ledger](setup-budget.json) includes the fixed window and repair history. No further repair extension assumed. Windows Git checkout synchronization and remote authenticated Git access remain unverified; authored evidence is committed/pushed through the Mac.

## Decision and next prerequisite

Retain RflySim as a **dynamics/control candidate**: PX4/CopterSim connection demonstrated, bounded flight not tested. Native visual baseline blocked by DirectX prerequisite. Defer reconstruction rendering, calibrated replay and policy evaluation. No measured indoor/outdoor/racing performance, sparse-capture fidelity or real-world transfer claim.

**Preparation-ready: yes for preserved test design. Execution-ready: no.** Smallest next prerequisite: in a newly authorized session, review/install the official or bundled DirectX dependency and retest RflySim3D in the interactive L4 desktop; then finish installed SDK adapter, truthful telemetry/camera timing mappings and frozen startup watchdog before unchanged experiments. Existing presentation remains historical preparation; measured deck pending. No duplicate presentation created.
