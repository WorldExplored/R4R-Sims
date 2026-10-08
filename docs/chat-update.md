# Shared update for simulator planning chats

Revise this chat's simulator plan and produce an updated, self-contained Codex prompt using the instructions below. Apply them to the simulator being discussed here. Remove Unreal-specific wording unless this chat is actually about Unreal. Preserve all previously agreed tests and deliverables; do not silently replace the full evaluation with an installation or smoke test.

## Repository and workspace

Use https://github.com/WorldExplored/R4R-Sims (`WorldExplored/R4R-Sims`) as the shared repository for all Real4Real simulator work. Read `README.md`, `AGENTS.md`, existing simulator notes, and relevant plans before editing.

Local checkout: `~/Downloads/AL/R4R-Sims/`. Reuse an existing checkout if present. `AL` is the parent workspace, not a different repository to commit this work to. Preserve unrelated files and existing Git histories.

Create or reuse `simulators/<simulator-name>/` for simulator-specific work. Use `configs/` and `scripts/` for genuinely shared files, `docs/` for plans and research notes, and `results/<simulator-name>/<run-id>/` for run records, metrics, and summaries. Large local outputs belong in ignored `artifacts/` or another documented artifact location. Do not assume a project pack, simulator installation, engine download, dataset, or checkpoint exists. Inspect first, then obtain required dependencies and document their sources and versions.

## Allowed rental options

These are the only GPU candidates in the user-supplied 2026-10-08 availability screenshot. Use this list until I provide an updated one.

| GPU label | VRAM shown | Displayed hourly price | Listed GPU counts |
| --- | --- | --- | --- |
| A100 | 80 GB | $1.82/hr | x8, x1 |
| A40 | 48 GB | $0.62/hr | x2, x1 |
| A6000 | 48 GB | $0.54/hr | x2, x1 |
| L40 | 48 GB | $0.86/hr | x1 |
| L40S | 48 GB | $0.82/hr | x1 |
| RTX6000 Ada | 48 GB | $0.75/hr | x1 |
| A10 | 24 GB | $1.29/hr | x1 |
| L4 | 24 GB | $0.62/hr | x1 |
| A4500 | 20 GB | $0.28/hr | x1 |

CPU Node is also listed: x1, $0.06/hr, or $0.05/hr spot. It is not a GPU replacement.

Choose the cheapest compatible configuration for this simulator's actual tests. State the exact GPU label and count to rent, why it is sufficient, and required CPU, RAM, storage, OS, and driver/rendering support. The screenshot does not provide those host specifications or establish multi-GPU billing units. Verify full-instance cost before rental. There is no fixed budget cap, but unnecessary spending should still be avoided. Do not recommend an unlisted GPU. Do not assume the cheapest GPU can run every simulator.

## Remote execution and preservation

The intended rental workflow uses an Ubuntu instance. Verify that this simulator and its available release actually support Ubuntu. If Windows or a different environment is required, explain the blocker rather than inventing an Ubuntu installation path.

Tell me which instance to rent and whether Codex needs the SSH command, host, username, port, and local private-key path. The key stays outside the repository; never request its contents in chat or commit credentials.

Use an authenticated Git clone on the instance and `git pull`, `git commit`, and `git push` to synchronize authored code, configs, notes, and small outputs in both directions. Verify repository read and write access on both machines. Do not force-push or overwrite uncommitted work. There is no `git copy` command.

Avoid recursive SCP transfers of huge engine or dataset trees. Download reproducible dependencies directly on the instance when local copies are unnecessary. Use resumable `rsync` over SSH or durable artifact storage for large outputs. Required remote outputs must be copied locally or durably preserved, with paths or links and SHA-256 checksums recorded in the run record. Git commits alone do not preserve ignored outputs.

Before terminating an instance, verify code and small results are pushed, required large artifacts are preserved, and transferred-file checksums match. Never leave the only copy of completed work on the rental instance. Do not commit engine installations, caches, datasets, checkpoints, or large videos to ordinary Git.

## What to return now

Give me the exact machine recommendation, any genuinely missing prerequisites, and one complete copy-paste Codex prompt. Embed the repository, workspace, simulator folder, chosen hardware, installation steps, every previously agreed test, evaluation criteria, output paths, Git synchronization, and artifact preservation instructions. Recover this chat's prior test plan before writing the prompt; if essential details are unavailable, identify them explicitly rather than inventing tests or dropping them.
