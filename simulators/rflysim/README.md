> **10 October 2026 update:** [Current execution readiness](../../docs/rflysim/current-execution.md) supersedes the historical host/installer/access-permission assumptions below. Execution is authorized on the selected AirGPU host; Moonlight desktop is verified, while SSH/transfer and a complete installer remain blocked. Numerical pending tests are preserved.

# RflySim preparation tools

Execution is disabled. Read `../../docs/rflysim/handoff.md` and `runner-review.md` first. The reviewed configuration is `audit-config.json`; execution freeze remains incomplete pending the installed scene/SDK and host. Recovery code is historical only.

`python3 run.py validate --config audit-config.json` checks exact route/criteria/deadlines.
`python3 run.py readiness --config audit-config.json` reports blocked execution, exit 2.
`python3 run.py manifest --root <closed-result-directory> --output <manifest-outside-root>` hashes immutable evidence.
`python3 run.py verify --root <copied-directory> --manifest <source-manifest>` verifies byte sizes and SHA-256.

No SDK imports, networking, provisioning or simulator calls exist in the current entry point. The SDK-independent watchdog/queue/route/landing core is `runtime_core.py`, covered by synthetic local tests. The installed SDK adapter and Windows verification remain pending signatures, compatible host and authorization. Read `../../docs/rflysim/readiness.md` for the execution gates.

The deck builder uses the bundled Codex Artifact Tool, not python-pptx. To reproduce, supply `PRESENTATION_SKILL_DIR`, `RUNTIME_NODE_MODULES`, `RUNTIME_NODE`, `RUNTIME_PYTHON` from `load_workspace_dependencies`, make the package path available to the builder, and run `node build-preparation-deck.mjs <private-build-workspace> <result/deck-content.json> <new-output.pptx>`. Finalize, render every slide, inspect, then export the rendered PDF. Existing output files are preserved.
