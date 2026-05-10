# PiGenus Status

## Current Checkpoint

- Name: `pigenus-v0.2.19-orchestrator-guard-preview`
- Branch: `codex-orchestrator-guard-preview`
- Status: ready to checkpoint
- Test command: `.venv\Scripts\python.exe -m pytest`
- Last verified result: `140 passed`

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
- A minimal cell lifecycle surface
- A minimal context inspection surface
- A minimal permission inspection surface
- A minimal audit inspection surface
- A minimal event inspection surface
- A minimal runtime overview CLI
- A minimal health-check CLI
- Additive Systemform schema models for actors, rooms, meaning objects, cell contracts,
  resource grants, and governance decisions
- Deterministic Systemform adapters for memory, cells, and contexts
- Storage-free Systemform contract validator
- Storage-free room flow rules for semantic movement between rooms
- Storage-free guard pipeline with ordered decision traces
- Shadow-mode guard runtime preview against adapted runtime objects
- Governance decision logging through the durable decision log
- Demo orchestrator guard preview in warning mode
- GENUS Systemform hardening documents
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
- Registered cells expose lifecycle status and passive fitness metadata.
- Orchestrated cells update `last_used_at`.
- `cell-list` is read-only.
- Context registry output matches known runtime contexts.
- `context-list` is read-only and does not create missing databases.
- Permission registry output matches runtime default permissions.
- `permission-list` is read-only.
- Audit logs are append-only.
- `audit-list` is read-only.
- Stored events can be listed and inspected without mutation.
- Unknown event IDs return a clean CLI error.
- Runtime overview summarizes storage counts and static boundaries without mutation.
- Health check validates storage structure without applying migrations or repairs.
- Systemform models are additive and do not mutate existing storage or CLI behavior.
- Systemform adapters are deterministic and side-effect free.
- Contract validation is storage-free and does not alter orchestration behavior.
- Room flow rules are deterministic, storage-free, and not wired into orchestration yet.
- Guard pipeline decisions are storage-free and do not alter orchestration behavior.
- Guard runtime preview is shadow mode only and does not publish, persist, block, or enforce.
- Governance decision logging preserves ordered traces and does not enforce decisions.
- Orchestrator guard preview logs decisions but keeps task execution unchanged.

## Next Recommended Work

Checkpoint Orchestrator Guard Preview, then build Selective Guard Enforcement:

- Enforce only hard `block` decisions.
- Keep `review` and `escalate` as logged warning states until a human approval stub exists.
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
