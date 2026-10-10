> **10 October 2026 update:** [Current execution readiness](current-execution.md) supersedes the historical host/installer/access-permission assumptions below. Execution is authorized on the selected AirGPU host; guest access and complete installer remain blocked. Numerical pending tests are preserved.

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

Preparation validation checks preserve recovered files and exact routes/criteria, prevent simulator execution, detect manifest traversal, and detect altered evidence. SDK-independent watchdog, queue isolation and telemetry evaluation now have synthetic local tests in `runtime_core.py` / `tests/test_runtime.py`. Installed SDK lifecycle, real timing and sensor/flight validation remain pending. See the classification and integration contract below.


## Responsibility and current disposition

| Category | Finding | Disposition |
|---|---|---|
| Recovered audit-script defects | Unbounded blocking calls; timed route advances; synchronous PNG/GPU work; guessed fields; intent-only landing; cached image saves; assumed `stopRun`. | **Our defects**, not RflySim failures. Originals retained. Independent supervision, queue isolation, route/landing evaluation fixed in authored offline core; SDK mappings/capture lifecycle deliberately omitted. |
| Installed SDK uncertainties | Signatures/fields, timestamps, truth freshness, acks/mode/arming/landed messages, locking/copying and lifecycle. | **Unverified**, no installed source or adapter; public SDK mismatch is evidence to inspect the installed build, not a measured binary failure. |
| Upstream launcher hazards | Pinned RflyArena launcher elevates, copies custom model, builds PX4 and broadly kills executable names. | **Source-inspected hazard**, not stock-runtime failure. Do not run that launcher; inspect installed stock script and preserve any authored launcher diff. |
| Platform blockers | ISO link/bytes/hash/license missing; Windows graphics/access/driver/resources/price not inspected; complete Free Linux visual release not established. | **Blocked execution**; checklist in `readiness.md`. No remote connection or installation performed. |
| Missing research assets | AirLab images/calibration/poses/origin/scale/reconstruction/splits/held-out horizontal/vertical views, downstream model and approved fidelity thresholds. | **Blocked real-scene fidelity/transfer**, independent of stock A/B. No PSNR/SSIM/LPIPS or autonomy findings. |

## Authored core and local verification

`simulators/rflysim/runtime_core.py` imports only the standard library and has no SDK or network calls. `run.py run` still exits 2. Six preparation tests are retained and fourteen new tests use synthetic samples/functions only. They do not validate Windows process behavior, RflySim dynamics, PX4 control or cameras.

- `WorkerContext.call`: publish an active-call generation token before a potentially blocking call; the parent measures elapsed time on its own clock independently. The child checks its own elapsed duration; absolute clocks are never compared across processes. Returned late calls also fail. No abandoned SDK thread continues issuing actions.
- `run_phase` / `supervise`: spawn owned control and separate capture/writer/GPU callbacks; callbacks wait for the parent monitoring-ready flag before any SDK work; 75 s flight and separate 15 s cleanup defaults; per-call 2 s limit. Side worker termination does not join in the control-monitor loop. Cleanup gets a fresh process even after control exception/timeout. Each process reports PID/exit status/stop reason/error/attempted land/disarm; attempts are never confirmation. No blanket taskkill.
- Watchdog polls at 0.01 s; call timing starts on parent detection (up to one scheduled poll delay); process reaping is capped at 0.1 s per terminate/kill step (at most two per child). The wall record includes spawning/reaping, distinct from phase decision time. Native process creation, OS scheduling and kill semantics need Windows verification; this is not a hard real-time guarantee. Worker callbacks must not launch descendants; installed simulator startup ownership is a separate pending adapter requirement. A parent/host crash is not a confirmed landing.
- `offer`: only prebuilt immutable metadata ≤64 KiB enters the control queue using `put_nowait`. Overflow increments counts; essential evidence overflow marks evidence incomplete. Capture owns pixel copies; writer owns encoding and files; GPU worker owns polling. Queues must have fixed capacities; never pass a pixel array through the control path. Actual SDK receiver/writer/telemetry transport remains unimplemented until mapping is verified.
- `FlightEvaluation`: ordered legs 1–4, ≤0.25 m / continuous sampled 2 s dwell, 12 s leg/75 s flight deadlines; fresh increasing source and receive times; stale/future/duplicate/wrong-source rejection resets dwell. `tick` runs even without telemetry. Takeoff requires fresh armed telemetry and ≥1 m height for 1 s. Landing requires a recorded landing request **after takeoff**, fresh on-ground telemetry and speed ≤0.2 m/s for 2 s, then a fresh disarmed heartbeat at/after touchdown. Unknown/missing fields cannot be replaced by command success. Minimum pass requires legs 2 and 3 plus takeoff/landing/disarm; full pass requires every leg. Estimate-only evaluation explicitly blocks a ground-truth outcome.

