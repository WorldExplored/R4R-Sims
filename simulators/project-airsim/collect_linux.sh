#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "$0")/../.." && pwd)"
id="${1:?run id}"
small="$repo/results/project-airsim/$id"
raw="$repo/artifacts/project-airsim/$id"
test -d "$small"
test -d "$raw"
( cd "$repo"; find "results/project-airsim/$id" "artifacts/project-airsim/$id" -type f -print0 | sort -z | xargs -0 sha256sum ) > "$small/manifest.sha256"
du -sb "$small" "$raw" > "$small/sizes.txt"
echo "Manifest: $small/manifest.sha256"
echo "Transfer both results/$id and artifacts/$id to the isolated local worktree; then sha256sum -c manifest.sha256 at destination."
