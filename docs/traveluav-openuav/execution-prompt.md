# TravelUAV/OpenUAV Real4Real execution prompt

Continue the TravelUAV/OpenUAV evaluation below. This is an execution task for local Codex with access to my Mac and the supplied Ubuntu instance. Complete the evidence, report, and preservation work; do not stop at installation. No First Mate setup, policy training, new Unreal project, or Gaussian-scene implementation is authorized.

## Research brief and limits

AirLab's Real4Real asks whether a small real outdoor capture can support realistic camera observations along many new drone trajectories. The lab brief targets residential, suburban, and campus scenes below 100 m, including changed altitude (for example, capture at 15 m and render at 50 m). Its pipeline is real images plus camera poses, reconstruction, scene representation, new trajectory, and novel-view rendering. The eventual scientific test needs calibrated held-out real imagery and appropriate image-quality and downstream-task metrics.

This task evaluates what TravelUAV/OpenUAV can contribute to that pipeline. OpenUAV is the UE4/original-AirSim platform; TravelUAV/UAV-Need-Help supplies the outdoor task/data; LLaMA-UAV is the learned model. IAMAI Project AirSim is a separate stack with a different API. The R2R ground-navigation benchmark is unrelated.

Preserve the agreed tests:
- A: six known reference states to five-view RGB/depth and calibration evidence.
- B: corresponding world-frame waypoints through SimpleFlight to achieved states/sensors.
- C: released-weight, assistant-guided policy inference to actions and task evidence, one episode and at most ten learned decisions.

C includes end-to-end inference and learned waypoint generation. It is a bounded smoke test, not training or a full benchmark. Native UE success does not validate real capture, sparse reconstruction, altitude extrapolation, Gaussian imagery, or real-drone transfer. Indoor/racing coverage is a documented capability assessment, not additional runtime tests. Do not silently expand to new scenes, algorithms, or trials.

## Repository, paths, and parallel work

Shared repository: https://github.com/WorldExplored/R4R-Sims
Canonical Mac checkout: ~/Downloads/AL/R4R-Sims/
Remote checkout: /workspace/R4R-Sims
Authored simulator code: simulators/traveluav-openuav/
Plans, sources, report, and slides.md: docs/traveluav-openuav/
Run records and small results: results/traveluav-openuav/<run-id>/
Large output on both machines: artifacts/traveluav-openuav/<run-id>/, ignored by Git.
Third-party source, assets, environments, and caches: explicitly ignored directories, preferably third_party/traveluav-openuav/ and artifacts/traveluav-openuav/dependencies/. Check ignore rules before staging.

Read README.md, AGENTS.md, relevant plans, existing notes, and applicable nested instructions before editing. Check actual repository state, not README status alone.

Other simulator jobs may run concurrently. Do not share a mutable local working tree or Git index with them. Use a dedicated branch named audit/traveluav-openuav-<unique-id> and a separate local worktree under ~/Downloads/AL/R4R-Sims-worktrees/. Keep canonical output copies in the Mac artifacts path above. Use the same task branch remotely. Record resolved absolute paths and branch names. Do not edit another simulator's files or shared root documents without coordinating with their owner.

Use clean-status checks and git pull --ff-only when safe. Preserve uncommitted changes and unrelated histories. Never reset, clean, force-push, overwrite another job's work, or stage the whole repository indiscriminately. Synchronize changes through authored commits, pushes, and pulls. Within this task, only one machine should produce edits at a time; push, pull, then hand over. Push the task branch and provide direct links. Integrate into main only if safe and authorized under repository instructions; otherwise clearly report that integration is pending and give the branch paths.

## 1. Recover and verify the prior work locally before large remote setup

Inspect the original candidate directory if present:
 /Users/srreyanshsethi/Documents/AirLab/Real4Real/sim-audit/traveluav-openuav

Recover and inspect the actual handoff.md, sources.md/source ledger, asset_inventory.md, expected-sha256.txt, slides.md, host.sh, policy_smoke.sh, collect.sh, eval_observe.patch, and any Python helpers, configurations, split metadata, and patches referenced by them. A prose description of a runner is not the runner. Import authored work into the appropriate shared folders, preserving originals and provenance. Adapt hardcoded old paths, output roots, and working-directory assumptions explicitly. Preserve executable bits and verify every referenced helper resolves.

