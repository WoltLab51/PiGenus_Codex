# PiGenus

PiGenus is the always-on private orchestration and memory node for the GENUS ecosystem. It is designed for a Raspberry Pi 5 class device: low power, reliable, auditable, and recoverable.

PiGenus is not a local giant model host. It accepts trusted requests, persists state, turns work into jobs, leases those jobs to stronger workers, records results, and runs maintenance workflows.

The binding product definition lives in [docs/PIGENUS_CHARTER.md](docs/PIGENUS_CHARTER.md). When architecture or feature choices are unclear, PiGenus must choose the reliable private orchestration node path over flashy AI features.

## Core Identity

PiGenus is the always-available private infrastructure core of GENUS. It preserves information, organizes work, connects systems, and maintains long-term continuity.

Its five permanent responsibilities are:

- Persistence
- Orchestration
- Administration
- Interface readiness
- Continuity

## Phase 1 MVP

- FastAPI service
- SQLite persistence
- Bearer token admin auth
- Trusted worker registration
- Worker heartbeat
- Job submit, lease, ack, and fail lifecycle
- Job list, detail, and cancellation
- User and trusted device administration
- Session and message persistence APIs
- Memory create/search/update APIs
- Audit log and job event history
- Nightly maintenance with backup, stale-worker detection, stuck-job recovery, and maintenance job queueing
- systemd deployment files
- pytest coverage for core API flows

## Quick Start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
$env:PIGENUS_ADMIN_TOKEN="change-this-long-random-token"
uvicorn pigenus.main:app --reload
```

Open `http://127.0.0.1:8000/health`.

## Operations

Initialize the database:

```powershell
pigenus-admin init-db
```

Run migrations:

```powershell
pigenus-admin migrate
```

Create a SQLite backup:

```powershell
pigenus-admin backup
```

Restore from a backup requires an explicit confirmation flag:

```powershell
pigenus-admin restore .\backups\pigenus-example.sqlite3 --yes
```

Run the local maintenance worker after registering a worker with the `maintenance` capability:

```powershell
$env:PIGENUS_BASE_URL="http://127.0.0.1:8000"
$env:PIGENUS_WORKER_ID="1"
$env:PIGENUS_WORKER_TOKEN="worker-token-from-registration"
pigenus-worker --once
```

## Production Posture

Set secrets through environment or an environment file owned by the service account. Do not commit real tokens. Prefer Tailscale or WireGuard for remote access, and bind PiGenus to private interfaces unless there is a specific reason to do otherwise.
