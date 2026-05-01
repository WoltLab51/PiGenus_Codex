# PiGenus Deployment Runbook

This runbook describes the first Raspberry Pi deployment path for PiGenus. It favors reliability, recoverability, and private networking over cleverness.

## Target

- Raspberry Pi 5
- Raspberry Pi OS 64-bit
- USB SSD preferred
- Ethernet preferred
- Private access through Tailscale or WireGuard
- Python 3.12+
- systemd

## 1. Prepare The Pi

Create or choose a deployment directory:

```bash
sudo mkdir -p /opt/pigenus
sudo chown "$USER":"$USER" /opt/pigenus
```

Clone or copy the repository:

```bash
git clone https://github.com/WoltLab51/PiGenus_Codex.git /opt/pigenus
cd /opt/pigenus
```

Create a virtual environment:

```bash
python3.12 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

## 2. Install systemd Units

```bash
sudo ./deploy/install-systemd.sh
```

Edit secrets:

```bash
sudo nano /etc/pigenus/pigenus.env
```

Required production values:

- `PIGENUS_ADMIN_TOKEN`: long random secret
- `PIGENUS_TOKEN_PEPPER`: different long random secret
- `PIGENUS_DATABASE_URL=sqlite:////var/lib/pigenus/pigenus.sqlite3`
- `PIGENUS_BACKUP_DIR=/var/lib/pigenus/backups`

Keep `PIGENUS_HOST=127.0.0.1` unless access is restricted through a private network or reverse proxy.

## 3. Initialize Database

```bash
sudo -u pigenus -H bash -lc 'cd /opt/pigenus && . .venv/bin/activate && set -a && . /etc/pigenus/pigenus.env && set +a && pigenus-admin migrate'
```

## 4. Start Core Service

```bash
sudo systemctl start pigenus
sudo systemctl status pigenus --no-pager
```

Run healthcheck:

```bash
cd /opt/pigenus
. .venv/bin/activate
set -a
. /etc/pigenus/pigenus.env
set +a
pigenus-healthcheck --admin
```

Expected result: health status is `ok`, database is `ok`, and admin status returns counters.

## 5. Register Local Maintenance Worker

```bash
cd /opt/pigenus
. .venv/bin/activate
set -a
. /etc/pigenus/pigenus.env
set +a
pigenus-register-worker --name pigenus-maintenance --capability maintenance
```

Copy the printed values into `/etc/pigenus/pigenus.env`:

- `PIGENUS_WORKER_ID`
- `PIGENUS_WORKER_TOKEN`

Then start the worker:

```bash
sudo systemctl enable --now pigenus-worker
sudo systemctl status pigenus-worker --no-pager
```

## 6. Smoke Test Maintenance

Trigger maintenance:

```bash
curl -X POST http://127.0.0.1:8000/admin/maintenance/run \
  -H "Authorization: Bearer ${PIGENUS_ADMIN_TOKEN}"
```

Give the worker one cycle, then inspect jobs:

```bash
curl http://127.0.0.1:8000/jobs \
  -H "Authorization: Bearer ${PIGENUS_ADMIN_TOKEN}"
```

Create a direct backup check:

```bash
pigenus-admin backup
ls -lh /var/lib/pigenus/backups
```

## 7. Operational Checks

Useful commands:

```bash
systemctl status pigenus --no-pager
systemctl status pigenus-worker --no-pager
journalctl -u pigenus -n 100 --no-pager
journalctl -u pigenus-worker -n 100 --no-pager
pigenus-admin schema-version
pigenus-healthcheck --admin
```

## Recovery

Stop services before restore:

```bash
sudo systemctl stop pigenus-worker
sudo systemctl stop pigenus
```

Restore:

```bash
sudo -u pigenus -H bash -lc 'cd /opt/pigenus && . .venv/bin/activate && set -a && . /etc/pigenus/pigenus.env && set +a && pigenus-admin restore /var/lib/pigenus/backups/pigenus-example.sqlite3 --yes'
```

Restart:

```bash
sudo systemctl start pigenus
sudo systemctl start pigenus-worker
```

Run `pigenus-healthcheck --admin` afterwards.

## Security Notes

- Prefer Tailscale or WireGuard for remote access.
- Do not expose PiGenus directly to the public internet.
- Keep secrets in `/etc/pigenus/pigenus.env`, not in Git.
- Register workers intentionally and rotate worker tokens by disabling/recreating workers when needed.
- Keep backups on the SSD and periodically copy them off-device.
