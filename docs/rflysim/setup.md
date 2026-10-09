# Host gate and deferred installation

Preparation only. The supplied SSH command is complete but host/OS/GPU/display/access/price are unverified. The local key exists with mode 0400; contents were not read or uploaded. No automatic connection or key copy. Actual remote installation, repository and artifact paths must be discovered.

The candidate host must supply either a documented complete licensed Linux Free visual stack (not found), or supported Windows 10/11 x64 with NVIDIA graphics driver and interactive GPU desktop, installation privilege/reboot access, and PX4 in WSL1 `RflySim-20.04`. Official WinWSL says WSL1 default; confirm installed release. WSL2 would require separately verified virtualization support and change review; do not propose Wine/nested Windows or paid/engine-build workarounds.

Pending authorization, exact first Windows inventory commands are:

```powershell
Get-ComputerInfo | ConvertTo-Json -Depth 3 | Out-File host.json
Get-PSDrive -PSProvider FileSystem | ConvertTo-Json | Out-File disks.json
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv > gpu.csv
wsl -l -v > wsl.txt
Get-NetUDPEndpoint | ConvertTo-Json | Out-File udp.json
Get-FileHash <actual-ISO-path> -Algorithm SHA256
```

Use actual paths, preserve native exit statuses, and collect failures. Archive stdout/stderr of every process. On a POSIX verified inspection host use `ssh -p <supplied-port> -i <absolute-key> <supplied-user>@<supplied-address>` only after authorization; no address or username is invented. Authenticating SSH is not a desktop/RflySim networking test.

After release/license and desktop gate: mount ISO, inspect fast installer prompts and `EnableWSL.bat` before authorizing changes. Standalone Python path is the first choice. Test a small resumable transfer and SHA-256 equality before generating media. Active install/debug/startup budget is 2 h excluding downloads, at most 2 repairs. Freeze executable paths, startup ownership/PIDs, SDK signatures, port map and deadlines before execution. No blanket `taskkill`, `CloseALL`, authentication/security changes or instance shutdown.

Python dependencies should be isolated using the release's bundled Python with a dedicated venv if supported; record resolved packages. Do not pip-install into system/global Python or patch upstream files. No generic pip version lock is invented until the installed SDK is known.
