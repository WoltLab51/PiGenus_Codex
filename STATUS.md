# PiGenus Status

## Current Checkpoint

- Name: `pigenus-v0.4.0-worker-runtime-preparation-dev`
- Latest stable release checkpoint: `pigenus-v0.3.2-post-release-runtime-verification`
- Package version: `0.4.0.dev0`
- Branch: `main`
- Status: Worker Runtime preparation in progress; no worker execution
- Test command: `.venv\Scripts\python.exe -m pytest`
- CI command: `python -m pytest` on GitHub Actions / Python 3.12
- Last verified result: `332 passed`
- Naming: GENUS is the broader systemform; PiGenus is the local Python
  reference runtime distribution
- Canonical orientation: `docs/GENUS_CANONICAL_SYSTEMFORM.md` is the current
  alignment source of truth for GENUS systemform direction and conflicts.
- Canonical alignment: `docs/CANONICAL_ALIGNMENT_PLAN.md` maps existing docs
  and runtime surfaces against the canonical systemform before future cleanup.
- Metabolic graph direction: `docs/GENUS_METABOLIC_STATE_GRAPH.md` defines a
  future derived diagnostic view, not a second source of truth.
- Canonical implementation: `docs/CANONICAL_IMPLEMENTATION_PLAN.md` bridges the
  canonical systemform to next build cycles and initial cellular inventory.
- Cellular inventory review: `docs/CELLULAR_INVENTORY_REVIEW.md` code-checks
  the initial inventory and recommends Cell-DNA framing before new worker
  behavior.
- Cell-DNA protocol: `docs/CELL_DNA_PROTOCOL.md` defines the lightweight
  non-runtime frame, with applied frames for `WorkerAssignmentValidator` and
  `WorkerAssignmentSchedulingEligibilityValidator`, plus the first
  write-capable frame for `WorkerAssignmentCreator` and the lifecycle-changing
  frame for `WorkerAssignmentStatusTransitionService`, plus the freshness
  policy frame for `WorkerFreshnessPolicyValidator`.
- Cell-DNA consolidation: `docs/CELL_DNA_CONSOLIDATION_REVIEW.md`
  recommendation is applied; opt-in eligibility decision logging implementation
  remains a separate code slice.
- Scheduling eligibility logging:
  `worker-assignment-scheduling-eligibility --log` can now persist one
  governance decision for allow, deny, or review results only.
- WorkerAssignment tissue consolidation:
  `docs/WORKER_ASSIGNMENT_TISSUE_CONSOLIDATION_REVIEW.md` confirms assignment
  intent remains separate from scheduling, reservation, routing, and execution.
- Worker Scheduling Enforcement readiness:
  `docs/WORKER_SCHEDULING_ENFORCEMENT_READINESS_GAP_REVIEW.md` identifies
  freshness, room/context, resource/risk, reflex, approval, and reservation
  gaps before enforcement code.
- Worker Freshness Policy:
  `docs/WORKER_FRESHNESS_POLICY.md` defines heartbeat and governance evidence
  freshness semantics now used by assigned-intent scheduling eligibility before
  any scheduling enforcement code.

## Current Cycle

Worker Runtime / scheduling eligibility:

- Frame: check whether assigned WorkerAssignment intent may be considered by
  future scheduling.
- Result: read-only validator and CLI inspection are implemented.
- Structure: worker-assignment command handling is split into a stable router,
  read-only inspection commands, and lifecycle commands.
- Explicitly not now: no scheduling enforcement, reservation, routing,
  provider calls, execution logs, execution, or implicit logging.
- Consolidation: read-only boundary is complete for the first pass, no-write
  proof is covered by tests, reason codes are stable for the implemented
  worker inputs, and opt-in decision logging is implemented only for loggable
  allow, deny, or review results.
- Tissue review: WorkerAssignment now has validated creation, lifecycle
  transitions, eligibility inspection, and explicit eligibility decision
  logging without scheduling or execution.
- Enforcement readiness: scheduling enforcement is not ready yet; freshness
  is now a read-only eligibility input, and the next safe boundary is
  consolidation before any enforcement behavior.
- Freshness policy: heartbeat and preflight evidence age bands are documented;
  assigned-intent scheduling eligibility now evaluates those bands read-only.
- Freshness Cell-DNA: `WorkerFreshnessPolicyValidator` is framed as a
  read-only CapabilityCell / GovernedCellCandidate and now exists as a
  storage-free implementation.
