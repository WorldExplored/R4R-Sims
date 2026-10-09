# Observed rendering continuation

Recorded 2026-10-08 America/Indianapolis (UTC runs October9). Debugging was bounded to45min/two attempts; it stopped after12.12min and one materially different repair. No package install, training, additional rental, system-alternative/driver change or instance termination.

## Confirmed compiler root cause and repair

Default `/usr/bin/gcc`12.3.0 reports `cc1plus` without a resolved executable path. Both `/usr/bin/gcc-11` and `/usr/bin/g++-11`11.4.0 resolve `/usr/lib/gcc/x86_64-linux-gnu/11/cc1plus`. The historical nvcc command lacked `-ccbin`. The same minimal CUDA program without explicit selection reproduced:

```text
gcc: fatal error: cannot execute ‘cc1plus’: execvp: No such file or directory
compilation terminated.
nvcc fatal   : Failed to preprocess host compiler properties.
```

Minimal C++ and CUDA programs compiled and executed with GCC11. Candidate launch now sets CC/CXX to GCC11/G++11; emitted build uses `-ccbin /usr/bin/gcc-11` and CXX `/usr/bin/g++-11`. gsplat1.0.0 actually linked `gsplat_cuda.so` and rendered. This establishes the compiler-selection repair, not merely an environment-variable change. No unsupported-compiler checks were bypassed. Historical errors and before/after environment/build commands remain in [compiler evidence](../../results/grad-nav/20261009T020316Z-compiler-preflight/).

## A: rendering works; capture alignment is unresolved

The frozen five-camera route from `20261009T013743Z-a-b58f3b/reference_route.jsonl` is preserved unchanged numerically (new derivation asserted within1e-6). Loaded gate_mid step30000/265631 Gaussians, hardcoded K `[185.1824036,185.2008057,129.2303925,72.4736023]`,256×144. The authors' active renderer loops over cameras. Same model, settings and numerical camera matrices through direct Nerfstudio and author path give **zero maximum RGB, depth and camera matrix differences** for all five poses.

Observed float RGB range across five poses is 0.052663464–0.597270906. RGB float NPY, uint8 PNG, depth, alpha, raster depth, K/view matrices are preserved. Model output is clamped[0,1]; no extra gamma transform is added. Linear-radiance semantics are not established.

**Image-based acceptance remains partial:** first frozen view is blurred and does not visually match associated `frame_00010.png`. The rounded mount introduces maximum reference rotation residual0.0001499653. The direct path receives the same effective matrix, so pixel parity does not validate physical camera registration. A diagnostic with exact COLMAP-derived pose and original capture K also produces the blurred view. COLMAP conversion matches released transforms.json exactly (max delta0). Saved training dataparser transform is identity/scale1; loaded parser reports the recorded COLMAP applied transform while leaving the already saved poses in their frame. No normalization or hardcoded mount/scene transform was added or altered. Capture-to-checkpoint relationship/artifact consistency remains a hypothesis requiring author provenance or independently verified registration. The released camera-path pose produces a recognizable room looking downward, but is a separate diagnostic with hardcoded K, not a replacement for A or a reproduction of that path's75° FOV.

## Depth and background

Pinned Nerfstudio uses gsplat `RGB+ED`: alpha-normalized expected camera-axis depth, scene units; it is not Euclidean ray range, guaranteed nearest surface or body-volume collision geometry. In all five frozen poses, alpha>0 everywhere; returned depth exactly equals raw raster ED, and RGB exactly matches clamped raster RGB plus(1−alpha)×background. No-hit fallback could not be exercised by those five views.

A separate camera at[0,0,−1000], identity orientation, looks away from the scene. It yields alpha0 for100%pixels, RGB equal to evaluation background (range0.1490000–0.2157000), raw ED0 and returned depth0. This confirms `where(alpha>0, ED, max(ED))` for this no-hit case. A zero depth is not contact or a measured obstacle distance. Empty crop output's separate constant10 path is only statically inspected, not executed. Metric scale and real depth truth remain blocked.

## Synchronized timing on this host

Each path has five warmups,50 measured calls, CUDA synchronization before/after each interval. Five-route comparison occurs first. Timings use reference pose0 and256×144,265631 Gaussians. These are diagnostic workload measurements despite unresolved capture alignment, not fidelity-qualified camera or larger outdoor-scene performance promises.

