#!/usr/bin/env bash
set -euo pipefail
deps="${R4R_AIRSIM_DEPS:-/root/r4r-airsim-deps}"
attempt="${1:?launch attempt number}"
[[ "$attempt" =~ ^[123]$ ]] || exit 2
pid="$(cat "$deps/launch${attempt}.pid")"
test "$pid" -gt 1
cmd="$(ps -p "$pid" -o args= || true)"
[[ "$cmd" == *"runuser -u nobody"* && "$cmd" == *"Blocks.sh"* ]] || { echo "recorded PID no longer matches audit launch" >&2; exit 3; }
kill -- "-$pid"
