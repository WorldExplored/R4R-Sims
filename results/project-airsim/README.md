# Project AirSim audit results index

The [findings report](../../docs/project-airsim/findings.md) explains results and limits, including the 2026-10-08 local-only failure analysis. This directory contains small, browsable run records. Large raw captures, native metadata traces, videos, plots and calibration/pose records are in the ignored local `artifacts/project-airsim/<run-id>/` directories in the isolated worktree. Every listed raw directory was transferred from the A5000 host by resumable rsync and verified locally using its `manifest.sha256`; this is local preservation, not a durable off-machine backup. Each manifest gives per-file SHA256; `sizes.txt` gives directory byte totals. The manifest itself is hashed below. Historical run files were not changed by the later analysis.

| UTC run ID | Outcome | Ignored raw size (`du -sh`) | Manifest SHA256 |
| --- | --- | ---: | --- |
| `20261009T002738Z-pose-1` | Original A pass; DownCamera tilted 11.46° | 2.6M | `de4957cbff848827e3a652a6cae0e54bce5ea479d789367568dacf50ac2079ae` |
| `20261009T002820Z-pose-2` | Identical A repeat pass; same mount | 2.6M | `1889e9dcf76ae24470fa77df01ce7328e0486fabdddbec7766f6106aecdbda26` |
| `20261009T002844Z-smoke-1` | Blocked by server crash | 4.0K | `ffe4f8b92f9a2e4ef811261d3713060fd1200eb0e8d2f7abb7e5390829c7b4fd` |
| `20261009T002933Z-smoke-2` | Failed controller tasks and landing receive timeout | 76M | `30d177725a38884f3f7c12e5e6a23a980ca3209ed395cd5f382d4e5b2a16dc9b` |
| `20261009T003251Z-smoke-repair` | First timeout edit ineffective; same failure | 75M | `16bdaa933d7d8d9c58bfb425eb030e47eab2277871014bc56a596aba977311c0` |
| `20261009T003453Z-flight-1` | Route completed/landed; mixed false task results | 156M | `95773143a0d9f9f780f35d2a68ab889a1b5b83a09a55c8462ecd5c5dc0d53082` |
| `20261009T003606Z-flight-2` | Route repeated/landed; mixed false task results | 157M | `f93e47bb5b198a68b85e29c3efcc63a498f5d37e083d570895a38efbda451ccb` |
| `20261009T003933Z-pose-corrected` | Single separate A repair with 90° downward mount | 2.6M | `33539d5585964f1fee14461c8519af137ee707b6c87ce1eeb7d7b2e44fb1d093` |

## Openable evidence

The small [horizontal plot](previews/trajectory_horizontal.png), [vertical plot](previews/trajectory_vertical.png), [RGB preview](previews/rgb_preview.png), [labeled depth preview](previews/depth_preview.png) and [corrected downward view](previews/corrected_downward.png) are committed for browsing. Their [SHA256 list](previews/SHA256SUMS) is in this directory. Full-resolution plots for both B runs and the forward RGB videos are in each run's ignored `analysis/` directory; the raw `.npy` depths and PNGs are authoritative. A deck and PDF are under `artifacts/project-airsim/deliverables/` with a separate checksum list. The video uses ordered saved ForwardCamera frames at fixed 10 fps playback; it is not a real-time recording.

