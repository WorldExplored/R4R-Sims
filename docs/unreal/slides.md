# Unreal R4R audit presentation map — 2026-10-08

Current deck: `Unreal_R4R_Audit_2026-10-08_v3.pptx` (17 slides). Builder: `simulators/unreal/build_slides.mjs`. v2 and [its map](archive/slides-d981d5a.md) remain intact. All camera images and plots come from locally copied, VM source-manifested evidence. The dark splat frame demonstrates narrow export and carries no fidelity result.

The current deck incorporates [focused validation](focused-validation.md) and [closeout recovery](../../results/unreal/closeout-20261008/recovery.json). It explicitly distinguishes partial B acceptance, unvalidated splat appearance, higher-order SH loss and unresolved R4R science. No GPU experiment ran during this deck update.

1. **Title and status.** Camera checks pass; flight acceptance and splat appearance remain unresolved. Complete R4R workflow unproven.
2. **Real4Real question.** Small real residential/suburban/campus capture below 100 m; 15 m capture → 50 m render unresolved. A/B/C/S distinctions.
3. **Native Blocks path.** UE4.27 packaged scene, AirSim control/dynamics/collision, RGB/depth and state. No learned policy.
4. **A camera replay.** Eight target/actual centers at 640×480. Actual RGB contact sheet from `ue-20261008T215319Z-a-5fe9b7c3`.
5. **Yaw sanity.** Large yaw changes visibly alter the scene. Recorded capture poses match; RGB/depth timestamps differ by 5–8 ms.
6. **A planar depth.** Original eight arrays, 50 m display clip and five-column spatial check. Original missing depth timestamps remain missing.
7. **B route.** Five square waypoints reached; full acceptance remains failed.
8. **Isolated B failure.** Altitude/vertical-velocity/LandedState trace. Takeoff False despite flight, land True despite Flying after contact.
9. **Timing/resources.** Measured RPC latency, 0.187 Hz images and sampled memory; renderer throughput and policy latency unmeasured.
10. **Failures preserved.** Startup/port/spawn failures and reproduced landing-state discrepancy, with separate attempt IDs.
11. **Final-color export.** Usable mesh and one visible dark splat frame after light correction. Appearance remains unvalidated.
12. **Representation loss.** Selected importer drops higher-order SH. This limits view-dependent appearance and does not explain the dark frame by itself.
13. **Three architectures.** UE internal splat, external observations with dynamics retained, or full UE removal. Unbuilt owners/adapters remain explicit.
14. **Applicability.** Indoor/outdoor/racing limitations; complete R4R workflow unproven.
15. **Host and storage.** GPU experiments stopped. Proven A5000 compatibility and actual archive sizes; cheaper machine remains provisional.
16. **Next science.** Same-PLY matched-camera reference comparison before more scenes; approved calibrated outdoor holdout afterward. Control-stack diagnosis is separate.
17. **Recovery and instance dependency.** All 18 runs and required inputs/project assets locally recoverable. TRAVELUAV uses a different A6000 host; no other current audit dependency found. Instance remains running.

The deck's speaker notes point to run IDs and primary sources. It does not compare unrelated Blocks and vase scenes or report fabricated fidelity metrics. The follow-up science figure requires one scene with matched mesh/splat representations or approved held-out real images, matching camera poses, intrinsics, resolution, scale and documented lighting/exposure assumptions.

To rebuild, verify the run folders against their VM source manifests, then set `UNREAL_ARTIFACT_ROOT`, `SKILL_DIR`, `RUNTIME_PYTHON` and `RUNTIME_NODE_MODULES` to the existing evidence and bundled presentation runtime. Run `node simulators/unreal/build_slides.mjs` from the repository root. It reads the closeout recovery record and validates the 17-slide package/layout before publishing. It refuses to overwrite the final deck; use another version filename for later changes. v2 can be rebuilt with the builder at commit `d981d5a`.