`Sample` fields are an **authored normalized contract**, not guessed names on an installed SDK object. Source time must be verified advancing acquisition/simulation time; receive time and heartbeat/landed receive stamps refer to newly observed raw messages. Pass origin from a recorded verified initial state. A confirmed event is retained with its monotonic time; preserving raw messages and clock mappings is the adapter's obligation. Sampled dwell permits no gap beyond the frozen 0.5 s stale limit; it does not prove unsampled motion.

Frozen numerical A/B configuration and all acceptance criteria are unchanged. Adapter must still provide offboard keepalive/setpoint cadence and actual acks, installed lifecycle/reset, camera association and image deduplication. No generic SDK fields were invented. The core is not an operational flight runner.

Local retest commands (no simulator access):

```sh
python3 -B -m unittest discover -s simulators/rflysim/tests -v
python3 -B simulators/rflysim/run.py validate --config simulators/rflysim/audit-config.json
python3 -B simulators/rflysim/run.py run  # expected exit 2, closed gate
```

## Future measured-run evidence

Keep the original A/B/coupled-capture repeat and timing limits. After compatible host selection and authorization, inspect installed source, implement the adapter, replay these tests on Windows, freeze actual inputs/interfaces, then execute. C stays blocked without complete compatible released weights/task/adapter.

Every measured run must preserve this joined trace independently of chat:

`asset URL/hash + config hash + code/patch/installed build → command ID/setpoint → raw acknowledgment and mode/arm records → timestamped actual estimate AND simulator truth → actual camera pose/extrinsic/calibration → frame ID/path/hash`.

Preserve separate JSONL records for reference route, commands, raw acks/modes/arming/landed messages, PX4 estimate, simulator truth, actual camera poses and frame associations. Include IDs, units, coordinate/origin/scale, source/raw field mappings, source/acquisition clock meanings, UTC and receiver monotonic times with process ID/clock origin. Do not compare absolute monotonic times across processes without a verified common clock. A commanded camera pose is not actual pose. Unknown stage/association is null with reason; never use receiver time as acquisition. Keep immutable config, provenance (installer/SDK/model/scene/PX4/parameters hashes), dependency/OS/GPU/driver versions, seeds/split and policy weights `none`.

Control setpoints target 10 Hz, state 20 Hz, camera 10 Hz, GPU polling 1 Hz. Record actual intervals/deadline misses/stale/gaps/overflow counts, clock offsets/association uncertainty and simulation versus wall time. Camera/file/GPU queues cannot block control; failed essential logging invalidates completeness. Measure capture throughput, control rate and GPU usage separately; report unavailable policy latency and unknown acquisition latency as missing. Retain warmup and synchronization method; video playback FPS is not throughput.

Keep `run.json`, `commands.log` and `console.log`, underlying native exit codes even with tee, supervisor/cleanup attempts AND telemetry confirmations, failure/timeout detail, configs/patches/route/state/camera/frame records and media. Checkpoint closed files every 15 s and on failure. Freeze/test transfer before media, close writers, hash/size manifests, transfer resumably, verify local hashes and media opens. Stop only recorded audit-owned PIDs. No shutdown until verified preservation; never terminate the instance automatically.

Failure record template: **observed symptom; exact inputs/reproduction conditions; confirmed cause or remaining hypotheses; repair hypothesis/change/duration (within two attempts/2 h active budget); retest exit status/outcome; trace/media preservation and unmeasurable stages**. An unavailable field is an interface blocker, not a fabricated telemetry failure. No measured simulator run exists in this pass.

A local evidence review caught premature cleanup termination caused by comparing absolute monotonic clocks across Python 3.9/macOS processes. [Official Python time documentation](https://docs.python.org/3/library/time.html#time.monotonic) records the macOS cross-process guarantee starting at 3.10. The authored core now uses generation tokens and process-local elapsed timers; final tests check both lower and upper timing bounds. Superseded local logs/cases and repair/retest conditions are retained in the local result directory. This defect and the initial queue-fixture teardown error are ours, not RflySim findings.
