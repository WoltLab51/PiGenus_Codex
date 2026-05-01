# PiGenus

PiGenus is the always-on private orchestration and memory node for the GENUS ecosystem. It is designed for a Raspberry Pi 5 class device: low power, reliable, auditable, and recoverable.

PiGenus is not a local giant model host. It accepts trusted requests, persists state, turns work into jobs, leases those jobs to stronger workers, records results, and runs maintenance workflows.

## Phase 1 MVP

- FastAPI service
- SQLite persistence
- Bearer token admin auth
- Trusted worker registration
- Worker heartbeat
- Job submit, lease, ack, and fail lifecycle
- Audit log and job event history
- Nightly maintenance skeleton
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

## Production Posture

Set secrets through environment or an environment file owned by the service account. Do not commit real tokens. Prefer Tailscale or WireGuard for remote access, and bind PiGenus to private interfaces unless there is a specific reason to do otherwise.

