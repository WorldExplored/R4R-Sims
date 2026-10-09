#!/usr/bin/env bash
set -euo pipefail
deps="${R4R_AIRSIM_DEPS:-/root/r4r-airsim-deps}"
attempt="${1:?launch attempt number 1, 2 or 3}"
[[ "$attempt" =~ ^[123]$ ]] || exit 2
if ss -ltn | grep -q ':8990 '; then
  echo "A simulator already listens on 8990; inspect it before launching another." >&2
  exit 3
fi
cd /tmp/r4r-airsim-run
test -x ./Blocks.sh
( setsid runuser -u nobody -- env HOME=/tmp/r4r-airsim-run/home XDG_RUNTIME_DIR=/tmp/r4r-airsim-run/runtime \
  ./Blocks.sh -RenderOffScreen -nosound > "$deps/launch${attempt}.log" 2>&1 < /dev/null &
  echo $! > "$deps/launch${attempt}.pid" )
pid="$(cat "$deps/launch${attempt}.pid")"
for second in $(seq 1 120); do
  if ss -ltn | grep -q ':8990 '; then
    echo "ready after at most ${second}s, audit process group $pid"
    exit 0
  fi
  if ! kill -0 "$pid" 2>/dev/null; then
    echo "launch exited; inspect $deps/launch${attempt}.log" >&2
    exit 1
  fi
  sleep 1
done
echo "not ready within 120s; inspect $deps/launch${attempt}.log" >&2
exit 124
