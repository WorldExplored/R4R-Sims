#!/usr/bin/env bash
set -u
set -o pipefail
: "${AUDIT_RUN:?set AUDIT_RUN to a unique run directory}"
: "${AUDIT_UPSTREAM:?set AUDIT_UPSTREAM to cloned upstream directory}"
if [[ ! -d "$AUDIT_UPSTREAM/.git" ]]; then echo "missing upstream checkout" >&2; exit 2; fi
if [[ -e "$AUDIT_RUN/run.json" ]]; then echo "run ID already used" >&2; exit 2; fi
mkdir -p "$AUDIT_RUN" "$AUDIT_RUN/config" "$AUDIT_RUN/patches"
printf '%q ' "$@" >> "$AUDIT_RUN/commands.log"
printf '\n' >> "$AUDIT_RUN/commands.log"
date -u +%FT%TZ > "$AUDIT_RUN/start_utc.txt"
{ uname -a; python --version; python -m pip freeze; nvidia-smi; df -h "$AUDIT_RUN"; } > "$AUDIT_RUN/environment.txt" 2>&1
git -C "$AUDIT_UPSTREAM" rev-parse HEAD > "$AUDIT_RUN/source_commit.txt"
git -C "$AUDIT_UPSTREAM" status --short > "$AUDIT_RUN/source_status.txt"
git -C "$AUDIT_UPSTREAM" diff > "$AUDIT_RUN/patches/unstaged.patch"
git -C "$AUDIT_UPSTREAM" diff --staged > "$AUDIT_RUN/patches/staged.patch"
find "$AUDIT_UPSTREAM/envs/assets" -type f \( -name '*.ply' -o -name 'config.yml' -o -name '*.ckpt' -o -name '*.pt' \) -print0 2>/dev/null | xargs -0 -r sha256sum > "$AUDIT_RUN/assets.sha256"
cp "$AUDIT_UPSTREAM/examples/cfg/gradnav/drone_long_traj.yaml" "$AUDIT_RUN/config/" 2>/dev/null || true
if command -v nvidia-smi >/dev/null; then
  (while :; do date -u +%FT%TZ; nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader; nvidia-smi --query-compute-apps=pid,used_gpu_memory --format=csv,noheader 2>/dev/null; sleep 1; done) > "$AUDIT_RUN/gpu.csv" 2>&1 &
  gpu_pid=$!
else gpu_pid=""; fi
start_epoch=$(date +%s)
timeout "${AUDIT_TIMEOUT:-180s}" "$@" 2>&1 | tee "$AUDIT_RUN/console.log"
status=${PIPESTATUS[0]}
end_epoch=$(date +%s)
if [[ -n "$gpu_pid" ]]; then kill "$gpu_pid" 2>/dev/null || true; wait "$gpu_pid" 2>/dev/null || true; fi
RUN_STATUS="$status" RUN_START="$start_epoch" RUN_END="$end_epoch" python - "$AUDIT_RUN" <<'PY'
import hashlib, json, os, pathlib, platform, sys
r = pathlib.Path(sys.argv[1]); commit = (r/'source_commit.txt').read_text().strip()
files = {}
for p in r.rglob('*'):
    if p.is_file() and p.name not in ('run.json', 'manifest.sha256'):
        digest = hashlib.sha256()
        with p.open('rb') as f:
            for block in iter(lambda: f.read(1024 * 1024), b''):
                digest.update(block)
        files[str(p.relative_to(r))] = digest.hexdigest()
detail = json.loads((r/'run_detail.json').read_text()) if (r/'run_detail.json').exists() else {}
data = {'source_commit': commit, 'source_dirty_status': (r/'source_status.txt').read_text(),
        'command': (r/'commands.log').read_text().strip(), 'run_dir': str(r.resolve()),
        'host': platform.platform(), 'start_epoch_s': int(os.environ['RUN_START']),
        'end_epoch_s': int(os.environ['RUN_END']), 'wall_duration_s': int(os.environ['RUN_END'])-int(os.environ['RUN_START']),
        'exit_status': int(os.environ['RUN_STATUS']), 'timed_out': int(os.environ['RUN_STATUS']) == 124,
        'files_sha256': files, 'detail': detail}
(r/'run.json').write_text(json.dumps(data, indent=2)+'\n')
(r/'manifest.sha256').write_text(''.join(f'{h}  {name}\n' for name,h in sorted(files.items())))
PY
exit "$status"
