#!/usr/bin/env bash
set -Eeuo pipefail

source "$(dirname "$0")/layout.sh"
ENV_ROOT="$ASSETS/envs"
DATA_ROOT="$ASSETS/dataset"
EPISODE_REL='ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f/merged_data.json'
SCENE="$ENV_ROOT/closeloop_envs/ModernCityMap.sh"
PORT=41451

preflight() {
  test "$(uname -s)" = Linux || { echo 'Requires Linux'; return 2; }
  test -x "$SCENE" || { echo "Missing executable: $SCENE"; return 2; }
  test -s "$DATA_ROOT/$EPISODE_REL" || { echo "Missing episode: $DATA_ROOT/$EPISODE_REL"; return 2; }
  test -s "$DATA_ROOT/ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f/mark.json" || { echo 'Missing mark.json'; return 2; }
  command -v nvidia-smi >/dev/null
  command -v timeout >/dev/null
  command -v python >/dev/null
  python -c 'import airsim,numpy,PIL'
  test "$(git -C "$UPSTREAM" rev-parse HEAD)" = 5cc26e9a4a55b9c788e918f7c3bb2dc5076a85e6
  df -h "$ROOT"
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
  if ss -ltn | grep -q ":$PORT "; then echo "Port $PORT occupied"; return 2; fi
}

write_settings() {
  local target="$1"
  python - "$target" "$PORT" <<'PY'
import json,sys
from pathlib import Path
cams={}
for name,x,y,z,pitch,yaw in [
    ('FrontCamera',1,0,0,0,0),('LeftCamera',0,-1,0,0,-90),
    ('RightCamera',0,1,0,0,90),('RearCamera',-1,0,0,0,180),
    ('DownCamera',0,0,0,-90,0)]:
    cams[name]={'X':x,'Y':y,'Z':z,'Pitch':pitch,'Roll':0,'Yaw':yaw,
                'CaptureSettings':[{'ImageType':t,'Width':256,'Height':256,'FOV_Degrees':90}
                                   for t in (0,2)]}
settings={'SettingsVersion':1.2,'SimMode':'Multirotor','ApiServerPort':int(sys.argv[2]),
          'ClockSpeed':1,'ViewMode':'NoDisplay',
          'Vehicles':{'Drone_1':{'VehicleType':'SimpleFlight','AutoCreate':True,'Cameras':cams}}}
Path(sys.argv[1]).write_text(json.dumps(settings,indent=2)+'\n')
PY
}

