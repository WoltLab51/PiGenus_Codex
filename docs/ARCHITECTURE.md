# PiGenus Architecture

## Role

PiGenus is a persistent private orchestration node. It runs continuously on low-power hardware and coordinates stronger workers. It owns durable state, job lifecycle, auditability, and maintenance scheduling.

The binding product charter is [PIGENUS_CHARTER.md](PIGENUS_CHARTER.md). It is the first reference for architecture decisions, scope control, and future milestones.

## Boundaries

PiGenus does:

- Accept trusted requests over a private API
- Persist memories, sessions, messages, task state, decisions, project data, workers, jobs, audit events, and settings
- Lease jobs to capable workers
- Track job events and results
- Run nightly maintenance triggers
- Expose health and admin status
- Connect clients, workers, cloud APIs, GitHub, and later GENUS modules through private, auditable interfaces

PiGenus does not:

- Host a heavyweight local LLM
- Require GPUs
- Run a microservice fleet
- Self-modify without human oversight
- Become a disposable demo or a frontend-only project
- Optimize for short-term spectacle over long-term reliability

## Runtime Shape

Phase 1 is a single FastAPI process with internal modules:

- `api`: HTTP routes and dependency wiring
- `core`: config, logging, time helpers
- `db`: SQLAlchemy engine, sessions, ORM models
- `models`: Pydantic request and response schemas
- `security`: token auth and future rate-limit extension point
- `services`: transactional domain logic
- `workers`: worker-side contract helpers
- `memory`: long-term memory store primitives
- `scheduler`: nightly maintenance skeleton
- `monitoring`: status aggregation

This keeps deployment simple on Raspberry Pi while preserving clean boundaries for later extraction if needed.

## Security Model

- Admin calls require a long bearer token from environment/config.
- Worker registration requires admin auth.
- Registered workers receive a generated token once.
- Only token hashes are stored.
- Remote access should be private network first, using Tailscale or WireGuard.
- Rate limiting is an explicit Phase 2 extension point.

## Persistence Model

SQLite is the default. It is appropriate for a private low-throughput orchestration node and keeps backup/recovery simple. The SQLAlchemy layer leaves room for PostgreSQL later if PiGenus outgrows SQLite.

The operational CLI exposes `init-db`, `migrate`, `schema-version`, `backup`, and guarded `restore` commands. Restore refuses to overwrite the configured database unless `--yes` is supplied.

Schema management uses a lightweight internal migration ledger in Phase 2. This avoids adding an external migration dependency before the Raspberry Pi deployment path is proven. If schema churn increases, the ledger can be replaced with Alembic without changing API contracts.

## Administration Surface

PiGenus now exposes baseline admin surfaces for:

- Users
- Trusted devices
- Audit events
- Manual maintenance runs
- Job listing, inspection, and cancellation
- Session/message persistence
- Memory creation, search, and update

## Rate Limiting

PiGenus includes an in-process fixed-window rate limiter. It is intentionally simple and dependency-free for a single Raspberry Pi node. Deployments that place PiGenus behind a reverse proxy can add proxy-level limits later without removing this baseline protection.

## Night Mode

Night mode implements a maintenance trigger, stuck-job requeue path, SQLite backup creation, stale-worker detection, and queueing of maintenance jobs. Worker implementations can then perform heavier tasks off-device or on suitable machines.

- Rotate logs: queued as `maintenance.rotate_logs`
- Create backups: implemented for file-backed SQLite
- Summarize sessions: queued as `maintenance.summarize_sessions`
- Compress memory: queued as `maintenance.compress_memory`
- Requeue stuck jobs: implemented
- Prepare daily briefing: queued as `maintenance.daily_briefing`
- Check worker availability: stale online workers are marked offline, and a worker availability job is queued

## Operating Philosophy

PiGenus prioritizes maximum reliability over maximum raw performance. It should not do every task locally; it should preserve state, choose the right worker or service, coordinate execution, and keep the system recoverable.

GENUS is the larger organism. PiGenus is its local memory, coordination layer, circulation, and operations desk. Workers provide muscle, models provide thinking tools, and clients provide eyes, hands, and voice.
