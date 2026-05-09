# PiGenus Build Plan

This file is the living technical plan for PiGenus. Update it whenever a phase
is completed, renamed, split, or moved.

## Build Rule

Every checkpoint should leave the repository with:

- Passing tests
- Updated `CHANGELOG.md`
- Updated `STATUS.md`
- This build plan adjusted when the next step changes
- `docs/ARCHITECTURE_HISTORY.md` updated when the architecture changes
- `docs/DECISIONS.md` updated when a durable decision is made
- A Git commit
- A version tag for stable phase checkpoints

## Completed

### pigenus-v0.1-core

Phase 1 Core Runtime established the executable nucleus:

- Structured schemas
- SQLite storage
- Event bus
- Cell registry
- Permission engine
- Audit logger
- MVP cells
- CLI demo
- Core tests

### pigenus-v0.1.5-contracts

Phase 1.5 Core Contracts made core behavior more explicit:

- Known event types and required payload keys
- `MemoryProposal` before durable memory writes
- Guard decisions tied to the source proposal
- Separate `CellState` for operational cell-local state
- Invariant tests for direct-write rejection and cell-state separation

### pigenus-v0.1.6-contexts

Phase 1.6 Context Boundaries establishes minimal room separation:

- Structured context schema
- Known context names
- Event and memory context validation
- Cell `allowed_contexts` enforcement in the orchestrator
- Invariant tests for context rejection and preservation

### pigenus-v0.2-memory-lifecycle

Phase 2 Memory Lifecycle makes memory age, review, and protect itself without
adding external AI.

Specification:

- `docs/PHASE_2_MEMORY_LIFECYCLE.md`

Implemented scope:

- `review_due_at` and `expires_at` behavior
- Status transition rules
- `canonical` protection
- Memory review CLI
- Audit logs for memory status changes
- Tests for lifecycle invariants

### pigenus-v0.2.1-lifecycle-polish

Phase 2.1 hardens lifecycle ergonomics without adding intelligence:

- CLI command conventions and exit-code documentation
- Primitive SQLite migration policy
- Read-only memory listing command for inspection

### pigenus-v0.2.2-migrations

Phase 2.2 adds the smallest useful migration runner before future schema
evolution:

- `schema_migrations` table
- idempotent migration application
- smoke tests for fresh and existing databases
- no destructive migrations

### pigenus-v0.2.3-schema-registry

Phase 2.3 makes runtime contracts inspectable:

- event contract registry
- `schema-list` CLI
- tests that registry output matches runtime validation

### pigenus-v0.2.4-decision-log

Phase 2.4 makes important decisions queryable separately from raw events and
audit logs:

- `DecisionRecord` schema
- `decision_logs` SQLite table
- decision repository
- lifecycle decision recording
- read-only `decision-list` CLI

### pigenus-v0.2.5-cell-lifecycle

Goal: make cells observable as lifecycle-managed runtime units without adding
evolution.

Implemented scope:

- explicit cell lifecycle status handling
- update `last_used_at`
- simple fitness fields remain passive
- read-only cell listing CLI

Out of scope:

- LLM reasoning
- Dashboards
- Distributed workers
- Autonomous evolution
- Vector search

### pigenus-v0.2.6-context-inspection

Phase 2.6 makes known contexts inspectable without changing boundary behavior:

- read-only context registry
- `context-list` CLI
- optional allowed-cell display from an existing SQLite database
- tests proving context inspection does not create missing databases

### pigenus-v0.2.7-permission-inspection

Phase 2.7 makes built-in permissions inspectable before adding richer guard
behavior:

- read-only permission registry
- `permission-list` CLI
- tests tying inspection output to runtime permission defaults

### pigenus-v0.2.8-audit-inspection

Phase 2.8 makes audit logs safely inspectable:

- read-only `audit-list` CLI
- actor, action, and context filters
- tests proving audit inspection does not mutate storage

### pigenus-v0.2.9-event-inspection

Phase 2.9 makes stored events safely inspectable:

- read-only `event-list` CLI
- filters for event type, created-by cell, context, and limit
- read-only `event-show` CLI with JSON payload output
- clean error handling for unknown event IDs

### pigenus-v0.2.10-runtime-overview

Phase 2.10 provides one small operator overview of the local runtime:

- read-only runtime overview builder
- `runtime-overview` CLI
- counts for events, memory objects, cells, audit logs, and decision records
- known contexts and default permissions

### pigenus-v0.2.11-health-check

Phase 2.11 reports whether local runtime storage is structurally healthy:

- read-only health checker
- `health-check` CLI
- migration-state checks
- required-table checks
- non-zero exit for unhealthy storage

## Current

### pigenus-v0.2.11-health-check

Phase 2.11 is the current runtime shape.

## Next

### Phase 2.12 Snapshot/Backup Minimal

Goal: create safe local snapshots of healthy runtime storage.

Planned scope:

- `snapshot-create` CLI
- health-check before snapshot
- timestamped SQLite copy
- tests for successful snapshot and unhealthy refusal

Out of scope:

- restore
- scheduling
- cloud sync
- dashboards
- exports

## Later

- Context boundary expansion
- Guard families
- Worker interface
- Controlled cell evolution
