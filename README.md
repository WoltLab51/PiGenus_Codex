# PiGenus

PiGenus Phase 1 is the local cognitive operating core for the GENUS system. It
is intentionally small: a testable Python runtime for cells, structured events,
memory objects, permissions, audit logging, and simple orchestration.

This repository does not include the broader GENUS system. There are no
dashboards, trading systems, LLM providers, external APIs, graph databases,
Redis, RabbitMQ, or autonomous evolution loops in Phase 1.

## What Phase 1 Includes

- Pydantic schemas for events, memory objects, cell specs, and cell state
- A SQLite-backed event, memory, cell, cell-state, and audit store
- A cell registry
- A local event bus
- A minimal context boundary engine
- A deterministic memory lifecycle engine
- A simple permission engine
- MVP cells for input, rule guarding, memory proposal, memory writing, and explanation
- A deterministic demo orchestrator
- Pytest coverage for the core flow

## Phase 1.5 Core Contracts

PiGenus keeps durable memory under core control. Cells may propose memory through
structured `MemoryProposal` events, but only guarded proposals can become
`MemoryStored` events and persisted `MemoryObject` rows.

Cell-local state is stored separately from core memory. It is intended for
operational data such as caches, cursors, counters, and telemetry, not for
canonical facts about the user, world, or projects.

## Phase 1.6 Context Boundaries

Events and memory objects carry a structured context. The core currently knows
`developer/default`, `private/default`, `family/default`, and `trading/default`.
Cells declare `allowed_contexts`, and the orchestrator checks that boundary
before a cell can process an event. No cell may silently move work from one
context to another.

## Phase 2 Memory Lifecycle

Memory does not get deleted automatically. The lifecycle engine applies
deterministic review and expiry rules, updates memory status, and records audit
logs for status changes. Canonical memory is protected from automatic
downgrade, expiry, deletion, or fossilization.

Run lifecycle review with:

```powershell
python -m pigenus.cli.main memory-review --db pigenus.sqlite3
```

Inspect memory without modifying it:

```powershell
python -m pigenus.cli.main memory-list --db pigenus.sqlite3
```

## Demo Flow

The demo input is:

```text
Merke dir: PiGenus ist der Zellkern.
```

The runtime executes:

```text
InputCell -> RuleGuardCell -> MemoryProposerCell -> MemoryWriterCell -> ExplainCell
```

Expected response:

```text
Gespeichert: PiGenus ist der Zellkern.
```

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Run The Demo

```powershell
python -m pigenus.cli.main run-demo
```

The command prints the final response, the created memory object ID, and the
number of events stored. By default it writes SQLite data to `pigenus.sqlite3`
in the current working directory.

## Run Tests

```powershell
pytest
```

## Project Control

- `BUILD_PLAN.md` defines completed phases, the current phase, and the next build step.
- `STATUS.md` records the current checkpoint, runtime shape, invariants, and next work.
- `CHANGELOG.md` records versioned changes.
- `docs/ARCHITECTURE_HISTORY.md` explains the architectural evolution.
- `docs/DECISIONS.md` records durable design decisions.
- `docs/CLI_CONVENTIONS.md` defines CLI behavior and exit codes.
- `docs/MIGRATIONS.md` defines the early SQLite migration policy.

Update these files before every checkpoint commit.

## Database Migrations

`Database.initialize()` applies recorded SQLite migrations. The current runner
creates `schema_migrations` and records `0001_initial_schema`.

## Phase 1 Boundary

PiGenus Phase 1 is only the nucleus: cells, meaning objects, permissions,
memory, and auditability. Future phases can add richer orchestration,
interfaces, providers, or distributed infrastructure without changing this
core contract.