Correct upstream:
 https://github.com/prince687028/TravelUAV
 pinned commit: 5cc26e9a4a55b9c788e918f7c3bb2dc5076a85e6

The official project page links to that repository. The same SHA does not resolve in buaa-colalab/TravelUAV; that is an earlier related repository, not the checkout to use for this pinned handoff. Verify the original checkout's origin, HEAD, dirty state, and diffs. Keep third-party Git history in an ignored directory and store patches/retrieval instructions in the shared repository, never a nested tracked repository.

Before expensive downloads, produce a short preflight record showing:
- recovered/missing files and versions;
- actual A/B/C entry points, inputs, budgets, outputs, cleanup behavior;
- the logging patch's actual changes and whether they affect inputs/actions/stops;
- dependency/asset list, archive expansion/free-space plan;
- authenticated shared-repository reads and an actual authored commit/push from each machine, verified by the receiving checkout. Do not create throwaway commits solely to test access.

If essential authored files are missing, recover from existing checkouts/backups or an accessible durable copy. Do not claim recovery or silently regenerate the agreed runners. If exact recovery is impossible, document the missing pieces. A newly reconstructed implementation must be labeled as such and checked against this contract and pinned code. Continue independent branches where possible; block an unverifiable C path instead of inventing its semantics.

## 2. SSH and host verification

Mac source key: ~/Downloads/private_key.pem
Host: 209.137.198.205
User: ubuntu
Port: 22 (implicit in supplied command)

The supplied command was:
 ssh ubuntu@209.137.198.205 -i private_key.pem

Resolve the Downloads key locally. Copy it to a uniquely named protected file in ~/.ssh/, without overwriting another key, and chmod 400 the protected copy; ~/.ssh/ should have restrictive permissions. Use the protected absolute identity path. Never print, log, commit, or upload private-key contents. Inspect/verify the SSH host fingerprint through available provider information; preserve normal host-key checking. Remote Git authentication must use its own suitable credentials, such as a scoped instance deploy key/token or an existing authenticated channel, without copying my Mac private key to the instance. If authentication needs human action, identify the exact action and continue useful independent work.

Chosen host target: one A6000, 48 GB VRAM; Ubuntu 22.04 x86-64; 16 vCPU, 64 GB RAM, 300 GB SSD; NVIDIA graphics/Vulkan support and CUDA 11.8 compatibility.
The displayed GPU price was $0.54/hour, not a verified full-instance quote.
Only allowed alternative labels: A100, A40, A6000, RTX6000 Ada, A10. These override the broader older repository list. Do not rent, upgrade, or substitute hardware yourself.

Verify and record actual GPU identity/count/memory, CPU, RAM, storage/free space, OS, NVIDIA driver, graphics device access, Vulkan/rendering path, and full-instance/storage pricing when accessible. nvidia-smi success alone does not establish scene rendering support. CUDA wheel compatibility and graphics support are separate checks. The provision target is an engineering allowance, not a measured minimum. Unknown prices or resource requirements remain unknown.

## 3. Install only required dependencies and verify assets

Inspect existing installations/files first. Verify the selected released ModernCityMap Linux executable and its launcher/archive layout; do not impose Windows or create an Unreal editor project. Download large dependencies directly on the instance. Check compressed sizes, 7z listings, expansion, duplicate-cache footprint, and free space before extraction. Preserve version/retrieval information and inspect redistribution terms before placing upstream material on GitHub.

Use separate Python 3.10 environments for A/B and C. Recover the exact dependency pins; the prior handoff specifies A/B airsim==1.8.1, numpy==1.26.3, Pillow==10.2.0, huggingface_hub==0.27.1 plus the documented AirSim compatibility fix. Inspect and preserve that fix as a concrete diff. For C use torch==2.0.1, torchvision==0.15.2, torchaudio==2.0.2 with cu118, editable LLaMA-UAV and compatible pinned upstream requirements. Record final package freezes and prevent later installations from silently replacing core versions.

