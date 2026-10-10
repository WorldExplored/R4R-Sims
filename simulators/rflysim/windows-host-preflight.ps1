# Read-only host inspection. Run in the interactive Windows desktop.
# No RflySim launch, installer, WSL feature change, SSH/firewall change or credentials.
param([string]$RunId = ('host-' + (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')),
      [string]$OutputRoot = '')
$ErrorActionPreference = 'Stop'
if ($RunId -notmatch '^[a-zA-Z0-9][a-zA-Z0-9._-]{1,100}$') { throw 'Invalid run ID' }
if (-not $OutputRoot) {
    $OutputRoot = Join-Path ([Environment]::GetFolderPath('MyDocuments')) ('R4R-Sims-Audit\' + $RunId)
}
if (Test-Path -LiteralPath $OutputRoot) { throw "Preserve existing directory: $OutputRoot" }
$null = New-Item -ItemType Directory -Path $OutputRoot
$OutputRoot = (Resolve-Path -LiteralPath $OutputRoot).Path
$commands = Join-Path $OutputRoot 'commands.log'

function Snapshot($Name, [scriptblock]$Read) {
    try { $data = & $Read; $record = @{status='read'; data=$data} }
    catch { $record = @{status='error'; error=$_.Exception.Message} }
    $record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $OutputRoot ($Name + '.json')) -Encoding UTF8
}

function Native($Name, $Executable, [string[]]$Arguments, [int]$TimeoutSeconds = 15) {
    $stdout = Join-Path $OutputRoot ($Name + '.stdout.txt')
    $stderr = Join-Path $OutputRoot ($Name + '.stderr.txt')
    $watch = [Diagnostics.Stopwatch]::StartNew()
    $record = @{executable=$Executable; arguments=$Arguments; timeout_s=$TimeoutSeconds;
                start_utc=(Get-Date).ToUniversalTime().ToString('o'); timed_out=$false}
    try {
        $process = Start-Process -FilePath $Executable -ArgumentList $Arguments -PassThru -NoNewWindow `
            -RedirectStandardOutput $stdout -RedirectStandardError $stderr
        $record.pid = $process.Id
        if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
            $record.timed_out = $true
            $process.Kill() # Only this inspection process, never a name-wide taskkill.
            $null = $process.WaitForExit(1000)
        }
        if ($process.HasExited) { $process.Refresh(); $record.exit_status = $process.ExitCode }
        else { $record.exit_status = $null; $record.error = 'owned process still alive after bounded stop' }
    } catch { $record.error = $_.Exception.Message; $record.exit_status = $null }
    $record.wall_s = $watch.Elapsed.TotalSeconds
    ($record | ConvertTo-Json -Compress -Depth 5) | Add-Content -LiteralPath $commands -Encoding UTF8
}

Snapshot 'identity' {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    @{name=$identity.Name; sid=$identity.User.Value;
      administrator_group_in_token=($identity.Groups.Value -contains 'S-1-5-32-544');
      elevated_administrator=$principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator);
      powershell=$PSVersionTable.PSVersion.ToString(); documents=[Environment]::GetFolderPath('MyDocuments')}
}
Snapshot 'os' { Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,OSArchitecture,LastBootUpTime }
Snapshot 'resources' {
    @{cpu=@(Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors);
      ram_bytes=(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory;
      disks=@(Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | Select-Object DeviceID,Size,FreeSpace)}
}
Snapshot 'graphics' { Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion,DriverDate,CurrentHorizontalResolution,CurrentVerticalResolution }
Snapshot 'sshd' { Get-Service sshd -ErrorAction Stop | Select-Object Name,Status,StartType }
Snapshot 'ssh_listeners' { @(Get-NetTCPConnection -LocalPort 22 -State Listen -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,OwningProcess) }
Snapshot 'ssh_firewall' { @(Get-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -ErrorAction SilentlyContinue | Select-Object Name,Enabled,Direction,Action,Profile) }
Snapshot 'wsl_feature' { Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux | Select-Object FeatureName,State }
Snapshot 'commands' { Get-Command nvidia-smi,wsl,git,python,py -ErrorAction SilentlyContinue | Select-Object Name,Source }
$gpu = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($gpu) { Native 'gpu' $gpu.Source @('--query-gpu=name,memory.total,driver_version,uuid', '--format=csv') }
$wsl = Get-Command wsl -ErrorAction SilentlyContinue
if ($wsl) { Native 'wsl-list' $wsl.Source @('--list','--verbose') }
$files = @(Get-ChildItem -LiteralPath $OutputRoot -File | ForEach-Object {
    @{path=$_.Name; bytes=$_.Length; sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLower()}
})
@{run_id=$RunId; kind='read-only host preflight, not simulator validation'; output_root=$OutputRoot;
  simulator_executed=$false; files=$files} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $OutputRoot 'manifest.json') -Encoding UTF8
Write-Output "Inspection records: $OutputRoot"