| Scope | Median ms | p95 ms | Rendered images / wall s | Peak Torch allocated bytes |
|---|---:|---:|---:|---:|
| Direct model render, resident GPU camera | 2.7647 | 2.8021 | 361.56 | 174016512 |
| Author render + pose/stack | 3.4256 | 3.4903 | 288.51 | 174164480 |
| Author raw RGB/depth + CPU transfer | 3.4996 | 3.5952 | 284.48 | 174164480 |

Torch peak reserved190,840,832bytes; allocation excludes driver/context/non-Torch memory. GPU/driver sampling every1wall second is preserved separately and can miss subsecond peaks. Direct uses a preloaded GPU camera matrix and excludes camera upload/CPU transfer/disk IO, author includes camera transform and stack, raw observation includes CPU transfer and excludes file writes. Instrumentation wrapper retains last raster outputs; measurements include this bookkeeping. Learned-feature/policy latency remains blocked. No sustained closed-loop rate is inferred from render throughput. Video playback20FPS is encoding cadence, not throughput.

## D: achieved-state coordinate coupling

Run `20261009T020926Z-d-748818` uses the existing height PD kp2 N/m,kd0.8 N/(m/s),target1.25,initial1.15 and zero rates/noise. This separate predeclared D start has−0.10 perturbation; B's−0.25 perturbation and completed gains/outcomes were not rerun/tuned.20actions,21states including initial,20mounted poses and20RGB/depth frames are synchronized at0.05simulation seconds. Actions precede their achieved state/camera sample; wall UTC and elapsed times accompany records. No missing samples. Applied action fields record identical requests before torchfloat32 conversion, with no native delay/filter; exact float32 input values are independently derived in `actions-float32-derived.jsonl`. These derived values are not new sensor measurements.

Final height1.218289733,drift+0.068289733,error0.031710267; no overshoot/saturation in1s. Achieved position+[-6,0,0],Y/Zflip, wxyz→xyzw and unchanged mount feed the renderer. Observed first/final views are upright and show gates/ceiling. The mounted-camera translation follows achieved height by0.068289733scene units. Numerical composition checks and image-based upright scene validation are distinct records. This establishes the causal coordinate path action→dynamics→achieved state→mounted camera→RGB/depth. It does not establish metric capture registration, calibrated flight, native reward/collision/task success, learned policy or outdoor fidelity.

Integrated wall duration4.730206s includes cold renderer initialization inside the first frame, CPU copies/file writes and video encoding; it is not steady control latency. H264 video:20frames,256×144,1s at20playback FPS. Raw depth/RGB are uncompressed NPYs. Planned height setpoint is separate from achieved vehicle and camera records. No learned modules were used.

## Preservation and scope

All16 renderer/dynamics historical+new run directories are locally copied and bytes/SHA256 checked; compiler diagnostics are additionally preserved.1213scientific input files/1,139,790,444bytes reverified against the committed source manifest. Original captures are preservation/qualitative orientation material; trustworthy held-out fitting/reconstruction exclusion was not supplied. No fidelity metric is computed. C remains blocked by compatible original actor,normalizer,VAE and trained visual components.

Collection used explicit resumable rsync calls during build and after settlement with new SSH connections; all completed transfers returned0. No background periodic collector or automatic reconnect cadence is claimed. Settled hash verification follows transfer. No remote evidence/toolkit deletion. No unrelated files,environments,drivers,processes or other candidate code changed; final ownership checks accompany closeout. Instance remains running.

Latest A timing run: `20261009T022120Z-a-e1d652`. Earlier A timing retained; its direct interval included camera tensor construction/upload. The latest interval preloads the matrix, then repeats only the frozen five-camera check and5warmups/50samples. This corrects measurement scope, not scene quality or controller tuning. No second compiler/compatibility repair.

D video decoded locally with macOS AVFoundation at all20timestamps after hash-verified transfer. Initial sandboxed decoding failed with AVFoundation−11821/OSStatus−12911; the same unchanged file decoded outside the sandbox. No media/package repair. Verification source and console retained beside D records.