Recovered retrieval pins, to verify before using:
- wangxiangyu0814/TravelUAV_env dataset, revision 44de5739a95a2f6a88767446421cddada9606642, only closeloop_envs.* partitions.
- wangxiangyu0814/TravelUAV dataset, revision faa8f2514156455ea7423464cc1295e6f92575cb, only ModernCityMap.* partitions plus exact small metadata required by the evaluator.
- wangxiangyu0814/llama-uav-7b, revision 6cd1a273ba26338a1be4eb93b43489ee0099fbce.
- wangxiangyu0814/traveluav-traj-model, revision 583a3f6b9111fd80e76d6905eaa0f1793f3fd03f.
- lmsys/vicuna-7b-v1.5, revision 3321f76e3f527bd14065daf69dad9344000a201d.
- EVA: https://storage.googleapis.com/sfr-vision-language-research/LAVIS/models/BLIP2/eva_vit_g.pth
- QFormer: https://storage.googleapis.com/sfr-vision-language-research/LAVIS/models/InstructBLIP/instruct_blip_vicuna7b_trimmed.pth
- Grounding DINO: https://huggingface.co/ShilongLiu/GroundingDINO/resolve/main/groundingdino_swint_ogc.pth

Recover authoritative expected hashes and select checks by exact file paths, never head/tail line positions. Distinguish a verified match to an expected hash from a hash first measured after downloading. Pin mutable external asset URLs to a revision or preserve verified bytes where possible. Record URL, revision, actual size, SHA-256, and status for every required asset. Inspect loaders for additional runtime/tokenizer dependencies, including Grounding DINO text-encoder assets, and document any required downloads.

Verify required checkpoint keys and adapters loaded, expected dtype, device placement, and missing/unexpected keys. Do not allow silently missing learned modules to be treated as released-weight inference. No substitute weights, quantization, random-weight model, DAgger, or training. Missing C assets do not cancel A/B.

Validate graphics, permissions, ports, and scene startup. Use a non-root user if the executable requires it. Preserve the recovered budgets: A/B scene startup 60 s and probe 90 s after startup; C evaluation 600 s after server startup and server lifetime 900 s. Verify wrapper timeout boundaries, including whether model loading consumes the evaluation budget, and record their actual meaning. The previous handoff uses ports 30000 (scene server), 30001 (AirSim scene), and 20001 (DDP); check for occupation and never kill unrelated processes. Do not run scripts/eval.sh verbatim: its pinned defaults include different ports, an invalid 80005 DDP port, batch size two, developer paths, and 200 decisions.

## 4. Execute A, then B, then eligible C

Episode: ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f

Preserve the official seen_valset source and exact selected rows. Repeated rows identify one merged_data.json episode, not independent trials. Record split/data hashes, instruction, target object identity/position, reference trajectory, and placement metadata. Preserve path rewrites separately from original metadata. If malformed/incompatible, retain the failure and use the next lexicographic ModernCityMap episode from the pinned split, with a fresh run ID and reason. Do not replace a merely unsuccessful episode.

A, pose replay:
Replay the first six reference states using the recovered state-setting runner. State replay establishes image generation, not physics/control. Capture front, left, right, rear, and down RGB and raw float DepthPerspective at each state, expected 30 RGB plus 30 depth outputs. Decode every expected file and validate dimensions, finite/valid depth ranges, units and sentinel values. Also create fixed-scale depth previews; keep raw metric arrays separately. Confirm depth semantics, including ray distance versus optical-axis depth.

Record configured camera mounting transforms, actual image-response camera poses/timestamps, vehicle reference/requested/measured poses separately, FOV/intrinsics, quaternion ordering, axis conventions, units, projection convention, and camera ordering. Derived intrinsics must be labeled and checked against actual dimensions/projection. Measure timestamp spread across cameras and RGB/depth pairs; do not equate one RPC batch with proven simultaneous exposure. Inspect pose/frame consistency at known states and record any mismatch.

