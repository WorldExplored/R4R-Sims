# GRaD-Nav usability decision and camera correspondence

## Firm decision

**NO-GO for calibrated camera replay in R4R using this released gate_mid package until scene/capture provenance is resolved.** The controlled diagnostic did not demonstrate camera correspondence. Native Gaussian rendering and direct dynamics/control integration are usable as research components. The package is not approved here as a calibrated real-scene replay baseline or a reproduced autonomous-navigation policy. This is a scope-specific decision, not proof that all authors' code or other maps are broken.

This pass started2026-10-09T03:31:03UTC and stopped compatibility debugging03:42:51UTC,11.8minutes within45minutes. One controlled1.1.4 compatibility attempt; the second was unused. No broad version search, training, parameter update, scene alignment fit, upstream change, driver change, extra rental or instance termination.

## What can go in and come out?

| Path | Inputs | Outputs | Usability for this audit |
|---|---|---|---|
| Native rendering | Matching Splatfacto config+Gaussian checkpoint+parser dataset, explicit camera-to-world matrices and intrinsics | Float RGB, PNG, expected axial depth and alpha | Executes; calibrated correspondence to released capture is not demonstrated |
| Direct dynamics | Achieved position/velocity/quaternion/rates; requested body rates and normalized total thrust | Next simulated state | Component tested; real-drone calibration unverified |
| D component chain | Named height PD controller -> dynamics -> achieved pose -> unchanged camera mount -> Gaussian scene | Synchronized actions, states, camera poses, RGB/depth and video | Demonstrated coordinate-level integration; camera pixels are not consumed by that controller |
| Learned-policy C | Matching original actor/critic package, observation RMS, VAE and trained visual network, map/task config | Learned actions and navigation outcomes | Blocked: compatible original weights not acquired; no replacement trained |
| R4R calibrated replay/fidelity | Existing reconstruction registered to calibrated real captures; known scale; trusted held-out poses/images | Corresponding novel-view observations and fidelity/downstream evaluation | Not usable with this package under current provenance; outdoor/altitude/sparse-capture/racing fidelity untested |

A Gaussian PLY alone is not the native config/checkpoint loader interface. Rendering, scripted feedback, original learned inference and real-scene fidelity are separate experiments. No complete visual-policy E2E result is claimed.

## Checkpoint restoration: demonstrated correct

Both NS1.1.3 and1.1.4 strict model loads report **missing keys=[];unexpected keys=[]**, with no fallback to non-strict loading. The Pipeline loader intentionally loads non-model state with strict=False after the separate strict model load; the reported empty key lists refer to that model load. All saved model tensors restore exactly, including camera-optimizer values and metric-network buffers. All six Gaussian arrays—means, scales, quats, opacities, features_dc and features_rest—match checkpoint shape, SHA256 and values with maximum difference0. Gaussian count265631. The checkpoint is the unchanged author asset `step-000029999.ckpt`. Saved step29999 versus loaded model step30000 is the Splatfacto loader's explicit behavior; it is recorded, not corrected. All learned parameter hashes before and after rendering are identical. Zero optimizer updates and zero training steps.

The checkpoint is a Gaussian reconstruction checkpoint, not the six-object navigation policy package. No missing Gaussian weights or random Gaussian substitute explains these images.

## Camera optimizer and filename mapping

Saved modeSO3xR3,270x6 adjustments. Across270rows, translation norm min/median/max0.000900322/0.015972268/0.041558184scene units; rotation tangent norm0.001360798/0.006330102/0.018274246radians (maximum about1.047degrees). Translation is not independently calibrated in metres. Saved camera optimizer Adam lr0.0001,eps1e-15, exponential final lr5e-7,max30000steps,warmup1000; these historical training settings were only inspected, not run.