| Key locally preserved artifact | Exact size | SHA256 |
| --- | ---: | --- |
| `artifacts/project-airsim/20261009T003453Z-flight-1/analysis/forward_rgb_10fps.mp4` | 376,385 bytes | `539c67517fb56dad220abcc358cde737199980a964ceb67fd908f765a123f3f7` |
| `artifacts/project-airsim/20261009T003606Z-flight-2/analysis/forward_rgb_10fps.mp4` | 379,906 bytes | `bb2c7c816e7b8bbb2dce5ca8e34060435cdd96068762e41a8d4395d30936f50b` |
| `artifacts/project-airsim/20261009T003453Z-flight-1/analysis/trajectory_horizontal.png` | 63,525 bytes | `0eedd4ad02048d1425d97dbd80d6780d2c5f760279146fcd9bcb39451063943a` |
| `artifacts/project-airsim/20261009T003453Z-flight-1/analysis/trajectory_vertical.png` | 66,860 bytes | `e554cb8858df6104cdf1608b8ab238960cbbc094d9f5a99751324add6efb8f20` |
| `artifacts/project-airsim/20261009T003933Z-pose-corrected/images.jsonl` | 12,260 bytes | `6575d92798af204b77cffdad6c2e4e15bd092c2e04dae6bd75a4f7ceb83e6926` |
| `artifacts/project-airsim/deliverables/R4R_Project_AirSim_Audit.pptx` | 441,621 bytes | `d90530d34c6ea4c2f9fdbe841106390dc50fd61a4371fbc625917636e0a1094e` |
| `artifacts/project-airsim/deliverables/R4R_Project_AirSim_Audit.pdf` | 384,937 bytes | `e2e0062e8a070fde442a4fa3bb171e95e2a3e378685ee8d282c12c25e9224013` |
| `artifacts/project-airsim/deliverables/R4R_Project_AirSim_Audit_Revised.pptx` | 448,154 bytes | `7c04b1d23982f51908789ba6fc1c22fd01c8a57c9f5d31130d1e420b0eeb818a` |
| `artifacts/project-airsim/deliverables/R4R_Project_AirSim_Audit_Revised.pdf` | 400,112 bytes | `1c6a5cd023459a5292db9c43f34fe0ce0872f8256a990b25208aa17016db77e2` |
| `artifacts/project-airsim/deliverables/build_deck_revised.mjs` | 12,224 bytes | `4814fc4ca82161a85c86e3d725491b2e0d35beb984c79b5899aaf906b2c5c3bb` |

The host acquisition and launch logs are in `artifacts/project-airsim/host-setup/`, with a local `SHA256SUMS`. The later local preservation check recovered the previously remote-only `projectairsim_server.log` and `projectairsim_client.log`; all six logs verify against that list. A 16-file snapshot of relevant pinned source is in ignored `artifacts/project-airsim/source-pinned/`, with its own `SHA256SUMS`. Revised slide source and a checksum list are in `artifacts/project-airsim/deliverables/`. The revised 12-slide PPTX passed structural/layout/import validation, every rendered slide was visually scanned, the PDF has 12 pages, and its last page was visually checked. These are ignored local deliverables; the report and small index are pushed.

The pre-analysis local branch and pushed GitHub branch both resolved to `0a781497f6102184939902a09e090e7bb04c947e`. All recorded manifests and deliverables were verified locally. No essential Project AirSim evidence is known to remain only on the rental GPU. **Project AirSim remote files can be deleted.** This clearance excludes other projects on the instance; no remote deletion was performed.

Each run directory includes the exact historical command, runner commit, host/package freeze, config copies and hashes, logs, GPU CSV when sampled, run status, sizes and manifest. Full vehicle and image metadata streams live in the paired raw directory. The raw manifests use paths relative to the isolated worktree root, so check from there:

```bash
cd /Users/srreyanshsethi/Downloads/AL/R4R-Sims-worktrees/project-airsim
shasum -a 256 -c results/project-airsim/20261009T003453Z-flight-1/manifest.sha256
shasum -a 256 -c results/project-airsim/previews/SHA256SUMS
```

To reproduce a **new** run on the configured host, use a fresh UTC ID and the scripts in `simulators/project-airsim/` after verifying graphics and launching the official package. Do not reuse a historical ID; `run_one.sh` refuses an existing raw directory. The analysis invocation is:

```bash
/root/r4r-airsim-deps/venv/bin/python simulators/project-airsim/analyze.py \
  artifacts/project-airsim/<fresh-run-id> artifacts/project-airsim/<fresh-run-id>/analysis
simulators/project-airsim/collect_linux.sh <fresh-run-id>
```

Remote checkout revision for the two measured runs: `df28a7602c72cc84f6b966708e479f8de7150893`. Analysis was added at `31c626e` and video padding at `6b153bb`; the camera mount repair was `768ab92`. These later analysis changes do not change the stored measured flight records. The branch was pushed locally to GitHub; the remote checkout advanced by Git bundles because the VM had no GitHub credentials.
