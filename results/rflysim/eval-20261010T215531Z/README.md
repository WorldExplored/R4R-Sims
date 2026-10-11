# RflySim measured evaluation, 10 October 2026

Branch `audit/rflysim`, baseline `7188f4d`. Authored executed code hashes: [provenance](executed-code-provenance.json). Installed SDK/build identity is separate from public repository HEAD. This is stock integration evidence for AirLab Real4Real (R4R), unrelated to the R2R navigation benchmark.

## Outcomes

| Test | Measured status | Limits |
|---|---|---|
| B1, capture off | **Demonstrated** minimum integration and full route, takeoff/landing/disarm, exit0,38.750s supervised wall. | PX4 estimated local NED. Ground-truth criterion outcome blocked. |
| B2, capture on | **Demonstrated** minimum integration and full route, takeoff/landing/disarm, exit0,39.219s supervised wall.365RGB frames. | Same route after stock reset. Calibrated image-pose coupling blocked. |
| A1/A2 | **Demonstrated** native camera images and metadata:260/261frames. A2 ran26s. | A1 short25.797s. **Failed authored rotation conversion**. Geometric checks blocked. Strict A1-retest261frames/26s observed on Windows but raw not exported, not a verified local result. |
| Rate | **Demonstrated**351frames,5s warmup +30s window,300post-warmup frames,10.013Hz measured record rate. | Zero duplicate native timestamps, no receipt gap>150ms after warmup. Acquisition latency unknown. |
| Coupled | **Demonstrated** command/state/native-camera/RGB records alongside B2. | Native camera/body data recorded, verified acquisition-time transform/interpolation unavailable. RGB never entered control. |
| C | **Blocked**. | No compatible released R4R policy/weights/task/adapter. PX4 and waypoints are scripted control. |

Exact route: origin, (0,0,-2), (2,0,-2), (2,2,-2), (0,0,-2), land, in local NED metres. Criteria unchanged:≤0.25m continuously sampled2s,12s/leg,10Hz target updates,0.5s freshness,75s flight +15s separate cleanup. [B1 freeze](B1/freeze.json), [B2 freeze](B2/freeze.json), [raw sampled dwell corroboration](dwell-corroboration.json). Takeoff armed and≥1m for1s. Landing fresh ON_GROUND and speed≤0.2m/s for2s plus fresh disarmed heartbeat. Both cleanup workers returned fresh landing/disarm confirmations, but the supervisor killed them at the15s deadline and their raw cleanup files are empty. This is an authored lifecycle/preservation issue, separately from the flight-worker passes. Local fresh-queue and exit-status corrections are not host retested.

![B1 estimated route](B1/trajectory.png)
![B2 estimated route](B2/trajectory.png)
![Actual B2 RGB frame](B2/rgb/preview-middle.png)

## Control timing and resources

| Measurement | B1 camera off | B2 camera on |
|---|---:|---:|
| Control setpoint mean interval |100.022ms|100.034ms|
| Maximum setpoint interval |109ms|110ms|
| Maximum control tick lateness |12ms|16ms|
| Ticks late>10ms / total |56/280|116/292|
| Ticks late>100ms |0|0|
| Maximum position receipt gap |125ms|110ms|
| PX4 boot-clock recorded span |38.148s|38.549s|
| GPU memory peak, whole100-sample window |1761MiB|1758MiB|
| GPU utilization mean / peak |16.93% /24%|17.47% /26%|

These two sequential flights are a small comparison, not a causal estimate of capture overhead. Different tracking transition times, scheduler quantization and reset state remain. GPU samples include Moonlight and desktop, requested1Hz, observed~1.05s between samples. B1 sampling covers the flight; B2 sampling appears to stop about22s into its39s flight under the inferred UTC−04 alignment. It does not cover B2 landing. [Coverage](resource-coverage.json). No GPU synchronization microbenchmark, renderer-only throughput, policy inference latency or playback-FPS inference is claimed. No minimum VRAM follows from observed allocation. CopterSim multiplex truth records permit diagnostic receive-nearest comparison after fitted initial origin offset: mean disagreement0.0196m B1 and0.0181m B2. Timing/coordinate calibration incomplete, so this is not a truth pass. [Metrics](metrics.json), [B2 timing](B2/tracking-timing.png), [truth diagnostic](B2/truth-disagreement.png).

