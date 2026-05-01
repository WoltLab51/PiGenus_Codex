#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/pigenus}"
STATE_DIR="${STATE_DIR:-/var/lib/pigenus}"
LOG_DIR="${LOG_DIR:-/var/log/pigenus}"
ENV_DIR="${ENV_DIR:-/etc/pigenus}"
SERVICE_USER="${SERVICE_USER:-pigenus}"

if [[ "${EUID}" -ne 0 ]]; then
  echo "install-systemd.sh must be run as root" >&2
  exit 1
fi

if ! id "${SERVICE_USER}" >/dev/null 2>&1; then
  useradd --system --home "${STATE_DIR}" --shell /usr/sbin/nologin "${SERVICE_USER}"
fi

mkdir -p "${APP_DIR}" "${STATE_DIR}/backups" "${LOG_DIR}" "${ENV_DIR}"
chown -R "${SERVICE_USER}:${SERVICE_USER}" "${STATE_DIR}" "${LOG_DIR}"
chmod 750 "${STATE_DIR}" "${LOG_DIR}"

if [[ ! -f "${ENV_DIR}/pigenus.env" ]]; then
  install -m 640 -o root -g "${SERVICE_USER}" deploy/pigenus.env.example "${ENV_DIR}/pigenus.env"
  echo "Created ${ENV_DIR}/pigenus.env. Edit secrets before starting the service."
fi
chown root:"${SERVICE_USER}" "${ENV_DIR}/pigenus.env"
chmod 640 "${ENV_DIR}/pigenus.env"

install -m 644 deploy/pigenus.service /etc/systemd/system/pigenus.service
install -m 644 deploy/pigenus-worker.service /etc/systemd/system/pigenus-worker.service
systemctl daemon-reload
systemctl enable pigenus.service

echo "PiGenus systemd unit installed. Edit ${ENV_DIR}/pigenus.env, deploy code to ${APP_DIR}, then run:"
echo "  systemctl start pigenus"
echo "After registering a maintenance worker and adding PIGENUS_WORKER_ID/TOKEN, run:"
echo "  systemctl enable --now pigenus-worker"
