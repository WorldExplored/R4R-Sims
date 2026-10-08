#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/layout.sh"
RUN="${1:?usage: collect.sh /absolute/path/to/result-run}"
RUN="$(cd "$RUN" && pwd)"
CAPTURE="$ARTIFACTS/$(basename "$RUN")"
mkdir -p "$CAPTURE" "$ARTIFACTS/collections"
python "$ROOT/analyze.py" "$RUN" "$CAPTURE"
archive="$ARTIFACTS/collections/$(basename "$RUN").tar.gz"
[[ ! -e "$archive" ]] || { echo "Archive already exists: $archive"; exit 2; }
tar -C "$ARTIFACTS" -czf "$archive" "$(basename "$RUN")"
sha256sum "$archive" > "$archive.sha256"
tar -tzf "$archive" >/dev/null
python - "$RUN" "$archive" <<'INNER'
import json,sys,hashlib
from pathlib import Path
p=Path(sys.argv[1])/'archive.json';a=Path(sys.argv[2]);h=hashlib.sha256()
with a.open('rb') as f:
 for b in iter(lambda:f.read(8388608),b''):h.update(b)
p.write_text(json.dumps({'remote_path':str(a),'bytes':a.stat().st_size,'sha256':h.hexdigest(),'local_verification':'pending'},indent=2)+'\n')
INNER
echo "$archive"
