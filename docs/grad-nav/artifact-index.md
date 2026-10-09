# Artifact index

Candidate branch: [audit/grad-nav](https://github.com/WorldExplored/R4R-Sims/tree/audit/grad-nav). [Findings](findings.md), [handoff](handoff.md), [sources](sources.md), [learning guide](learning-guide.md), [repair history](repair-history.json), [asset inventory](asset-inventory.csv), [preservation](preservation.json).

## Current v4 deck and executed results

**Start here:** [viewable v4 PDF](GRaD-Nav_R4R_Audit-v4.pdf), [editable v4 PowerPoint](GRaD-Nav_R4R_Audit-v4.pptx), [observed rendering findings](render-results.md) and current editable source `deck-source.mjs`. A now produces RGB/depth with exact direct/author parity; capture registration remains unresolved. D produces achieved-state camera frames and video. C and real-scene fidelity remain blocked. The pre-repair deck below is historical.

| Run | Status | Small records | Verified local raw directory |
|---|---|---|---|
| 20261009T020334Z-a-630efe | compiler repaired; A initial parity | [records](../../results/grad-nav/20261009T020334Z-a-630efe/) | `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T020334Z-a-630efe` |
| 20261009T020714Z-a-1004f1 | A frozen route + raw-depth/timing diagnostics | [records](../../results/grad-nav/20261009T020714Z-a-1004f1/) | `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T020714Z-a-1004f1` |
| 20261009T020926Z-d-748818 | D native coordinate coupling; physical calibration blocked | [records](../../results/grad-nav/20261009T020926Z-d-748818/) | `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T020926Z-d-748818` |
| 20261009T021154Z-scene-diagnostic-64cb11 | pose/background diagnostics | [records](../../results/grad-nav/20261009T021154Z-scene-diagnostic-64cb11/) | `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T021154Z-scene-diagnostic-64cb11` |
| 20261009T020316Z-compiler-preflight | minimal C++/CUDA and emitted build proof | [records](../../results/grad-nav/20261009T020316Z-compiler-preflight/) | `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/compiler-diagnostics/20261009T020316Z-compiler-preflight` |

Viewable [D video](/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T020926Z-d-748818/coupled.mp4), [first D frame](/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T020926Z-d-748818/frames/000-coupled.png), [frozen A frame](/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T020714Z-a-1004f1/frames/000-direct.png). Files are local, not externally hosted. Scientific-input manifest is committed in results/grad-nav/preflight/scientific-manifest.json; small state/action/reference/camera records are now committed for historical and new runs after byte/hash comparison.

Latest timing: [20261009T022120Z-a-e1d652](../../results/grad-nav/20261009T022120Z-a-e1d652/); verified raw `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T022120Z-a-e1d652`. Direct camera matrix uploaded before timing. Earlier intervals and outputs remain preserved.

## Preserved scientific inputs

Local scientific inputs: `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/scientific-inputs/`. The [committed scientific-input manifest](../../results/grad-nav/preflight/scientific-manifest.json) records per-file bytes/SHA256; output manifests live in each run and verification in preservation.json. These scientific inputs are stored on this Mac, rather than in GitHub. Original capture PNGs support preservation and qualitative registration checks; they are not rendered outputs or trustworthy held-out fidelity references.

## Historical first-session records

Historical pre-repair deck: [editable PowerPoint](GRaD-Nav_R4R_Audit.pptx), [viewable PDF](GRaD-Nav_R4R_Audit.pdf) and source data in results. These files are committed for GitHub review. Raw local paths are separate from repository links. No externally hosted durable link was created.

| Test | Status | GitHub-viewable small records | Verified raw local path |
|---|---|---|---|
| baseline-none | failed, exit 1 | [records](../../results/grad-nav/20261009T012421Z-baseline-none-c8dc72/) | `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T012421Z-baseline-none-c8dc72` |
| force | completed, exit 0 | [records](../../results/grad-nav/20261009T012423Z-force-21326e/) | `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T012423Z-force-21326e` |
| smoke | completed, exit 0 | [records](../../results/grad-nav/20261009T012426Z-smoke-b457b8/) | `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T012426Z-smoke-b457b8` |
| recovery | completed, exit 0 | [records](../../results/grad-nav/20261009T012429Z-recovery-e58f8a/) | `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T012429Z-recovery-e58f8a` |
| conversion | completed, exit 0 | [records](../../results/grad-nav/20261009T012433Z-conversion-04f90b/) | `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T012433Z-conversion-04f90b` |
| a | failed, exit 1 | [records](../../results/grad-nav/20261009T013414Z-a-ba21bc/) | `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T013414Z-a-ba21bc` |
| a | failed, exit 1 | [records](../../results/grad-nav/20261009T013523Z-a-4178ca/) | `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T013523Z-a-4178ca` |
| a | failed, exit 1 | [records](../../results/grad-nav/20261009T013625Z-a-dd2ac9/) | `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T013625Z-a-dd2ac9` |
| d | failed, exit 1 | [records](../../results/grad-nav/20261009T013641Z-d-3a4637/) | `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T013641Z-d-3a4637` |
| a | failed, exit 1 | [records](../../results/grad-nav/20261009T013743Z-a-b58f3b/) | `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T013743Z-a-b58f3b` |
| d | failed, exit 1 | [records](../../results/grad-nav/20261009T013759Z-d-1ca173/) | `/Users/srreyanshsethi/Downloads/AL/R4R-Sims-grad-nav/artifacts/grad-nav/20261009T013759Z-d-1ca173` |


**Historical status — first stopped session, before the GCC11 repair:** “No rendered RGB/depth or video was produced.” At that time only B trajectories were demonstrated and used in the deck chart. This statement no longer describes the current audit: the continuation above produced and preserved A RGB/depth and D video.

## Shutdown readiness

See [shutdown-readiness.json](shutdown-readiness.json) for the dated read-only check. GRaD-Nav local evidence is verified; shared-host shutdown is currently blocked by four unmatched TravelUAV support logs requiring preservation. No instance termination or new experiment occurred.
