# Recovered runner review

The exact October 4 `run.py` is preserved with hash in `recovery.json`. Its CLI is historical. Current `simulators/rflysim/run.py` is a preparation-only guard/validator and preservation tool, not an installed-SDK adapter.

| Recovered lines | Problem | Required change before execution |
|---|---|---|
| 177–200 | SDK calls/startup can block; no independent timeout | Parent watchdog with 2 s SDK deadline and process-owned children; freeze 75 s flight /15 s cleanup independently. |
| 210–216 | Timed segment changes and break near 50 s; no tolerance/dwell | Maintain exact route; advance only on fresh state ≤0.25 m for continuous 2 s, with bounded leg/total limits. |
| 222–228 | Guessed field names, no freshness/source clock, camera pose always null | Installed field mapping, raw messages/acks/modes/landed/arming, simulator truth and camera transform verification. |
| 233–254 | PNG writes and up-to-2 s GPU query block 10 Hz control | Separate owned capture/writer/GPU workers and bounded queues; measure missed intervals and dropped frames. |
| 233–240 | Cached `hasData` can re-save stale images; receiver time used | Sensor timestamps/sequence + duplicate hashes, locking/copy semantics; do not assign receiver time as acquisition. |
| 266–283 | Landing sent then six-second observation; no independent cleanup watchdog/disarming confirmation | Fresh landed-state + disarmed telemetry confirmation; record timeout, attempted landing/disarm and owned-PID termination. Never classify a killed runner as landed. |
| 287–292 | Calls `vis.stopRun()` | Inspected public VisionCaptureApi version has no `stopRun` definition; installed lifecycle must be checked rather than copied. |
| preflight / assets metadata | 20 GB gate and placeholder versions/paths do not verify full host or assets | Host/driver/display/license/build/model/scene/ports/ISO inventory gate. |

Pinned RflyArena `windows/rflysim/SITLRun.bat` is **source evidence only**: lines 1–5 elevate; 27–36 copy custom FX150 model; 39 sets SITL; 49 selects CameraRoom; 124 and 168–170 broadly terminate processes; 157 calls WSL distribution and compiles PX4. Its custom-model route must not become the stock test. Installed scripts must be audited for similar behavior.

Preparation validation checks preserve recovered files and exact routes/criteria, prevent simulator execution, detect manifest traversal, and detect altered evidence. Runtime watchdog, stale-telemetry handling, capture isolation and SDK lifecycle tests remain pending an installed adapter; syntax checking does not establish those properties.