## What was installed and launched

Verified complete Free ISO23,151,480,832bytes from maintenance-group official folder, releasev5.01-20260831. Minimum OnekeyScript install completed previously. Bundled Microsoft-signed runtime2.7.8, distributionRflySim-20.04 in **WSL1**, VirtualMachinePlatform disabled. Current bundled Epic prerequisite1.0.14.0 installed exit0. Correct-working-directory RflySim3D launched with **D3D11 NVIDIA L4** confirmed in engine log. NativeCopterSimFree5.0.1 and bundledPX4 1.12.3dev ran Iris/model0/Grasslands. QGC launched as monitor. Licensed MATLAB/model generation and UE editor were not needed for this precompiled stock path.

Empirical host: WindowsServer2025 Datacenter26100, driver596.86, L4 reported23034MiB,8logical CPU/4physicalEPYC7R13,32GBRAM,400GBSSD. Vendor install documentation names Windows10/11, so Server2025 success here is observed compatibility, not general support. Compute display$1.95/hour. Storage/taxes and complete charges unresolved. Full installed footprint and current free-disk inventory not exported. Use the same tested class for a repeat; no cheaper complete Linux Free renderer path established and no A6000 requirement demonstrated. [Assets](assets.json), [failures](failures.md).

## R4R decision

| Role/evidence dimension | Decision and evidence |
|---|---|
| Dynamics/control host | **Reuse for bounded PX4 SITL integration.** Two full scripted routes passed using estimated state. Physical calibration and real-drone transfer remain untested. |
| Native renderer/RGB baseline | **Keep stock visual baseline.** Actual640×480 nativeRGB and requested10Hz capture work on Free/vehicle1. Depth/collision semantics not tested. |
| Calibrated camera replay | **Defer.** Translation/control metadata exist, but our degree bug requires replay repair, independently verified intrinsics/extrinsics/axes and acquisition-clock association. Repeated0.02m/1° and2%feature criteria not passed. |
| Real capture/reconstruction renderer | **Defer as R4R's primary renderer.** No verified direct photo+pose or Gaussian loader. UE cooked mesh/XML route documented, Free/custom-map eligibility and installed loader implementation unresolved. |
| Policy evaluation | **Blocked C.** No released compatible observation/action/weight path. |
| Sparse scenes/indoor/outdoor/racing | **Not tested as tasks.** Stock grass rendering/control supports integration discussion only. Sparse image coverage concerns unseen surfaces/view extrapolation; sparse physical content concerns perception/navigation structure. They require separate data and tasks. |
| Below100m horizontal/vertical novel views | **Blocked fidelity/downstream usefulness.** Missing real captures/reconstruction/held-out views, approved thresholds and downstream model. NoPSNR/SSIM/LPIPS or transfer result. |
| Setup/maintenance/preservation | **Demonstrated Windows stock path**, significant manual desktop/setup and lifecycle effort. All1237main frames open and threeZIP manifests verify. Final Windows-only files remain explicitly missing from local delivery. |

[Installed interface guide and reproduction](../../../docs/rflysim/installed-execution.md) covers scene inputs, algorithms, protocols, clocks, learning guide and Gaussian classifications. Matched common-scene/common-camera tests remain future work. These native results do not rank simulators using unmatched worlds/hardware/controllers.

## Preservation and review

Raw artifacts: `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-rflysim/artifacts/rflysim/eval-20261010T215531Z` (ignored), private Drive `ChatGPT/R4R-RflySim-Audit`, ZIP3fileID1gydzS0cL8c635wACELIjVgf0HonZr6sa. Archive651,522,799bytes SHA256`d601dc38134b20d1287b0d14e991abb3120b9212795eca4517959cde548fb6d2`. ZIP CRC plus1300internal files pass; earlier27+33files pass. Essential B1/B2 telemetry, camera frames/metadata, source snapshots, configs and B1ULog are durable onMac. [Verification](checkpoint3-preservation.json). All1237PNG images opened, selected images/plots inspected. B2ULog, final transcript, strict A1-retest, final asset/launcher records remain on stopped Windows disk, not silently considered preserved here. Complete ISO remains Windows-only with official URL/hash as retrieval provenance.

