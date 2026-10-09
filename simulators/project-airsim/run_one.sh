#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "$0")/../.." && pwd)"
mode="${1:?pose, smoke or flight}"
id="${2:?fresh UTC run id}"
case "$mode" in pose|smoke|flight) ;; *) exit 2;; esac
[[ "$id" =~ ^[0-9]{8}T[0-9]{6}Z-[a-z0-9-]+$ ]] || { echo "invalid ID" >&2; exit 2; }
deps="${R4R_AIRSIM_DEPS:-/root/r4r-airsim-deps}"
raw="$repo/artifacts/project-airsim/$id"
small="$repo/results/project-airsim/$id"
mkdir -p "$small"
test ! -e "$raw"
scene="scene_audit_fast.json"
[[ "$mode" == pose ]] && scene="scene_audit_pose.json"
echo "UTC $(date -u +%FT%TZ)" > "$small/commands.log"
printf 'command: %q ' "$0" "$@" >> "$small/commands.log"
printf '\n' >> "$small/commands.log"
git -C "$repo" rev-parse HEAD > "$small/code-revision.txt"
sha256sum "$repo"/simulators/project-airsim/config/*.json > "$small/config-sha256.txt"
"$deps/venv/bin/python" -m pip freeze > "$small/python-freeze.txt"
uname -a > "$small/host.txt"
nvidia-smi -q > "$small/gpu.txt"
df -h "$repo" > "$small/disk.txt"
free -h > "$small/memory.txt"
cp "$repo"/simulators/project-airsim/config/*.json "$small/"
if ! ss -ltn | grep -q ':8990 '; then
  echo "simulator service port 8990 is not ready" | tee -a "$small/commands.log"
  exit 3
fi
mkdir -p "$(dirname "$raw")"
nvidia-smi --query-gpu=timestamp,memory.used,utilization.gpu --format=csv -l 1 > "$small/gpu-timeseries.csv" 2>&1 &
monitor_pid=$!
trap 'kill "$monitor_pid" 2>/dev/null || true; wait "$monitor_pid" 2>/dev/null || true' EXIT
limit=180
[[ "$mode" == pose ]] && limit=120
set +e
timeout --signal=TERM --kill-after=5s "${limit}s" "$deps/venv/bin/python" "$repo/simulators/project-airsim/audit.py" \
  --mode "$mode" --scene "$scene" \
  --config-dir "$repo/simulators/project-airsim/config" --output "$raw" 2>&1 | tee "$small/console.log"
status=${PIPESTATUS[0]}
set -e
printf '%s\n' "$status" > "$small/exit-status.txt"
printf 'exit_status=%s\n' "$status" >> "$small/commands.log"
test -f "$raw/run.json" && cp "$raw/run.json" "$small/run.json"
for file in counts.json errors.jsonl actions.jsonl reference_route.jsonl freshness.jsonl; do
  test ! -f "$raw/$file" || cp "$raw/$file" "$small/$file"
done
exit "$status"
