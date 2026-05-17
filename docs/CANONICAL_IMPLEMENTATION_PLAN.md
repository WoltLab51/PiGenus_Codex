# Canonical Implementation Plan

This document translates `docs/GENUS_CANONICAL_SYSTEMFORM.md` and
`docs/GENUS_METABOLIC_STATE_GRAPH.md` into practical implementation planning
for the next build cycles.

It does not enable execution, dynamic runtime cells, graph databases, trading,
autonomous organisms, schemas, migrations, or runtime code changes.

## Purpose

The canonical documents define the direction. This plan defines how that
direction becomes concrete work without overbuilding.

It bridges:

```text
canonical systemform
-> cellular inventory
-> Cell-DNA construction protocol
-> worker runtime consolidation
-> future graph projection and homeostasis work
```

The first safe build slice is not a new feature. It is an initial cellular
inventory that classifies current runtime and operator surfaces by cellular
maturity.

## Current Canonical Truth

GENUS is a bio-cybernetic operating systemform.

PiGenus is the local Python reference runtime distribution for GENUS.

Every meaningful control point is cell-shaped. This does not mean every helper
is a heavy RuntimeCell. Cell ceremony scales with responsibility.

Canonical structure:

```text
MicroCell / Cell / CapabilityCell / GovernedCell / RuntimeCell
-> Tissue
-> Organ
-> Organism
-> Character
```

Cells compose into organs. Organs compose into organisms. Organisms live on
habitats and devices. Characters are social organisms with role, voice, memory,
and relationship behavior.

The Metabolic State Graph is a derived diagnostic and planning view over state,
dependencies, flows, resources, inhibition, activation, recovery, and lifecycle.
It is not a source of truth.

SQLite and current runtime stores remain the source of truth for PiGenus.

## Current Runtime State

PiGenus currently has:

- Systemform kernel models and adapters
- Meaning Store with indexed local SQLite persistence
- Guard pipeline, room flow rules, decision logging, and audit logging
- Human approval stub records
- Worker Store for durable worker profiles and current heartbeats
- Worker inspection CLI
- Worker scheduling preview with explicit optional decision logging
- Worker execution preflight with explicit optional decision logging
- WorkerAssignment intent model and SQLite store
- WorkerAssignment validation against matching preflight allow evidence
- WorkerAssignment creation service and CLI
- WorkerAssignment lifecycle transition validator, service, and CLI
- WorkerAssignment scheduling eligibility validator and CLI
- WorkerAssignment scheduling eligibility logging with explicit opt-in
- Worker Scheduling Enforcement readiness gap review
- Worker Freshness Policy semantics
- storage-free WorkerFreshnessPolicyValidator with Cell-DNA frame
- WorkerFreshnessPolicyValidator integrated into assigned-intent scheduling
  eligibility without new writes or execution behavior
- Static CLI module boundaries for worker, worker assignment, and meaning
  commands
- GitHub Actions CI and local test suite

PiGenus currently does not have:

- worker execution
- scheduling enforcement
- provider routing
- reservation records
- graph implementation
- dynamic RuntimeCell routing
- autonomous organisms
- trading behavior

## Forbidden Directions

The next build cycles must not introduce:

- worker execution
- trading or live high-risk execution
- graph database
- graph schema migration
- dynamic runtime-cell routing
- mutation activation
- autonomous organism behavior
- dashboard-first architecture
- LLM-first orchestration
- hidden prompt bus
- treating a worker as intelligence
- treating assigned WorkerAssignment status as execution proof

These are not merely "later features." They are blocked until the relevant
physiology exists: room policy, resource/risk budget, worker/habitat health,
capability contracts, guard decision path, reflexes, kill switch, audit/trace,
approval thresholds, recovery path, and shadow/dry-run evidence.

## Implementation Arcs

### Arc A: Cellular Inventory And Classification

Status: complete for the first pass.

Source:

- `docs/CELLULAR_INVENTORY_REVIEW.md`

Classify current runtime and operator surfaces by cellular maturity.

Goal:

- know which components are functions, MicroCells, CapabilityCells,
  GovernedCell candidates, tissues, operator surfaces, storage boundaries, or
  later RuntimeCells/organs
- avoid treating every helper as a RuntimeCell
- identify which surfaces need Cell-DNA frames before promotion

### Arc B: Cell-DNA Construction Protocol

Status: first three frames complete; consolidation complete for this pass.

Source:

