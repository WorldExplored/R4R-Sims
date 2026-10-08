# Real for Real Simulator Evaluations

Working repository for AirLab's Real4Real simulator reproduction and evaluation work. Keep evaluation code, configurations, setup instructions, experiment records, and reviewable results here so humans, GPT, and Codex can continue from the same source of truth.

## Where things go

| Path | Contents |
| --- | --- |
| `simulators/` | Simulator-specific code and setup notes under `simulators/<simulator-name>/`. |
| `configs/` | Shared evaluation settings and machine-independent configurations. |
| `scripts/` | Shared setup, execution, evaluation, and artifact transfer scripts as needed. |
| `results/` | Run records, small metrics, summaries, and links to larger artifacts. |
| `docs/` | Evaluation plans, sources, and research notes. |
| `artifacts/` | Local copies of large outputs. Contents are ignored by Git. |

## Current status

The Unreal candidate has measured native camera replay and scripted closed-loop flight on the user-supplied A5000. A focused check reproduced the landing-state failure without route/images and corrected the UE5 mesh capture enough to export one dark Gaussian frame; useful appearance and fidelity remain unresolved. See [`docs/unreal/handoff.md`](docs/unreal/handoff.md), [`docs/unreal/focused-validation.md`](docs/unreal/focused-validation.md), [`results/unreal/`](results/unreal/) and the locally source-manifested raw artifacts. Other simulator candidates have separate evidence and status.

The broader work includes simulator reproduction and evaluation of drone dynamics, camera behavior, and rendering as required by each confirmed experiment plan. This scaffold does not define a benchmark or claim that any candidate simulator has been validated. Record the actual scope in `docs/` before running a new evaluation. Do not introduce policy training unless explicitly requested.

See [`docs/gpu-options.md`](docs/gpu-options.md) for the user-supplied GPU availability snapshot.

## Local and remote workflow

Suggested local checkout: `~/Downloads/AL/R4R-Sims/`. Use a separate checkout of this same repository on the rented Ubuntu instance. Keep each simulator's work inside `simulators/<simulator-name>/`.

1. Clone this repository on each machine using the GitHub URL. Keep credentials and SSH keys outside the repository.
2. Before work, run `git status` and `git pull --ff-only`. Preserve uncommitted work and resolve divergence without overwriting it.
3. Commit and push code, configs, setup notes, and small outputs on the machine that produced them. Pull those commits on the other machine.
4. Save each run under `results/<simulator>/<run-id>/`, including commands, code revision, environment, parameters, metrics, failures, and artifact locations.
5. Transfer large outputs separately with resumable `rsync` over SSH or durable artifact storage. Record the location, file size, and SHA-256 in the run record. Avoid recursive SCP transfers of entire engine or dataset trees.
6. Before shutting down a rented instance, verify code and small results are pushed, and required large outputs are copied locally or to durable storage and their checksums match. Do not leave the only copy on the instance.

Git tracks changes; it is not a bulk-transfer service. Do not commit engine installations, build caches, checkpoints, datasets, large videos, or raw image sequences. Install or download these directly on the instance when local copies are unnecessary. Preserve acquisition instructions, upstream revisions, licenses, and required output artifacts instead.

## Shared planning update

The simulator-neutral update for other planning chats is in [`docs/chat-update.md`](docs/chat-update.md). It includes the GPU candidate list and instructions for revising each simulator's Codex prompt.

## Access from GPT and Codex

Repository access depends on the GitHub account and integration permissions. Grant the ChatGPT GitHub connection access to this repository if it uses selected-repository permissions. Connect or select this repository in Codex; local Codex can use an authenticated clone. A link alone does not grant write access, and some GPT environments only support reading GitHub. An assistant must verify its available write capability before promising edits.

Start by reading this README and `AGENTS.md`. Use the repository itself for ongoing work, rather than independent folders whose changes never get synchronized.