- Freshness integration: `WorkerAssignmentSchedulingEligibilityValidator` now
  uses `WorkerFreshnessPolicyValidator` for heartbeat and preflight evidence
  age checks without adding CLI behavior, logging, scheduling enforcement,
  reservation, routing, provider calls, execution logs, or execution.
- Freshness eligibility consolidation:
  `docs/WORKER_FRESHNESS_ELIGIBILITY_CONSOLIDATION_REVIEW.md` accepts the
  read-only integration and led to room/context recheck semantics as the next
  readiness boundary.
- Room/context recheck semantics:
  `docs/WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK.md` defines assignment room,
  worker home room, ContextStack, and RoomFlow recheck rules before scheduling
  enforcement.
- Room/context recheck Cell-DNA:
  `docs/CELL_DNA_WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK_VALIDATOR.md` frames
  the future validator as read-only CapabilityCell / GovernedCellCandidate.
- Room/context recheck implementation:
  `WorkerAssignmentRoomContextRecheckValidator` now exists as a read-only
  validator with targeted no-write tests and no CLI, logging, enforcement,
  reservation, routing, provider calls, execution logs, or execution.
- Room/context recheck consolidation:
  `docs/WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK_CONSOLIDATION_REVIEW.md`
  accepts the read-only validator and sets the next decision as whether and
  how to wire it into scheduling eligibility without new effects.
- Room/context eligibility integration:
  `WorkerAssignmentSchedulingEligibilityValidator` now accepts an optional
  `WorkerAssignmentRoomContextRecheckValidator` plus caller-supplied context
  inputs and maps allow/review/deny/not-considered results without writes,
  CLI changes, logging, scheduling enforcement, reservation, routing, provider
  calls, execution logs, or execution.
- Fitness note: the worker-assignment CLI slicing decision has been applied;
  future growth should keep inspection and lifecycle surfaces separate.

## Current Runtime Shape

PiGenus is a small local GENUS runtime core. It has:

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
- Read-only `worker-scheduling-preview` CLI for candidate suitability previews
- Explicit `worker-scheduling-preview --log` support for one preview decision
  record with actor, room, and optional event metadata
- Storage-free Worker Execution Preflight for checking one worker before
  assignment, routing, or execution
- Read-only `worker-execution-preflight` CLI for inspecting execution
  eligibility for one worker
- Opt-in Worker Execution Preflight logging through the durable decision log
- Explicit `worker-execution-preflight --log` support for one preflight
  decision record with actor, room, and optional event metadata
- Model-only WorkerAssignment and WorkerAssignmentStatus Systemform concepts
  for later governed assignment records
- SQLite-backed WorkerAssignment Store for governed assignment intent requiring
  a known worker and existing governance decision evidence
- Dedicated worker storage repository module for worker profiles, current
  heartbeats, and assignment intent
- Read-only worker assignment inspection CLI with `worker-assignment-list`
- Worker assignment creation semantics documented before assignment creation
  was exposed
- WorkerAssignmentValidator for matching preflight allow evidence without
  persisting assignments
- Worker assignment creation audit behavior documented before any creation
  service or command
- WorkerAssignmentCreator for validated pending assignment creation with audit
- `worker-assignment-create` CLI for validated pending assignment creation via
  WorkerAssignmentCreator
- WorkerAssignment status transition semantics documented before transition
  services or commands
- WorkerAssignmentStatusTransitionValidator for read-only status graph checks
  before transition services or commands
- WorkerAssignmentStatusTransitionService for service-only status updates with
  audit before CLI exposure
- `worker-assignment-transition` CLI for validated status updates via
  WorkerAssignmentStatusTransitionService
- Worker Scheduling Enforcement boundary documented before real scheduling,
  reservation, routing, provider calls, execution logs, or execution
- WorkerAssignmentSchedulingEligibilityValidator for read-only assigned-intent
  scheduling eligibility checks without writes
- `worker-assignment-scheduling-eligibility` CLI inspection for
  assigned-intent scheduling eligibility, read-only unless `--log` is explicit
- Explicit `worker-assignment-scheduling-eligibility --log` support for one
  eligibility decision record on allow, deny, or review results
- Worker Scheduling Enforcement readiness gap review documenting why
  freshness semantics must precede enforcement code
- Worker Freshness Policy semantics for heartbeat age, preflight evidence age,
  review-stale, hard-stale, and no-side-effect requirements
- Cell-DNA frame for `WorkerFreshnessPolicyValidator`
- Storage-free `WorkerFreshnessPolicyValidator` with explicit `now`,
  heartbeat/evidence freshness labels, and no-write tests
