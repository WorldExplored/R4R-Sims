Execute the GRaD-Nav Real4Real audit below. Preserve all tests and deliverables. Do not train policies, train new scene reconstructions, rent additional machines, or terminate the instance automatically.

Research objective

Real4Real aims to reuse a small real capture to reconstruct an environment and render observations along new drone trajectories. The primary target is outdoor residential, suburban and campus environments below 100 m. Horizontal and vertical held-out trajectories and downstream perception usefulness matter. Capture at 15 m → rendering at 50 m is a research question, not an established capability.

Indoor navigation and racing are additional applicability questions. An indoor gate scene establishes integration only; it cannot validate the outdoor goal. Distinguish sparse capture coverage from sparse physical scene content.

Repository and isolated workspaces

Repository: https://github.com/WorldExplored/R4R-Sims
Canonical local checkout: ~/Downloads/AL/R4R-Sims/
Candidate branch: audit/grad-nav
Separate local candidate worktree: ~/Downloads/AL/R4R-Sims-grad-nav/
Remote candidate checkout: ~/R4R-Sims-grad-nav/

Read README.md, AGENTS.md, docs/r4r-audit-context.md, relevant plans and simulator notes before implementation. Record absolute workspace paths.

Inspect relevant evidence read-only on:
- eval/project-airsim
- unreal-a5000-audit
- audit/traveluav-openuav-20261008T2215Z

Resolve current branch SHAs. Read relevant findings, artifact indexes and preservation records without switching another agent’s checkout or merging whole branches merely to read them. Main may not contain candidate results.

Create or reuse audit/grad-nav from an explicitly recorded base. Preserve existing branch work. Use separate worktrees/checkouts for parallel candidates and one active writer on this branch at a time. Coordinate shared-file edits; preserve unrelated/uncommitted changes.

Recover prior preparation if present at:
`/Users/srreyanshsethi/Documents/AirLab/Real4Real/sim-audit/grad-nav`
Inspect handoff.md, sources.md, asset-inventory.csv, run_a.py, run_b.py, capture.sh and slides.md. Import authored files with provenance while preserving originals. Identify essential missing inputs rather than inventing their contents.

Within the candidate checkout use:
- simulators/grad-nav/: candidate code, setup and configurations.
- docs/grad-nav/: plans, sources, findings, learning guide and reviewable presentation.
- results/grad-nav/<run-id>/: small records, metrics, summaries and artifact index.
- Ignored artifacts/grad-nav/<run-id>/: full frames, raw depth and large media.
- Shared scripts/ and configs/: only genuinely shared work.

Keep upstream repositories, installations, environments, caches, datasets and checkpoints outside tracked files.

Connection and existing host

Supplied connection:
`ssh ubuntu@209.137.198.205 -i private_key.pem`
Supplied key: ~/Downloads/private_key.pem
Username: ubuntu. Port: 22. The hostname is complete.

Inspect existing local SSH configuration first. TravelUAV records:
`~/.ssh/r4r-209.137.198.205.pem`
`~/.ssh/r4r-209.137.198.205.known_hosts`

Reuse these if present and applicable, retaining restrictive permissions and strict host-key checking. Otherwise create a non-overwriting protected copy of the supplied key under ~/.ssh/ and adjust the connection. Never print private-key contents, copy private keys to the VM, or commit credentials. If the host identity differs from the recorded identity, stop connection attempts and report it.

This is the existing TravelUAV A6000 host, not a clean machine. Its handoff reports Ubuntu 22.04.5, A6000 48 GB, 6 vCPUs, approximately 47 GiB RAM and 251 GiB disk. Reinspect actual specifications and free space. Six vCPUs alone must not block execution because the earlier eight-vCPU target was provisional.

Verify driver, CUDA toolkit/compiler and GPU access. The displayed $0.54/hour is not confirmed full-instance pricing. Record elapsed rental/session time and charges where known; distinguish estimates and unknowns.

Existing-host reuse and targeted cleanup

Read TravelUAV’s current handoff, report and preservation.json on its candidate branch. Do not modify its existing /workspace/R4R-Sims checkout.

Inspect processes, GPU consumers, persistent sessions, listening ports, disk usage, checkouts, uncommitted work and ignored artifacts. Identify project ownership before touching anything. Do not kill processes by broad names/patterns or compete with active GPU jobs.

Prefer retaining unrelated work and installing GRaD-Nav in a separate environment/dependency root.

If space requires cleanup, first reverify relevant source manifests against actual receiving Mac files. Preserve missing outputs, patches, configs, logs and reproduction-critical inputs. The repository preservation record is supporting evidence, not fresh verification.