B, controller flight:
Use the corresponding first-six-state world-frame path and recovered SimpleFlight runner. Preserve initial reset and controller parameters, with 1 m/s where configured. Record every command, async completion, achieved state/IMU, actual camera observations, simulator collision information, pause/reset events, timeout, and termination. Never use per-waypoint teleporting as evidence of controller tracking.

Distinguish zero exit / API completion, motion, and route-following success. Record endpoint displacement, achieved path length, final endpoint error, and geometric point-to-requested-polyline error (with RMSE/max and stated sample weighting). Use time-aligned tracking error only if a timed reference/control target exists, and state interpolation/time alignment. Do not compare arbitrary reference timestamps to wall timestamps. Plot reference/requested and achieved paths in a common metric frame with collision/termination markers, and show actual camera poses/frusta or camera pose error where meaningful. Preserve reference, controller requests, and achieved paths as separate data.

C, released policy smoke:
After A/B and checkpoint checks, run the recovered one-episode released policy with batch size one, seed 100, maxWaypoints=10, and the original timeout budgets. Preserve always_help=True/use_gt=True where configured. Trace actual instruction and assistant notices, observation identities/preprocessing, state/history, coarse model waypoint, refined/world-frame waypoint path, controller calls/achieved states, detector predictions, stop rules, latency, and final outcome. Count actual learned decisions.

Important pinned-code findings to verify against the recovered patch:
- prepare_data_to_inputs in src/model_wrapper/utils/travel_util.py uses the known target position to orient the history/input coordinate frame. Record this privileged dependency as well as GT assistant guidance; do not describe C as unassisted visual navigation.
- AirVLNSimulatorClientTool.move_path_by_waypoints calls simSetKinematics at each path segment before moveOnPathAsync. Log these reset events, not only the initial episode reset. Preserve upstream behavior and avoid claiming uninterrupted physical rollout.
- Upstream movement has a five-second subroutine budget and heuristic progress/stuck detection. Preserve and report internal limits as well as outer budgets.
- EvalBatchState and Assist can label depth/stuck/distance heuristics and increasing target distance as collisions. Separate these from simGetCollisionInfo contact events.
- env_uav.makeActions may pad missing state samples and set oracle success using requested waypoints. Label padded data and commanded-waypoint oracle evidence; separately report achieved-state distances.
- C converts depth to 8-bit after clipping to 0..100 m. Preserve policy preprocessing; do not replace its depth input with scientific float arrays. Record RGB channel ordering and view order from code and runtime.

Do not silently repair task semantics or official metric logic to improve the outcome. Instrumentation/installation fixes must be bounded, diffed, and validated; semantic bugs or incompatibilities may block official comparability even if the loop executes. Retain each failed run and retry corrective changes with a fresh run ID. Stop an irreducible failing branch after documenting its cause; continue independent evidence and preservation.

Distinguish detector/model stop prediction, evaluator termination, actual simulator contact, heuristic collision, RPC failure, scene failure, timeout, and decision-budget truncation. A stop prediction is not automatically terminal in this evaluator. Export raw official metrics only when the official expected episode result exists, with selected denominator one and clear eligibility. Keep metric output directories separate from audit metadata so os.listdir-based denominators are not contaminated. If timeout prevents an official result, report metrics unavailable; do not fabricate a completed result. A budget-truncated result remains a smoke result. Do not claim the published benchmark score or estimate population success from this episode.

## 5. Measure and preserve evidence

Use persistent execution such as tmux plus file logs; SSH loss must not lose the run. Capture incremental snapshots every 5–10 minutes during long operations and immediately after failure. Transfer them off the instance where practical. Final checksums refer to settled files, not changing live snapshots.

