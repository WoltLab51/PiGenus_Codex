# PiGenus Architecture History

This file records how PiGenus evolves over time. It is written for future
readers who need to understand why the system has its current shape.

## Origin

PiGenus is the core runtime of GENUS. The architectural direction is a small,
local, event-driven cognitive core where durable identity, memory, permissions,
contexts, auditability, and cell contracts are protected by the core rather
than improvised by individual agents.

The guiding idea:

```text
Events -> Cells -> Rules -> Memory -> Guards -> Decision -> Explanation
```

Natural language is an interface. The core exchanges structured meaning
objects.

## pigenus-v0.1-core

Phase 1 turned the idea into an executable nucleus.

The system gained:

- Structured schemas for events, memory, and cells
- SQLite persistence
- Event storage
- Cell registry
- Permission checks
- Audit logging
- MVP cells
- A deterministic CLI demo
- Core tests

Why it mattered:

PiGenus stopped being only a blueprint. It could run a small cell flow, persist
memory, emit events, and prove the flow with tests.

## pigenus-v0.1.5-contracts

Phase 1.5 made the runtime more explicit.

The important decision was:

```text
Cells may propose memory.
Only the core may store durable memory.
```

The system gained:

- Known event types
- Required payload keys
- `MemoryProposal`
- Guard decisions tied to the proposal they approve
- Separate `CellState` for operational cell-local state
- Invariant tests for contract boundaries

Why it mattered:

This prevented each cell from creating its own private truth. Operational cell
state became distinct from canonical core memory.

## pigenus-v0.1.6-contexts

Phase 1.6 added minimal context boundaries.

The important decision was:

```text
Memory must know where it belongs before it can safely age or spread.
```

The system gained:

- Structured context names
- Event and memory context validation
- A context boundary engine
- Cell `allowed_contexts`
- Orchestrator checks before cell execution
- Tests that block unknown or foreign contexts

Why it mattered:

PiGenus now has the first form of room separation. A cell cannot silently move
work across contexts, and a memory proposal preserves its source context.

## pigenus-v0.2-memory-lifecycle

Phase 2 implemented memory aging and protection.

The system gained:

- Explicit status transitions
- Review due behavior
- Expiry behavior without deletion
- `canonical` protection
- `memory-review` CLI
- Audit logs for lifecycle changes
- Implementation contract in `docs/PHASE_2_MEMORY_LIFECYCLE.md`

Why it mattered:

PiGenus now knows where memory belongs and how memory ages. Expiry no longer
means deletion; it means a controlled status transition. Canonical memory is
protected from automatic lifecycle changes.

## Next: Phase 2.1 Lifecycle Polish

Phase 2.1 added operational clarity:

- CLI conventions and exit-code documentation
- A primitive SQLite migration policy
- Read-only memory inspection through `memory-list`

Why it mattered:

The lifecycle system became inspectable without mutation, and future schema
changes now have a documented migration policy.

## Next: Phase 2.2 Migration Runner

Phase 2.2 implemented the smallest useful migration runner before more schema
evolution:

- `schema_migrations`
- idempotent migration application
- smoke tests for fresh and existing databases

Why it mattered:

PiGenus now records schema evolution inside SQLite itself. Future schema changes
can become explicit migrations instead of hidden side effects of initialization.

## Next: Phase 2.3 Schema Registry Minimal

Phase 2.3 made runtime contracts inspectable:

- known event types
- required payload keys
- CLI inspection for schema contracts

Why it mattered:

PiGenus can now describe its structured event contracts through the same source
of truth used by runtime validation.

## Next: Phase 2.4 Decision Log Minimal

Phase 2.4 preserves important decisions separately from raw events and audit
logs:

- decision record schema
- SQLite persistence
- read-only decision list CLI

Why it mattered:

PiGenus can now answer "what important decision was made?" without forcing
operators to reconstruct that from raw events and audit rows.

## Next: Phase 2.5 Cell Lifecycle Minimal

Phase 2.5 made cells observable as runtime units:

- explicit cell lifecycle status handling
- `last_used_at` updates
- read-only cell listing

Why it mattered:

PiGenus can now show which cells are registered and when orchestrated cells were
used, while keeping fitness passive and avoiding autonomous mutation.

## Next: Phase 2.6 Context Inspection Minimal

Phase 2.6 made known contexts inspectable:

- read-only context registry
- `context-list` CLI
- optional allowed-cell display from an existing database

Why it mattered:

PiGenus can now show its room boundaries directly. Inspection stays passive, so
looking at contexts does not create a database or mutate runtime state.

## Next: Phase 2.7 Permission Inspection Minimal

Phase 2.7 made built-in permissions inspectable:

- read-only permission registry
- `permission-list` CLI
- tests tied to runtime permission defaults

Why it mattered:

PiGenus can now show what default actions are allowed before adding richer guard
families or editable policies. The inspection path reads enforcement defaults
instead of maintaining a second description.

## Next: Phase 2.8 Audit Inspection Minimal

Phase 2.8 made audit logs safely inspectable:

- read-only `audit-list` CLI
- filters for actor, action, and context
- tests proving inspection does not mutate storage

Why it mattered:

PiGenus can now show its append-only audit trail directly. This makes runtime
actions inspectable without adding export systems, dashboards, or mutation
paths.

## Next: Phase 2.9 Event Inspection Minimal

Phase 2.9 made stored events inspectable:

- read-only `event-list` CLI
- filters for object type, created-by cell, context, and limit
- read-only `event-show` CLI with JSON payload output

Why it mattered:

PiGenus can now show the structured runtime trace directly. Operators can
inspect recent events or one event by ID without introducing replay, mutation,
or export behavior.

## Next: Phase 2.10 Runtime Overview CLI

Phase 2.10 added a compact runtime overview:

- counts for stored runtime objects
- known contexts
- default permissions

Why it mattered:

PiGenus now has a single operator-facing summary of its local state. The command
stays read-only and avoids becoming a health check, repair tool, dashboard, or
export path.

## Next: Phase 2.11 Health Check Minimal

Phase 2.11 added structural storage diagnosis:

- read-only `health-check` CLI
- required-table checks
- migration-state checks
- non-zero exit for unhealthy storage

Why it mattered:

PiGenus can now distinguish "what exists" from "is the storage structurally
sound?" The health check diagnoses without applying migrations or repairs, so it
does not mask damage while inspecting it.
