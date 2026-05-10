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

Inspect known schema contracts:

```powershell
python -m pigenus.cli.main schema-list
```

Inspect durable decision records:

```powershell
python -m pigenus.cli.main decision-list --db pigenus.sqlite3
```

Inspect registered cells without modifying them:

```powershell
python -m pigenus.cli.main cell-list --db pigenus.sqlite3
```

Inspect known contexts without modifying storage:

```powershell
python -m pigenus.cli.main context-list
```

Include registered cells allowed in each context from an existing database:

```powershell
python -m pigenus.cli.main context-list --db pigenus.sqlite3 --show-cells
```

Inspect built-in default permissions:

```powershell
python -m pigenus.cli.main permission-list
```

Inspect audit logs without modifying them:

```powershell
python -m pigenus.cli.main audit-list --db pigenus.sqlite3
```

Inspect stored events without modifying them:

```powershell
python -m pigenus.cli.main event-list --db pigenus.sqlite3
python -m pigenus.cli.main event-show evt_example --db pigenus.sqlite3
```

Show a compact runtime overview:

```powershell
python -m pigenus.cli.main runtime-overview --db pigenus.sqlite3
```

Check local runtime storage health:

```powershell
python -m pigenus.cli.main health-check --db pigenus.sqlite3
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
creates `schema_migrations` and records forward-only migrations including the
initial schema, decision logs, and cell lifecycle columns.

## Phase 1 Boundary

PiGenus Phase 1 is only the nucleus: cells, meaning objects, permissions,
memory, and auditability. Future phases can add richer orchestration,
interfaces, providers, or distributed infrastructure without changing this
core contract.

## Systemform Hardening

Phase 0 is now treated as hardening of the existing runtime prototype, not a
rewrite. The GENUS Systemform documents live in `docs/`, and
`docs/SYSTEMFORM_GAP_ANALYSIS.md` tracks how current prototype concepts map to
the stricter kernel vocabulary: actors, rooms, meaning objects, cell contracts,
resource grants, and governance decisions.

The current bridge is intentionally additive: `pigenus.schemas.systemform`
defines the target vocabulary, while `pigenus.schemas.systemform_adapters`
maps existing `MemoryObject`, `CellSpec`, and `Context` contracts into that
vocabulary without changing storage or CLI behavior.

`pigenus.core.contract_validator` is the first executable Systemform hardening
rule. It validates actors, rooms, cell contracts, capabilities, permissions,
resource grants, and human-approval requirements without changing the current
orchestrator.

`pigenus.core.room_flow` adds the first semantic flow policy. It decides whether
meaning may move between rooms using a fixed matrix plus conservative
sensitivity and truth-status overrides. It is storage-free and not wired into
orchestration yet.

`pigenus.core.guard_pipeline` composes the storage-free contract validator and
room flow rules into an ordered decision trace. It keeps final decision
precedence explicit: block beats escalation, and escalation beats allow.

`pigenus.core.guard_runtime_preview` runs that pipeline against adapted runtime
objects in shadow mode. It returns a decision trace but does not persist,
publish, block, or otherwise alter the current orchestrator flow.

`pigenus.core.governance_decision_log` persists `GovernanceDecision` results and
their ordered traces through the existing durable decision log.

The demo orchestrator now runs the guard preview in warning mode before memory
writes. Preview decisions are logged, but the current task flow still runs.
Selective enforcement is intentionally narrow: only hard `block` decisions stop
execution. `review` and `escalate` remain logged warning states until a human
approval workflow exists.
