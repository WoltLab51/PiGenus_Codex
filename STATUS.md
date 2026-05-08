# PiGenus Status

## Current Checkpoint

- Name: `pigenus-v0.1.6-contexts`
- Branch: `main`
- Status: checkpointed
- Test command: `.venv\Scripts\python.exe -m pytest`
- Last verified result: `20 passed`

## Current Runtime Shape

PiGenus is a small local cognitive core. It has:

- Pydantic contracts for events, memory, cells, cell state, and context
- SQLite persistence for events, memory objects, cells, cell state, and audit logs
- A deterministic event flow
- A cell registry
- A permission engine
- A context boundary engine
- Audit logging
- A CLI demo
- Living project control documents

Current demo flow:

```text
TaskRequest -> MemoryProposal -> GuardDecision -> MemoryStored -> HumanResponse
```

## Stable Invariants

- Unknown event types are rejected.
- Known event types require their contract payload keys.
- Durable memory writes require a guarded `MemoryProposal`.
- A guard decision must match the proposal it allows.
- Cell state is not core memory.
- Unknown contexts are rejected.
- Cells may only process allowed contexts.
- Memory proposals preserve their source context.

## Next Recommended Work

Build Phase 2 Memory Lifecycle:

- Define explicit memory status transition rules.
- Implement review and expiry behavior.
- Protect `canonical` memory from automatic deletion.
- Add a small review CLI.
- Audit lifecycle changes.
- Add invariant tests before expanding intelligence or interfaces.

## Operator Note

Keep PiGenus boring at the core. New intelligence should sit on top of stable
contracts, not inside ambiguous storage, context, or guard behavior.

## Project Control Files

- `BUILD_PLAN.md`: current phase map and next work
- `CHANGELOG.md`: versioned changes
- `docs/ARCHITECTURE_HISTORY.md`: narrative system evolution
- `docs/DECISIONS.md`: durable architectural decisions
- `docs/PHASE_2_MEMORY_LIFECYCLE.md`: next phase implementation contract