Remove only explicitly identified, inactive TravelUAV dependencies/temporary files with documented reacquisition, or outputs whose receiving copies have just been verified. Record exact removed paths and before/after free space. Preserve source checkouts, credentials, system packages, NVIDIA drivers and other candidates’ files. No blanket deletion, git clean -fdx, or broad process termination.

If ownership/preservation cannot be established, retain files and report the specific space blocker.

Preflight and compatibility

Check asset availability and compressed/expanded storage requirements before installing a large stack.

Inspect upstream revision d9b00e16107338e49071c65f44582c013e522633 and current upstream documentation; record both SHAs. Preserve the pinned reproduction baseline unless a justified change is recorded separately.

Inspect current CUSTOM_SCENE.md and tools/validate_scene.py for import, normalization, origin-offset and planner-start issues. Verify their absence/presence at the baseline. Do not run training instructions. Nearest-point clearance does not prove continuous free space, valid collision geometry or metric scale. Preserve provenance for any diagnostic backport.

Inspect archive configs/checkpoint metadata, dataparser requirements and actual APIs. Keep Gaussian scene checkpoints, perception weights and navigation-policy checkpoints distinct.

Use an isolated environment. Previous PyTorch 2.1.2/cu118, torchvision 0.16.2, Nerfstudio 1.1.3 and compatible gsplat versions are provisional. Resolve compatibility against assets/APIs; record exact installation commands, versions and patches.

Inspect author-linked point_cloud.zip and gs_data.zip, sources, sizes and hashes. Resolve gate_mid’s config, Gaussian checkpoint, point cloud and dataparser inputs. Do not assume every required input or policy weight is included.

Allow at most two documented compatibility-repair attempts and two hours total compatibility setup/debugging, excluding active downloads. Stop unresolved heavy setup when either limit is reached. Preserve failures and complete findings/deck even when blocked.

Execution plan

Before running, freeze poses, controller/action definitions, durations, settings, seeds, termination and diagnostic criteria. Recover prior numerical definitions; label replacements explicitly. Do not invent lab-approved thresholds.

Use persistent sessions, file-backed logs and bounded subprocess timeouts. Preserve failures, exit status and incomplete runs. Continue independent tests when another is blocked.

A/B/D must not depend on unavailable learned components. Exercise renderer/dynamics directly where needed, documenting bypasses. Never substitute random visual features or VAE outputs for trained observations.

A: Camera integration and timing

Recover the prior five numerical poses. If unavailable, derive a labeled replacement set from scene cameras with explicit reference camera and horizontal/vertical offsets. Save numerical poses, intrinsics, units, split and provenance before rendering.

Trace the actual environment → utils/gs_local.py → renderer call path. Resolve conflicting quaternion comments/implementation, hardcoded calibration/mount and differing entry-point pose expectations.

Verify quaternion order, body/camera axes, origin offsets, dataparser normalization and transform composition exactly once. Use numerical identity, known-rotation and translation checks to detect flips/swaps/double normalization; save the verified conversion for D.

Render equivalent cameras through direct Nerfstudio and the authors’ path under matched settings. Compare transforms and outputs; preserve discrepancies and minimal patches.

Save RGB/raw depth for all five poses. Record actual rescaled resolution/intrinsics, RGB encoding/range, depth definition/scale and invalid/background handling. Inspect images and arrays.

After correctness checks, benchmark identical settings with at least five warmups and 50 measured renders, CUDA synchronization, median/p95 latency, throughput and peak memory. Separate render-only and raw RGB/depth observation timing. Define whether transfers/logging are included.

Complete learned-observation timing must additionally identify feature extraction and required weights. If these are unavailable, mark that measurement blocked. Video playback FPS is not rendering speed.

A establishes asset/camera/render integration, not fidelity.

B: Dynamics and feedback behavior

Preserve 20 × 0.05 s as a one-second smoke test. Verify outer timestep, inner substeps, state ordering, thrust/body-rate units, conversion, filtering, delay, noise and saturation. Record requested/applied actions.

Separate force balance from feedback recovery: constant hover thrust cannot restore displaced altitude.

For recovery use a named controller with height setpoint, explicit gains and correct action conversion. A minimal labeled adapter controller is acceptable, but is not the authors’ learned controller. Apply a documented small altitude perturbation.

Specify the bounded extension, maximum simulated duration and diagnostic criteria before execution. Report quantitative drift, error, response time where reached, overshoot and saturation. One second does not establish stable hover; no invented lab thresholds.

B establishes tested dynamics/controller behavior, not real-drone calibration.

D: Causal dynamics-to-rendering integration

Use one scene-valid bounded maneuver/route with a named controller or action sequence.

Requested/applied actions must change vehicle state; achieved state must determine mounted-camera pose; that pose must generate RGB/depth. Do not independently animate a desired camera route and present it as achieved flight.

Reuse A’s verified conversion. Save synchronized actions, vehicle states, camera transforms, RGB, raw depth and simulated/wall timestamps. Separate planned route, achieved vehicle trajectory and achieved camera trajectory.

