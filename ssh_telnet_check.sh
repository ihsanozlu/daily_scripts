#!/usr/bin/env bash

set -euo pipefail

SSH_KEY="your_ssh_key"
SSH_USER="ssh_username"

# SSH hosts (jump hosts)
SSH_HOSTS=(
  "1.1.1.1"
  "1.1.1.2"
  "1.1.1.3"
)

# Telnet targets
TARGET_HOSTS=(
  "1.1.1.4"
  "1.1.1.5"
)

PORT=6432

for ssh_host in "${SSH_HOSTS[@]}"; do
  echo "===== SSH HOST: $ssh_host ====="

  for target in "${TARGET_HOSTS[@]}"; do
    echo "Checking $target:$PORT"

    ssh -i "$SSH_KEY" -o ConnectTimeout=5 "${SSH_USER}@${ssh_host}" \
      "timeout 5 bash -c '</dev/tcp/${target}/${PORT}' && echo 'OPEN' || echo 'CLOSED'" \
      2>/dev/null

  done

  echo
done