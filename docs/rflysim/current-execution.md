# Current execution state — 10 October 2026

The latest human message authorizes Free Edition installation and the existing bounded A/B/coupled tests on **airgpu-d27cc1d09d**. Numerical criteria remain unchanged. Historical preparation flags do not revoke that authorization.

**Current:** AirGPU **Running**, refreshed IP **18.191.160.139**, Windows user `user`, paired Moonlight endpoint `d27cc1d09d.my.airgpu.com`. The interactive Windows desktop and official OneDrive package page are verified. SSH is **not required to download or install through the desktop**. A supported, tested artifact transfer is required before experiments generate large outputs.

## Immediate readiness checklist

| Step | Evidence / required action | Status |
|---|---|---|
| Complete installer | Windows Edge is open to the supplied [official folder](https://1drv.ms/f/s!AumI9wM9CHrXou02EWLuwKozkM-I-w). Download `RflySimToolchain-v5.01-20260831.iso`; listing21.6GB. Record actual path, bytes, SHA256 and ISO volume completeness before mounting/installing. | Downloading on Windows; bytes/hash/completeness pending. Preserve truncated Mac original. |
| Minimum installation | Inspect OnekeyScript.exe help, package terms and prompts; standalone Python/stock binaries where sufficient. Explicit WSL1 only; bundled script contains automatic WSL2/VirtualMachinePlatform branches and must not run blindly. | Explicit Windows WSL1 feature enabled; restart required, deferred during download. Distribution/RflySim installer unexecuted. |
| Platform | Guest observed Server2025 Datacenter26100, L4 23034MiB/596.86, EPYC7R13 4cores/8logical, RAM33067937792bytes; Cfree396542255104bytes. Bundled requirement names Windows10/11x64≥1903, not Server2025. | Compatibility/engine NVIDIA selection still need bounded test; no alternate OS/workaround. |
| Command access | Mac IP remains72.12.218.187, matching saved scoped rules. New host IP22 times out before auth. After restart sshd was confirmed Stopped/Manual. Restarted; Running with IPv4/IPv6 port22 listeners. Both rules still match Mac IP; keys untouched. | External cause unresolved. Continue installation via desktop. |
| Transfer | Verify SSH if service restored, otherwise a supported desktop-accessible transfer and small file size/hash probe. Windows transcript from previous pass still needs a durable Mac copy. | Required before scientific recording; not a prerequisite for installer download. |
| Installed interfaces/freeze | Hash canonical SDK/launchers/PX4/parameters/stock model/scene; verify ACK/mode/armed/landed freshness, truth, camera extrinsics/FOV/clocks/lifecycle. Preserve launcher copies/diffs and stop only owned processes. | Adapter absent; no guessed installed fields. |
| Experiments | B capture off → successful reset → identical route capture on; A two seven-pose replays and separate rate test. Preserve numerical config, watchdogs and cleanup. C requires complete compatible released policy. | A/B/coupled pending; C blocked. |

## Setup/debug allowance

The previous pass did not record an exact active timer. Conservatively reserve **64 minutes** of the120-minute total for its17:11–18:15UTC investigation span. This includes waits/source inspection and therefore overcounts. Human idle time between turns and installer download waits are excluded. At this continuation's start, **56 minutes remain**; new active phases must be accumulated in [setup-budget.json](../../results/rflysim/continue-20261010T191100Z/setup-budget.json). Count the previous scoped SSH setup as **one repair**, leaving one. Do not restart this allowance. No simulator installation repair has occurred.

## Preserved prior evidence

[Installer/source and guest investigation](../../results/rflysim/install-20261010T171109Z/README.md) preserves prior IPs, access attempts, source hashes, inventory and raw-transcript location. Local ISO is10,218,483,712bytes, SHA256 `3153167473469b1ab592e7058d10734076e418173cf767a65bc4430c21222e1a`; ISO volume declares **23,151,480,832bytes**. Shortfall12,932,997,120bytes confirms truncation. Preserve it; never install from it or overwrite it. Readable metadata namesV5.01-20260831 and Free edition0, but does not establish a complete release/license/installed build.

Example SDK copies recovered from the partial archive are not canonical installed interfaces. `initOffboard` in one inspected example changes failsafe parameters and automatically arms; cached flags lack verified freshness. These remain source findings requiring installed inspection. Authored watchdog/route/landing/queue fixes and20synthetic tests at54bdaf1 remain **local tests, not simulator validation**; [runner review](runner-review.md).

A/B/coupled have no measured outcomes, minimum/full B results or sensor frames. C lacks a compatible released visual-policy/task/adapter. AirLab capture/calibration/reconstruction/held-out views/downstream model/approved thresholds remain separate missing research inputs. Current R4R recommendation: candidate dynamics/control host and native visual baseline; defer reconstruction renderer/calibrated replay/policy claims until evidence. No resource-use measurements or transfer claims are inferred from stock documentation.

The human activated **Download** for the named ISO; Windows Edge shows it in progress. Wait for completion, then verify bytes/hash/volume completeness before mounting. Windows WSL1 optional feature is Enabled with RestartNeeded=True; defer reboot until download is safe. Keep credentials in secure login forms. No private key or personal GitHub credentials are copied to Windows; no broad security weakening, instance shutdown or deletion.
