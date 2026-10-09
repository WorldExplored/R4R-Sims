#!/usr/bin/env bash
set -euo pipefail
deps="${R4R_AIRSIM_DEPS:-/root/r4r-airsim-deps}"
mkdir -p "$deps"
cd "$deps"
url=https://github.com/iamaisim/ProjectAirSim/releases/download/v1.0.1/Blocks-Linux-1.0.1.zip
if [[ ! -f Blocks-Linux-1.0.1.zip ]]; then
  timeout 2700 curl -fL --connect-timeout 15 -C - -o Blocks-Linux-1.0.1.zip "$url"
fi
echo '4a0c7b6de27ed32bdf4de1c31c222c19b796500108b654382b5d76b4ba000040  Blocks-Linux-1.0.1.zip' | sha256sum -c -
if [[ ! -d ProjectAirSim/.git ]]; then
  timeout 2700 git clone --depth 1 --branch v1.0.1 https://github.com/iamaisim/ProjectAirSim.git ProjectAirSim
fi
test "$(git -C ProjectAirSim rev-parse HEAD)" = 09755454b8d82b0231af7e59fd1ab8f980ff32c5
mkdir -p package
timeout 2700 unzip -qn Blocks-Linux-1.0.1.zip -d package
if [[ ! -x venv/bin/python ]]; then
  timeout 2700 python3.11 -m venv venv
  timeout 2700 venv/bin/python -m pip install --disable-pip-version-check projectairsim==1.0.2
fi
mkdir -p /tmp/r4r-airsim-run/home /tmp/r4r-airsim-run/runtime
cp -a package/. /tmp/r4r-airsim-run/
chown -R nobody:nogroup /tmp/r4r-airsim-run
chmod 700 /tmp/r4r-airsim-run/home /tmp/r4r-airsim-run/runtime
du -sh package venv