run_probe() {
  local mode="$1"
  preflight
  local run_id="$(date -u +%Y%m%dT%H%M%SZ)-${mode}-$$"
  local run="$RESULTS/$run_id"
  capture="$ARTIFACTS/$run_id"
  mkdir -p "$capture"
  mkdir -p "$run"
  write_settings "$run/settings.json"
  cp "$DATA_ROOT/$EPISODE_REL" "$run/episode.json"
  cp "$DATA_ROOT/ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f/mark.json" "$run/mark.json"
  git -C "$UPSTREAM" status --short > "$run/git-status.txt"
  git -C "$UPSTREAM" diff > "$run/upstream.patch"
  git -C "$UPSTREAM" diff --staged > "$run/upstream-staged.patch"
  python -m pip freeze > "$run/pip-freeze.txt"
  cp "$REPO/docs/traveluav-openuav/asset_inventory.md" "$run/asset_inventory.md"
  test -s "$ASSETS/verified-sha256.txt" && cp "$ASSETS/verified-sha256.txt" "$run/verified-sha256.txt" || true
  lscpu > "$run/cpu.txt"
  uname -a > "$run/os.txt"
  free -h > "$run/ram.txt"
  nvidia-smi -q > "$run/gpu.txt"
  find "$ROOT/assets" -type f -printf '%p\t%s bytes\n' > "$run/asset-files.tsv"
  sha256sum "$run/episode.json" "$run/mark.json" "$run/settings.json" > "$run/input-sha256.txt"
  python - "$run" "$mode" "$UPSTREAM" "$SCENE" "$DATA_ROOT/$EPISODE_REL" <<'PY'
import json,sys,datetime,subprocess
from pathlib import Path
run,mode,repo,scene,episode=map(Path,sys.argv[1:])
data={'run_id':run.name,'status':'starting','level':mode.name.upper(),
      'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'repo_commit':subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(),
      'upstream_modifications':'upstream.patch and upstream-staged.patch',
      'scene_executable':str(scene),'episode':str(episode),'policy_weights':'none',
      'seed':100,'camera_frame':'AirSim NED; body camera offsets in settings.json',
      'sampling':'A: each of first six reference poses; B: 0.2 s wall interval, at most 31 samples; absent samples are missing data',
      'timeout_s':90,'gpu_timing':'RPC wall latency only; no CUDA events in simulator',
      'missing_data':[]}
(run/'run.json').write_text(json.dumps(data,indent=2)+'\n')
PY
  local scene_pid='' monitor_pid='' status=1
  cleanup() {
    if [[ -n "$monitor_pid" ]]; then kill "$monitor_pid" 2>/dev/null || true; wait "$monitor_pid" 2>/dev/null || true; fi
    if [[ -n "$scene_pid" ]]; then kill -- "-$scene_pid" 2>/dev/null || true; wait "$scene_pid" 2>/dev/null || true; fi
  }
  trap cleanup EXIT INT TERM
  printf '%q ' setsid "$SCENE" -RenderOffscreen -NoSound -NoVSync "-settings=$run/settings.json" >> "$run/commands.log"
  printf '\n' >> "$run/commands.log"
  setsid "$SCENE" -RenderOffscreen -NoSound -NoVSync "-settings=$run/settings.json" > "$run/scene.log" 2>&1 &
  scene_pid=$!
  (while true; do date -u +%FT%TZ; nvidia-smi --query-gpu=timestamp,index,memory.used,utilization.gpu --format=csv,noheader,nounits; sleep 1; done) > "$run/gpu-samples.log" 2>&1 &
  monitor_pid=$!
  local ready=0
  for _ in $(seq 1 60); do
    if ! kill -0 "$scene_pid" 2>/dev/null; then break; fi
    if ss -ltn | grep -q ":$PORT "; then ready=1; break; fi
    sleep 1
  done
  if [[ "$ready" -eq 1 ]]; then
    printf '%q ' timeout 90s python "$ROOT/probe.py" "$mode" --output "$run" --frames-dir "$capture/frames" --episode "$run/episode.json" --port "$PORT" >> "$run/commands.log"
    printf '\n' >> "$run/commands.log"
    set +e
    timeout 90s python "$ROOT/probe.py" "$mode" --output "$run" --frames-dir "$capture/frames" --episode "$run/episode.json" --port "$PORT" 2>&1 | tee -a "$run/console.log"
    status=${PIPESTATUS[0]}
    set -e
  else
    printf 'Scene did not open port %s within 60 s\n' "$PORT" | tee -a "$run/console.log"
    status=124
  fi
  python - "$run" "$status" <<'PY'
import json,sys,datetime
from pathlib import Path
p=Path(sys.argv[1])/'run.json';d=json.loads(p.read_text())
d['exit_status']=int(sys.argv[2]);d['status']='complete' if d['exit_status']==0 else 'failed'
d['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
p.write_text(json.dumps(d,indent=2)+'\n')
PY
  (cd "$run" && find . -type f ! -name output-sha256.txt -print0 | sort -z | xargs -0 sha256sum > output-sha256.txt)
  echo "$run"
  return "$status"
}

case "${1:-}" in
  preflight) preflight ;;
  a|b) run_probe "$1" ;;
  *) echo "Usage: $0 preflight|a|b"; exit 2 ;;
esac