Document adapters, bypassed components and timing differences. If physical scale/alignment is unresolved, retain component evidence but mark coupled physical interpretation blocked.

Inspect native point-cloud obstacle handling separately: distance/reward penalties, termination and physical contact response, including coverage limitations. Successful rendering does not validate collision geometry.

D establishes the demonstrated causal integration only.

C: Conditional original-policy inference

Search author-linked releases/documentation/assets once for a compatible original GRaD-Nav inference checkpoint. Verify all required learned components, including visual features, history encoding/VAE, normalization, map/config and action interfaces. Record loader coverage and runtime use.

train_gradnav.py defaults to training. Supply explicit supported inference/play flags. Creating optimizer objects is not training; verify no optimizer updates and unchanged learned parameter tensors during evaluation.

If compatible weights exist, run one bounded, fully logged episode with explicit outcome. One episode is integration evidence, not a robust success-rate estimate.

If components/weights are missing, mark C blocked. Scripted controllers, random networks, scene checkpoints and GRaD-Nav++ models cannot substitute.

Real-capture import and fidelity

Inspect original images, calibrated poses/intrinsics, reconstruction settings and trustworthy split provenance. Determine whether references were excluded from reconstruction and earlier fitting.

If suitable held-out images and an existing compatible reconstruction are available, render matching cameras and report per-view/aggregate PSNR, SSIM and LPIPS. Document implementations, preprocessing, color space/range, resizing/cropping, masks, exclusions and coverage. Separate horizontal/vertical and altitude coverage where supported. Training-view agreement is diagnostic only.

Otherwise mark fidelity blocked and list exact missing inputs. Do not fabricate references/splits/outdoor results or train a reconstruction.

Document how AirLab imagery, cameras, existing checkpoint, metric frame, point cloud and held-out split would enter the system. Downstream perception usefulness remains untested without a supplied task/model and references.

Git synchronization and preservation

Record commands, revisions/patches, environment, asset/config hashes, seeds, weights/controller definitions, scene/split, conventions, trajectories, timings, GPU memory and termination.

Verify an authenticated GitHub publishing path on the designated writer. Use remote authentication if already available and appropriate; do not copy personal credentials merely to satisfy synchronization.

When remote publishing is unavailable, transfer Git bundles or equivalent verified Git objects to the authenticated local writer, preserving commit identities. Verify receiving and pushed SHAs.

Maintain one writer per branch. Use pull --ff-only when safe; inspect rejected pushes/divergence and integrate non-destructively. Never force-push or overwrite unrelated work.

Run the five-minute resumable rsync collector on the local Mac with reconnect/retry and final collection after completion/failure. Transfer finalized outputs incrementally and preserve partial logs separately. Never delete unrelated local files through synchronization.

After outputs settle, generate final byte-size/SHA-256 manifests and verify destination checksums. Parse JSONL, inspect images/raw depth and check videos. Preserve full required outputs locally or in verified durable storage.

Commit an artifact index linking tests to logs, metrics, representative images, trajectories, media and deck. Distinguish repository links, verified durable links and local-only paths. Include small GitHub-viewable previews where permitted.

Nothing essential may remain only on the rental. Document reproducible dependency reacquisition and preserve irreplaceable outputs. Do not terminate the instance automatically.

Findings and presentation

Report demonstrated, documented, inferred, failed, blocked or not tested, with sources/run paths, across:
capture import; representation; trajectory/camera interface; RGB/depth; dynamics/control; collision mechanism; outdoor coverage; policy availability; setup burden; performance; reproducibility.

Assess unseen viewpoints, altitude changes, vegetation, moving objects and lighting from evidence; mark untested questions. Compare candidates only using repository evidence. Do not rank unmatched scenes, resolutions, hardware, controllers or tasks as equivalent benchmarks.

Update handoff, inventory, findings, reproducible instructions and learning guide. State A/B/D/C and fidelity status independently.

Produce the evidence-backed slideshow even if experiments are blocked. Include editable slide source, a readily viewable PDF, data-flow diagram, representative outputs, measured findings, failures, discussion points, missing outdoor/held-out evidence and provenance appendix.

Commit a reasonably sized review PDF and editable slide source under docs/grad-nav/ where practical. Keep large raw media outside Git. Otherwise provide verified reviewer-accessible durable presentation links. Ignored local paths alone are not GitHub-viewable delivery.

End with a concrete recommendation: reuse GRaD-Nav as a renderer, dynamics/control host or visual baseline; defer it; or reject it for this task. Explain decisive evidence and remaining blockers.

Return candidate-branch links, verified absolute local artifact/deck paths, durable links where available, preservation status, elapsed time and cost where known. Claim only what evidence establishes.