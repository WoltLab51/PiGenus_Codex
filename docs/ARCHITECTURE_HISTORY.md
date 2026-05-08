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

## Next: Phase 2 Memory Lifecycle

The next architectural step is memory aging and protection.

The planned direction:

- Explicit status transitions
- Review due dates
- Expiry behavior
- `canonical` protection
- Memory review CLI
- Audit logs for lifecycle changes
- Implementation contract in `docs/PHASE_2_MEMORY_LIFECYCLE.md`

Why this is next:

PiGenus now knows what a memory proposal is and where that memory belongs. The
next question is how long that memory should remain active, when it should be
reviewed, and what must never be automatically deleted.
