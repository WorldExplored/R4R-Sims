> **Measured update, 10 October 2026:** [Two bounded flights and native RGB evidence](../../results/rflysim/eval-20261010T215531Z/README.md) supersede historical pending-runtime statements below. B1/B2 full-route and landing/disarm pass using PX4 estimates. A images/rate ran, geometric replay remains blocked and authored rotation conversion failed. Host Off, main artifacts Mac verified. See [installed guide](../../docs/rflysim/installed-execution.md). Historical records remain intact.

> **10 October 2026 update:** [Current execution readiness](../../docs/rflysim/current-execution.md) supersedes the historical host/installer/access-permission assumptions below. Execution is authorized on the selected AirGPU host; Moonlight desktop is verified, while SSH/transfer and a complete installer remain blocked. Numerical pending tests are preserved.

# Installed proof code

`installed_adapter.py` is the measured Free SDK adapter. It uses canonical installed source hashes, raw MAVLink, fresh mode/arm/land state, independent 75 s / 15 s supervision and a separate capture worker. `capture_adapter.py` records native RGB and CameraData independently. `analyze_evidence.py` reproduces measured plots/diagnostics from ignored raw evidence. Read [installed reproduction](../../docs/rflysim/installed-execution.md) first.

Local post-run corrections (camera degree units/durations, bounded camera cleanup, fresh cleanup queue and exit-status reporting) are not Windows retested. The numerical criteria and executed snapshots remain unchanged. Twenty-five local synthetic tests pass, separately from actual flight outcomes. Use Python 3.12 and `analysis-requirements.txt` in an isolated analysis environment. The historic `run.py` preparation gate stays closed and is a validator/preservation utility, not the installed entry point.

# Historical preparation tools

Execution is disabled. Read `../../docs/rflysim/handoff.md` and `runner-review.md` first. The reviewed configuration is `audit-config.json`; execution freeze remains incomplete pending the installed scene/SDK and host. Recovery code is historical only.

`python3 run.py validate --config audit-config.json` checks exact route/criteria/deadlines.
`python3 run.py readiness --config audit-config.json` reports blocked execution, exit 2.
`python3 run.py manifest --root <closed-result-directory> --output <manifest-outside-root>` hashes immutable evidence.
`python3 run.py verify --root <copied-directory> --manifest <source-manifest>` verifies byte sizes and SHA-256.

No SDK imports, networking, provisioning or simulator calls exist in the current entry point. The SDK-independent watchdog/queue/route/landing core is `runtime_core.py`, covered by synthetic local tests. The installed SDK adapter and Windows verification remain pending installed signatures, release compatibility and verified freeze. Authorization is recorded in audit-config.json and does not open the independent execution gate. Read `../../docs/rflysim/readiness.md` for the execution gates.

The deck builder uses the bundled Codex Artifact Tool, not python-pptx. To reproduce, supply `PRESENTATION_SKILL_DIR`, `RUNTIME_NODE_MODULES`, `RUNTIME_NODE`, `RUNTIME_PYTHON` from `load_workspace_dependencies`, make the package path available to the builder, and run `node build-preparation-deck.mjs <private-build-workspace> <result/deck-content.json> <new-output.pptx>`. Finalize, render every slide, inspect, then export the rendered PDF. Existing output files are preserved.
