# R4R context for simulator audits

Prepared 2026-10-08. This briefing separates the lab's project motivation from the current simulator-audit task. It does not report new experiments.

## Confirmed project purpose

The lab document **Real4Real (1).pdf**, pages 1–2, describes reducing repeated outdoor drone flights: collect a small real capture once, reconstruct the environment, and generate realistic camera observations for new trajectories. Its pipeline is:

**real images + camera poses → reconstruction → scene representation → new trajectory → rendered camera observations → downstream evaluation**

The stated target is outdoor residential, suburban and campus environments below 100 m. The example of capture at 15 m and rendering at 50 m is a research goal, not an established result. The document calls for an outdoor train/test dataset, horizontal and vertical trajectories, PSNR/SSIM/LPIPS, and metrics relevant to a downstream application. Dataset preparation is assigned to the PhD students. Do not assume these assets have been supplied to this checkout.

The user additionally wants simulator applicability examined for indoor navigation, outdoor navigation including sparse scenes, and racing. These are candidate-use questions. They do not replace the lab's outdoor reconstruction and novel-view question, or establish a racing benchmark to run.

## Current task boundary

- Investigate sources and executable paths, prepare a reproducible handoff, then execute supported experiments on a user-supplied host.
- No new learned-policy training, random-weight substitute, or new scene training is authorized for this audit. The lab's broader reconstruction-training plan remains a separate task.
- Existing published scenes can establish integration. Faithfulness to AirLab's environment requires calibrated real captures, a defined split and held-out images.
- Do not invent unavailable project context, datasets, checkpoints, a downstream model, task thresholds or hardware specifications.
- Prior FiGS outputs are reported in earlier research notes. Import actual files and provenance before treating them as baseline evidence in this repository.

## What each experiment can establish

| Experiment | Inputs and outputs | Valid conclusion | Additional evidence needed |
| --- | --- | --- | --- |
| A: camera replay | Scene + explicit calibrated camera poses → images | Rendering and pose interface work | Held-out real images for fidelity |
| B: closed-loop control | Controller observes state/sensors → actions → simulated state → observations | Specified dynamics/control/sensor path works | Calibrated dynamics for real-drone claims |
| C: pretrained policy | Released compatible weights + task observations → actions and outcomes | That policy works or fails on that specified task | Comparable tasks/interfaces for cross-system performance claims |
| Common-camera comparison | Same scene, poses, intrinsics and rendering settings → paired outputs | Differences under matched inputs | Document remaining rendering differences |
| Real-scene evaluation | Reconstruction fitted on training captures + held-out real poses → paired render/real images | Fidelity in the evaluated coverage | Separate altitude, sparse-region and downstream evaluation |

A/B/C are experiment levels, not a requirement that every candidate supports all levels. A completed square flight is an integration check, not evidence of outdoor navigation or racing performance. A real-time video is not evidence of novel-view accuracy.

## Shared evidence to return

Each candidate should report the same dimensions using **demonstrated**, **documented**, **inferred**, **failed**, **blocked**, or **not tested**, with a source or run path:

1. Real capture import, representation formats, camera calibration and arbitrary trajectory replay.
2. Native scene execution, action/state interfaces, dynamics owner, controller, timing and camera capture.
3. RGB, depth semantics, collisions and any other requested sensors, assessed separately.
4. Sparse capture coverage versus sparse physical scene content. Vegetation, missing surfaces, unseen viewpoints, moving objects and lighting changes are distinct failure questions.
5. Released policy availability and task/interface compatibility. No comparable policy means no policy leaderboard.
6. Setup/access/maintenance burden, hardware compatibility, storage, elapsed time, measured resource use and preservation.
7. Indoor/outdoor/racing applicability, distinguishing demonstrated task performance from plausible use.
8. Concrete R4R decision: reuse as renderer, reuse as dynamics/control host, keep as visual baseline, defer, or reject for this task; explain the decisive evidence and remaining blocker.

Native scenes may differ. Compare native results as integration evidence only. Quantitative renderer comparisons require matching representations of the same world; policy comparisons also require compatible tasks and controllers. Different hardware and image workloads must be disclosed rather than ranked as intrinsic simulator speed.

## Repository and parallel work

Canonical repository: https://github.com/WorldExplored/R4R-Sims

User's local checkout: `~/Downloads/AL/R4R-Sims/`. Remote checkout: `~/R4R-Sims/` unless an existing authenticated checkout is explicitly selected. Code belongs in `simulators/<candidate>/`, notes in `docs/<candidate>/`, small records in `results/<candidate>/<run-id>/`, and large outputs in ignored `artifacts/<candidate>/<run-id>/` or verified durable storage.

Parallel candidates use separate branches and worktrees/checkouts. Do not run four agents against one mutable checkout. Each candidate owns its directories. Changes to shared files must be coordinated; do not add a framework just to enforce a common report. Push each candidate branch and pull that same branch locally. Integration must preserve other candidates' changes without force-pushing.

Git preserves authored code and small records. It does not preserve ignored videos, engine project assets, model weights or captured frames. Required artifacts must have a verified local or durable copy with a source manifest, byte sizes and SHA-256 hashes. A second folder on the same VM is insufficient.

For new rentals, use the choices in `docs/gpu-options.md` unless the user supplies an updated selection. Its prices and VRAM are an October 8 user-supplied snapshot, not live provider specifications. Phase 1 requires no rented GPU. Provision only after a candidate has a feasible artifact/OS path; verify the actual host's CPU/RAM/disk, graphics access and total price. The user subsequently supplied an already running A5000 host for Unreal; its actual compatibility evidence takes precedence over earlier provisional recommendations. See `docs/unreal/in-progress-followup.md`.

## Sources and limits of this briefing

- Primary internal project source: **Real4Real (1).pdf**, 2 pages, supplied September 4, read October 8. This is the source for project purpose, target environments, altitude example, pipeline and intended fidelity evaluation.
- User's October 8 prompt and concern: source for simulator breadth, audit scope, reproducibility, no training, local/GitHub preservation and blind-Codex context.
- Repository `README.md`, `AGENTS.md`, `docs/chat-update.md`, `docs/gpu-options.md`, read October 8: source for workspace and storage conventions and allowed rental list.
- **Real4Real_Simulator_Research_2026-10-02.md**, earlier assistant research: historical secondary context only. Reverify upstream capability claims before implementation. It is not a lab-approved benchmark specification.
- Unavailable here: approved AirLab dataset/checkpoint paths, capture calibration and split, chosen downstream algorithm, real-drone dynamics calibration, and a lab-approved numerical fidelity pass threshold.
