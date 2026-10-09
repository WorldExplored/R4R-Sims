# Frozen execution definitions

Recorded 2026-10-08 local date. This is an integration audit, not an outdoor fidelity benchmark. Baseline upstream d9b00e16107338e49071c65f44582c013e522633. Current inspected upstream 95218abe9a5d355519cdaab78d915365303066fe.

A preserves five offsets from the prior runner: reference evaluation camera, then +0.1 and -0.1 on transformed scene X and Y, unchanged orientation. Numerical absolute matrices cannot be recovered because no scene camera was supplied in phase 1. These would be derived and frozen before rendering if the matching scene is available. They are scene units until dataparser scale is verified. No pose output is invented. At least 5 warmups and 50 measured renders, matching direct/author paths, sync around GPU intervals, median/p95, render-only versus raw observation timing. Learned feature timing requires the actual trained visual network.

B force balance: initial [0,0,1.25] m, zero velocity/rates, wxyz [1,0,0,0], normalized thrust 9.81/24, 20 ticks at 0.05 s. B smoke: recovered prior initial height 1.0 m versus setpoint1.25 m, gains kp2 N/m and kd0.8 N/(m/s), desired thrust (9.81+2*(1.25-z)-0.8*vz)/24, clamp0..1, desired body rates zero. Dynamics mass1kg, inertia[0.01,0.012,0.025], angular PD[1,1.2,2.5]/[.001,.001,.002], 200Hz inner loop, 10 substeps/tick. Recovered None-noise setting is executed separately as a baseline failure diagnostic. Deterministic adapter uses noise std0.0, not None. A bounded extension uses the same feedback law for100ticks/5s, with initial -0.25m height perturbation. Log every requested/applied action and state. Diagnostic 0.02m error band is an explicitly authored response-time diagnostic, not a lab-approved success threshold. Fixed horizon or nonfinite error terminates. Report drift, error, first band entry, overshoot and saturation.

Numerical checks execute exact AST-selected helper functions without Nerfstudio imports. Identity, yaw90 and translation check actual xyzw helper and wxyz dynamics orders. Environment Y/Z flips and [-6,0,0] offset compose once with the camera mount. Native scene transform/metric scale remains a separate gate. Synthetic FOV distance diagnostics test rear, front and coincident points without claiming native obstacle coverage.

D requires the actual scene and verified alignment. Use B's bounded achieved state under the named adapter controller, convert achieved state through A's verified mount, render each sampled pose. Never animate desired camera motion independently. If assets/scale cannot be verified, D stays blocked.

C inspects author repository releases, README/project and Drive assets once. Missing actor, critic/normalization, CENet/VAE or trained visual projection blocks inference. Explicit --play flags are mandatory and optimizer/parameter updates must be checked if weights become available. No training.

Fidelity requires calibrated original images, held-out split provenance and an existing compatible reconstruction. Missing inputs block PSNR/SSIM/LPIPS and downstream perception assessment.

Compatibility limits: two documented repair attempts and two hours excluding downloads. Do not install the full rendering stack if scene acquisition is blocked. No old candidate data or processes are removed without preservation/ownership verification.
