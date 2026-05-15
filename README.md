# PiGenus

PiGenus is the local governed runtime core for GENUS.

It is not a single AI agent. It is a small, testable Python runtime for
structured events, cells, memory, meaning, rooms, guards, governance decisions,
auditability, and worker-readiness.

The current development arc is:

```text
pigenus-v0.4.0-worker-runtime-preparation-dev
```

The latest stable checkpoint is:

```text
pigenus-v0.3.2-post-release-runtime-verification
```

Current package version:

```text
0.4.0.dev0
```

## Read First

The documentation entry point is:

- [`docs/INDEX.md`](docs/INDEX.md)

The short orientation set is:

- [`docs/GENUS_PHILOSOPHY.md`](docs/GENUS_PHILOSOPHY.md) - why GENUS is built this way
- [`docs/GENUS_ARCHITECTURE_SUMMARY.md`](docs/GENUS_ARCHITECTURE_SUMMARY.md) - compact architecture map
- [`docs/GENUS_VOCABULARY.md`](docs/GENUS_VOCABULARY.md) - shared terms and implementation status
- [`STATUS.md`](STATUS.md) - current repository truth
- [`BUILD_PLAN.md`](BUILD_PLAN.md) - roadmap and current work
- [`docs/ARCHITECTURE_CONTRACT.md`](docs/ARCHITECTURE_CONTRACT.md) - what future work must not break

## Current Runtime Shape

PiGenus currently includes:

- structured event contracts and event persistence
- SQLite-backed memory, meaning, worker, cell, audit, and decision surfaces
- memory lifecycle with review, expiry, canonical protection, and fossils
- Systemform models for actors, rooms, meaning objects, cell contracts,
  resource grants, governance decisions, context frames, context stacks, and
  worker-readiness concepts
- deterministic adapters from current runtime concepts into Systemform concepts
- contract validation, room flow rules, guard pipeline, and guard families
- governance decision logging and focused guard-decision inspection
- human approval stub records
- Meaning Store with read-only inspection and explicit memory-to-meaning ingestion
- health checks, backups, runtime overview, and read-only inspection CLI commands
- Worker Runtime preparation through worker profiles, heartbeats, worker store,
  worker inspection, scheduling preview, execution preflight, and model-only
  assignment shape
- GitHub Actions CI for the Python test suite

Current verified local test result:

```text
246 passed
```

## What Is Intentionally Not Included

PiGenus does not currently include:

- worker execution
- worker assignment creation
- provider routing
- remote worker discovery
- LLM orchestration
- vector search
- dashboards
- trading execution
- federation
- autonomous agents
- self-modification or evolution loops

The core rule is:

```text
capability must not bypass governance
```

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Run Tests

```powershell
.venv\Scripts\python.exe -m pytest
```

GitHub Actions also runs the test suite on pushes and pull requests to `main`.

## Run The Demo

```powershell
python -m pigenus.cli.main run-demo
```

The demo writes local SQLite data to `pigenus.sqlite3` by default.

The demo flow is:

```text
TaskRequest -> MemoryProposal -> GuardDecision -> MemoryStored -> HumanResponse
```

## Useful CLI Commands

Most inspection commands are read-only.

Runtime overview and health:

```powershell
python -m pigenus.cli.main runtime-overview --db pigenus.sqlite3
python -m pigenus.cli.main health-check --db pigenus.sqlite3
```

Memory, meaning, and events:

```powershell
python -m pigenus.cli.main memory-list --db pigenus.sqlite3
python -m pigenus.cli.main memory-review --db pigenus.sqlite3
python -m pigenus.cli.main meaning-list --db pigenus.sqlite3
python -m pigenus.cli.main meaning-show bo_example --db pigenus.sqlite3
python -m pigenus.cli.main meaning-ingest-memory mem_example --db pigenus.sqlite3
python -m pigenus.cli.main event-list --db pigenus.sqlite3
python -m pigenus.cli.main event-show evt_example --db pigenus.sqlite3
```

Decisions, guards, audit, context, and permissions:

```powershell
python -m pigenus.cli.main decision-list --db pigenus.sqlite3
python -m pigenus.cli.main guard-decision-list --db pigenus.sqlite3
python -m pigenus.cli.main guard-decision-summary --db pigenus.sqlite3
python -m pigenus.cli.main audit-list --db pigenus.sqlite3
python -m pigenus.cli.main context-list
python -m pigenus.cli.main permission-list
```

Cells and workers:

```powershell
python -m pigenus.cli.main cell-list --db pigenus.sqlite3
python -m pigenus.cli.main worker-list --db pigenus.sqlite3
python -m pigenus.cli.main worker-show worker_local --db pigenus.sqlite3
```

Worker scheduling preview:

```powershell
python -m pigenus.cli.main worker-scheduling-preview meaning_ingester --db pigenus.sqlite3 --runtime python
```

Log one scheduling preview explicitly:

```powershell
python -m pigenus.cli.main worker-scheduling-preview meaning_ingester --db pigenus.sqlite3 --runtime python --log --actor agent_preview --room room_developer
```

Worker execution preflight:

```powershell
python -m pigenus.cli.main worker-execution-preflight worker_local meaning_ingester --db pigenus.sqlite3 --runtime python
```

Log one execution preflight explicitly:

```powershell
python -m pigenus.cli.main worker-execution-preflight worker_local meaning_ingester --db pigenus.sqlite3 --runtime python --log --actor agent_preflight --room room_developer
```

These worker commands still do not assign, reserve, route, call providers, or
execute work.

## Worker Runtime Boundary

Current worker work is preparation, not execution.

Implemented worker surfaces:

- `WorkerProfile`
- `WorkerHeartbeat`
- `WorkerRegistry`
- `WorkerInspectionService`
- SQLite Worker Store for durable profiles and current heartbeats
- `worker-list` and `worker-show`
- Worker Scheduling Preview and explicit preview logging
- Worker Execution Preflight and explicit preflight logging
- model-only `WorkerAssignment` and `WorkerAssignmentStatus`
- static worker CLI command module boundary

Not implemented:

- assignment storage
- assignment creation CLI
- scheduling enforcement
- reservation
- provider routing
- execution records
- execution

## Database Migrations

`Database.initialize()` applies recorded SQLite migrations. Migrations are
forward-only and recorded in `schema_migrations`.

Current local SQLite storage includes tables for:

- events
- memory objects
- cells and cell state
- audit logs
- decision logs
- meaning objects
- worker profiles
- current worker heartbeats

Assignment storage does not exist yet.

## Project Control

Important project-control files:

- [`STATUS.md`](STATUS.md)
- [`BUILD_PLAN.md`](BUILD_PLAN.md)
- [`CHANGELOG.md`](CHANGELOG.md)
- [`docs/DECISIONS.md`](docs/DECISIONS.md)
- [`docs/ARCHITECTURE_HISTORY.md`](docs/ARCHITECTURE_HISTORY.md)
- [`docs/DOCUMENTATION_MAINTENANCE.md`](docs/DOCUMENTATION_MAINTENANCE.md)
- [`docs/FULL_CHECK.md`](docs/FULL_CHECK.md)

For non-trivial changes, update only the documentation whose truth changed.
Documentation should stay current, not maximal.

## Development Rule

Before adding capability, preserve:

```text
contract + context + room + meaning + guard + decision + trace + test
```

The project should remain boring at the core. New intelligence belongs on top
of stable contracts, not inside ambiguous storage, context, or guard behavior.
