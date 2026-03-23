#!/usr/bin/env bash
set -euo pipefail

# ===== MODE =====
MODE="${1:-key}"   # key OR pass

# ===== USERS =====
SSH_USER_KEY="ssh_username"
SSH_USER_PASS="ssh_username_1"

SSH_KEY="your_ssh_key"
SSH_PASS=""

PORT=6432
PARALLEL=10

SSH_HOSTS=(
)

TARGET_HOSTS=(
)

# ===== PASSWORD MODE SETUP =====
if [[ "$MODE" == "pass" ]]; then
  if ! command -v sshpass >/dev/null; then
    echo "❌ sshpass is required for password mode"
    exit 1
  fi

  if [[ -z "$SSH_PASS" ]]; then
    read -s -p "Enter SSH password for ${SSH_USER_PASS}: " SSH_PASS
    echo
  fi
fi

# ===== FUNCTION =====
check() {
  local ssh_host="$1"
  local target="$2"

  local user result raw

  if [[ "$MODE" == "key" ]]; then
    user="$SSH_USER_KEY"

    raw="$(
      ssh -i "$SSH_KEY" \
        -o BatchMode=yes \
        -o StrictHostKeyChecking=no \
        -o ConnectTimeout=5 \
        "${user}@${ssh_host}" \
        "timeout 5 telnet ${target} ${PORT}" \
        2>&1 || true
    )"

  else
    user="$SSH_USER_PASS"

    raw="$(
      sshpass -p "$SSH_PASS" ssh \
        -o StrictHostKeyChecking=no \
        -o ConnectTimeout=5 \
        "${user}@${ssh_host}" \
        "timeout 5 telnet ${target} ${PORT}" \
        2>&1 || true
    )"
  fi

  # ===== PARSE RESULT =====
  if echo "$raw" | grep -q "Connected to"; then
    result="OPEN"
  elif echo "$raw" | grep -q "Connection refused"; then
    result="REFUSED"
  elif echo "$raw" | grep -q "Trying"; then
    result="TIMEOUT"
  else
    result="UNKNOWN"
  fi

  printf "%-15s %-10s %-45s %-6s %s\n" \
    "$ssh_host" "$user" "$target" "$PORT" "$result"
}

export -f check
export MODE SSH_KEY SSH_USER_KEY SSH_USER_PASS SSH_PASS PORT

# ===== HEADER =====
printf "%-15s %-10s %-45s %-6s %s\n" "SSH_HOST" "USER" "TARGET" "PORT" "STATUS"
printf "%-15s %-10s %-45s %-6s %s\n" "---------------" "----------" "---------------------------------------------" "------" "----------"

# ===== PARALLEL EXEC =====
for ssh_host in "${SSH_HOSTS[@]}"; do
  for target in "${TARGET_HOSTS[@]}"; do
    echo "$ssh_host $target"
  done
done | xargs -n 2 -P "$PARALLEL" bash -c 'check "$1" "$2"' _