Record commands/exit statuses (including the actual pipeline command's status, not tee), source commits/diffs, packages, hardware, settings, seed, inputs/asset identities, wall/simulator times, failures, trajectories, image manifests, camera poses, policy traces, and output validation. Stop/clean up only owned processes.

Measure scene-only A/B separately from C's combined scene/policy:
- five-camera RGB/depth RPC wall latency, batch/view count, resolution, sample count, and warmup status;
- model latency with appropriate CUDA synchronization in its own process, separately from preprocessing, detector, controller, and logging;
- achieved control/state sample timing, simulation progress versus wall time, pauses and resets;
- GPU memory samples and model-process allocator memory where available.

A client CUDA synchronization does not synchronize the separate UE renderer. Label RPC time as RPC-plus-render/transport where components cannot be isolated. Separate cold start/first decision from later decisions; with ten decisions report sample counts and avoid strong percentile/throughput claims. Report requested sampling cadence, achieved cadence, and dropped samples. Distinguish GPU-wide memory, per-process memory, and PyTorch allocation; do not subtract them into an exact policy-only VRAM claim. Video playback FPS is not simulation throughput. Label instrumentation overhead and verify it preserves model inputs/actions/stopping semantics.

Commit/push authored code, configs, source ledger, asset manifest, notes, report, slide text, metrics and small reviewable results from the producing machine; pull onto the other checkout. Keep installations, third-party source, datasets, weights, caches, raw frame sequences, and large videos out of Git. Commit a small five-view RGB/depth contact sheet and trajectory plot if size/rights permit so results can be reviewed through GitHub.

Use resumable rsync over SSH to preserve all required generated run evidence in the canonical Mac artifacts path, or verified durable storage. Do not recursively SCP dependency directories. Downloaded reproducible dependencies may remain remote if exact retrieval/version/hash are documented and availability is verified from another machine; preserve custom/unique assets and irreplaceable outputs. Where upstream dependencies cannot be reliably re-obtained, preserve their verified bytes durably.

Record artifact location, size, SHA-256 and whether locally/durably verified in each run's manifest. After transfer, verify every required file/archive checksum, list/test archives, decode every A output, and open representative B/C RGB, raw depth, traces, trajectories and logs locally. A Git push or a path on the rented machine is not preservation. If using durable storage instead of a full local copy, retain representative local previews and explicitly distinguish local paths from durable links.

Nothing essential may remain only on the rented instance. Do not delete assets or stop/terminate the instance. Declare it safe for me to stop only after code/results are pushed, local checkout(s) are current, and required artifacts are verified away from the instance. If any preservation check fails, clearly state it is not yet safe.

## 6. Finish report, comparison, and slide material

Update docs/traveluav-openuav/report.md and slides.md using evidence, with direct source/code and result/artifact links. Include:
- executed, failed, blocked, and untested branches;
- scene/data/model provenance and observation to model to controller to state to camera flow;
- all privileged target/assistant inputs and resets;
- requested/achieved trajectories and calibrated camera evidence;
- representative five-view RGB/raw-depth previews and a short video where frames permit;
- measured setup/runtime/storage/memory/latency with methods and sample counts;
- exact episode outcome, stopping reason and official-metric caveats;
- what a human must learn to interpret the outputs, with exact relevant code entry points;
- Real4Real fit and the concrete Gaussian observation-replacement boundary.

Inspect the exact call sites to state what consumes RGB, depth, state, target position and history. Identify the smallest boundary for supplying Gaussian observations at the same camera poses/timestamps, including shape/channel order, dtype/range, five-view order, intrinsics, world-to-reconstruction transform/scale, pause semantics, and depth definition. State what would still provide dynamics, collision geometry, target identities/placement, and nonvisual sensors. Explain whether the packaged binary suffices for client-side observation replacement or which source changes would be needed. Do not implement an unrequested adapter.

Compare to other candidates only using available repository evidence. Use common dimensions: arbitrary calibrated pose replay, action-driven state evolution, camera/depth contract, real-capture import, observation replacement, collision/dynamics coupling, released-policy availability, setup burden, and measured resources. Label source-only versus measured entries. Different native scenes/tasks/hardware are not controlled speed, realism, or navigation comparisons. Missing other-candidate results stay unknown.

Keep native execution separate from a future Gaussian-scene comparison. Fidelity needs corresponding calibrated scenes and valid held-out imagery, not unrelated UE and real scenes. If no AirLab dataset/calibration/split is supplied, explicitly leave the central fidelity claim untested; no reconstruction/policy training is part of this run.

Finish with concise measured findings, remaining blockers, pushed commit and branch links, report/slides links, locally verified artifact paths or durable links, and the preservation verdict. Do not describe a successful installation as a completed evaluation.