- `docs/CELL_DNA_PROTOCOL.md`
- `docs/CELL_DNA_WORKER_ASSIGNMENT_VALIDATOR.md`
- `docs/CELL_DNA_WORKER_ASSIGNMENT_SCHEDULING_ELIGIBILITY_VALIDATOR.md`
- `docs/CELL_DNA_WORKER_ASSIGNMENT_CREATOR.md`
- `docs/CELL_DNA_CONSOLIDATION_REVIEW.md`
- `docs/CELL_DNA_WORKER_ASSIGNMENT_STATUS_TRANSITION_SERVICE.md`

Define a lightweight implementation template for new responsible capabilities.

The protocol should require:

- capability
- maturity
- input
- output
- reads
- writes
- allowed effects
- forbidden effects
- trace/audit behavior
- tests

This should be lightweight enough for services and validators, and strict
enough to prevent hidden capability growth.

### Arc C: Worker Runtime Consolidation

Consolidate the v0.4 Worker Runtime preparation arc before adding new worker
power.

Focus:

- confirm assignment intent lifecycle boundaries
- consolidate scheduling eligibility decision logging before scheduling
  enforcement
- consolidate freshness-integrated scheduling eligibility before any new
  logging or enforcement behavior
- define room/context recheck semantics before scheduling enforcement
- use the Cell-DNA frame for the room/context recheck validator before
  further maturity
- keep the first room/context recheck implementation read-only and free of
  CLI, logging, scheduling enforcement, reservation, routing, provider calls,
  execution logs, and execution
- consolidate the first room/context recheck implementation before any wiring
- if wiring the room/context recheck into scheduling eligibility later, keep it
  read-only and separate from CLI, logging, scheduling enforcement,
  reservation, routing, provider calls, execution logs, and execution
- consolidate the read-only room/context scheduling eligibility integration
  before exposing it through CLI, logging, or enforcement behavior
- define resource, risk, and reflex readiness semantics before any scheduling
  enforcement code
- keep assigned status separate from execution proof
- keep worker as host, not intelligence
- avoid scheduling enforcement until resource/risk/reflex boundaries exist

### Arc D: Metabolic Graph Projection Preview

Prepare a future read-only projection plan for the Metabolic State Graph.

This remains conceptual until a separate implementation decision exists.

First acceptable implementation shape would be:

- derived in-memory graph projection
- built from existing stores
- no graph database
- no graph schema migration
- no hot-path dependency
- no second source of truth

### Arc E: Resource / Homeostasis / Reflex Foundations

Define resource budgets, health signals, risk pressure, reflexes, and recovery
boundaries before any high-risk behavior.

Focus:

- resource/risk budget vocabulary
- worker/habitat health readiness
- circuit breaker concepts
- kill-switch boundaries
- quarantine and recovery paths
- audit/trace requirements

### Arc F: RuntimeCell / Organ Preparation

Prepare for future RuntimeCells and organs after static boundaries and
Cell-DNA frames are stable.

Focus:

- explicit cell identity
- capability contract
- lifecycle
- inspection
- registry expectations
- execution boundary requirements
- organ composition rules

Do not implement dynamic RuntimeCell routing in this arc.

### Arc G: Habitat / Device Runtime Profiles

Model the environment where future organisms live.

Focus:

- device constraints
- worker/habitat health
- resource limits
- privacy constraints
- local/edge/server/family/diagnostic deployment shapes

This remains behind Worker Runtime readiness and source-of-truth policy.

### Arc H: High-Risk Execution Readiness, Concept Only

Define what would be required before any high-risk organ can act live.

This is concept-only.

Requirements must include:

- room policy
- resource/risk budget
- worker/habitat health
- capability contract
- guard decision path
- reflexes / circuit breakers
- kill switch
- audit and trace
- human approval thresholds where required
- rollback, abort, or recovery path
- shadow mode or dry-run evidence

## First Safe Build Slice

Recommended next safe slice:

```text
Initial Cellular Inventory
```

Goal:

Classify existing major runtime and operator surfaces by cellular maturity.

This gives the project a practical map before promoting services, validators,
or CLI boundaries toward stronger cell forms.

Acceptance:

- docs-only or test-only classification work first
- no runtime behavior change
- no schema or migration
- no CLI additions
- no execution, scheduling enforcement, graph implementation, or trading
- current source-of-truth boundaries remain unchanged

## Initial Cellular Inventory

This inventory is an initial classification. It is intentionally conservative.
The maturity label says what the component is closest to today, not what it
should become immediately.

