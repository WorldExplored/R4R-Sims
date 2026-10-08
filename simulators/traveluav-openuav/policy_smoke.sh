#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/layout.sh"
MODEL="$UPSTREAM/Model/LLaMA-UAV"
POLICY="$ASSETS/runtime/llama-uav-7b"
EPISODE_REL='ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f/merged_data.json'

[[ "$(uname -s)" == Linux ]]
[[ "$(git -C "$UPSTREAM" rev-parse HEAD)" == 5cc26e9a4a55b9c788e918f7c3bb2dc5076a85e6 ]]
for file in \
  "$ASSETS/dataset/$EPISODE_REL" \
  "$ASSETS/dataset/ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f/mark.json" \
  "$ASSETS/envs/closeloop_envs/ModernCityMap.sh" \
  "$ASSETS/models/llama-uav-7b/adapter_model.bin" \
  "$ASSETS/models/llama-uav-7b/mm_projector.bin" \
  "$ASSETS/models/llama-uav-7b/non_lora_trainables.bin" \
  "$ASSETS/models/vicuna-7b-v1.5/config.json" \
  "$ASSETS/models/LAVIS/eva_vit_g.pth" \
  "$ASSETS/models/LAVIS/instruct_blip_vicuna7b_trimmed.pth" \
  "$ASSETS/models/traj/model_5.pth" \
  "$ASSETS/models/groundingdino_swint_ogc.pth"; do
  [[ -s "$file" ]] || { echo "Missing $file"; exit 2; }
done
for port in 30000 30001 20001; do
  if ss -ltn | grep -q ":$port "; then echo "Port $port occupied"; exit 2; fi
done
run_id="$(date -u +%Y%m%dT%H%M%SZ)-c-$$"
run="$RESULTS/$run_id"
  capture="$ARTIFACTS/$run_id"
  mkdir -p "$capture"
mkdir -p "$run" "$capture/policy"
cp "$ASSETS/metadata/selected_seen_one.json" "$run/selected_seen_one.json"
cp "$ASSETS/dataset/$EPISODE_REL" "$run/episode.json"
cp "$ASSETS/runtime/config-rewrites.json" "$run/config-rewrites.json"
cp "$POLICY/config.json" "$run/model-runtime-config.json"
cp "$ASSETS/dataset/ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f/mark.json" "$run/mark.json"
git -C "$UPSTREAM" status --short > "$run/git-status.txt"
git -C "$UPSTREAM" diff > "$run/upstream.patch"
git -C "$UPSTREAM" diff --staged > "$run/upstream-staged.patch"
python -m pip freeze > "$run/pip-freeze.txt"
cp "$REPO/docs/traveluav-openuav/asset_inventory.md" "$run/asset_inventory.md"
  cp "$ASSETS"/verified-*.json "$run/" 2>/dev/null || true
  git -C "$REPO" rev-parse HEAD > "$run/shared-commit.txt"
  cp "$ASSETS/metadata/seen_valset.json" "$capture/seen_valset.json"
  cp "$ASSETS/metadata/selected_seen_one.json" "$run/selected_seen_one.json"
test -s "$ASSETS/verified-sha256.txt" && cp "$ASSETS/verified-sha256.txt" "$run/verified-sha256.txt" || true
lscpu > "$run/cpu.txt"
uname -a > "$run/os.txt"
free -h > "$run/ram.txt"
nvidia-smi -q > "$run/gpu.txt"
find "$ASSETS" -type f -printf '%p\t%s bytes\n' > "$run/asset-files.tsv"
sha256sum "$run/episode.json" "$run/mark.json" "$run/selected_seen_one.json" > "$run/input-sha256.txt"
python - "$run" <<'PY'
import json,sys,datetime
from pathlib import Path
p=Path(sys.argv[1])/'run.json'
p.write_text(json.dumps({'run_id':p.parent.name,'level':'C','status':'starting',
    'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'repo_commit':'5cc26e9a4a55b9c788e918f7c3bb2dc5076a85e6',
    'policy_weights':'assets/models/llama-uav-7b; assets/models/traj; assets/models/groundingdino_swint_ogc.pth',
    'scene':'ModernCityMap','split':'seen_valset, one episode','seed':100,
    'assistant':'L1 always_help True, use_gt True','max_waypoints':10,
    'server_timeout_s':900,'evaluation_timeout_s':600,
    'sampling':'one trace per model action; upstream observation archive per step; missing samples explicitly absent',
    'gpu_timing':'torch.cuda.synchronize after model.run; first step is warmup and excluded from steady latency',
    'camera_extrinsics':'eval_observe.patch records image-response poses/timestamps in camera_observations.jsonl; raw captures under artifact run/observations'},indent=2)+'\n')
