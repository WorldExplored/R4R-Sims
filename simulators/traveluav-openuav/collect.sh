#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/layout.sh"
RUN="${1:?usage: collect.sh /absolute/path/to/run [destination] }"
DEST="${2:-$ARTIFACTS/collections}"
test -f "$RUN/run.json"
mkdir -p "$DEST"
RUN="$(cd "$RUN" && pwd)"
python - "$RUN" <<'PY'
import json,sys
from pathlib import Path
from PIL import Image
import numpy as np
p=Path(sys.argv[1]);errors=[]
for f in p.rglob('*.json'):
    try: json.loads(f.read_text())
    except Exception as e: errors.append(f'{f}: {e}')
for f in p.rglob('*.jsonl'):
    try:
        for line in f.open(): json.loads(line)
    except Exception as e: errors.append(f'{f}: {e}')
for f in p.rglob('*.png'):
    try:
        with Image.open(f) as im: im.verify()
    except Exception as e: errors.append(f'{f}: {e}')
for f in p.rglob('*.npy'):
    try:
        a=np.load(f,allow_pickle=False,mmap_mode='r')
        if not a.size: raise ValueError('empty array')
    except Exception as e: errors.append(f'{f}: {e}')
(p/'validation.json').write_text(json.dumps({'errors':errors,'json_png_depth_opened':not errors},indent=2)+'\n')
if errors: raise SystemExit('\n'.join(errors))
PY
(cd "$RUN" && find . -type f ! -name output-sha256.txt -print0 | sort -z | xargs -0 sha256sum > output-sha256.txt)
archive="$DEST/$(basename "$RUN").tar.gz"
test ! -e "$archive" || { echo "Already exists: $archive"; exit 2; }
tar -C "$(dirname "$RUN")" -czf "$archive" "$(basename "$RUN")"
sha256sum "$archive" > "$archive.sha256"
tar -tzf "$archive" >/dev/null
echo "$archive"