| Component | Current Role | Maturity Label | Reads | Writes | Allowed Effects | Forbidden Effects | Next Possible Maturity | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `GuardPipeline` | Composes contract and room-flow checks into decisions and traces. | Tissue | Contracts, room-flow inputs, meaning/context-shaped data | None by itself | Produce guard decision and ordered trace | Persistence, execution, hidden policy, LLM judgement | GovernedCell candidates inside immune tissue | Best understood as immune/governance tissue rather than one cell. |
| Meaning Store / `MeaningRepository` | Persists and queries `MeaningObject` rows. | StorageBoundary | SQLite `meaning_objects` | Meaning rows through repository calls | Store/query structured meaning | Truth promotion, vector search, LLM ranking, hidden mutation | Meaning Tissue support | Storage boundary, not a cell by itself. |
| DecisionLog / `DecisionRepository` | Persists durable decision records. | StorageBoundary | SQLite decision records | Decision rows | Store/query governance evidence | Enforce policy by itself, mutate unrelated state | Governance Tissue support | Current source for decision evidence. |
| `GovernanceDecisionLogger` | Converts and persists governance decisions. | GovernedCellCandidate | GovernanceDecision, DecisionRepository | Decision records | Persist explicit governance decision evidence | Schedule, execute, mutate decisions after write | GovernedCell | Cell-worthy because it changes durable governance evidence. |
| `AuditRepository` | Persists and queries audit rows. | StorageBoundary | SQLite audit records | Audit rows | Append/query operational accountability | Decide policy, execute, rewrite audit history | Audit Tissue support | Storage boundary under append-only semantics. |
| `WorkerRepository` | Stores worker profiles and current heartbeats. | StorageBoundary | Worker SQLite tables | Worker profile/current heartbeat rows | Store/query worker source-of-truth records | Discover workers, schedule, execute, infer intelligence | Worker/Habitat Tissue support | Worker remains execution host. |
| `WorkerAssignmentRepository` | Stores worker assignment intent. | StorageBoundary | WorkerAssignment rows, worker/decision existence | Assignment rows/status updates | Persist governed assignment intent and lifecycle state | Schedule, reserve, route, execute, treat assigned as execution proof | Worker Assignment Tissue support | Repository enforces basic existence, not semantic approval. |
| `WorkerAssignmentValidator` | Validates matching preflight allow evidence for assignment creation. | GovernedCellCandidate | WorkerAssignment, WorkerRepository, DecisionRepository | None | Return validation result and stable reasons | Persist, audit, schedule, execute | GovernedCell | Strong Cell-DNA candidate: clear membrane and forbidden effects. |
| `WorkerAssignmentCreator` | Creates pending assignment intent after validation and writes audit. | GovernedCellCandidate | Validator, WorkerAssignmentRepository, AuditRepository | Assignment row and creation audit on success | Create pending intent and audit one operational action | Create decisions, assign status, schedule, route, execute | GovernedCell | Meaningful control point with writes. |
| `WorkerAssignmentStatusTransitionValidator` | Checks allowed assignment lifecycle transitions. | MicroCell | Current assignment, target status | None | Return transition validation and reason codes | Persist, audit, execute, schedule | CapabilityCell | Small, responsibility-bearing, read-only capability. |
| `WorkerAssignmentStatusTransitionService` | Applies validated assignment status transitions and writes audit. | GovernedCellCandidate | Assignment repository, transition validator | Assignment status and audit row on success | Update lifecycle status under rules | Create decisions, schedule, route, execute | GovernedCell | Lifecycle control point; not execution proof. |
| `WorkerAssignmentSchedulingEligibilityValidator` | Checks whether assigned intent may be considered by future scheduling. | GovernedCellCandidate | WorkerAssignmentRepository, WorkerRepository, DecisionRepository, WorkerFreshnessPolicyValidator, optional WorkerAssignmentRoomContextRecheckValidator | None | Produce eligibility result, freshness labels, room/context details, and reasons | Audit, assignment mutation, reservation, routing, execution | GovernedCell | Validator stays read-only; logger handles explicit decision persistence. |
| `WorkerAssignmentSchedulingEligibilityLogger` | Persists loggable eligibility results as governance decisions only when explicit. | GovernedCellCandidate | Eligibility result, DecisionRepository | One decision row for allow, deny, or review | Persist operator evidence for review | Implicit logging, audit, assignment mutation, reservation, routing, execution | GovernedCell | Not-considered results are intentionally not persisted in the first slice. |
| Worker assignment CLI router | Registers and dispatches assignment commands. | OperatorSurface | Parsed args | None directly | Route commands to inspection/lifecycle modules | Own policy, schedule, execute, hidden writes | StaticCellBoundary | Keep thin. |
| Worker assignment inspection CLI | Lists assignments and inspects scheduling eligibility. | OperatorSurface | Assignment/worker/decision repositories | One decision row only with explicit `--log` | Operator inspection and opt-in evidence logging | Implicit logging, audit, mutation, reservation, execution | StaticCellBoundary / future command cells | Logging is not scheduling. |
| Worker assignment lifecycle CLI | Wraps assignment creation and transition services. | OperatorSurface | Parsed args, services | Through services only | Operator access to validated lifecycle actions | Own policy, bypass services, schedule, execute | StaticCellBoundary / future command cells | Writes must stay service-backed. |
| Shared storage repositories | Store events, memory, cells, audit, decisions, meaning compatibility exports. | StorageBoundary | SQLite | SQLite through repositories | Source-of-truth access | Hidden policy, graph truth, execution | Storage Tissue support | Continue slicing by domain when pressure grows. |
| Worker storage module | Worker profile, heartbeat, and assignment repository domain. | StorageBoundary | SQLite worker tables | SQLite worker tables | Worker source-of-truth access | Scheduling, routing, execution | Worker/Habitat Tissue support | Already domain-sliced. |
| Worker CLI command module | Worker inspection, scheduling preview, and execution preflight operator surface. | OperatorSurface | Worker store, decision store when explicit logging | Decision records only with explicit `--log` | Inspect and optionally log preview/preflight evidence | Assign, schedule, route, execute | StaticCellBoundary / future command cells | Keep explicit logging boundary. |
| Meaning CLI command module | Meaning list/show/ingest-memory operator surface. | OperatorSurface | Meaning/memory repositories | Meaning rows only through explicit ingestion | Inspect meaning and explicitly bridge memory to meaning | Audit, decision, lifecycle, LLM ranking | StaticCellBoundary / future command cells | Ingestion is explicit and bounded. |
| `MeaningIngestionPreview` | Bridges MemoryObject to MeaningObject explicitly. | GovernedCellCandidate | MemoryRepository, MeaningRepository | Meaning row when ingested | Deterministic memory-to-meaning persistence | Audit, decision, lifecycle mutation, LLM extraction | GovernedCell | Meaning metabolism candidate. |
| `SimpleOrchestrator` / demo runtime flow | Deterministic task-to-memory demo flow with guard preview/enforcement. | OrganLater | Events, cells, guard preview, memory path | Events, memory, decisions depending on flow | Demonstrate governed runtime path | Autonomous planning, worker execution, hidden agent behavior | OrganLater | Should not become autonomous agent loop. |
| Primitive runtime cells in `pigenus/cells` | Early executable cells for input, memory proposal/write, rules, explanation. | RuntimeCellLater | Events/context/memory path depending on cell | Event/memory path through orchestrator | Execute current deterministic demo roles | Self-routing, private truth, bypass guards | RuntimeCellLater after canonical Cell-DNA review | Current MVP cells predate full canonical maturity ladder. |
| `ContextBoundaryEngine` | Checks cell/context compatibility. | CapabilityCell | CellSpec, context | None | Allow/block context processing | Persist, execute, replace room policy | GovernedCellCandidate | Stable protection surface. |
| `PermissionEngine` | Checks default action permissions. | CapabilityCell | Permission mapping | None | Allow/block permission checks | Persist, grant dynamic authority, bypass guards | GovernedCellCandidate | Current simple permission tissue. |
| `MemoryLifecycleService` | Applies memory lifecycle transitions with audit/decisions. | GovernedCellCandidate | Memory repository, lifecycle engine, audit/decision surfaces | Memory status, audit, decisions | Review/expire memory under lifecycle rules | Delete memory, mutate canonical memory automatically | GovernedCell | Memory metabolism control point. |
| `SnapshotBackupService` | Creates local SQLite backup snapshots. | CapabilityCell | SQLite source | Backup file | Create explicit local snapshot | Initialize/migrate/repair/overwrite source storage | GovernedCellCandidate | Recovery/regeneration support candidate. |

## Verification Rules

Use verification proportional to risk:

- docs-only changes may skip tests, but must run `git diff --check`
- code changes require targeted tests and the full suite
- storage changes require migration and repository tests
- governance changes require allow/block/escalate/trace tests
- worker changes must prove no execution unless explicitly in a future
  execution arc
- graph changes must prove no second source of truth

## Non-Goals

This plan does not add:

- runtime code changes
- schemas
- migrations
- graph implementation
- CLI additions
- execution
- scheduling enforcement
- trading behavior
- dynamic cell runtime

## Current Conclusion

The next safe movement is not "build agents" or "build a graph."

The next safe movement is:

```text
classify the existing organism
then define Cell-DNA for new responsible capabilities
then consolidate Worker Runtime
```

This keeps GENUS cell-first without becoming RuntimeCell-first, and it keeps
PiGenus boring enough to remain testable.
