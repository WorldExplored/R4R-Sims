# TravelUAV/OpenUAV — local evidence review

Reviewed 2026-10-08 (local time). **Read-only recovery and analysis of existing evidence; no old-host connection, installation, asset download, rental, training or simulator/model experiment.** GitHub was queried only for the audit branch and used for the authorized review push.

## Verdict and locations

We can explain the recorded native A/B/C workflows and bounded outcomes confidently. The required **manifest-listed unique outputs and scientific inputs survive locally**. Fresh checks verified **37 runs, 2,581 files / 685,225,135 bytes, and nine archives**, with zero size/SHA-256 mismatches or decode errors. This is preservation of evidence, not a self-contained executable simulator installation.

- Previously pushed audit commit: [`568759aca5628858f8881407de6562d986190280`](https://github.com/WorldExplored/R4R-Sims/commit/568759aca5628858f8881407de6562d986190280); local task HEAD and GitHub branch matched before this review.
- Branch: [`audit/traveluav-openuav-20261008T2215Z`](https://github.com/WorldExplored/R4R-Sims/tree/audit/traveluav-openuav-20261008T2215Z). The review commit follows that baseline; main integration remains pending.
- Task worktree: `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-worktrees/traveluav-openuav-20261008T2215Z`.
- Canonical artifacts: `/Users/srreyanshsethi/Downloads/AL/R4R-Sims/artifacts/traveluav-openuav/`. Raw runs are immediate `<run-id>/` children; archives are in `collections/`.
- Original candidate: `/Users/srreyanshsethi/Documents/AirLab/Real4Real/sim-audit/traveluav-openuav/`. All ten original authored-file hashes in [recovery.json](recovery.json) still match; its upstream origin/HEAD are preserved, with two pre-existing source modifications left untouched.
- Small, ignored review bundle: `/Users/srreyanshsethi/Downloads/AL/R4R-Sims/artifacts/traveluav-openuav/reviews/evidence-review-20261008T224708-65bb3b/`. Contains fresh verification, a C decision chain, key summaries, configs/manifests and redacted log excerpts; no duplicated raw frame/asset trees.

The canonical checkout is still on its older `main` and has an unrelated `simulators/unreal/analyze.py` modification. It was not switched, merged, reset or staged. Work used the clean dedicated audit worktree. Root README's “no experiments” scaffold statement is stale; run records supersede it. Root instructions, R4R context and candidate notes were read; no nested candidate instructions were found.

### Completeness table

“Verified” below means current local bytes/records checked. “Recorded” means an earlier measured result survives, not that it was rerun now.

| Item | Verified evidence path | Status | Limitation |
| --- | --- | --- | --- |
| Preservation | [global verdict](preservation.json); every run's `settled_manifest.json` and `preservation.json`; review `verification.json` | Fresh verification passed | Older `archive.json`/`artifact_manifest.json` can still say pending; settled manifests and final preservation records supersede them. No pending unique-output transfer found. |
| Final A | [A run][A], [calibration][AC] | 30 RGB + 30 raw depth arrays decode; six vehicle positions match reference | Actual camera mounting differs from nominal by up to 0.209720 m; cause unresolved. |
| Final B | [B events][BE], [states][BS], [metrics][BM] | 25 state/IMU/contact samples and four image batches preserved | **RPC settled with `result:false`, no exception.** Exit zero is not positive path-command success. |
| Final C | [C run][C], [traces][CT], [termination][CE] | Ten learned decisions and official-format result preserved | Decision-budget truncation, not completed benchmark evaluation. |
| Scientific inputs | [metadata verification][M]; original split in raw captures; isolated episode under canonical artifacts `20261008T2348Z-metadata-verification/isolated-dataset/` | Every recorded source-input hash/size matches; generated metadata hashes match | Original published description selection unknown; C uses regenerated metadata. |
| Released dependencies | [asset manifest](asset_manifest.json), [retrieval history](retrieval-from-mac.json) | Identity/size/hash/retrieval records preserved; three metadata files also match in original candidate | Scene executable, archive partitions, checkpoint/tokenizer bytes and installed environments are not locally retained. Historical HTTP checks are not current availability guarantees. |
| Source and patch | preserved original upstream Git; [reusable patch][P], [historical validation](patch-validation.json); review `patch-check.json` | SHA `68070f9d…e7185a`; clean pinned-source apply check passed again, ten files | Needs authored `r4r_observe.py`/runtime helpers and dependencies; source-only patch excludes bytecode churn. |
| Weight eligibility | [load records][CL], [tensor comparisons][CV], [gates][CG] | Saved exact-value/shape checks passed | Checkpoint bytes absent; not independently reloaded now. Checks occurred at loader destination dtype, before later wrapper bfloat16 conversion. |
| Camera/sensor contract | [A camera records][AR], [A settings][AS], [C settings][CS] | Actual timestamps/poses, configured rig, FOV/projection and raw depth preserved | A has separate depth poses; historical B/C do not. No physical exposure or physical calibration proof. |
| C observation-to-action chain | [identity map](policy-observation-map.json); review `decision-0-chain.json`; [input records][CI] | Recorded waypoint values equal controller request; ordering checks pass | Pixel-tensor hash and explicit step IDs on raw state/controller events were not recorded; some links are source/time associations. |
| Presentation | [slides.md](slides.md); review `presentation-search.json` | Slide outline and linked figures exist | **No finished PPTX/PDF/Keynote/HTML deck or deck-generation source found** in task-owned roots. |

## Exact inputs and contracts

**Platform:** OpenUAV is UE4/original AirSim; TravelUAV/UAV-Need-Help is task/data; LLaMA-UAV is the learned model. IAMAI Project AirSim and R2R are separate. Upstream is `prince687028/TravelUAV@5cc26e9a4a55b9c788e918f7c3bb2dc5076a85e6`, verified from local Git objects. [Sources/licensing](sources.md) preserve primary URLs and scope caveats.

**Scene:** released Linux `closeloop_envs/ModernCityMap.sh` launches `ModernCityDowntown/Binaries/Linux/ModernCityDowntown`. Recorded ELF SHA-256: `4a14a76a135dfd5269faffaf5603888ba88e35f404029ffb7b8aa1f9f727af06`. The ELF itself is absent locally; this identity cannot be rehashed here. Environment dataset pin `44de5739a95a2f6a88767446421cddada9606642`; map dataset pin `faa8f2514156455ea7423464cc1295e6f92575cb`; metadata pin `5a1ed4c99d3e7bb2b35fa34135910cb7687fc831`. Episode: `ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f`. Its 33 original seen-valset rows identify one episode, not 33 trials. Selected original logs/images/description/mark are locally preserved and hashed.

**Metadata:** author preprocessing's `random.seed = 1` overwrites the function. The explicit [seed patch][MP] uses `random.seed(100)`. Two saved isolated generations hash to `997395d41354692e9f13c4ca05b427044b7dfe42ede71acab9bcd3edd108f719`; runtime episode hashes to `5e137ae9b7112e92e4f259ad16cbbacf5d81794b90dc6db67b6d0f5f77f86f60`. Only the absolute image-feature path differs; that feature file is not used in this evaluation. Current checks compare existing bytes, not regenerate metadata.

Exact instruction in [C episode][EP] and trace:

> `<image>` followed by a newline, then: There is a target in the  back of uav. Using your front as the x-axis and your right as the y-axis, The target is at a yaw angle of -182.0 degrees from you. The green motorcycle is located on a city street with concrete paving, adjacent to a beige building with a lamp post casting shadows nearby; it's surrounded by parked vehicles, trees lining the sidewalk, and bordered by multi-story brick and glass buildings. Please control the drone and find the target.

[Target placement][OP] records `AASM_Kawasaki` → `my_object_0`, position `[-64.05489349365234,34.93773651123047,-0.1879906952381134]` NED m, scale `[1.1,1.1,1.1]`, target physics disabled. Target position is privileged model input, not inferred exclusively from images.

**Weights:** exact file SHA-256/URLs are in the asset manifest. LLaMA-UAV adapter/projector/non-LoRA pin `6cd1a273ba26338a1be4eb93b43489ee0099fbce`; trajectory `583a3f6b9111fd80e76d6905eaa0f1793f3fd03f`; Vicuna `3321f76e3f527bd14065daf69dad9344000a201d`; DINO `a94c9b567a2a374598f05c584e96798a170c56fb`; BERT `86b5e0934494bd15c9632b12f734a8a67f723594`. EVA/QFormer have first-measured SHA-256 and immutable Google generation IDs, rather than independently published expected SHA-256.

Saved final gates: LoRA **448/448 exact**, zero missing/different; non-LoRA **23/35 matched**, 1,612 partial missing keys and 12 unexpected auxiliary keys; projector **353/365 matched**, 1,282 partial missing keys and the same 12 unexpected keys; trajectory **520/520**; DINO **938/940**, zero missing, two unused entries. Every matched tensor comparison reports zero shape/value mismatches. Full lists remain in the logs and review `checkpoint-key-summary.json`.

The 12 names belong to `base_model.model.waypoints_predictor.{weight_ih,weight_hh,bias_ih,bias_hh}` and `base_model.model.{is_help_predictor,history_predictor}.{0,2}.{weight,bias}`. They are absent from the pinned inference class; its live heads are `waypoint_emb`, `waypoints_fc`, `waypoints_output`, `history_preprocessor`. This is supplemental checkpoint content ignored by the pinned loader, not a naming remap. Other missing keys are partial-file omissions supplied through base/vision/adapter loaders; the gate checks core heads and rejects unknown keys. DINO's unused keys are `label_enc.weight` and `bert.embeddings.position_ids`. No gate bypass, weight substitution or training is evidenced. This is saved runtime eligibility evidence, not an exhaustive new verification of every final parameter's provenance.

## Input → processing → output

- **A:** scene + first six reference vehicle states → `simSetKinematics`, frame settling/pause/reapply → five camera RGB/DepthPerspective responses → separate reference/actual vehicle and camera records, 30 PNGs, 30 float32 metric arrays and wire payloads. Pose replay is not controller flight. World/body use AirSim NED, metres, quaternion `(x,y,z,w)`. Configured front/left/right/rear/down offsets are `(1,0,0)/(0,-1,0)/(0,1,0)/(-1,0,0)/(0,0,0)`; yaw `0/-90/90/180`, down pitch `-90`. Actual response poses take precedence over nominal mounts.
- **B:** one initial reset + corresponding world-frame path → SimpleFlight `moveOnPathAsync`, 1 m/s, ForwardOnly, fixed yaw mode, lookahead 3/adaptive 1 → independent control, state/IMU/contact and image clients → final state before pause, state intervals and geometric errors. Endpoint proximity no longer itself pauses B. **The RPC response is false; only settlement and observed motion are established, not successful completion of the requested path.**
- **C:** instruction + five raw uint8 HWC views + state/IMU/history + known-target frame → CLIP processor resize/centre crop 224, documented mean/std → recorded `[5,3,224,224]` float32 CUDA input, native bfloat16 model conversion → coarse learned waypoint → front-view/state-conditioned trajectory refiner → seven requested NED waypoints. Original depth is clipped 0–100 m and quantized to uint8 for assistance; two 1024² record views feed DINO. `always_help=True/use_gt=True`; actual notices were `None` once, `take off` five times, `cruise` four times.

**C controller design matters:** pinned `AirVLNSimulatorClientTool.py:294–350` resets kinematics at every segment, submits the path without awaiting its future, and uses `target_idx=5`: it records a target when distance begins increasing, then pauses after five such progress targets. It has a five-second wall budget and a 20-position/0.1 m stuck heuristic. Seven requested waypoints therefore do **not** imply seven physically completed waypoints. Environment padding/oracle and assistance collision heuristics differ from simulator contact. All ten recorded pre-padding counts were five; no short-count padding was needed in this run.

### One recoverable C decision: step 0

1. Raw navigation sample **1791503882242316783**, files under canonical `C/observations/<sample>/`: e.g. `FrontCamera.png` SHA `a4711988b64e93fcdc374989f7cba6e02d05e2b47dd724c9ea49d5e14010dddc`, raw depth SHA `9e41ed36dfc168709409c9cffca4849d3bbb2cb1a2caeaaa209a64d89182c829`; all five view hashes are verified in the identity map.
2. [Input record][CI] line 1 retains token IDs, history, target position/frame rotations and image shape/device. Its time lies after the raw camera writes and before [trace][CT] line 1. The sample→input association follows source call order and timestamps; no live normalized pixel tensor digest was saved. Complete token-to-text decoding would need absent tokenizer bytes; the raw instruction is directly recorded.
3. Trace step 0: assistant notice `null`; coarse waypoint `[0.49365446,-0.08208170,-4.88065910]` in the model's transformed frame; seven refined world points. The first is `[34.74061049,51.24589212,-2.14540398]`, last `[33.97923941,51.25575825,-8.27821648]`. The refined array **exactly equals** [controller event][CC] line 2's request. Line 1 records the segment reset. These are direct value/record checks.
4. Three raw controller samples fall between this reset and the next: positions approximately `[34.779606,51.252651,-1.243721]`, `[34.608051,51.247314,-3.478442]`, `[34.349018,51.249916,-5.558310]`. Assignment to step 0 is reconstructed by UTC boundaries, not an explicit step field on the samples.
5. Next navigation sample **1791503885274282885** follows the action and precedes the next reset. Saved evaluator `policy/<episode>/log/000005.json` contains state `[34.256008,51.250900,-6.252397]`; its sample-index association follows five returned states/action. Next front **camera**, a different quantity, is `[33.256161,51.268242,-6.252202]`. Review `decision-0-chain.json` preserves the complete chain and distinctions.

## Outcomes and measurement qualifications

| Run | Recorded outcome | Measurements recovered/rechecked |
| --- | --- | --- |
| A `20261009T001125Z-a-23177` | Pose capture completed, all 60 files decode | Maximum nominal→actual camera residual 0.209720 m / 0.001427°; RGB/depth positions match; batch timestamp spread 0 ns while paused. FOV 89.903625°, derived `fx=fy=128.215484,cx=cy=128`; projection interpretation has a 0.215 px caveat. Raw depth 0.778–16,432 m: far/background meaning is not validated. First RPC 0.661 s, five steady batches mean **0.173 s**, sampled scene-only GPU peak 631 MiB. |
| B `20261008T234423Z-b-17460` | RPC settled/no exception/runner exit 0, **response false**; final state before pause | Fresh recomputation: 25 states; intervals mean 0.199296 s, range 0.183566–0.213139; displacement 4.438462 m; sampled length 4.493467 m; endpoint error 0.393934 m; equal-weight point→requested-polyline RMSE 0.025536/max 0.035031 m. Four moving batches, timestamp spread up to **54.001152 ms**; zero contact-positive samples; GPU peak 742 MiB. |
| C `20261008T235452Z-c-21144` | Ten learned decisions; budget truncation; no predicted stop/success/oracle success/heuristic collision | Official-format full/easy denominator one: SR/OSR/SPL 0, NE 85.52 m (logger rounded; despite “Normalized” label, source uses Euclidean distance). Model.run cold 1.136 s, nine later mean **0.279 s**; five-view RPC ten later mean 0.182 s; two-view 1024² RPC ten later mean 0.333 s. Combined sampled GPU peak **21,396 MiB**. Thirty raw states have gaps up to 3.522 s; not continuous contact/flight coverage. |

B geometry uses the requested polyline including the initial state, equal weights per measured state, no time alignment. Length is a sampled lower bound; contact absence is sampled evidence. C length includes resets. RPC is renderer+transport+decoder wall time, not pure GPU rendering; model timing synchronizes only its own CUDA process. Video 1 fps is playback. PyTorch allocator, late per-process samples and GPU-wide totals cannot yield exact policy-only VRAM. Actual host was Ubuntu22.04.5/A6000, six vCPU/~47 GiB RAM/251 GiB disk; these are measured resources, not minima. C's 600 s budget includes loading, server lifetime 900 s; actual total ~229 s. No completed/full benchmark or population performance claim follows.

## Failure / repair history

The [run index](run_index.json) and review `log-excerpts/` retain every attempt; original logs are unchanged. Grouped IDs below refer to full `20261008T…` run names. Where the exact mechanism is not independently established, it is labelled as such.

| Class / evidence | Symptom and cause status | Exact repair and verification |
| --- | --- | --- |
| Runner/setup: [221326 setup][F1] | HF download retries then shell EOF, exit2. EOF confirmed; editing an active script is a historical explanation, not proven solely by this log. | Corrected shell; [launch.sh][L] freezes code. Verified downloaded hashes and later runs; no clean whole-install rerun after all edits. |
| Compatibility: [222632][F2] | Resolver installed NumPy2.2.6/OpenCV5; historical matplotlib cache permission warning. | Pin NumPy1.26.3/OpenCV4.10, AirSim install `--no-deps`; own MPLCONFIGDIR. Final freezes/import checks survive. Legacy Tornado aliases in `compat/sitecustomize.py`; no settings/security edits needed. |
| Setup tooling: [222410][F3], [222553][F4] | Permission failures overwriting CUDA LICENSE files. | `compile_cuda.py`: preserve old target, fresh extraction namespace, copy only compiler/header/library directories. Later extension setup succeeds. |
| Compatibility: [222804][F5], [223040][F6] | Missing `cusparse.h` and host compiler `cc1plus` lookup failure. Exact lower-level host-package cause not retained. | Verified CUDA math headers plus coherent explicit gcc/g++11/CUDAHOSTCXX; [223730][F8] compilation/import succeeds. |
| Compatibility: [223534][F7] | `_C` import cannot find libc10.so. | Import torch before GroundingDINO extension; final extension check and C inference succeed. |
| Runner: [224043][F9], [224242][F10] | Missing `python` (127); then archive wildcard selected **zero files despite exit0**. | Explicit isolated interpreter and exact episode prefix in `extract.sh`; [224431][F11] extracts492files. Its exit1 is a subsequent missing-merged-metadata check, not failed extraction. |
| Upstream/preprocessing: [224747][F12], [metadata verification][M] | Released episode lacks merged_data; source seed function is overwritten. | Author preprocessing, explicit `random.seed(100)` patch; two saved matching generations and fresh source/input hash checks. Original published choice remains unknown. |
| Runner: [224748 A][F13] | Frozen-code `assets` path nonexistent, before scene startup. | Separate ASSETS/UPSTREAM/output roots; 224947A and later native captures succeed. |
| Compatibility/instrumentation: [225714][F14], [final decoder][AD] | Legacy pure-Python decoder; slow RPCs. First attempted wire interception did not capture the bound callback. | Msgpack1.1 C decoder and concrete transport diff; active-socket unpacker proxy. Identical actual response metadata/RGB/depth payload tests survive (n=1 CPU decode, not renderer speed proof). |
| Runner: [230303 B][F15], [final B][BE] | Endpoint<2m paused while RPC incomplete; five samples. Earlier225148B had only two samples due image blocking. | `5b4c4b9`: wait RPC, final-state-before-pause, separate sampling/image clients. Final25states/cadence verified. False API response remains unresolved. |
| Runner/integration: [234414 A][F16], [final A][AC] | First vehicle pose error0.790m; earlier230118A error0.049m; separate depth poses missing. Startup update ordering is a hypothesis. | Frame wait/pause/reapply (`69e3f93`), depth fields/wire retention (`286489e`). Final vehicle positions match; camera residual remains. B/C historical depth poses cannot be recovered. |
| Compatibility: [230606 C][F17], [231514 C][F19] | bitsandbytes CUDA libraries unresolved; NumBa import missing. | Task-local LD_LIBRARY_PATH (`d07e475`), numba0.60/llvmlite0.43 (`069712c`). Later loader/C run succeeds; no quantization. |
| Audit gate: [231144 C][F18], [231915 C][F20], [232627 C][F21] | Detector unused entries, then non-LoRA/projector auxiliary keys rejected. | Narrow source-justified unused-key classification (`6f4b1ee/1366e16/af62e3f`) plus shape/value/core-head gates. [Loader diagnostic][FD] and final C pass; raw lists preserved. BrokenPipe after failed/diagnostic shutdown is secondary, not independent proof of a model failure. |
| Compatibility: [233131 C][F22], [234829 C][F23] | Byte scene ID fails dictionary lookup (600s timeout); then byte returned IP fails str assertion (owned run stopped143). | UTF-8 decode at those protocol boundaries (`6b615a8/6dbaf53`), no task/stop change. Final C opens scene and executes ten decisions. |
| Reusable patch: [patch validation](patch-validation.json) | Historical diffs contain tracked bytecode/binary notices, unsuitable as executable patch. | `7499dc4`: source-only patch, bytecode writes disabled. Fresh local clean-source apply check passes. |

**Upstream design choices, not silently repaired:** target-position history rotation; GT assistance; segment resets; five-progress-target pausing; padding and requested-waypoint oracle; heuristic collisions separate from contacts; original clipped uint8 depth; official terminal/metric logic. The final C cutoff is the requested audit budget, not a new technical failure.

## Remaining questions and presentation readiness

**Answerable locally:** more source/log examination, cross-view pose calculations, sample-time plots and a finished evidence deck can use preserved data. Original timestamped dataset logs exist, but B had no imposed timed reference, so arbitrary reference-to-wall comparison is invalid. The current review rederived B metrics and validated C ordering rather than accepting summaries alone.

**Needs dependency restoration, not necessarily another simulator experiment:** executable/checkpoint/tokenizer byte rehashes, independent weight reload and token decoding. Those bytes existed on the former instance and are not locally preserved; pinned retrieval identities survive. Their present availability was not rechecked here. No essential *unique captured file within the inventories* was found only on that instance; loss of its installation still prevents an immediate offline rerun.

**Needs matching backend source or a future instrumented run:** why B returned false; the physical/source cause of camera residuals; effective C physics engine (settings literally spell `PhysiceEngineName`, so an ExternalPhysicsEngine claim is unverified); depth/background accuracy; physical exposure synchronization; missing historical B/C depth poses, dense transient-contact/state data, normalized live pixel tensors and full untruncated task outcomes. Unrecorded historical values cannot be retroactively measured. Strong instrumentation-invariance/performance claims would need controlled comparison; current logs establish values, not zero overhead.

**Needs real-scene data/study:** calibrated AirLab images/poses, held-out split and reference imagery, reconstruction→NED metric transform/scale, appropriate depth/background definition and aligned collision geometry. Gaussian observation replacement is unimplemented. Native UE evidence cannot establish sparse outdoor reconstruction, capture15m→render50m fidelity, indoor/racing benchmarks, or real-drone transfer.

**Presentation status:** only `slides.md` plus images/videos; no finished deck to validate. Outline numbers/privileges/reset caveats largely agree with records, but a future deck must add **B's false RPC result**, **C's five-target pause**, regeneration/dtype verification scope and preservation-versus-runnable-installation distinction. Proposed timing histogram/provenance/failure figures are not all finished slide assets. No deck was created by this evidence-only task.

**Final preservation verdict:** unique recorded evidence is complete locally under the verified inventories; no pending unique-output transfers or newly missing listed files. Executable dependencies are retrieval-only, and never-recorded measurements remain unavailable. The old-instance loss does not prevent reviewing the existing integration and policy smoke; it does prevent reconstructing omitted measurements or resuming execution without restoring dependencies. Do not describe slide material as a finished presentation or RPC settlement as successful path execution.

[A]: ../../results/traveluav-openuav/20261009T001125Z-a-23177/run.json
[AC]: ../../results/traveluav-openuav/20261009T001125Z-a-23177/calibration-validation.json
[AR]: ../../results/traveluav-openuav/20261009T001125Z-a-23177/actual_camera.jsonl
[AS]: ../../results/traveluav-openuav/20261009T001125Z-a-23177/settings.json
[AD]: ../../results/traveluav-openuav/20261009T001125Z-a-23177/decoder-equivalence.json
[B]: ../../results/traveluav-openuav/20261008T234423Z-b-17460/run.json
[BE]: ../../results/traveluav-openuav/20261008T234423Z-b-17460/events.jsonl
[BS]: ../../results/traveluav-openuav/20261008T234423Z-b-17460/actual_vehicle.jsonl
[BM]: ../../results/traveluav-openuav/20261008T234423Z-b-17460/metrics.json
[C]: ../../results/traveluav-openuav/20261008T235452Z-c-21144/run.json
[CT]: ../../results/traveluav-openuav/20261008T235452Z-c-21144/policy_trace.jsonl
[CE]: ../../results/traveluav-openuav/20261008T235452Z-c-21144/termination.json
[CC]: ../../results/traveluav-openuav/20261008T235452Z-c-21144/controller_events.jsonl
[CI]: ../../results/traveluav-openuav/20261008T235452Z-c-21144/model_inputs.jsonl
[CL]: ../../results/traveluav-openuav/20261008T235452Z-c-21144/checkpoint_loads.jsonl
[CV]: ../../results/traveluav-openuav/20261008T235452Z-c-21144/checkpoint_tensor_verification.jsonl
[CG]: ../../results/traveluav-openuav/20261008T235452Z-c-21144/checkpoint_gate.jsonl
[CS]: ../../results/traveluav-openuav/20261008T235452Z-c-21144/settings.json
[EP]: ../../results/traveluav-openuav/20261008T235452Z-c-21144/episode.json
[OP]: ../../results/traveluav-openuav/20261008T235452Z-c-21144/object_placement.jsonl
[M]: ../../results/traveluav-openuav/20261008T2348Z-metadata-verification/metadata-verification.json
[MP]: ../../results/traveluav-openuav/20261008T2348Z-metadata-verification/metadata_seed.patch
[P]: ../../simulators/traveluav-openuav/eval_observe.patch
[L]: ../../simulators/traveluav-openuav/launch.sh
[F1]: ../../results/traveluav-openuav/20261008T221326Z-setup-ab-7356/console.log
[F2]: ../../results/traveluav-openuav/20261008T222632Z-compatibility-ab/console.log
[F3]: ../../results/traveluav-openuav/20261008T222410Z-setup-c-extension/console.log
[F4]: ../../results/traveluav-openuav/20261008T222553Z-setup-c-extension/console.log
[F5]: ../../results/traveluav-openuav/20261008T222804Z-setup-c-extension/console.log
[F6]: ../../results/traveluav-openuav/20261008T223040Z-setup-c-extension/console.log
[F7]: ../../results/traveluav-openuav/20261008T223534Z-setup-c-extension/console.log
[F8]: ../../results/traveluav-openuav/20261008T223730Z-setup-c-extension/console.log
[F9]: ../../results/traveluav-openuav/20261008T224043Z-extract-8696/console.log
[F10]: ../../results/traveluav-openuav/20261008T224242Z-extract-8830/console.log
[F11]: ../../results/traveluav-openuav/20261008T224431Z-extract-8949/console.log
[F12]: ../../results/traveluav-openuav/20261008T224747Z-episode-preprocess/console.log
[F13]: ../../results/traveluav-openuav/20261008T224748Z-a-9124/console.log
[F14]: ../../results/traveluav-openuav/20261008T225714Z-rpc-compatibility/console.log
[F15]: ../../results/traveluav-openuav/20261008T230303Z-b-10593/termination.json
[F16]: ../../results/traveluav-openuav/20261008T234414Z-a-17280/metrics.json
[F17]: ../../results/traveluav-openuav/20261008T230606Z-c-10877/console.log
[F18]: ../../results/traveluav-openuav/20261008T231144Z-c-11112/console.log
[F19]: ../../results/traveluav-openuav/20261008T231514Z-c-11420/console.log
[F20]: ../../results/traveluav-openuav/20261008T231915Z-c-11710/console.log
[F21]: ../../results/traveluav-openuav/20261008T232627Z-c-12544/console.log
[F22]: ../../results/traveluav-openuav/20261008T233131Z-c-13364/server.log
[F23]: ../../results/traveluav-openuav/20261008T234829Z-c-18961/console.log
[FD]: ../../results/traveluav-openuav/20261008T234538Z-c-17859/loader-diagnosis-summary.json
