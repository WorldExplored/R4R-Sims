# GRaD-Nav Real4Real findings

Audit date 2026-10-08 in America/Indiana/Indianapolis. Runs use UTC October9. **Recommendation: reuse the tested differentiable dynamics component for controlled research diagnostics, and defer the complete GRaD-Nav renderer/policy workflow for Real4Real.** The selected Gaussian scene loads, but rendering is blocked by the host compiler. The central outdoor novel-view fidelity question remains untested.

## Independent status

| Experiment | Status | Evidence and meaning |
|---|---|---|
| A known-camera rendering | Failed, rendering blocked | Four A attempts preserve path/shape/launch failures and final CUDA JIT compiler error. Numerical five-pose routes exist for later attempts. No RGB or raw rendered depth was produced. No render throughput, median/p95 render latency or rendered-camera validation is claimed. |
| B force balance | Demonstrated short component behavior | 20×0.05 s, initial height1.25 m, thrust9.81/24, zero body rates/noise. Final1.25 m, measured drift0.0 at float32 precision. This does not test displaced-altitude recovery. |
| B feedback smoke | Demonstrated short component behavior | 20×0.05 s, initial1.0 m/setpoint1.25 m, perturbation−0.25 m, PD gains kp2 N/m and kd0.8 N/(m/s). Final1.170566 m, error0.079434 m, drift+0.170566 m, no overshoot within1 s, no saturation. |
| B bounded feedback extension | Demonstrated response with overshoot | 100×0.05 s with same gains and perturbation. Final1.214410 m, error0.035590 m, drift+0.214410 m. Overshoot above setpoint0.102959 m. First entry into authored0.02 m diagnostic band at1.25 s. This is not settling time and is not a lab acceptance threshold. No saturation. |
| D causal dynamics/rendering | Failed, rendering blocked | Requested actions reached direct dynamics then the mounted-camera renderer, which failed at JIT. No completed synchronized achieved-state/camera/image sequence. Physical metric alignment also lacks independent validation. |
| C original learned policy | Blocked | No compatible released six-object actor/critic/normalizer/VAE/visual checkpoint. Public Gaussian checkpoints and mocap tensors do not satisfy C. No random features, VAE output substitute, training or GRaD-Nav++ substitution. |
| Real-scene fidelity | Blocked | Existing author capture/reconstruction inputs acquired, but trustworthy held-out exclusion across reconstruction/fitting is not supplied, and no renders succeeded. AirLab capture, calibrated metric frame, held-out split and downstream model/references are also missing. No PSNR/SSIM/LPIPS/outdoor or real-transfer results. |

B uses the authors' pinned dynamics via a direct module import. Its named adapter controller observes achieved height and vertical velocity, requests zero body rates and normalized total thrust `(9.81 + 2*(1.25-z) - 0.8*vz)/24`, clamped0–1. It bypasses native visual observation, policy, CENet, delay/filter and reward/contact logic. Dynamics mass1 kg, inertia[0.01,0.012,0.025] kg m², angular PD[1,1.2,2.5] and[0.001,0.001,0.002], inner200 Hz, outer20 Hz, ten inner steps per outer tick. All requested/applied actions and achieved state samples are preserved. Force/smoke have21 state records and20 actions; recovery101 states/100 actions. No state samples are missing in completed B runs. Dynamics median step latency around14.0–14.3 ms on this host excludes transfers/logging, after five disposable warmups and CUDA synchronization. This is component timing, not policy latency or sustained online control rate. Torch peak allocated8,547,840 bytes excludes CUDA context and allocator/driver totals, which have separate1 s GPU samples.

## Camera algebra versus rendered validation

Exact helper definitions were executed from the baseline AST without importing learned modules. Identity, yaw90 and translation checks pass. The camera helper actually accepts xyzw although its docstring says wxyz. Dynamics uses wxyz. The environment flips Y/Z after adding[-6,0,0], then the helper applies F, rounded mount and camera-basis matrices. These checks establish numerical composition only. No image-based flips, visible-feature matching, direct-versus-author RGB/depth equivalence or native scale/alignment was validated. The rounded mount rotation has Frobenius orthonormality residual0.00042425 and remains unchanged.

