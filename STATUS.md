# PiGenus Status

## Current Checkpoint

- Name: `pigenus-v0.3.2-post-release-runtime-verification`
- Branch: `main`
- Status: runtime verification checkpoint cut ready
- Test command: `.venv\Scripts\python.exe -m pytest`
- Last verified result: `226 passed`

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
- Exclusive pending migration application to avoid concurrent migration version
  races
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
- Additive ContextFrame and ContextStack Systemform concepts
- Model-only WorkerProfile and WorkerHeartbeat Systemform concepts
- Storage-free WorkerRegistry for known worker profiles and latest heartbeats
- Read-only WorkerInspectionService for storage-free worker inspection rows
- Deterministic Systemform adapters for memory, cells, and contexts
- Storage-free Systemform contract validator
- Storage-free room flow rules for semantic movement between rooms
- Storage-free guard pipeline with ordered decision traces
- Stable guard decision families on results and trace steps
- Shadow-mode guard runtime preview against adapted runtime objects
- Governance decision logging through the durable decision log
- Read-only guard decision inspection by decision and family
- Read-only guard decision summaries by decision and family
- Demo orchestrator guard preview in warning mode
- Selective guard enforcement for hard block decisions only
- Human approval stub with pending, approved, and rejected states
- SQLite-backed Systemform Meaning Store for local `MeaningObject` persistence
- SQLite-backed Worker Store for durable `WorkerProfile` records and current
  `WorkerHeartbeat` records
- Read-only worker inspection CLI with `worker-list` and `worker-show`
- Storage-free Worker Scheduling Preview for candidate suitability reasoning
- Worker Scheduling Preview to GovernanceDecision conversion without
  persistence
- Opt-in Worker Scheduling Preview logging through the durable decision log
- GENUS Systemform hardening documents
- GENUS philosophy document
- Living project control documents
- Build plan structured as architecture tracks from foundation runtime through
  controlled evolution
- Release semantics that distinguish `0.2.x` kernel checkpoints from the
  planned `0.3.0` governed runtime cut
- v0.3 governed runtime readiness document
- v0.3 governed runtime changelog section
- Post-release concept documents for Liquid Runtime, Worker Runtime, Resource
  Economy, Human Governance, Evolution Sandbox, GitHub Idea Harvest, and
  Internal Communication
- Central GENUS vocabulary glossary that distinguishes implemented, documented,
  planned, and conceptual terms
- Documentation maintenance rules for keeping project control files, vocabulary,
  decisions, and architecture history current
- Architecture contract defining non-breaking rules for future runtime and
  architecture work
- Documentation index for orientation across philosophy, vocabulary, build
  plan, status, architecture contract, and concept tracks
- Threat model covering current governed runtime risks and future worker, LLM,
  federation, resource, and evolution risks
- Data lifecycle map for events, meaning objects, memory objects, governance
  decisions, decision traces, audit logs, fossils, and future mutation proposals
- Data architecture map for storage roles, performance boundaries, and
  truth/index/cache/payload distinctions
- Compact GENUS architecture summary for current runtime orientation
- Worker source-of-truth policy: SQLite for durable profiles and current
  heartbeats, local files as bootstrap/import only, no discovery before
  federation and trust
- Full check process for documentation, concept, runtime, release, PR, and
  external ChatGPT review workflows
- Worker Runtime readiness boundary for identity, heartbeat, capability
  profile, cost profile, privacy profile, and failure semantics before
  scheduling or execution
- Multimodal Systemform concept boundary for future language, graph, state,
  visual, spatial, and action representations as governed meaning

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
- Pending migrations are applied under an immediate SQLite transaction.
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
- `guard-decision-summary` is read-only and summarizes logged governance decisions by final decision and family.
- `BUILD_PLAN.md` is organized as an architecture map instead of repeated current checkpoint sections.
- GENUS philosophy is documented separately from the build plan.
- Version numbers distinguish local checkpoints from larger release arcs.
- Context frames are modeled as conditions around actions and do not replace rooms, actors, cells, organs, agents, or characters.
- `ContextFrame` and `ContextStack` remain ontology-only until after v0.3 unless a separate migration and inspection plan exists.
- `WorkerProfile` and `WorkerHeartbeat` are model-only and do not add storage,
  scheduling, routing, provider calls, or execution.
