# TravelUAV/OpenUAV native audit — evidence slides

2026-10-08. This is slide material, not a claimed real-world validation. See report.md and linked run records. Final C and preservation status require settled evidence.

## 1. R4R question and tested boundary

- Lab pipeline: real images/poses → reconstruction → new trajectories → novel camera views.
- Residential/suburban/campus below100m; capture15m/render50m remains a research question.
- This audit: native UE camera replay, short controller flight, released policy smoke.
- Figure: report input/output flow, labels A/B/C; central fidelity claim untested.

## 2. One platform, task and model

- OpenUAV: UE4/original AirSim; TravelUAV/UAV-Need-Help: outdoor task/data; LLaMA-UAV: learned model.
- Canonical author-linked repository, exact5cc26e9a revision.
- Separate IAMAI Project AirSim and unrelated R2R.
- Figure: provenance table with scene/data/base/adapter/trajectory/detector pins.

## 3. A: actual views and calibration evidence

- Six reference states →30RGB+30 raw ray-depth arrays, all decode256².
- Final measured vehicle poses match reference; actual camera responses are separate.
- Five-view timestamp spread0ns while paused; no physical synchronization claim.
- Figure: five-view RGB/fixed0–100m depth contact sheet from20261008T234631Z-a-18267.
- Figure: actual camera orientation/mount residual; maximum translation discrepancy0.204m, not silently treated as nominal mount.
- First RPC0.550s, five later mean0.182s; loader overlapped, GPU-wide memory not scene-only.

## 4. B: controller completion and achieved route

- Corrected20261008T234423Z-b-17460 completed RPC, final state before pause.
- Separate clients:25states,24intervals mean0.199s versus requested0.2s.
- Displacement4.438m; final endpoint error0.394m; geometric RMSE0.026m.
- Sampled path length4.493m is lower bound;0/25 contact-positive samples is sampled evidence.
- Figure: requested/achieved3D trajectory with terminal/contact markers, and timing histogram.
- Video: short captured sequence, playbackFPS explicitly separated from control/simulation rate.

## 5. Corrections and failure evidence

- PreviousB paused within2m while RPC incomplete: incomplete flight, five states only.
- Modern MessagePack decoder active in both isolated environments.
- Same real wire payload: identical RGB bytes/float32 depth; one decode sample0.492s legacy vs0.01755s active.
- Earlier0.173s is five steady RGB/depthRPC batches, not pure render time or sustained throughput.
- Figure: failure ledger and decoder equality/timing record.

## 6. Released policy eligibility and privileged inputs

- Non-LoRA23 matched +12 auxiliary tensors absent from pinned inference class; projector353 matched +same12unused.
- Full missing/unexpected/shape lists retained; exact delivered values after dtype conversion; no remapping/quantization/training.
- LoRA exact; trajectory520matched; DINO938matched with2 documented unused entries.
- Metadata regenerated twice with actualrandom.seed(100), identical hashes/description/instruction; original published description unknown.
- Known target orients history frame; always_help/use_gt remains true; segment resets/padded state/requested oracle are disclosed.
- C outcome pending final settlement; no published benchmark-score claim.

## 7. Resources and setup burden

- MeasuredA6000, Ubuntu22.04,6vCPU/47GiB/251GiB; below targetCPU/RAM/disk.
- Native scene-only sampled peak652MiB(A),742MiB(B); C combined peak to add from settled run.
- Selected compressed archives28.50GB; extracted scene2.168GB +episode19.03MB; models~22GiB.
-37min to nativeA,96min to loader eligibility including failures; separate training's8A100 from inference.
- Full-instance/storage quote unknown; user GPU display$0.54/h only.

## 8. Gaussian replacement: interface and missing science

- Client observation boundary: actual camera poses/intrinsics/time, five256² views plus two1024² detector views.
- Match raw RGB order and depth semantics; ray-depth conversion, invalid depth and NED→reconstruction metric transform.
- UE still owns dynamics, contacts, nonvisual sensors and target identities unless separately aligned.
- No adapter implemented. Native policy result cannot prove sparse capture/altitude extrapolation/real transfer.
- Needed evidence: corresponding real reconstruction/held-out imagery, horizontal/vertical routes, coverage masks, quality and downstream metrics.

## 9. Preservation and next decision

- Branch commits, small records/plots, canonical Mac raw files and checksums.
- Exact model/archive retrieval verified from receiving Mac; custom outputs preserved locally.
- Main integration pending; other candidate branches are not controlled comparisons.
- Final verdict requires local settled checksums and readable files; never infer preservation from Git push alone.
