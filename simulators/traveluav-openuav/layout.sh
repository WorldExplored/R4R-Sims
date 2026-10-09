#!/usr/bin/env bash
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$ROOT" rev-parse --show-toplevel)"
ARTIFACTS="$REPO/artifacts/traveluav-openuav"
RESULTS="$REPO/results/traveluav-openuav"
ASSETS="$ARTIFACTS/dependencies/assets"
UPSTREAM="$ARTIFACTS/dependencies/upstream"
ENV_AB="$ARTIFACTS/dependencies/env-ab"
ENV_C="$ARTIFACTS/dependencies/env-c"
export PYTHONPATH="$ROOT:$ROOT/compat${PYTHONPATH:+:$PYTHONPATH}"

export MPLCONFIGDIR="$ARTIFACTS/dependencies/cache/matplotlib"
mkdir -p "$MPLCONFIGDIR"

export PYTHONDONTWRITEBYTECODE=1
