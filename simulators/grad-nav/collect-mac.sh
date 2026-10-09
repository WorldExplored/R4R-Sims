#!/bin/bash
set -u
LOCAL_ROOT=${1:?local candidate worktree}
SSH_COMMAND='ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=/Users/srreyanshsethi/.ssh/r4r-209.137.198.205.known_hosts -o IdentitiesOnly=yes -i /Users/srreyanshsethi/.ssh/r4r-209.137.198.205.pem'
mkdir -p "$LOCAL_ROOT/artifacts/grad-nav/live"
while [[ ! -f "$LOCAL_ROOT/artifacts/grad-nav/collector-stop" ]]; do
  date -u +%FT%TZ
  rsync -az --partial -e "$SSH_COMMAND" ubuntu@209.137.198.205:/home/ubuntu/R4R-Sims-grad-nav/artifacts/grad-nav/ "$LOCAL_ROOT/artifacts/grad-nav/live/"
  rsync -az --partial -e "$SSH_COMMAND" ubuntu@209.137.198.205:/home/ubuntu/R4R-Sims-grad-nav/results/grad-nav/ "$LOCAL_ROOT/artifacts/grad-nav/live/results/"
  sleep 300
done
