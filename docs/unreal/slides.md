# Unreal R4R audit presentation map — 2026-10-08

Deck: `Unreal_R4R_Audit_2026-10-08_v2.pptx` (13 slides). Builder: `simulators/unreal/build_slides.mjs`. All displayed camera images and plots are generated from locally copied, VM source-manifested evidence; S control images are **failed-test evidence**, not a Gaussian fidelity result.

1. **Title and status.** User-supplied A5000; native A/B demonstrated, Gaussian sensor RGB failed, real scene pending.
2. **Real4Real question.** Small real residential/suburban/campus capture below 100 m; 15 m capture → 50 m render unresolved. A/B/C/S distinctions.
3. **Native Blocks path.** UE4.27 packaged scene, AirSim control/dynamics/collision, RGB/depth and state. No learned policy.
4. **A camera replay.** Eight target/actual centers at 640×480. Actual RGB contact sheet from `ue-20261008T215319Z-a-5fe9b7c3`.
5. **A planar depth.** Eight paired depth arrays, displayed at 50 m clip. Five-column first-frame RGB/depth edge check; depth timestamp limit.
6. **B closed-loop route.** Actual versus requested 1 m square; five reached waypoints, P velocity script and SimpleFlight. Landing not confirmed.
7. **Timing/resources.** Measured image RPC, actual 0.187 Hz capture, action intervals and rate across action span, sampled GPU memory; 2 FPS video playback is separate.
8. **Failures.** Startup race, occupied port, spawn collision, later new floor collision and `LandedState` failure. Unique IDs retained.
9. **Gaussian runtime gate.** UE5.5.4 Linux `BuildPlugin` and author PLY import passed. Ticked UE cube base-color image versus near-black splat final-color image from `ue-20261008T225105Z-s-control-e488bef0`. The lit cube scene-color was also black, so isolate the camera render channel first.
10. **Three architectures.** Splats inside UE, external splat observations with dynamics retained, or UE removed with replacement owners and adapters.
11. **Applicability.** Indoor/outdoor sparse/racing questions; no outdoor reconstruction, novel-view fidelity or real transfer result.
12. **Machine/space.** Supplied Ubuntu A5000 graphics VM, actual ZIP/build sizes and tested Vulkan; cheaper 8 GB Vulkan VM only a provisional packaged-Blocks option.
13. **Next gate and handoff.** Correct final-color SceneCapture control, then actual splat RGB; separately obtain approved AirLab capture/calibration/holdout for real-scene research. Source hashes and artifact paths.

The deck's speaker notes point to run IDs and primary sources. It does not compare unrelated Blocks and vase scenes or report fabricated fidelity metrics. The follow-up science figure requires one scene with matched mesh/splat representations or approved held-out real images, matching camera poses, intrinsics, resolution, scale and documented lighting/exposure assumptions.

To rebuild the deck, first verify the local run folders against their VM-created `source-manifest.json` with `simulators/unreal/manifest.py verify`. Set `UNREAL_ARTIFACT_ROOT` to their parent directory, `SKILL_DIR` to the installed Presentations skill directory, and `RUNTIME_PYTHON`/`RUNTIME_NODE_MODULES` to its bundled workspace dependency paths. Then run `node simulators/unreal/build_slides.mjs` from the repository root. The builder validates the 13-slide package and layout before publishing. It refuses to overwrite an existing final deck; preserve the current copy or remove it deliberately before regenerating.
