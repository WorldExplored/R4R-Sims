# Current execution state — 10 October 2026

**Installation and the preserved bounded experiments are authorized. Installation is incomplete; no simulator experiment has run.** Numerical criteria remain unchanged. Baseline 6304b53; authored authorization correction 9aff509. Historical preparation flags do not revoke human authorization.

## Readiness checklist

| Step | Verified evidence / exact next step | Status |
|---|---|---|
| Installer acquisition | Full official `RflySimToolchain-v5.01-20260831.iso` downloaded to `C:\Users\user\Downloads\`. Actual and ISO-declared length **23,151,480,832 bytes** match; SHA256 **ed5f41add2e97469c900f4ccff87f615eae4e7cfbedcc7d99211afd4d5dc7973**. Mounted inventory: 92 files. Executable package-info identifies **V5.01-20260831, Free, no activation required**. No vendor-published checksum supplied; archive payload integrity and dependency terms still need checking. | Acquisition complete. Truncated Mac original preserved, never installed. [Records](../../results/rflysim/continue-20261010T191100Z/download.json). |
| Platform/access | Interactive Moonlight desktop works on selected **airgpu-d27cc1d09d**; current IP **18.191.160.139**, user `user`. Guest Server 2025 Datacenter, build 26100, L4 **23034MiB**, driver 596.86, EPYC7R13 4 cores/8 logical processors, RAM 33,067,937,792 bytes. Prior C: free 396,542,255,104 bytes. Administrator elevation and Windows reboot demonstrated. | Server2025 release compatibility and UE NVIDIA adapter selection **not tested**. Documented installer requirements name Windows10/11, not Server2025. Compute $1.95/hour; full charges unresolved. |
| WSL1 prerequisite | Feature Enabled; reboot applied. Explicit `wsl.exe --set-default-version 1` asks for latest runtime and exceeds 15 s deadline; only owned PID killed, exit -1. Bundled **wsl.2.7.8.0.x64.msi**,258,678,784 bytes, SHA256 928506b99d6caad14e5a8938e3e3fd9d1c839df3ed4f40639bdb095fbf24cbf8 has **Valid Microsoft Corporation signature**. VirtualMachinePlatform **Disabled**. | Next: bounded install of this signed runtime, then explicit default1 and `wsl -l -v`; no default `wsl --install`, WSL2, or VMP workaround. Pending setup allowance extension. |
| Minimum RflySim install | OnekeyScript.exe help/package-info/dry-run actually executed. Proposed standalone Python/SITL flags below replace hardware/default block-output settings **before install**. | Actual installer not run; stock model eligibility, terms and final component versions unverified. |
| Transfer | Authorized private Drive folder **ChatGPT/R4R-RflySim-Audit**. Windows→Drive→Mac two closed ZIP checkpoints verified by bytes/SHA256, internal manifests/CRC; previous transcript preserved. Mac→Drive→Mac 76-byte probe passed; Git bundle uploaded. | Small-file transfer demonstrated. Large resumability untested; closed bounded chunks planned. Windows checkout/bundle consumption not yet verified. |
| Installed interfaces/freeze | Canonical SDK/launchers/PX4/params/model/scene must be hashed; verify ACK/mode/armed/landed freshness, actual truth, camera transform/FOV/acquisition clocks and lifecycle. Preserve launcher diffs; stop only owned PIDs. | No installed SDK adapter. Freeze remains incomplete. |
| Experiments | B capture off→successful reset→identical route capture on; A two seven-pose replays and rate test. Preserve 10 Hz, 75 s/15 s, 12 s waypoint deadline, 0.25 m/2 s dwell, 0.5 s freshness and all A criteria. | A/B/coupled **not tested**; C **blocked** (compatible released policy/task/adapter missing). No minimum/full B outcome. |

## Next installation commands — pending, not executed

Use elevated PowerShell in the interactive desktop. Derive mounted drive from `Mount-DiskImage ... -PassThru | Get-Volume`; currently D:. Record native command stdout/stderr, cached process handle, exit status, walltime and deadline independently. Inspect any terms/prompts. Do not silently accept EULAs or modify security settings.

```powershell
# After renewed setup allowance: signed bundled runtime only; no automatic WSL2 distribution.
msiexec.exe /i D:\0.UbuntuWSL\wsl.2.7.8.0.x64.msi /passive /norestart /L*v C:\Users\user\Documents\R4R-Sims-Audit\continue-20261010T191100Z\wsl-msi.log
wsl.exe --set-default-version 1
wsl.exe --list --verbose
# Pending WSL1 success and package terms review:
D:\OnekeyScript.exe --silent --install-dir C:\Users\user\Documents\RflySim --build-command px4_sitl_default --px4-version 6 --toolchain 1 --psp no --apps yes --compiler-env yes --firmware yes --prebuild yes --block-output no --lang en
```

These command lines alone are **not a bounded launcher**. Wrap runtime/WSL/install process waits with frozen deadlines and independent observation; do not paste an unbounded sequence. CLI dry-run resolves6toPX4v1.12.3 and1toWinWSL. Actual installed versions can differ and must be recorded. No licensed MATLAB/model generation is assumed necessary for the stock experiment; sufficiency remains unverified.

## Setup allowance and failures

The prior pass lacked an exact active timer. Conservatively reserve its entire64-minute investigation span, plus 56minutes this continuation. This overcounts source/UI/wait time; exact active consumption is unknown. The carried-over120-minute conservative allowance exhausted **20:09:36 UTC**; setup paused and a 60-minute extension requested, **not granted yet**. No allowance reset. Prior scopedSSH repair counts 1; one remains. Bundled WSL runtime repair has **not** been attempted. [Ledger](../../results/rflysim/continue-20261010T191100Z/setup-budget.json).

- **Access:** external TCP 22 timeout before authentication despite earlier local listeners/scoped rules; cause unresolved. After Windows reboot sshd Stopped/Manual again. Preserve keys/scope; desktop installation remains available.
- **Setup:** standard-token ISO mount failed HRESULT0x80070522; administrator mount succeeded. This was a privilege prerequisite, not an RflySim defect.
- **Platform:** feature-only WSL setup insufficient: command explicitly asks runtime update. Signed bundled runtime is next supported candidate; compatibility remains untested.
- **Authored recording defect:** earlier native helper recorded completed help command with null exit status. Holding process handle before wait/removingRefresh preserved killed-command exit -1; successful-command retest still needed. Do not claim the helper repaired/validated yet.
- **Authored collection defects:** WindowsZIP backslash lookup and optional filename typo repaired; all manifested hashes passed. Neither is a simulator failure.
- **SDK uncertainties:** no canonical installed fields/signatures yet. Partial archive/example source is not installed provenance. ExampleinitOffboard autoarming/failsafe changes require inspection before use.
- **Upstream hazards:** broad launcher taskkill and WSL2/VMP branches remain source findings; use reviewed authored copies only, no upstream silent edits.
- **Research assets:** AirLab imagery/calibration/reconstruction/split/heldout horizontal+vertical views/downstream model/approved thresholds missing, separately from stock setup prerequisites.

## Preservation and R4R decision

Two Windows checkpoints are private Drive+Mac durable copies under `artifacts/rflysim/continue-20261010T191100Z/`, with [verification1](../../results/rflysim/continue-20261010T191100Z/checkpoint-preservation.json) and [verification2](../../results/rflysim/continue-20261010T191100Z/checkpoint2-preservation.json). Original Windows transcripts, package source/help/dry-run, reboot and runtime records preserved. No frames/flight logs exist. ISO is still Windows-only; official retrievable folder and observed hash recorded, continued accessibility not guaranteed. Never delete the Windows input before preservation terms are resolved.

**Preparation-ready: yes for preserved test design; installed adapter incomplete. Execution-ready: no.** Dynamics/control host and native visual baseline remain candidates, not demonstrated. Defer reconstruction renderer, calibrated replay and pretrained visual-policy evaluation. A blocked setup is not proof RflySim cannot work. Free Linux complete renderer/camera path not established; supplied ISO contains Windows UE4 binaries. See [interfaces](interfaces.md) and [readiness](readiness.md) for source evidence and Gaussian path classifications. No real-world transfer or fidelity result is claimed.
