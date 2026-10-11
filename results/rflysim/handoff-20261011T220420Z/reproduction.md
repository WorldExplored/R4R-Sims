# Offline reproduction

No Mac simulator install or compute session. Start in this repository. Retrieve the archived inputs only if existing verified local copies are absent. Use a new output directory for each derivative. The review encoder intentionally refuses to overwrite an existing video directory.

```sh
python3.12 -m venv /tmp/rflysim-review-env
/tmp/rflysim-review-env/bin/pip install -r simulators/rflysim/analysis-requirements.txt -r simulators/rflysim/review-requirements.txt
/tmp/rflysim-review-env/bin/python simulators/rflysim/inspect-native-log.py --input artifacts/rflysim/eval-20261010T215531Z/raw/B1-native.ulg --output /tmp/rflysim-ulog-new
/tmp/rflysim-review-env/bin/python simulators/rflysim/build-review-media.py --input artifacts/rflysim/eval-20261010T215531Z/raw --output /tmp/rflysim-videos-new --manifest /tmp/rflysim-videos-new.json
```

FFmpeg is the pinned imageio-ffmpeg wheel binary. Encoding depends on its FFmpeg version and the installed Arial caption font; version/SHA and exact arguments are in videos.json. Playback is ordinal 10 FPS. Scientific source PNG/clock records remain unchanged.

## Revised existing deck

Use the bundled Artifact Tool runtime and a fresh workspace. The preserved original deck is the font/design reference. Set these variables to the dependency paths reported by `load_workspace_dependencies`:

```sh
export RUNTIME_NODE=/Users/srreyanshsethi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node
export RUNTIME_NODE_MODULES=/Users/srreyanshsethi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules
export RUNTIME_PYTHON=/Users/srreyanshsethi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
export PRESENTATION_SKILL_DIR=/Users/srreyanshsethi/.codex/plugins/cache/openai-primary-runtime/presentations/26.1009.11318/skills/presentations
export PRESENTATION_REFERENCE=/Users/srreyanshsethi/Downloads/AL/R4R-Sims-rflysim/artifacts/rflysim/handoff-20261011T220420Z/before/results/rflysim/eval-20261010T215531Z/rflysim-evaluation.pptx
mkdir -p /tmp/rflysim-deck-new/output
ln -s "$RUNTIME_NODE_MODULES" /tmp/rflysim-deck-new/node_modules
cp simulators/rflysim/build-preparation-deck.mjs /tmp/rflysim-deck-new/build.mjs
"$RUNTIME_NODE" /tmp/rflysim-deck-new/build.mjs /tmp/rflysim-deck-new results/rflysim/eval-20261010T215531Z/deck-content.json /tmp/rflysim-deck-new/output/rflysim-evaluation.pptx
/tmp/rflysim-review-env/bin/python simulators/rflysim/export-review-pdf.py --previews /tmp/rflysim-deck-new/previews --content results/rflysim/eval-20261010T215531Z/deck-content.json --output /tmp/rflysim-deck-new/output/rflysim-evaluation.pdf
```

The original reference can alternatively be recovered from Git9749a40. Re-render and inspect changed slides before publication. Final PPTX/PDF bytes can differ across artifact/PDF metadata builds; input/scientific evidence hashes are stable. The three-page index is a navigation document, not an experimental metric.