- `WorkerFreshnessPolicyValidator` integrated into
  `WorkerAssignmentSchedulingEligibilityValidator` for read-only heartbeat and
  preflight evidence age checks
- Dedicated worker CLI command module for worker inspection, scheduling
  preview, and execution preflight command handling
- Dedicated worker-assignment CLI command modules for inspection and lifecycle
  command handling while preserving the stable worker-assignment dispatch
  surface
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
- GitHub Actions CI for running the Python test suite on push, pull request,
  and manual dispatch
- Worker Runtime readiness boundary for identity, heartbeat, capability
  profile, cost profile, privacy profile, and failure semantics before
  scheduling or execution
- Multimodal Systemform concept boundary for future language, graph, state,
  visual, spatial, and action representations as governed meaning
- Architecture fitness review for CLI, repository, and test-coupling hotspots
  before structural refactors
- Cellular Systemform concept defining GENUS cells as governed capability units
  and static module boundaries as temporary cell boundaries
- Architecture convergence now defines stable core vs variable runtime shapes
  as a future direction, not current dynamic behavior
- Philosophy Alignment Review Protocol defines a repeatable fit check for
  philosophy, governance, cellular maturity, RuntimeShape risk, and
  overengineering risk

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
- `worker-scheduling-preview` is read-only unless `--log` is provided; with
  `--log`, it writes one governance decision record and still does not write
  audit logs, schedule, assign, reserve, route providers, or execute tasks.
- `WorkerExecutionPreflightService` checks one worker and produces a trace plus
  log-compatible governance decision; it does not assign, reserve, route
  providers, persist, or execute tasks.
- `WorkerExecutionPreflightLogger` can persist preflight decisions through the
  existing decision log only when called explicitly; it does not assign,
  reserve, route providers, or execute tasks.
- `worker-execution-preflight` is read-only unless `--log` is provided; with
  `--log`, it writes one governance decision record and still does not write
  audit logs, assign, reserve, route providers, or execute tasks.
- `WorkerAssignment` requires governance decision evidence; it does not imply
  scheduling enforcement, reservation, routing, provider calls, execution logs,
  or execution result fields.
- `WorkerAssignmentRepository` persists assignment intent only when the worker
  and governance decision evidence already exist; it does not create workers,
  decisions, scheduling enforcement, reservations, routing, provider calls,
  execution logs, or execution results.
- `worker-assignment-list` is read-only and does not create assignments,
  decisions, audit logs, scheduling enforcement, reservations, routing,
  provider calls, execution logs, or execution results.
- Assignment creation requires matching `allow` evidence from
  `worker_execution_preflight` and may initially create only `pending`
  assignment intent.
- `WorkerAssignmentValidator` checks semantic evidence before assignment
  creation, but does not persist assignments or execute work.
- Successful assignment creation writes one pending assignment and
  one `worker_assignment_created` audit row; it must not create decisions,
  scheduling enforcement, routing, provider calls, or execution.
- `WorkerAssignmentCreator` validates, persists one pending assignment, and
  writes one audit row; it does not create decisions, expose CLI behavior,
  schedule, reserve, route, call providers, or execute work.
- `worker-assignment-create` is a thin CLI wrapper around
  WorkerAssignmentCreator; it creates pending assignment intent only and does
  not schedule, reserve, route, call providers, or execute work.
- WorkerAssignment status transitions are documented as intent lifecycle only:
  `pending -> assigned/rejected/cancelled/expired` and
  `assigned -> cancelled/expired`; terminal states do not reactivate.
- `WorkerAssignmentStatusTransitionValidator` checks that graph without
  mutating assignments, writing audit rows, scheduling, routing, or executing.
- `WorkerAssignmentStatusTransitionService` applies validated status changes
  and writes one audit row; it does not create decisions, schedule, reserve,
  route, call providers, or execute work.
- `worker-assignment-transition` is a thin CLI wrapper around
  WorkerAssignmentStatusTransitionService; it updates assignment lifecycle
  status only and does not schedule, reserve, route, call providers, or execute
  work.
- Worker Scheduling Enforcement is documented as the next boundary:
  `assigned` is necessary for future scheduling consideration, but it is not
  sufficient for scheduling, reservation, routing, provider calls, execution
  logs, or execution.
- `WorkerAssignmentSchedulingEligibilityValidator` checks whether assigned
  intent is eligible for future scheduling consideration; it does not write
  decisions, audits, assignments, reservations, routes, execution logs, or
  execution results. It now includes read-only heartbeat and preflight evidence
  freshness checks through `WorkerFreshnessPolicyValidator`.
