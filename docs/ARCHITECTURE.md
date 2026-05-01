# PiGenus Architecture

## Role

PiGenus is a persistent private orchestration node. It runs continuously on low-power hardware and coordinates stronger workers. It owns durable state, job lifecycle, auditability, and maintenance scheduling.

## Boundaries

PiGenus does:

- Accept trusted requests over a private API
- Persist sessions, messages, tasks, workers, jobs, memory, audit events, and settings
- Lease jobs to capable workers
- Track job events and results
- Run nightly maintenance triggers
- Expose health and admin status

PiGenus does not:

- Host a heavyweight local LLM
- Require GPUs
- Run a microservice fleet
- Self-modify without human oversight

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

## Night Mode

Phase 1 implements the maintenance trigger and stuck-job requeue path. The planned night mode responsibilities are:

- Rotate logs
- Create backups
- Summarize sessions
- Compress memory
- Requeue stuck jobs
- Prepare daily briefing
- Check worker availability

