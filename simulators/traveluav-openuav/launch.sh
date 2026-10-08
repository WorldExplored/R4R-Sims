#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/layout.sh"
level="${1:?usage: launch.sh a|b|c}"
snapshot="$ARTIFACTS/launch-$(date -u +%Y%m%dT%H%M%SZ)-$level-$$/code"
mkdir -p "$snapshot"
cp -a "$ROOT/." "$snapshot/"
export R4R_CODE_SNAPSHOT="$snapshot"
if [[ "$level" == c ]]; then
  export PATH="$ENV_C/bin:$PATH"
  bash "$snapshot/policy_smoke.sh"
else
  export PATH="$ENV_AB/bin:$PATH"
  bash "$snapshot/host.sh" "$level"
fi
