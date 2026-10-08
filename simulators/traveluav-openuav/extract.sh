#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/layout.sh"
run_id="$(date -u +%Y%m%dT%H%M%SZ)-extract-$$"
run="$RESULTS/$run_id";capture="$ARTIFACTS/$run_id"
mkdir -p "$run" "$capture" "$ASSETS/dataset"
exec > >(tee -a "$run/console.log") 2>&1
trap 'rc=$?; printf "{\"kind\":\"selective-extraction\",\"exit_status\":%s}\n" "$rc" > "$run/run.json"' EXIT
printf '%s\n' '7z l -slt ModernCityMap.zip; calculate expanded totals and free space; timeout 300s 7z x selected episode only' > "$run/commands.log"
7z l -slt "$ASSETS/downloads/data/ModernCityMap.zip" > "$capture/data-list.txt"
"$ENV_AB/bin/python" - "$capture/data-list.txt" "$run" "$ASSETS" <<'PY'
import json,sys,shutil
from pathlib import Path
p=Path(sys.argv[1]);run=Path(sys.argv[2]);assets=Path(sys.argv[3]);items=[]
for block in p.read_text().split('\n\n'):
 d=dict(x.split(' = ',1) for x in block.splitlines() if ' = ' in x)
 if d.get('Folder')=='-':items.append((d['Path'],int(d['Size'])))
selected=[x for x in items if '/00ac4ad3-1b8b-410d-9abc-43b65186571f/' in x[0]]
if not selected:raise RuntimeError('Selected episode absent from archive')
size=sum(x[1] for x in selected);free=shutil.disk_usage(assets).free
if free<size+10*1024**3:raise RuntimeError('Insufficient extraction headroom')
(run/'expansion.json').write_text(json.dumps({'all_dataset_expanded_bytes':sum(x[1] for x in items),'selected_episode_bytes':size,'selected_files':selected,'free_before_bytes':free,'scene_all_expanded_bytes':19576208267,'scene_selected_expanded_bytes':2168410072},indent=2)+'\n')
print('Selected episode:',size,'bytes;',len(selected),'files; free',free)
PY
timeout 300s 7z x -y "$ASSETS/downloads/data/ModernCityMap.zip" -o"$ASSETS/dataset" 'ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f/*'
test -s "$ASSETS/dataset/ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f/log/000000.json"
test -s "$ASSETS/dataset/ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f/mark.json"
find "$ASSETS/dataset" -name merged_data.json -o -name mark.json -o -name object_description.json
"$ENV_AB/bin/python" - "$ASSETS/metadata" <<'PY'
from pathlib import Path
import json,sys
p=Path(sys.argv[1]);rows=json.loads((p/'seen_valset.json').read_text());selected=[x for x in rows if x['json']=='ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f/merged_data.json']
(p/'selected_seen_rows.json').write_text(json.dumps(selected,indent=2)+'\n')
print(len(rows),'official rows;',len(selected),'rows refer to one selected episode')
PY
