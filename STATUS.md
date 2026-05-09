# PiGenus Status

## Current Checkpoint

- Name: `pigenus-v0.2.4-decision-log`
- Branch: `main`
- Status: ready to checkpoint
- Test command: `.venv\Scripts\python.exe -m pytest`
- Last verified result: `45 passed`

## Current Runtime Shape

PiGenus is a small local cognitive core. It has:

- Pydantic contracts for events, memory, cells, cell state, and context
- SQLite persistence for events, memory objects, cells, cell state, and audit logs
- A deterministic event flow
- A cell registry
- A permission engine
- A context boundary engine
- A memory lifecycle engine
- Audit logging
- A CLI demo
- CLI conventions
- Migration policy
- A minimal SQLite migration runner
- A minimal schema registry
- A minimal decision log
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
- Review-due memory moves conservatively to `watch`.
- Expired memory changes status but is not deleted.
- Expired `dormant` memory becomes `fossil`.
- `canonical` memory is not changed by automatic review or expiry.
- Lifecycle status changes create audit logs.
- `memory-list` is read-only.
- `Database.initialize()` applies recorded migrations idempotently.
- Schema registry output matches runtime event validation constants.
- Lifecycle status changes write durable decision records.
- `decision-list` is read-only.

## Next Recommended Work

Checkpoint Phase 2.4 Decision Log Minimal, then build Phase 2.5 Cell Lifecycle Minimal:

- Make cell lifecycle status handling explicit.
- Update `last_used_at` when orchestrated cells run.
- Add read-only cell listing CLI.
- Keep LLMs, dashboards, workers, and vector search out of scope.

## Operator Note

Keep PiGenus boring at the core. New intelligence should sit on top of stable
contracts, not inside ambiguous storage, context, or guard behavior.

## Project Control Files

- `BUILD_PLAN.md`: current phase map and next work
- `CHANGELOG.md`: versioned changes
- `docs/ARCHITECTURE_HISTORY.md`: narrative system evolution
- `docs/DECISIONS.md`: durable architectural decisions
- `docs/PHASE_2_MEMORY_LIFECYCLE.md`: next phase implementation contract
- `docs/CLI_CONVENTIONS.md`: CLI behavior and exit-code conventions
- `docs/MIGRATIONS.md`: SQLite migration policy