The dataset loader sorts filenames, selects its0.9fraction training split and assigns `cam_idx` in that270-image training order. `camera_optimizer_mapping.json` gives every current training index, exact image filename and saved6-vector. The deterministic selection is `[0,floor((Ntrain-1)/2),Ntrain-1]` ->0,134,269 ->frame_00001.png,frame_00149.png,frame_00300.png. Selection did not depend on image quality. The checkpoint stores indexed adjustments but no original filename list; this mapping is exact for the released config/current loader, while historical training-order identity remains a provenance limitation.

Canonical cameras come from upstream `FullImageDatamanager.next_train` as a data-fetch operation only. Separately corrected cameras use upstream `CameraOptimizer.apply_to_camera` on that same training camera with its exact `cam_idx`. SO3xR3 rotates camera directions in world coordinates and adds translation independently. The model remains evaluation-mode, so corrections are not automatically reapplied. No correction was assigned to frame_00010 or any evaluation image. No training-mode render, optimizer step or alignment guess was used.

## Preprocessing and frame trace

Original images1280x720; original Kfx900.585815,fy896.445923,cx636.294495,cy363.463837. Brown distortion `[k1,k2,k3,k4,p1,p2]` is `[0.058455251,-0.114667729,0,0,-0.004756260,0.001671401]`. The canonical cached_train loader uses OpenCV optimal K withalpha0, a−0.5principal-point shift before undistortion and+0.5after, ROI[x0,y0,w1279,h719]. The resulting source/render comparison resolution is1279x719 and Kfx901.256592,fy904.189514,cx638.494019,cy360.933167. Sourceuint8 is converted to RGBfloat by/255; rendered floats are used directly for differences. No extra resize, gamma, exposure/color fit, mask selection or guessed crop.

In inference loader mode, downscale factor is1. Config orientation/centering=none,auto_scale=false,scale_factor1. Current loader's applied-transform provenance is `[X,Z,−Y]`, while saved dataparser_transforms.json records identity/scale1. Already saved poses are not blindly normalized again. Nerfstudio/OpenGL camera axes are xright,yup,zbackward; rendering uses upstream view-matrix conversion. No vehicle quaternion/mount inverse is used in these training-view tests, so the historical helper's rounded-mount residual cannot explain this diagnostic failure.

## Training-view image differences

Metrics compare full canonical preprocessed source RGB against render RGB in[0,1]. They diagnose correspondence on training views, **not held-out fidelity**. No lab-approved PSNR threshold is invented. The decision also uses visible failure to reproduce the gates/table/room structure; a flat/blurred image cannot serve calibrated replay merely because its average color yields a finite PSNR.

| Training image | Canonical PSNR dB | Saved-correction PSNR dB | Canonical MAE | Corrected MAE |
|---|---:|---:|---:|---:|
| frame_00001.png | 14.7467 | 14.8001 | 0.128966 | 0.127631 |
| frame_00149.png | 13.1784 | 13.0754 | 0.188038 | 0.191199 |
| frame_00300.png | 15.5847 | 15.5810 | 0.116591 | 0.116709 |

Saved corrections do not recover visible source structure. NS1.1.4 produces exactly the same18RGB/depth/alpha arrays as NS1.1.3 for all six renders. Source originals, canonical undistorted/cropped sources, uncorrected/corrected renders, absolute difference PNGs, rawRGB/depth/alphaNPYs and camera matrices are retained for both runs.

## Controlled version comparison

Baseline NS1.1.3 is unchanged. NS1.1.4 uses a new isolated venv with a .pth reference to the baseline dependencies read-only. Torch2.1.2+cu118 and gsplat1.0.0 are retained, with the same existing GCC11/CUDA11.8toolkit/cache. Only NS1.1.4 and its required adjustments were installed into the new venv: opencv-python-headless4.10.0.84,viser0.2.3,tensorly0.9.0. Actual OpenCV runtime4.8.0 ->4.10.0 is documented; the baseline had multiple OpenCV distributions. NS requirement validation and `pip check` pass. Imported model/datamanager module paths/hashes prove1.1.4 code was actually used; Torch/gsplat paths/hashes match baseline. Complete freezes/install logs are preserved. Baseline freeze before/after is byte-identical. This excludes this specific version/preprocessing change as the remedy for these views; it does not certify all possible historical environments.