- `WorkerRegistry` is storage-free and does not add database persistence, CLI
  inspection, scheduling, routing, provider calls, or execution.
- `WorkerInspectionService` is read-only and does not add storage, CLI command
  wiring, scheduling, routing, provider calls, or execution.
- `WorkerRepository` persists worker identity and current heartbeat state only;
  it does not add heartbeat history, CLI commands, scheduling, routing,
  provider calls, remote discovery, or execution.
- `worker-list` and `worker-show` are read-only and do not create workers,
  record heartbeats, schedule work, route providers, discover workers, or
  execute tasks.
- `WorkerSchedulingPreviewService` explains candidate suitability only; it does
  not reserve workers, write assignments, route providers, discover workers, or
  execute tasks.
- Worker scheduling preview governance conversion is log-compatible but does
  not persist by itself.
- `WorkerSchedulingPreviewLogger` can persist preview decisions through the
  existing decision log only when called explicitly; it does not schedule,
  assign, route providers, reserve workers, or execute tasks.
- Internal communication uses governed meaning objects, structured events,
  decision traces, and persisted decisions instead of a free-form prompt bus.
- GENUS vocabulary is centralized before future schema, storage, or runtime
  expansion.
- Documentation maintenance is part of the checkpoint process for non-trivial
  runtime and architecture changes.
- Future capability growth must preserve contracts, rooms, meaning, guards,
  decisions, traces, and tests.
- `docs/INDEX.md` is the entry point for repository architecture documentation.
- Threat modeling precedes powerful runtime surfaces such as workers, LLM
  gateways, federation, and controlled evolution.
- Data objects should remain traceable from source through storage,
  inspection, and aging.
- Full checks scale with change risk; ChatGPT may review concepts, but Codex
  remains responsible for repository truth.

## Next Recommended Work

Worker Runtime preparation:

- Prepare the v0.4 Worker Runtime arc without implementing execution yet.
- Next, decide whether scheduling preview needs a read-only CLI inspection
  surface before durable scheduling exists.
- Keep discovery, remote workers, scheduling, execution, and provider routing
  out of scope.
- Keep LLM gateways, remote execution, federation, dashboards, and evolution
  out of scope until worker identity, heartbeat, capability profile, cost
  profile, privacy profile, and failure semantics are clear.
- Preserve the multimodal Systemform anchor: later LLM, vision, embedding, or
  state-field capabilities should enter through workers, cells, contracts,
  meaning, rooms, guards, decisions, and traces.

## Operator Note

Keep PiGenus boring at the core. New intelligence should sit on top of stable
contracts, not inside ambiguous storage, context, or guard behavior.

## Project Control Files

- `docs/INDEX.md`: documentation entry point
- `BUILD_PLAN.md`: current phase map and next work
- `CHANGELOG.md`: versioned changes
- `docs/ARCHITECTURE_HISTORY.md`: narrative system evolution
- `docs/DECISIONS.md`: durable architectural decisions
- `docs/PHASE_2_MEMORY_LIFECYCLE.md`: next phase implementation contract
- `docs/CLI_CONVENTIONS.md`: CLI behavior and exit-code conventions
- `docs/MIGRATIONS.md`: SQLite migration policy
- `docs/RUNTIME_VERIFICATION.md`: post-release runtime verification notes
- `docs/DOCUMENTATION_MAINTENANCE.md`: documentation upkeep rules
- `docs/ARCHITECTURE_CONTRACT.md`: non-breaking architecture rules
- `docs/THREAT_MODEL.md`: security and governance risk map
- `docs/DATA_LIFECYCLE.md`: data lifecycle map
- `docs/DATA_ARCHITECTURE.md`: storage roles and performance boundary map
- `docs/GENUS_ARCHITECTURE_SUMMARY.md`: compact architecture summary
- `docs/FULL_CHECK.md`: complete quality check workflow
- `docs/WORKER_RUNTIME_READINESS.md`: v0.4 worker readiness boundary
- `docs/MULTIMODAL_SYSTEMFORM.md`: future multimodal meaning boundary
