# Execution and collection handoff

Updated 2026-10-08. Read [report.md](report.md) for measurements, eligibility and limitations; [sources.md](sources.md) and [asset_inventory.md](asset_inventory.md) for provenance. Original authored files/hashes and original directory remain preserved in recovery.json and phase1-handoff.md. No nested upstream repository is tracked.

## Workspaces and synchronization

Task branch `audit/traveluav-openuav-20261008T2215Z` at [GitHub](https://github.com/WorldExplored/R4R-Sims/tree/audit/traveluav-openuav-20261008T2215Z).
Mac worktree: `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-worktrees/traveluav-openuav-20261008T2215Z`.
Remote: `/workspace/R4R-Sims`. Canonical raw output copies: `/Users/srreyanshsethi/Downloads/AL/R4R-Sims/artifacts/traveluav-openuav/`.

Only one machine produces authored edits at a time. Check status/diff/staged, commit intended paths, push, then pull --ff-only in the receiving clean task checkout. Do not switch/pull/stage the canonical Mac checkout: another candidate has changes there. Main integration is pending. Both machines have performed actual authored commits/pushes and received the other's commits. Remote gh credentials are independent of the Mac SSH identity.

Protected SSH identity is `/Users/srreyanshsethi/.ssh/r4r-209.137.198.205.pem`, mode 400. Connect with normal strict host checking and the recorded known-hosts file:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes \
  -o UserKnownHostsFile=/Users/srreyanshsethi/.ssh/r4r-209.137.198.205.known_hosts \
  -i /Users/srreyanshsethi/.ssh/r4r-209.137.198.205.pem ubuntu@209.137.198.205
```

SSH port 22. Fingerprint agrees with the host's public key; independent provider fingerprint information was unavailable. No private key was copied to the VM or Git. Host is not to be terminated automatically.

## Already prepared host

Non-root Ubuntu user; Ubuntu 22.04.5; A6000 48 GB class; actual 6 vCPU/47 GiB RAM/251 GiB disk. Recommended future allowance is A6000 ×1, Ubuntu 22.04 x86-64, 16 vCPU/64 GB/300 GB SSD with proprietary graphics/Vulkan access. Native scene-only measurements support a smaller rendering host, but inference/complex-scene minimum is not measured. A10 is a cheaper candidate within the allowed list, conditional on combined-memory headroom; not tested. Full-instance/storage pricing is unknown; $0.54/h is the user-displayed GPU quote only.

Dependencies are isolated at `artifacts/traveluav-openuav/dependencies/`: upstream checkout at SHA `5cc26e9a4a55b9c788e918f7c3bb2dc5076a85e6`; separate Python 3.10 env-ab/env-c; pinned datasets/models under assets; CUDA build components and LLaVA source ignored. A/B AirSim1.8.1, numpy1.26.3, Pillow10.2.0, Hub0.27.1; RPC modern MessagePack1.1.0 compatibility diff retained. C Torch2.0.1/cu118/TV0.15.2/TA2.0.2 and exact inference pins in requirements-c.txt/freezes. No quantization/training.

## Fresh setup, only if needed

Inspect existing files/installations, free space, ignored roots and ports before executing. These commands target this Ubuntu host. They were used in setup, but a clean-host full replay after final corrections has not been performed. Do not reapply an upstream patch over an already patched checkout. GPU-dependent commands are executed on this host; unexecuted on a new host until its preflight passes.

```sh
cd /workspace/R4R-Sims
S=simulators/traveluav-openuav
# Requires installed python3.10-venv, p7zip-full, build-essential, g++-11,
# rsync, ffmpeg, Vulkan utility and normal NVIDIA graphics device access.
timeout 3600s bash "$S/setup.sh" ab
timeout 3600s bash "$S/setup.sh" c
source "$S/layout.sh"
# Inspect listings/expanded size and require > selected expansion + 10 GiB headroom.
7z l -slt "$ASSETS/downloads/env/closeloop_envs.zip"
timeout 300s 7z x -y "$ASSETS/downloads/env/closeloop_envs.zip" \
  -o"$ASSETS/envs" 'closeloop_envs/ModernCityMap.sh' \
  'closeloop_envs/ModernCityDowntown/*' 'closeloop_envs/Engine/*'
timeout 300s bash "$S/extract.sh"
PYTHONPATH="$S:$S/compat" "$ENV_C/bin/python" "$S/prepare_episode.py"
# Fresh pinned upstream only: preserve prior diffs; git apply --check comes first.
PYTHONPATH="$S:$S/compat" "$ENV_C/bin/python" "$S/prepare_c.py"
timeout 1800s bash "$S/c-extension.sh"
```

The selected map archive lacks merged_data.json; preprocessing creates it with the explicit seed-function fix, not policy training. On an existing host prepare_episode refuses overwrite. `verify_metadata.py` regenerates twice in its own ignored isolated input copy and verifies hashes/instruction/source inputs. Dataset feature files not consumed by inference are not trained/generated. Scene is the released `ModernCityMap.sh` → `ModernCityDowntown/Binaries/Linux/ModernCityDowntown` ELF, not a new editor project. Setup's budgets cover installs/downloads; archive failures must not be treated as absent artifacts.

## Preflight, A/B/C and collection

```sh
cd /workspace/R4R-Sims
S=simulators/traveluav-openuav
source "$S/layout.sh"
export PATH="$ENV_AB/bin:$PATH"
bash "$S/host.sh" preflight
# Use persistent tmux; logs and run IDs are created by runners, not terminal scrollback.
tmux new-session -d -s r4r-a-next "cd /workspace/R4R-Sims && bash $S/launch.sh a > /workspace/R4R-Sims/artifacts/traveluav-openuav/a-next-launch.log 2>&1"
# After A settles, inspect its run.json/console and collect using the printed absolute path.
bash "$S/collect.sh" /workspace/R4R-Sims/results/traveluav-openuav/ACTUAL_A_RUN_ID
# Then B, same selected first-six-state route; no endpoint-threshold pause.
tmux new-session -d -s r4r-b-next "cd /workspace/R4R-Sims && bash $S/launch.sh b > /workspace/R4R-Sims/artifacts/traveluav-openuav/b-next-launch.log 2>&1"
bash "$S/collect.sh" /workspace/R4R-Sims/results/traveluav-openuav/ACTUAL_B_RUN_ID
# C only after compatible checkpoint gates; preserve official assistant/stops.
tmux new-session -d -s r4r-c-next "cd /workspace/R4R-Sims && bash $S/launch.sh c > /workspace/R4R-Sims/artifacts/traveluav-openuav/c-next-launch.log 2>&1"
bash "$S/collect.sh" /workspace/R4R-Sims/results/traveluav-openuav/ACTUAL_C_RUN_ID
```

Do not rerun solely to improve an unsuccessful task outcome. Each retry/failure gets a fresh UTC run ID. launch.sh freezes authored runner code; source patches are copied into each run. No `scripts/eval.sh` verbatim: upstream has developer paths, mismatched ports, invalid DDP80005, batch2 and 200 decisions. C uses server30000/scene30001/DDP20001; A/B41451. Occupied ports are blockers; do not kill unrelated jobs.

A/B scene-startup budget60s, probe90s. B's controller RPC is awaited through a separate client and state cadence is0.2s, images independent; timeout/error produces incomplete flight. Final state precedes pause. C server-start budget30s/server lifetime900s/evaluation600s including imports/model loading; batch1, seed100, ten learned decisions, always_help/use_gt true. Upstream internal five-second movement limit and reset/heuristic behavior stay unchanged. These are bounded smoke runs, not benchmark reproduction.

Expected A: reference/actions/state/camera/events, six poses, 30 PNG+30 raw depth arrays, 5-view contact sheet. B: completed/error RPC event, dense achieved state/IMU/contact samples, image observations, final-before-pause, polyline errors/trajectory plot. C: instruction/assistant notices/input identifiers, coarse/refined waypoints, segment resets/actions, actual unpadded states, detector/stop/outcome/timing traces and official result only if produced. No policy weights for A/B; all C asset identities in manifests. Run records retain exit statuses, configs/freeze/upstream diffs/seeds/paths/timestamps/errors. Pipeline status is PIPESTATUS[0], not tee.

Acceptance: every expected A PNG/depth opens; camera/vehicle/requested frames and observed timestamp spread are recorded; B distinguishes API completion from motion/tracking and reports achieved cadence/missing data; C all required load gates pass before any learned action, with truncation/failure clearly classified. Native fidelity/real transfer is outside these criteria. Official metric directories contain only evaluator episodes, not audit metadata. A handful of episodes cannot reproduce full-split scores.

## Preservation and follow-up

Snapshot small results every5–10min and after failure, then settle manifests and copy required outputs off VM with resumable rsync:

```sh
# On Mac: explicit private identity stays local; do not copy dependency trees.
rsync -az --partial --exclude=dependencies --exclude='launch-*' \
  -e 'ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=/Users/srreyanshsethi/.ssh/r4r-209.137.198.205.known_hosts -i /Users/srreyanshsethi/.ssh/r4r-209.137.198.205.pem' \
  ubuntu@209.137.198.205:/workspace/R4R-Sims/artifacts/traveluav-openuav/ \
  /Users/srreyanshsethi/Downloads/AL/R4R-Sims/artifacts/traveluav-openuav/
```

Use settled SHA manifests, not hashes of live files. Verify every A image/depth, representative B/C files and tar members locally; record bytes/hashes/locations and provenance of reproducible assets verified accessible from Mac. Never delete remote evidence before verification. Archive filenames are unique and collect.sh refuses overwriting an existing archive. Corrections to record metadata require fresh manifests without overwriting old archive bytes.

Follow-up prompt: “Read docs/traveluav-openuav/report.md, handoff.md and preservation.json on the audit branch. Verify current Git/host state. Continue only the explicitly outstanding blocker or a supplied calibrated R4R common-scene comparison; preserve native A/B/C records, upstream SHA, privileged inputs and budgets. Do not train, rent or terminate hardware.”

Final collection helper: `preserve.py inventory RUN CAPTURE --archive ARCHIVE` settles hashes on the producing host; `preserve.py verify LOCAL_RUN LOCAL_CAPTURE --archive LOCAL_ARCHIVE` checks destination bytes and decodes files/archives. Use bundled Mac Python withNumPy/Pillow or an existing isolated environment. `calibration.py RUN` checks nominal mounts against actualRGB/depth response poses. Final run IDs: A20261009T001125Z-a-23177, B20261008T234423Z-b-17460, C20261008T235452Z-c-21144. See preservation.json forverified local paths and finalstop verdict.