AirGPU entered Stopping without an agent Stop action and is **Off verified**. No Delete. CopterSim/renderer close requests preceded disconnect; final QGC/PX4 graceful exits unverified. Earlier ledgers retained, no renewal inferred. NoMac simulator install. Private Drive download used the separate browser, leaving mainChrome untouched.

Presentation: [editable PPTX](rflysim-evaluation.pptx), [PDF](rflysim-evaluation.pdf). [Small review ZIP in private Drive](https://drive.google.com/file/d/15NTapOy57r11r-x6CRLq9IsDPuL7oVl6/view?usp=drivesdk) contains report, essential telemetry/logs/configs, plots, representative media, manifests and code. Hash manifest published after final assembly. Local helper tests are synthetic and separate from measured simulator outcomes.

## Local corrections after execution

Twenty-five synthetic local tests pass, including serializers, camera degree units/durations, blocked calls, stale telemetry, queue pressure, false landing and cleanup-deadline exit status. Executed source snapshots remain immutable. Cleanup now gets a fresh queue and nonzero exit status on cleanup failure; camera cleanup SDK calls use the existing2s deadline. No corrected host retest is claimed. Analysis runs on isolated Python3.12, NumPy2.3.5, Matplotlib3.11.2 and Pillow12.3.0. Windows SDK Python environment versions were not fully exported.

## Reproduce local analysis

No Mac simulator install is needed. Use a separate Python3.12 environment:

```sh
python3.12 -m venv /tmp/r4r-rflysim-analysis
/tmp/r4r-rflysim-analysis/bin/pip install -r simulators/rflysim/analysis-requirements.txt
MPLCONFIGDIR=/tmp/r4r-rflysim-mpl /tmp/r4r-rflysim-analysis/bin/python simulators/rflysim/analyze_evidence.py --input artifacts/rflysim/eval-20261010T215531Z/raw --output /tmp/r4r-rflysim-reanalysis
```

For the deck, use the existing `build-preparation-deck.mjs` with this run's `deck-content.json`, bundled Artifact Tool dependencies and a fresh private build workspace. FontsArial,1280×720,12slides. Exported PDF uses final rendered slide PNGs. All final pages/slides visually inspected. Native PowerPoint application behavior untested. Editable text/objects remain in PPTX, scientific plots are rendered PNGs with separate analysis data.

[Process memory samples](process-resources.json) record maximum working sets: CopterSim88,899,584bytes, UE engine624,463,872bytes and wrapper7,700,480bytes. This subset excludes PX4/QGC/OS, and no per-sample timestamps exist. It is not a total RAM requirement or CPU utilization measurement. Main raw flight record counts20050/20280 exactly match accepted queue metadata counts. Cleanup raw records are missing as disclosed.

**Preparation-ready: yes** for this preserved measured package and unchanged numerical criteria. **Execution-ready: no for the remaining calibrated A and corrected cleanup retests**: the instance is Off, corrected code has not run there, and camera projection/extrinsics/acquisition clocks are unverified. Stock B/nativeRGB compatibility has already been demonstrated. No reinstallation or replacement host is the next prerequisite.

The initial B2 mounted camera/body records also show raw coordinate difference(0.30000001,0,−0.14999962), despite requested mount(0.3,0,0). This stationary receiver-near diagnostic suggests another origin offset but does not independently calibrate extrinsics. Model/actor-origin hypotheses remain unresolved. [Raw mount diagnostic](mount-diagnostic.json).




ReviewZIP remains ignored locally under this results directory,13,439,685bytes, SHA256`a5718698cc281068a8ac0daa7abceae2c4f0ba098c2f29ce8fdc4d0dd708c8a4`. Private Drive upload and normal-browser roundtrip verified identical bytes/hash. ZIP is a selected review snapshot, not the full raw archive. No Mac simulator installation or instance restart was needed.
