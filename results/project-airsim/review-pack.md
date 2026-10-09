# Project AirSim review pack

The local-only [review](../../artifacts/project-airsim/review-pack/review.md) indexes preserved runs, command failures, source provenance and selected native RGB/depth pairs. The [uploadable archive](../../artifacts/project-airsim/review-pack/review-pack.zip) includes that review, its linked evidence, plots, revised slides and a per-file manifest. The expanded pack is ignored by Git; this index and the [offline builder](../../simulators/project-airsim/build_review_pack.py) are tracked.

| Local artifact | Bytes | SHA256 |
| --- | ---: | --- |
| `artifacts/project-airsim/review-pack/review-pack.zip` | 6,400,515 | `2776411d11cc53ae297e595d919c42b1def88a527dd49d3016718a8d8bf09199` |
| `artifacts/project-airsim/review-pack/review.md` | 16,444 | `9dcd4eff95b331df28f9ff88943c651666e52c8d9e93e440e48b7c9e5607a2b1` |
| `artifacts/project-airsim/review-pack/MANIFEST.sha256` | 39,786 | `31aa6befd2ece40292783cef5e3e290e4ae770b63becd091738f52895a8d1c61` |
| `artifacts/project-airsim/review-pack/MANIFEST.tsv` | 40,957 | `23ca8af1eee6567c4107d95ea797b35fc3addbdd24405053b7c4e27aba3e7a31` |
| `simulators/project-airsim/build_review_pack.py` | 34,768 | `f3747f3c10f3953ce9147615b9e122e50c3afb42d6f11a7d3db42b13322fbe1e` |

All eight original run manifests and the preview, host-log, pinned-source and deliverable checksum lists were checked before assembly: **zero missing or mismatched files**. The archive contains 15 selected RGB/float16-depth pairs. Its measured-flight state traces, original logs and metadata are byte-for-byte copies; new command tables, contact sheets and altitude plots are identified as offline analysis. `MANIFEST.tsv` records each file's byte size and SHA256. The complete raw image sequences remain in the original ignored local run directories.

From the worktree root, rebuild into an empty review-pack location using the bundled Python environment with NumPy and Pillow:

```bash
/Users/srreyanshsethi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  simulators/project-airsim/build_review_pack.py "$PWD"
```

The builder refuses to overwrite an existing pack. No simulator or rental instance is accessed. To verify an extracted archive, run `shasum -a 256 -c MANIFEST.sha256` from its root. The final archive passed ZIP extraction, all 320 internal manifest checks, 15 original sensor-file hashes, relative review links, PPTX package check and 12-page PDF render check.

For ChatGPT review, attach **`review-pack.zip`**. The PDF may be attached separately for immediate slide reading. The archive is 6.4 MB, below the 25 MB target; no split archive was needed.
