# PiGenus

PiGenus Phase 1 is the local cognitive operating core for the GENUS system. It
is intentionally small: a testable Python runtime for cells, structured events,
memory objects, permissions, audit logging, and simple orchestration.

This repository does not include the broader GENUS system. There are no
dashboards, trading systems, LLM providers, external APIs, graph databases,
Redis, RabbitMQ, or autonomous evolution loops in Phase 1.

## What Phase 1 Includes

- Pydantic schemas for events, memory objects, and cell specs
- A SQLite-backed event, memory, cell, and audit store
- A cell registry
- A local event bus
- A simple permission engine
- MVP cells for input, rule guarding, memory writing, and explanation
- A deterministic demo orchestrator
- Pytest coverage for the core flow

## Demo Flow

The demo input is:

```text
Merke dir: PiGenus ist der Zellkern.
```

The runtime executes:

```text
InputCell -> RuleGuardCell -> MemoryWriterCell -> ExplainCell
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

## Phase 1 Boundary

PiGenus Phase 1 is only the nucleus: cells, meaning objects, permissions,
memory, and auditability. Future phases can add richer orchestration,
interfaces, providers, or distributed infrastructure without changing this
core contract.
