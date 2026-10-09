#!/usr/bin/env bash
set -euo pipefail
deps="${R4R_AIRSIM_DEPS:-/root/r4r-airsim-deps}"
test "$(sha256sum "$deps/Blocks-Linux-1.0.1.zip" | cut -d' ' -f1)" = "4a0c7b6de27ed32bdf4de1c31c222c19b796500108b654382b5d76b4ba000040"
test -x "$deps/package/Blocks.sh"
test -x "$deps/venv/bin/python"
"$deps/venv/bin/python" - <<'PY'
import projectairsim
from projectairsim import Drone, World, ProjectAirSimClient
from projectairsim.utils import unpack_image
assert projectairsim.__version__ == '1.0.2'
print('client', projectairsim.__version__)
PY
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
vulkaninfo --summary | grep -E 'deviceName|driverID|driverName'
df -h "$deps"
free -h