PY
server_pid='' monitor_pid='' status=1
cleanup() {
  if [[ -n "$monitor_pid" ]]; then kill "$monitor_pid" 2>/dev/null || true; wait "$monitor_pid" 2>/dev/null || true; fi
  if [[ -n "$server_pid" ]]; then kill -- "-$server_pid" 2>/dev/null || true; wait "$server_pid" 2>/dev/null || true; fi
}
trap cleanup EXIT INT TERM
(while true; do date -u +%FT%TZ; nvidia-smi --query-gpu=timestamp,index,memory.used,utilization.gpu --format=csv,noheader,nounits; sleep 1; done) > "$run/gpu-samples.log" 2>&1 &
monitor_pid=$!
printf '%q ' timeout 900s python -u "$UPSTREAM/airsim_plugin/AirVLNSimulatorServerTool.py" --gpus 0 --port 30000 --root_path "$ASSETS/envs" >> "$run/commands.log"; printf '\n' >> "$run/commands.log"
setsid timeout 900s python -u "$UPSTREAM/airsim_plugin/AirVLNSimulatorServerTool.py" --gpus 0 --port 30000 --root_path "$ASSETS/envs" > "$run/server.log" 2>&1 &
server_pid=$!
ready=0
for _ in $(seq 1 30); do
  if ! kill -0 "$server_pid" 2>/dev/null; then break; fi
  if ss -ltn | grep -q ':30000 '; then ready=1; break; fi
  sleep 1
done
if [[ "$ready" -eq 1 ]]; then
  cd "$UPSTREAM"
  export R4R_CAPTURE_DIR="$capture" R4R_RECORD_DIR="$run" R4R_BERT_PATH="$ASSETS/models/bert-base-uncased"
  cmd=(python -u src/vlnce_src/eval.py --run_type eval --name TravelLLM --gpu_id 0
       --simulator_tool_port 30000 --DDP_MASTER_PORT 20001 --batchSize 1
       --always_help True --use_gt True --maxWaypoints 10
       --project_prefix "$run" --dataset_path "$ASSETS/dataset"
       --eval_save_path "$capture/policy" --eval_json_path "$run/selected_seen_one.json"
       --model_path "$POLICY" --model_base "$ASSETS/models/vicuna-7b-v1.5"
       --vision_tower "$ASSETS/models/LAVIS/eva_vit_g.pth"
       --image_processor "$MODEL/llamavid/processor/clip-patch14-224"
       --traj_model_path "$ASSETS/models/traj"
       --map_spawn_area_json_path "$ASSETS/metadata/map_spawnarea_info.json"
       --object_name_json_path "$ASSETS/metadata/object_description.json"
       --groundingdino_config "$UPSTREAM/src/model_wrapper/utils/GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py"
       --groundingdino_model_path "$ASSETS/models/groundingdino_swint_ogc.pth")
  printf '%q ' timeout 600s "${cmd[@]}" >> "$run/commands.log"; printf '\n' >> "$run/commands.log"
  set +e
  timeout 600s "${cmd[@]}" 2>&1 | tee -a "$run/console.log"
  status=${PIPESTATUS[0]}
  set -e
else
  echo 'Server did not open port 30000 within 30 s' | tee -a "$run/console.log"
  status=124
fi
python - "$run" "$status" <<'PY'
import json,sys,datetime
from pathlib import Path
p=Path(sys.argv[1])/'run.json';d=json.loads(p.read_text());d['exit_status']=int(sys.argv[2]);d['status']='complete' if d['exit_status']==0 else 'failed';d['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();p.write_text(json.dumps(d,indent=2)+'\n')
PY
cleanup
trap - EXIT INT TERM
(cd "$run" && find . -type f ! -name output-sha256.txt -print0 | sort -z | xargs -0 sha256sum > output-sha256.txt)
echo "$run"
exit "$status"
