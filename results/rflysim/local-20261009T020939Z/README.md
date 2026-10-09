# RflySim bounded implementation pass / local-20261009T020939Z

**Preparation-ready: yes. Execution-ready: no.** Synthetic local tests only; no simulator, SDK, GPU, host connection, install, flight or camera experiment. Branch `audit/rflysim`, base `dd470aff5f9ed6eebf8859e136328c9cbc984570`; published implementation revision is recorded in `revision.json` after commit.

| Check | Result | Evidence |
|---|---|---|
| Preserved preparation tests | 6 pass | [Final console](console.log) |
| Added narrow authored-core tests | 14 pass | [Source](../../../simulators/rflysim/tests/test_runtime.py), [synthetic cases](local-cases/) |
| Blocking call and phase watchdogs | Local pass; independent parent termination, recorded exit status | [Blocked call](local-cases/blocked-call.json), [flight/cleanup limits](local-cases/bounded-flight-and-cleanup.json) |
| Capture/file/GPU isolation and queue pressure | Local pass; blocked side workers do not block control; drops counted | [Side workers](local-cases/isolated-side-workers.json), [queue pressure](local-cases/queue-pressure.json) |
| Route/landing evaluator | Local pass on synthetic samples; false landing/stale data rejected | [Synthetic route](local-cases/synthetic-route-and-landing.json), final console |
| Configuration and execution guard | Unchanged config validates; readiness/run exit 2 as expected | [Commands/exits](commands.log), [run record](run.json) |
| A / B minimum / B full / repeat / coupled capture | **Not run or measured**, all original tests pending | [Readiness checklist](../../../docs/rflysim/readiness.md) |
| C / AirLab fidelity | **Blocked**, compatible released path and research assets missing | [Handoff](../../../docs/rflysim/handoff.md) |

Our script defects, installed SDK uncertainty, upstream launcher hazards, platform blockers and absent research assets are separated in [runner review](../../../docs/rflysim/runner-review.md). [Failure/repair/retest records](failures.json) retain the initial queue fixture error and premature local watchdog termination; [superseded cases](before-clock-fix/) are explicitly local-only. The corrected core uses parent-clock elapsed deadlines and child-local duration checks, with polling/reap overhead recorded. Actual Windows scheduling/SDK/camera/flight behavior is unverified.

[Linux feasibility evidence](../../../docs/rflysim/readiness.md#complete-free-linux-camera-path-bounded-investigation), [official release listings](release-assets.json), [author repository inventory](author-repositories.json), [dated source hashes](source-manifest.json), and [inaccessible older links](link-checks.json) do not establish a complete licensed Free Linux renderer. Documented candidate remains native Windows/UE4 + default WSL1 PX4 with GPU desktop. No speculative workaround attempted.

[Gaussian path classifications](../../../docs/rflysim/interfaces.md#gaussian-paths-implementation-classification-bounded-follow-up) distinguish supported native building blocks, conditional small pose replay adapter, substantial dual-renderer/visual-controller integration and unresolved native splat/image injection paths. No renderer replacement implemented. Decision remains **defer renderer adoption; retain candidate dynamics/control host/native visual baseline**.

## Reproduce local checks and verify preservation

From the isolated checkout:

```sh
python3 -B -m unittest discover -s simulators/rflysim/tests -v
python3 -B simulators/rflysim/run.py validate --config simulators/rflysim/audit-config.json
python3 -B simulators/rflysim/run.py verify --root . --manifest results/rflysim/local-20261009T020939Z/file-manifest.json
python3 -B simulators/rflysim/run.py verify --root . --manifest results/rflysim/local-20261009T020939Z/asset-manifest.json
```

No dependency install needed for local checks. See [preservation verification](preservation.json) for hashes and media opens. Original 60-file prep package was verified **before** notes changed, then copied byte-for-byte to ignored `artifacts/rflysim/local-20261009T020939Z/preparation-snapshot/`. [Prior manifest/provenance](prior-preservation.json) records its exact retained paths. To reverify the original manifest now, use that snapshot as the root (or the original `dd470af` Git revision); updated working-tree notes intentionally differ from the historical prep manifest. Five recovery originals/imports and existing PPTX/PDF/previews are unchanged. Full old slide renders remain local. No new presentation or measured-results deck created.

Authored patch and bounded source snapshots are retained under ignored `artifacts/rflysim/local-20261009T020939Z/`, inventoried by byte count/SHA-256; all outputs were generated locally, so no remote transfer or shutdown occurred. Measured media remain absent because execution is blocked.

Smallest prerequisite: official Free Edition ISO link/file/terms plus an explicitly selected Windows GPU desktop and authorization for host inspection. Then inspect installed interfaces and complete the adapter before preserved A/B/capture execution.