Historical failed-run metadata labels RGB as linear, which is an unverified pre-render assumption. Treat model RGB as a [0,1] image output with no additional color transform; linear-radiance semantics were not established. No pixel-based depth/background validation occurred.

The loaded model has the hardcoded rendered-camera calibration scaled to256×144: fx185.1824, fy185.2008, cx129.2304, cy72.4736. Original capture intrinsics differ. Scene metadata records dataparser scale1.0 and its applied transform, but those numbers alone do not independently calibrate real-world metric scale. The active helper render path applies no dataparser normalization. The alternate render_quad_poses path has incompatible expectations and unset normalization members. See exact code references in sources.md and numerical conversion.json.

## Native collision and termination

Native obstacle handling filters points in a forward angular FOV and returns nearest XYZ distance. Synthetic diagnostics returned0.1 m for a front point but infinity for a rear point only and for a coincident point. This is a point-distance/reward mechanism, with incomplete view/point coverage. It supplies no swept body-volume collision or physical contact response. The collision-limit scalar is not a demonstrated termination/contact condition.

**Termination-field defect:** baseline `envs/drone_long_traj.py:777` calculates body-rate magnitude from privileged indices10:13. Quaternion occupies9:13 and angular rates13:16. A normalized quaternion slice cannot exceed the configured15 rad/s threshold. This is a source-index defect, not an observed native-policy flight failure. Direct B bypasses this code. No upstream patch was applied.

## Setup failures and preservation

The original README archive IDs returned404. The author-linked folder exposes replacement archives; both downloaded and were hashed. Full Gaussian archive5,049,024,705 bytes expands5,826,839,573. Point archive293,772,935 expands336,000,446. Selected gate_mid scientific inputs total1,139,790,444 bytes. The four Gaussian configs and six geometric clouds are inventoried independently. Only the selected inputs were extracted/used and copied to the Mac.

Two adapter repairs preserve the original failures: checkpoint-root relocation and scalar-camera shape. A launch PATH correction exposed an already installed Ninja. Final A/D failed with exact error `gcc: fatal error: cannot execute ‘cc1plus’: execvp: No such file or directory`, followed by nvcc preprocessing failure. Default gcc is12.3.0, g++11.4.0 and cc1plus exists under the GCC11 directory. This is a plausible compiler-selection mismatch, not a confirmed repaired cause. The user stopped further compiler/package repairs. See repair-history.json and full console logs.

The recovered None-noise B definition independently fails because upstream leaves thrust_noise undefined. The deterministic adapter uses noise standard deviation0.0 without changing upstream. No learned policy or scene was trained. Isolated audit environments and caches are under /home/ubuntu/grad-nav-deps. Existing TravelUAV CUDA toolkit was read only. No unrelated files, environments, drivers or processes were changed or removed. GPU was idle at preflight. The canonical local Unreal edit and remote /workspace/R4R-Sims checkout were preserved. No instance termination occurred.

## R4R scope and comparison

Outdoor residential/suburban/campus use below100 m requires a real capture with trustworthy calibrated poses and held-out horizontal/vertical trajectories. Capture at15 m to render at50 m remains a research question. Sparse capture coverage and sparse physical content are different risks. Vegetation, occluded surfaces, changing lighting and moving objects were not evaluated. Indoor/gate results reported by the paper motivate further work but are not measurements in this audit. Racing needs validated task/gate outcomes, high-speed sensor effects and dynamics calibration.

Replacing Unreal visuals with splats is plausible as an appearance interface, but this audit has not produced rendered observations. Gaussian depth needs alpha/background semantics and metric validation; splats do not automatically establish collision geometry or physics. Later common-scene work should freeze one approved existing reconstruction, a metric frame and calibrated camera route shared by both renderers. Compare held-out images first, then a supplied downstream task. No new scene reconstruction is authorized here.

Repository comparison evidence was read at Project AirSim db3891792f312c1cb8575f19465a40aafff741a0, Unreal bc14c24ad7288848019a4aea541853980fa2d7bb, TravelUAV568759aca5628858f8881407de6562d986190280. Their native scenes and workloads differ. They document packaged-camera/controller evidence and their own failures, not a matched speed or policy ranking.