- `worker-assignment-scheduling-eligibility` exposes that validator as a
  CLI inspection command; without `--log`, it does not write decisions,
  mutate assignments, reserve, route, or execute.
- `worker-assignment-scheduling-eligibility --log` is explicit decision
  logging only: one decision record for allow, deny, or review results, no
  decision record for not-considered results, no assignment mutation, no audit
  write, and no scheduling, reservation, routing, provider calls, execution
  logs, or execution.
- Internal communication uses governed meaning objects, structured events,
  decision traces, and persisted decisions instead of a free-form prompt bus.
- GENUS vocabulary is centralized before future schema, storage, or runtime
  expansion.
- Documentation maintenance is part of the checkpoint process for non-trivial
  runtime and architecture changes.
- `CHANGELOG.md` keeps `Unreleased` grouped by architecture arc and records
  only the latest verified test result there.
- Future capability growth must preserve contracts, rooms, meaning, guards,
  decisions, traces, and tests.
- `docs/INDEX.md` is the entry point for repository architecture documentation.
- Threat modeling precedes powerful runtime surfaces such as workers, LLM
  gateways, federation, and controlled evolution.
- Data objects should remain traceable from source through storage,
  inspection, and aging.
- Full checks scale with change risk; ChatGPT may review concepts, but Codex
  remains responsible for repository truth.
- GitHub Actions CI runs the test suite on push and pull request, but local
  checks still remain required before commits.
- Architecture fitness review precedes structural refactors so cell-like module
  boundaries are introduced without changing runtime behavior.
- Worker CLI command handling is structurally separated from the main CLI entry
  point without changing command behavior.
- WorkerAssignment CLI command handling is structurally separated into
  inspection and lifecycle modules without changing command behavior.
- Meaning CLI command handling is structurally separated from the main CLI
  entry point without changing command behavior, storage behavior, meaning
  ingestion behavior, or side-effect rules.
- Worker storage repositories are structurally separated from the shared
  repository module without changing SQL, migrations, import compatibility, CLI
  behavior, assignment behavior, or execution boundaries.
- PiGenus is a GENUS runtime distribution, not the entire GENUS system and not
  limited to Raspberry Pi hardware.
- Static CLI modules are temporary cell boundaries; modules above roughly 250
  lines should trigger a follow-up slicing decision before becoming new small
  monoliths.
- Runtime shapes remain documented/planned only; any future shape behavior must
  begin with preview, validation, guard decision, trace, and inspection.
- Non-trivial changes should pass a proportional Philosophy Alignment Review
  before they become code, storage, RuntimeShape, worker, cell, or governance
  behavior.

## Next Recommended Work

Worker Runtime preparation:

- Prepare the v0.4 Worker Runtime arc without implementing execution yet.
- WorkerAssignment read-only inspection exists as `worker-assignment-list`
  before pending assignment creation.
- Assignment creation semantics are documented before activation or execution
  paths.
- WorkerAssignmentValidator exists before `worker-assignment-create`.
- Assignment creation audit behavior is documented before assignment intent
  creation.
- WorkerAssignmentCreator exists before `worker-assignment-create`.
- `worker-assignment-create` exists as a small CLI wrapper around
  WorkerAssignmentCreator.
- WorkerAssignment status transition semantics, validator, service, and CLI
  wrapper now exist as lifecycle-only boundaries.
- `worker-assignment-transition` exists as a small CLI wrapper around
  WorkerAssignmentStatusTransitionService.
- Next, consolidate the read-only room/context scheduling eligibility
  integration before adding any CLI, logging, scheduling enforcement,
  reservation, routing, provider calls, execution logs, or execution behavior.
- Avoid adding scheduling, routing, reservation, provider, or execution
  behavior to assignment status transitions.
- Keep further CLI slicing focused and behavior-preserving; worker and meaning
  CLI command module boundaries are now separated from the main CLI entry
  point, and worker-assignment commands are split into inspection and lifecycle
  boundaries.
- Use the Cellular Systemform rule when slicing future CLI or service modules:
  smallest governable capability, not smallest possible function.
- Before implementing RuntimeShape or DeviceProfile behavior, keep shape
  formation preview-only and preserve the stable Systemform Kernel.
- Use the Philosophy Alignment Review Protocol before WorkerAssignment
  creation, service-to-cell promotion, or RuntimeShape implementation.
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
- `docs/ARCHITECTURE_FITNESS_REVIEW.md`: CLI/repository structural hotspot review