## Surviving hypotheses and exact author information needed

1. The released Gaussian checkpoint may have been reoriented/translated/scaled for the navigation frame after reconstruction without equivalent capture poses being supplied. Request every applied4x4world transform and scale, its direction/order, and whether it was baked into Gaussian means/quaternions/scales.
2. The checkpoint/config/capture files may be from different scene revisions. Request a verified matching bundle and hashes for checkpoint, original config, transforms, calibration and input images, plus a reference render for the three named training images.
3. Historical training camera ordering/preprocessing may differ. Request original270-image training filename order, split rules, undistortion/crop/downscale steps and the exact training environment/package versions or commit.
4. Some other common interpretation issue could remain beyond the permitted version test. Neither strict restoration nor1.1.4 fixes it; no proof is offered that the authors' original experiment failed.

Do not fit an arbitrary transform to make images plausible. The needed correction must be supported by author provenance or independent calibration. A metric scale number1 in a config is not independent physical calibration.

## Direct usefulness for Real4Real and use cases

**Use now:** study/reuse the differentiable dynamics API; reproduce the native coordinate-level control/render chain; use the working native gate render as an integration diagnostic. **Do not use now:** this gate_mid bundle as a calibrated common-camera renderer baseline, an outdoor novel-view fidelity source or a reproduced autonomous policy. Indoor autonomy/racing need actual policy weights, validated collision/body volume and calibrated task/dynamics; these were not demonstrated. Outdoor sparse capture, altitude changes, vegetation/motion and real transfer remain research questions. Replacing Unreal's appearance with splats still requires registered scene geometry/cameras and independently appropriate physics/collision handling.

## Reproduction and complete deliverables

From the remote candidate: `bash simulators/grad-nav/launch.sh correspondence` runs the unchanged1.1.3 baseline with new run ID. The1.1.4 executed setup and invocation are preserved in correspondence-support. On the already prepared host the exact bounded invocation is:

```bash
cd /home/ubuntu/R4R-Sims-grad-nav
export CUDA_HOME=/workspace/R4R-Sims/artifacts/traveluav-openuav/dependencies/cuda-11.8
export PATH=/home/ubuntu/grad-nav-deps/env-render114-20261009T0337Z/bin:/home/ubuntu/grad-nav-deps/env-render/bin:$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}
export CC=/usr/bin/gcc-11 CXX=/usr/bin/g++-11 MAX_JOBS=2
export MPLCONFIGDIR=/home/ubuntu/grad-nav-deps/cache/matplotlib
export TORCH_EXTENSIONS_DIR=/home/ubuntu/grad-nav-deps/cache/torch-extensions
/home/ubuntu/grad-nav-deps/env-render114-20261009T0337Z/bin/python simulators/grad-nav/run.py correspondence --root /home/ubuntu/R4R-Sims-grad-nav --upstream /home/ubuntu/grad-nav-deps/upstream --timeout 300
```
 Setup scripts refuse overwriting their isolated env. These commands were executed here; a fresh host is unverified until preflight.

Deliverables: this firm usability/report; exact diagnostic source; two bounded run records/freeze/commands/console/GPU samples; restoration hashes/keys;270-image optimizer mapping; three paired training-view comparisons per environment with raw outputs; controlled dependency/module/pixel comparison; Mac checksums/decode verification; reproduction instructions; updated artifact index and a focused decision deck/PDF. Historic results/decks remain intact. Policy/E2E/fidelity limits are explicit.

Four shared-host TravelUAV logs identified by shutdown-readiness.json have now been copied with resumable rsync and SHA256/byte-verified on the Mac (195892bytes). No remote originals were removed. This clears that historical log-preservation blocker; it is not an automatic shutdown instruction. The instance remains running.
