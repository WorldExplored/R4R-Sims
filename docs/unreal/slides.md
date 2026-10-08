# Actual result deck map — 2026-10-08

Deck: `Unreal_R4R_Audit_2026-10-08.pptx`. Every native figure comes from locally preserved source-manifested run evidence. Gaussian/real-scene findings are labelled pending or blocked, and no slide attributes generated images to AirLab captures.

1. **Question and scope.** R4R small real outdoor capture → new camera route; target below 100 m. The 15 m capture → 50 m render is an open research question. A/B/C/S distinctions.
2. **Native system path.** UE4.27 packaged Blocks scene, AirSim dynamics/controls, client RPC, RGB/depth and collision provenance. No learned policy.
3. **Level A camera replay.** Eight 640×480 RGB captures and exact target/actual camera centers. Figure: `...5fe9b7c3/figures/rgb-contact.png`.
4. **A planar depth.** Same eight captures; 50 m display clip, 23.09 m wall sample. Figure: `...5fe9b7c3/figures/depth-grid.png`. Depth timestamp pairing limitation.
5. **Level B flight.** 1 m square at z=−2 m, P/velocity + SimpleFlight, five reached waypoints. Figure: `...a3d4be49/figures/trajectory-xy.png`.
6. **Timing and memory.** Editable measurements: image RPC 3.21 s, median capture interval 5.36 s (0.187 Hz), command median 4.70 Hz but 2.01 Hz over action span, sampled 769 MiB GPU. All from failed landing-check run. No renderer FPS or policy latency.
7. **Failed attempts and acceptance.** RPC race, stale port, spawn collision, waypoint run, `landAsync`/`LandedState` mismatch and new floor collision. Each has unique run ID. Distinguish route acceptance from landing.
8. **Gaussian input and UE gate.** Italink commit, Linux descriptor, UE5.5.4 editor, author PLY fields/scale transform; SceneCapture import/export and depth remain pending.
9. **Three architectures.** UE internal splat, external renderer with existing dynamics, UE removed. Named owners and unbuilt adapters.
10. **Applicability.** Indoor/outdoor sparse/racing: integration evidence and missing task/fidelity evidence. No native-scene performance ranking.
11. **Real-scene protocol.** Approved training-only captures, held-out calibrated poses including new altitude, common-scene matched route, masks/exposure, PSNR/SSIM/LPIPS and downstream outcomes.
12. **Handoff and evidence.** Machine, hashes, local artifact directory, source-manifest transfer check, supervision topics and next decision. Appendix notes cite exact URLs/run paths.

The presentation is an audit result, not a claim of outdoor reconstruction or real-drone transfer. Regenerate figures from raw records with `simulators/unreal/analyze.py` and inspect its `analysis.json`; source-manifest verification details are in [handoff.md](handoff.md).
