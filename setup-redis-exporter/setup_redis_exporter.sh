#!/usr/bin/env bash
set -euo pipefail

# ----------------------------
# Redis Exporter installer + systemd setup
# - Downloads redis_exporter to /opt/redis_exporter
# - Creates 3 systemd services for Redis ports 7001/7002/7003
# - Each exporter listens on 9121/9122/9123 respectively
#
# Usage:
#   sudo ./setup_redis_exporter.sh --host localhost
#   sudo ./setup_redis_exporter.sh --host 127.0.0.1 --bind 0.0.0.0
#
# Optional auth:
#   sudo ./setup_redis_exporter.sh --host localhost --redis-user monitoring --redis-pass 'xxx'
#   sudo ./setup_redis_exporter.sh --host localhost --redis-pass 'xxx'        # (no user)
#
# Notes:
# - "host" is what exporter uses to reach Redis (usually localhost on Redis server)
# - "bind" is what exporter listens on for Prometheus (0.0.0.0 for remote scrape)
# ----------------------------

VERSION="v1.58.0"
ARCHIVE="redis_exporter-${VERSION}.linux-amd64.tar.gz"
URL="https://github.com/oliver006/redis_exporter/releases/download/${VERSION}/${ARCHIVE}"
OPT_DIR="/opt"
INSTALL_DIR="/opt/redis_exporter"
BIN="${INSTALL_DIR}/redis_exporter"

REDIS_HOST="localhost"
BIND_ADDR="0.0.0.0"

REDIS_USER=""
REDIS_PASS=""

PORTS=(7001 7002 7003)

usage() {
  cat <<EOF
Usage: sudo $0 --host <redis_host> [--bind <bind_ip>] [--redis-user <user>] [--redis-pass <pass>]

Examples:
  sudo $0 --host localhost
  sudo $0 --host 127.0.0.1 --bind 0.0.0.0
  sudo $0 --host localhost --redis-user monitoring --redis-pass 'secret'
  sudo $0 --host localhost --redis-pass 'secret'

EOF
}

require_root() {
  if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
    echo "ERROR: Please run as root (use sudo)." >&2
    exit 1
  fi
}

have_cmd() { command -v "$1" >/dev/null 2>&1; }

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --host) REDIS_HOST="${2:-}"; shift 2 ;;
      --bind) BIND_ADDR="${2:-}"; shift 2 ;;
      --redis-user) REDIS_USER="${2:-}"; shift 2 ;;
      --redis-pass) REDIS_PASS="${2:-}"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
    esac
  done

  if [[ -z "$REDIS_HOST" ]]; then
    echo "ERROR: --host is required" >&2
    usage
    exit 2
  fi
}

install_exporter() {
  echo "==> Installing redis_exporter ${VERSION} into ${INSTALL_DIR}"

  if ! have_cmd wget; then
    echo "ERROR: wget not found" >&2
    exit 1
  fi
  if ! have_cmd tar; then
    echo "ERROR: tar not found" >&2
    exit 1
  fi

  mkdir -p "${OPT_DIR}"
  cd "${OPT_DIR}"

  # Download only if missing (idempotent)
  if [[ ! -f "${ARCHIVE}" ]]; then
    wget -q "${URL}"
  else
    echo "==> Archive already exists: ${OPT_DIR}/${ARCHIVE}"
  fi

  # Extract to a temp dir to avoid half-installs
  tmpdir="$(mktemp -d)"
  tar -xzf "${ARCHIVE}" -C "${tmpdir}"

  rm -rf "${INSTALL_DIR}"
  mv "${tmpdir}/redis_exporter-${VERSION}.linux-amd64" "${INSTALL_DIR}"
  rm -rf "${tmpdir}"

  echo "Redis Exporter Version is:"
  "${BIN}" --version
}

exporter_web_port_for_redis_port() {
  local redis_port="$1"
  # 7001->9121, 7002->9122, 7003->9123
  echo "912${redis_port: -1}"
}

build_exporter_args() {
  local redis_port="$1"
  local web_port="$2"
  local args=()

  args+=( "--redis.addr=redis://${REDIS_HOST}:${redis_port}" )
  args+=( "--web.listen-address=${BIND_ADDR}:${web_port}" )

  if [[ -n "${REDIS_USER}" ]]; then
    args+=( "--redis.user=${REDIS_USER}" )
  fi
  if [[ -n "${REDIS_PASS}" ]]; then
    args+=( "--redis.password=${REDIS_PASS}" )
  fi

  printf "%q " "${args[@]}"
}

manual_test_tip() {
  echo
  echo "==> Manual test commands (run in a separate terminal if you want):"
  for rp in "${PORTS[@]}"; do
    wp="$(exporter_web_port_for_redis_port "${rp}")"
    echo "  ${BIN} $(build_exporter_args "${rp}" "${wp}")"
  done
  echo
  echo "Then verify locally on this server:"
  echo "  curl -s http://127.0.0.1:9121/metrics | grep -E '^redis_connected_clients\\b' | head"
  echo "  curl -s http://127.0.0.1:9122/metrics | grep -E '^redis_connected_clients\\b' | head"
  echo "  curl -s http://127.0.0.1:9123/metrics | grep -E '^redis_connected_clients\\b' | head"
  echo
}

create_systemd_service() {
  local redis_port="$1"
  local web_port="$2"
  local svc="redis-exporter-${redis_port}.service"
  local path="/etc/systemd/system/${svc}"

  echo "==> Writing systemd unit: ${path}"

  cat > "${path}" <<EOF
[Unit]
Description=Redis Exporter for Redis ${REDIS_HOST}:${redis_port}
After=network.target

[Service]
Type=simple
User=root
ExecStart=${BIN} $(build_exporter_args "${redis_port}" "${web_port}")
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF
}

enable_start_services() {
  echo "==> Reloading systemd"
  systemctl daemon-reload

  for rp in "${PORTS[@]}"; do
    svc="redis-exporter-${rp}.service"
    echo "==> Enabling ${svc}"
    systemctl enable "${svc}" >/dev/null
    echo "==> Starting ${svc}"
    systemctl restart "${svc}"
  done
}

show_status() {
  echo
  echo "==> Listening ports (expect ${BIND_ADDR}:9121/9122/9123):"
  if have_cmd ss; then
    ss -tunlp | egrep ':(9121|9122|9123)\b' || true
  else
    echo "(ss not installed)"
  fi

  echo
  echo "==> systemd status summary:"
  for rp in "${PORTS[@]}"; do
    svc="redis-exporter-${rp}.service"
    echo "---- ${svc} ----"
    systemctl --no-pager --full status "${svc}" | sed -n '1,12p' || true
    echo
  done

  echo "==> Quick curl check (local):"
  if have_cmd curl; then
    for p in 9121 9122 9123; do
      echo -n "  localhost:${p} -> "
      if curl -fsS "http://127.0.0.1:${p}/metrics" >/dev/null; then
        echo "OK"
      else
        echo "FAIL"
      fi
    done
  else
    echo "(curl not installed; skip)"
  fi
}

main() {
  require_root
  parse_args "$@"
  install_exporter
  manual_test_tip

  for rp in "${PORTS[@]}"; do
    wp="$(exporter_web_port_for_redis_port "${rp}")"
    create_systemd_service "${rp}" "${wp}"
  done

  enable_start_services
  show_status

  echo "==> Done."
  echo "Prometheus should scrape: ${HOSTNAME}:9121, :9122, :9123 (or the server FQDN you configured)."
}

main "$@"
