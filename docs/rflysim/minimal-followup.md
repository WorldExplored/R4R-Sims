# Minimal future Windows follow-up

Prepared offline 11 October 2026 from `eval-20261010T215531Z`. AirGPU stays Off. The component judgment needs no additional run. Estimates below include desktop and collection overhead; they are not a new session authorization.

## Resolved offline

- B1/B2 minimum and full-route passes, takeoff, landing and disarming are supported by retained MAVLink/JSONL. Do not rerun both passed flights automatically.
- B1 ULog is already durable on the Mac. It supplies firmware identity, 660 initial parameters and 11 early startup changes. B1 parameter recovery needs no host access.
- Stock scene/component identities, L4 D3D11 selection and native camera capture are evidenced. Full scene/model hash inventories remain missing.
- Executed A1/A2 rotations were invalid because our helper sent radians to a degree field. The unexported strict-duration A1 retest still had that defect. Later corrected code has not run on Windows.
- All 1,237 native frames open. A1/A2/B2 review videos fully decode and private Drive downloads match their Mac hashes. No Windows media regeneration is needed.

## Optional recovery only: about 15–20 minutes

| Action | Conclusion enabled | Estimated time |
|---|---|---:|
| Resume the existing desktop and locate final transcript, B2 ULog, strict-duration A1 retest and saved final inventory/launcher records | Recover missing historical evidence without a simulator launch, if files exist. | 3–5 min |
| Hash installed scene/model binaries and final launcher; export current PX4 parameters if no historical inventory exists | Establish exact installed identity. Current parameters do not prove historical B2 settings. | 5–8 min |
| Close records, ZIP only missing evidence, upload to private Drive, download and verify bytes/SHA256/internal manifest on the Mac | Establish durable recovery. | 5–7 min |
| Confirm audit processes are closed, Stop the same instance and verify Off | Bound usage and confirm end state. | 2 min |

If a file is absent, record the absence. Do not recreate a historical transcript or overwrite the executed source. B2 raw telemetry already supports its pass; its missing ULog is a corroboration and reproducibility gap.

## Measurements only for a selected reuse role

| Action | Conclusion enabled | Additional time estimate |
|---|---|---:|
| Verify exported body truth origin, axes, units and known displacement | Metric motion replay to an external renderer. That renderer may supply its own camera and clock. | 10–15 min |
| Run corrected seven-pose A twice from a documented reset | Actual intended 15° yaw and 10° pitch, with strict capture duration. A duration-only retest cannot establish corrected angles. | 10–15 min after startup |
| Verify native body-camera origin/extrinsics, FOV axis, projection, optical frame and pixel orientation using known geometry | Calibrated native camera replay and geometric comparison. If independent geometry is unavailable, keep images and mark checks blocked. | 15–25 min, potentially blocked |
| Establish acquisition clock ownership/offset and bracketed truth interpolation | Acquisition-time native image-pose association and latency. Receiver time cannot replace acquisition time. | 10–20 min, possibly vendor clarification |
| Retest bounded cleanup first with an already landed vehicle, then a short flight only if necessary | Reliability of our unattended helper, if reuse is desired. Confirm raw log closure and meaningful exit status. | 5–10 min |
| Inspect installed import controls/terms and clarify Free custom-map eligibility | Usable reconstructed-mesh import on this build. No speculative engine build or purchase. | 5–10 min or an offline vendor answer |

These actions overlap and do not mandate a full rerun. A native calibration session might need roughly 35–60 minutes after recovery/startup and could remain blocked by geometry or vendor clock semantics. External motion mapping can omit native-camera work. Cleanup validation is relevant only when reusing the helper.

## Unchanged numerical contract

A: one RGB camera, 640×480, requested 10 Hz, FOV 90°. Preserve seven desired poses in `audit-config.json`, 5 s warmup, 3 s per pose including 1 s settling, 26 s capture and 40 s replay watchdog. Preserve 0.02 m / 1° repeated-pose and 2% image-dimension feature criteria. Timing uses linear translation and quaternion SLERP, maximum bracket gap 0.1 s and clock residual 0.02 s, with no extrapolation. Acquisition semantics stay explicit. Existing rate records already satisfy the record-rate check; do not automatically repeat the 5 s + 30 s / 45 s watchdog test.

B, only if specifically necessary for a selected measurement: preserve the exact NED route, 10 Hz targets, 75 s flight plus separate 15 s cleanup, 12 s leg deadline, position error ≤0.25 m for 2 s and freshness ≤0.5 s. Takeoff requires armed height ≥1 m for 1 s. Landing requires fresh ON_GROUND and speed ≤0.2 m/s for 2 s plus disarming. Do not modify criteria after results. SDK calls remain bounded at 2 s, telemetry connection at 15 s and startup at 120 s.

## Decision before restart

Select recovery only, external motion mapping, native calibrated replay or helper lifecycle, then obtain renewed authorization for that bounded session. Preserve old ledgers, code/configuration provenance and failures. Use a unique run ID and verify essential evidence on the Mac before stopping. No reinstall, new machine, training, HITL, paid license or external-renderer implementation.

The minimal reason for a restart is missing-file recovery or one chosen measurement gap. It is unnecessary for the current control/native-baseline verdict or offline review.
