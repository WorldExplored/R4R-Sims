#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "$0")/../.." && pwd)"
id="${1:?run id}"
small="$repo/results/project-airsim/$id"
raw="$repo/artifacts/project-airsim/$id"
test -d "$small"
test -d "$raw"
du -sb "$small" "$raw" > "$small/sizes.txt"
( cd "$repo"; find "results/project-airsim/$id" "artifacts/project-airsim/$id" -type f ! -name manifest.sha256 -print0 | sort -z | xargs -0 sha256sum ) > "$small/manifest.sha256"
echo "Manifest: $small/manifest.sha256"
echo "Transfer both results/$id and artifacts/$id to the isolated local worktree; then sha256sum -c manifest.sha256 at destination."
