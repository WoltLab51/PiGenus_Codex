# PiGenus Status

## Current Checkpoint

- Name: `pigenus-v0.2.36-release-semantics`
- Branch: `codex-context-boundary-room-metadata`
- Status: ready to checkpoint
- Test command: `.venv\Scripts\python.exe -m pytest`
- Last verified result: `179 passed`

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
- A minimal local SQLite backup CLI
- A minimal meaning inspection CLI
- Additive Systemform schema models for actors, rooms, meaning objects, cell contracts,
  resource grants, and governance decisions
- Deterministic Systemform adapters for memory, cells, and contexts
- Storage-free Systemform contract validator
- Storage-free room flow rules for semantic movement between rooms
- Storage-free guard pipeline with ordered decision traces
- Stable guard decision families on results and trace steps
- Shadow-mode guard runtime preview against adapted runtime objects
- Governance decision logging through the durable decision log
- Read-only guard decision inspection by decision and family
- Demo orchestrator guard preview in warning mode
- Selective guard enforcement for hard block decisions only
- Human approval stub with pending, approved, and rejected states
- SQLite-backed Systemform Meaning Store for local `MeaningObject` persistence
- GENUS Systemform hardening documents
- GENUS philosophy document
- Living project control documents
- Build plan structured as architecture tracks from foundation runtime through
  controlled evolution
- Release semantics that distinguish `0.2.x` kernel checkpoints from the
  planned `0.3.0` governed runtime cut

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
- Selective guard enforcement stops hard block decisions only.
- Review and escalate decisions remain logged warning states.
- Human approval records persist through the decision log and do not alter current flow.
- Meaning objects persist as full Systemform JSON plus indexed query columns.
- Meaning Store filters are local, deterministic, and limited to room, type, truth status, and sensitivity.
- Snapshot backups use SQLite's backup API and do not initialize, migrate, repair, or overwrite storage.
- Created snapshots must pass SQLite integrity check.
- `meaning-list` is read-only and uses only indexed Meaning Store filters.
- `meaning-show` is read-only and returns deterministic JSON for one MeaningObject.
- Meaning ingestion preview can persist adapted memory as meaning without audit, decision, lifecycle, or orchestrator side effects.
- Runtime overview reports Meaning Store object count.
- Changelog is split into explicit checkpoint sections through `pigenus-v0.2.27`.
- Context boundary decisions expose Systemform room ID and protection level.
- Context boundary decisions can be preview-logged through the decision log with explicit operator opt-in.
- `context-boundary-list` is read-only and filters logged boundary decisions by cell, context, room, and allowed status.
- Guard pipeline results and trace steps expose stable decision families without changing policy outcomes.
- `guard-decision-list` is read-only and filters logged governance decisions by final decision and family.
- `BUILD_PLAN.md` is organized as an architecture map instead of repeated current checkpoint sections.
- GENUS philosophy is documented separately from the build plan.
- Version numbers distinguish local checkpoints from larger release arcs.

## Next Recommended Work

Finish Guard Family Summary Minimal:

- Summarize stored guard decisions by final decision and family.
- Keep new policy, storage migrations, enforcement changes, and dashboard inspection out of scope.

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
