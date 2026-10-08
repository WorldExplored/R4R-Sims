#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/layout.sh"
[[ $(uname -s) == Linux && $(id -u) != 0 ]]
level="${1:-ab}"
mkdir -p "$ARTIFACTS/dependencies" "$RESULTS"
run_id="$(date -u +%Y%m%dT%H%M%SZ)-setup-$level-$$"
run="$RESULTS/$run_id"; mkdir -p "$run"
exec > >(tee -a "$run/console.log") 2>&1
status=1
finish() {
  status=$?
  printf '{"run_id":"%s","level":"setup-%s","exit_status":%s,"ended_utc":"%s"}\n' "$run_id" "$level" "$status" "$(date -u +%FT%TZ)" > "$run/run.json"
}
trap finish EXIT
logged() { printf '%q ' "$@" >> "$run/commands.log"; printf '\n' >> "$run/commands.log"; if "$@"; then rc=0; else rc=$?; fi; printf 'exit_status=%s\n' "$rc" >> "$run/commands.log"; return "$rc"; }
if [[ ! -d "$UPSTREAM/.git" ]]; then logged git clone https://github.com/prince687028/TravelUAV.git "$UPSTREAM"; logged git -C "$UPSTREAM" checkout --detach 5cc26e9a4a55b9c788e918f7c3bb2dc5076a85e6; fi
[[ $(git -C "$UPSTREAM" rev-parse HEAD) == 5cc26e9a4a55b9c788e918f7c3bb2dc5076a85e6 ]]
git -C "$UPSTREAM" status --short > "$run/upstream-status.txt"
git -C "$UPSTREAM" diff > "$run/upstream-before.patch"
if [[ "$level" == ab ]]; then
  [[ -x "$ENV_AB/bin/python" ]] || logged python3.10 -m venv "$ENV_AB"
  py="$ENV_AB/bin/python"
  logged "$py" -m pip install pip==24.0 setuptools==68.2.2 wheel==0.41.3
  logged "$py" -m pip install numpy==1.26.3 Pillow==10.2.0 msgpack==1.1.0 tornado==4.5.3 huggingface_hub==0.27.1 matplotlib==3.10.0 psutil==6.1.1 opencv-contrib-python==4.10.0.84
  logged "$py" -m pip install --no-deps msgpack-rpc-python==0.4
  logged "$py" "$ROOT/compat_msgpack.py" "$run/rpc-compat"
  logged "$py" -m pip install --no-build-isolation --no-deps airsim==1.8.1
  logged "$py" -c 'import airsim,msgpackrpc,numpy; assert numpy.__version__ == "1.26.3"; print("AirSim import OK",airsim.__version__)'
  "$py" -m pip freeze > "$run/pip-freeze.txt"
  logged "$py" "$ROOT/assets.py" ab --record "$run/assets.json"
elif [[ "$level" == c ]]; then
  [[ -x "$ENV_C/bin/python" ]] || logged python3.10 -m venv "$ENV_C"
  py="$ENV_C/bin/python"
  logged "$py" -m pip install pip==24.0 setuptools==68.2.2 wheel==0.41.3
  logged "$py" -m pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
  logged "$py" -m pip install -r "$ROOT/requirements-c.txt"
  logged "$py" -m pip install --no-deps msgpack-rpc-python==0.4
  logged "$py" "$ROOT/compat_msgpack.py" "$run/rpc-compat"
  logged "$py" -m pip install --no-build-isolation --no-deps airsim==1.8.1
  logged "$py" -m pip install --no-deps -e "$UPSTREAM/Model/LLaMA-UAV"
  llava="$ARTIFACTS/dependencies/llava"
  if [[ ! -d "$llava/.git" ]]; then logged git clone https://github.com/haotian-liu/LLaVA.git "$llava"; logged git -C "$llava" checkout --detach 1619889c712e347be1cb4f78ec66e7cf414ac1a6; fi
  logged "$py" -m pip install --no-deps -e "$llava"
  "$py" -m pip freeze > "$run/pip-freeze.txt"
  logged "$py" "$ROOT/assets.py" c --record "$run/assets.json"
else echo "Usage: setup.sh ab|c"; exit 2; fi
status=0
