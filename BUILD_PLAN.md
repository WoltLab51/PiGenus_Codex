# PiGenus Build Plan

This file is the living technical map for PiGenus. It keeps the small
checkpoints, but groups them by architectural intent so the project stays
readable as GENUS grows.

The canonical GENUS orientation lives in `docs/GENUS_CANONICAL_SYSTEMFORM.md`.
The guiding philosophy lives in `docs/GENUS_PHILOSOPHY.md`. This build plan
describes how PiGenus grows; the canonical systemform and philosophy explain
why it grows in this order.

`docs/CANONICAL_IMPLEMENTATION_PLAN.md` is the bridge from the canonical
systemform to concrete build cycles and should be checked before the next
implementation arc is selected.

Naming rule: GENUS is the broader systemform and architecture. PiGenus is the
local Python reference runtime distribution for GENUS. The `pigenus` package
name remains stable during the current runtime arc.

## Build Rule

Every checkpoint should leave the repository with:

- Passing tests
- Updated `CHANGELOG.md` using grouped `Unreleased` summaries when the active
  arc has more than a few entries
- Updated `STATUS.md`
- `docs/GENUS_CANONICAL_SYSTEMFORM.md` checked before new implementation plans
  or architecture directions
- `docs/CANONICAL_ALIGNMENT_PLAN.md` checked when older documents or runtime
  surfaces may drift from the canonical systemform
- `docs/CANONICAL_IMPLEMENTATION_PLAN.md` checked before selecting the next
  build slice from canonical direction
- `docs/INDEX.md` kept useful as the documentation entry point
- This build plan adjusted when the next step changes
- `docs/GENUS_VOCABULARY.md` checked when terms, statuses, or boundaries change
- `docs/DOCUMENTATION_MAINTENANCE.md` followed for documentation upkeep
- `docs/PHILOSOPHY_ALIGNMENT_REVIEW_PROTOCOL.md` used for non-trivial
  philosophy, governance, cellular, worker, or RuntimeShape changes
- `docs/ARCHITECTURE_CONTRACT.md` preserved for non-trivial runtime changes
- `docs/ARCHITECTURE_HISTORY.md` updated when the architecture changes
- `docs/DECISIONS.md` updated when a durable decision is made
- `docs/CELLULAR_SYSTEMFORM.md` checked when code is sliced toward cell-like
  module boundaries
- A Git commit
- A version tag for stable phase checkpoints

## Why This Order

PiGenus should become more capable only after it becomes more observable and
governable. The ordering is intentionally boring:

1. Build a deterministic runtime nucleus.
2. Make memory and storage lifecycle behavior explicit.
3. Add read-only inspection and backup surfaces before larger features.
4. Formalize Systemform models and adapters without replacing the prototype.
5. Add guard, governance, and approval layers before autonomous behavior.
6. Persist and inspect meaning before semantic search or LLM extraction.
7. Treat internal communication as governed meaning flow, not loose prompts.
8. Treat future multimodal representations as governed meaning, not hidden
   model state.
9. Add workers, resources, federation, and evolution only after the kernel can
   explain what happened and why.

## Release Semantics

Checkpoint tags such as `pigenus-v0.2.33` are working checkpoints inside a
larger architecture arc. They are not meant to imply that every patch number is
a standalone semantic product release.

- `0.1.x`: primitive local runtime and core contracts
- `0.2.x`: kernel completion arc: Systemform, Meaning Runtime, governance,
  room/context safety, inspection, backups, and controlled enforcement
- `0.3.x`: governed runtime arc: a stable local GENUS runtime with meaning,
  guard families, decision logging, approval stubs, explainability, backup, and
  operator inspection as one coherent release line
- `0.4.x`: worker runtime arc: worker registry, capability routing, task
  scheduling, provider gateways, and tool workers
- `0.5.x`: federated runtime arc: remote rooms, trust, signatures, replication,
  and conflict handling
- `0.6.x`: controlled evolution arc: shadow mutation, fitness comparison,
  rollback, fossils, and approval-gated activation
- `1.0`: boring reliability for a local GENUS runtime with stable APIs,
  recovery, governance, meaning, workers, inspection, and reliable boundaries

The first semantic governed-runtime cut was
`pigenus-v0.3.0-governed-runtime`. The first post-release architecture-control
checkpoint is `pigenus-v0.3.1-architecture-control`.

## Roadmap Map

### A. Foundation Runtime

Purpose: establish the executable local core.

Completed checkpoints:

- `pigenus-v0.1-core`: schemas, SQLite storage, event bus, registry, permission
  engine, audit logger, MVP cells, CLI demo, and core tests
- `pigenus-v0.1.5-contracts`: explicit event contracts, guarded memory writes,
  source-linked guard decisions, and separate cell state
- `pigenus-v0.1.6-contexts`: minimal context boundaries, known context names,
  context validation, and cell `allowed_contexts`

### B. Memory Lifecycle

Purpose: make memory age, review, and protect itself without adding AI.

Completed checkpoints:

- `pigenus-v0.2-memory-lifecycle`: review/expiry behavior, lifecycle statuses,
  canonical protection, memory review CLI, audit logs, and lifecycle tests
- `pigenus-v0.2.1-lifecycle-polish`: CLI conventions, migration policy, and
  read-only memory listing

### C. Inspection And Operator Safety

Purpose: make the runtime inspectable before it becomes more autonomous.

Completed checkpoints:

- `pigenus-v0.2.2-migrations`: idempotent migration runner
- `pigenus-v0.2.3-schema-registry`: event contract inspection
- `pigenus-v0.2.4-decision-log`: durable decision records and `decision-list`
- `pigenus-v0.2.5-cell-lifecycle`: cell lifecycle and read-only `cell-list`
- `pigenus-v0.2.6-context-inspection`: read-only `context-list`
- `pigenus-v0.2.7-permission-inspection`: read-only `permission-list`
- `pigenus-v0.2.8-audit-inspection`: read-only `audit-list`
- `pigenus-v0.2.9-event-inspection`: read-only `event-list` and `event-show`
- `pigenus-v0.2.10-runtime-overview`: local runtime overview
- `pigenus-v0.2.11-health-check`: read-only storage health checks
- `pigenus-v0.2.23-snapshot-backup-minimal`: local SQLite snapshot backups
- `pigenus-v0.2.28-changelog-release-sections`: checkpointed changelog sections

### D. Systemform Kernel

Purpose: formalize GENUS vocabulary and guard behavior while preserving the
existing prototype as the compatibility layer.

Completed checkpoints:

- `pigenus-v0.2.12-systemform-models`: Systemform documents, gap analysis, and
  additive models for actors, rooms, meaning, contracts, resources, and
  governance decisions
- `pigenus-v0.2.13-systemform-adapters`: deterministic adapters for
  `MemoryObject -> MeaningObject`, `CellSpec -> CellContract`, and `Context -> Room`
- `pigenus-v0.2.14-contract-validator`: storage-free contract validation
- `pigenus-v0.2.15-room-flow-rules`: deterministic semantic room-flow rules
- `pigenus-v0.2.16-guard-pipeline`: storage-free guard pipeline and ordered traces
- `pigenus-v0.2.17-guard-runtime-preview`: shadow-mode guard checks against
  adapted runtime objects
- `pigenus-v0.2.18-governance-decision-logging`: guard decisions persisted
  through the durable decision log
- `pigenus-v0.2.19-orchestrator-guard-preview`: orchestrator warning-mode preview
- `pigenus-v0.2.20-selective-guard-enforcement`: hard blocks stop execution;
  review/escalate stay warning states
- `pigenus-v0.2.21-human-approval-stub`: pending, approved, and rejected
  approval records without UI coupling

### E. Meaning Runtime

Purpose: persist, inspect, and bridge semantic objects before adding semantic
search, extraction, or LLM ranking.

Completed checkpoints:

- `pigenus-v0.2.22-meaning-store-minimal`: SQLite-backed `MeaningRepository`
  and indexed filters
- `pigenus-v0.2.24-meaning-retrieval-queries`: read-only `meaning-list`
- `pigenus-v0.2.25-meaning-detail-view`: read-only `meaning-show`
- `pigenus-v0.2.26-meaning-ingestion-preview`: explicit memory-to-meaning
  ingestion
- `pigenus-v0.2.27-runtime-overview-meaning-count`: Meaning Store count in the
  runtime overview

### F. Context And Room Governance

Purpose: connect legacy context boundaries to Systemform room metadata and make
boundary decisions inspectable.

Completed checkpoints:

- `pigenus-v0.2.29-context-boundary-room-metadata`: room ID and protection level
  on context boundary decisions
- `pigenus-v0.2.30-context-boundary-decision-logging-preview`: explicit
  `context-boundary-check --log`
- `pigenus-v0.2.31-context-boundary-decision-inspection`: read-only
  `context-boundary-list`
- `pigenus-v0.2.37-context-stack-ontology`: additive `ContextFrame` and
  `ContextStack` models plus context model documentation

### G. Guard Families

Purpose: make guard output scannable by policy family without parsing low-level
reason strings.

Completed checkpoints:

- `pigenus-v0.2.32-guard-families-minimal`: `family` on guard results and trace
  steps
- `pigenus-v0.2.33-guard-family-decision-log-surface`: read-only
  `guard-decision-list` with decision and family filters
- `pigenus-v0.2.38-guard-family-summary-minimal`: read-only
  `guard-decision-summary` grouped by decision and family

## Current And Next

Current development arc:

- `pigenus-v0.4.0-worker-runtime-preparation`: prepare worker identity,
  heartbeat, capability profile, cost profile, privacy profile, and failure
  semantics without enabling remote execution or LLM orchestration
- Package version during this arc: `0.4.0.dev0`
- Latest stable release checkpoint remains
  `pigenus-v0.3.2-post-release-runtime-verification`

Completed worker surfaces in this arc:

- Worker identity and current heartbeat source of truth in SQLite
- read-only worker inspection through `worker-list` and `worker-show`
- storage-free `worker-scheduling-preview` with explicit `--log`
- storage-free `worker-execution-preflight` with explicit `--log`
- governed WorkerAssignment intent store and read-only
  `worker-assignment-list`
- validated pending assignment creation through `worker-assignment-create`
- validated lifecycle status transitions through
  `worker-assignment-transition`
- read-only assigned-intent scheduling eligibility through
  `WorkerAssignmentSchedulingEligibilityValidator`
- read-only `worker-assignment-scheduling-eligibility` CLI inspection
- dedicated worker CLI and worker storage module boundaries
- dedicated worker-assignment CLI module boundaries for inspection and
  lifecycle command handling
- GitHub Actions CI for push, pull request, and manual dispatch

Current stop lines:

- no worker execution
- no scheduling enforcement yet
- no scheduling eligibility decision logging yet
- no reservation
- no provider routing
- no remote worker discovery
- no heartbeat history
- no implicit decision logging
- no assignment status change as execution proof
- no LLM orchestration, federation, dashboard, or autonomous agents

Next decision:

- Define the lightweight Cell-DNA construction protocol and apply the first
  frame to `WorkerAssignmentValidator` before deciding whether opt-in
  scheduling eligibility decision logging is mature enough. Do not add real
  scheduling, reservation, routing, provider calls, execution logs, or
  execution.

Readiness source:

- `docs/CELLULAR_INVENTORY_REVIEW.md`
- `docs/WORKER_RUNTIME_READINESS.md`
- `docs/DATA_ARCHITECTURE.md`
- `docs/GENUS_ARCHITECTURE_SUMMARY.md`
- `docs/ARCHITECTURE_FITNESS_REVIEW.md`
- `docs/WORKER_ASSIGNMENT_SEMANTICS.md`
- `docs/WORKER_SCHEDULING_ENFORCEMENT.md`

## Later Architecture Tracks

These are intentionally not current work. They become safer after guard,
meaning, inspection, and backup surfaces remain stable.

### H. Worker Interface

- Worker identity and heartbeat
- Capability declarations
- Cost and privacy profile
- Local-first worker registry
- Failure and timeout semantics
- Worker means execution host, not agent intelligence
- Cells carry capability, organs carry composition, agents carry goal direction
- Readiness before implementation: identity, heartbeat, capability profile,
  cost profile, privacy profile, and failure semantics must be modelable before
  scheduling or execution exists
- Model-only WorkerProfile and WorkerHeartbeat come before WorkerRegistry,
  worker inspection, scheduling, or execution routing
- Storage-free WorkerRegistry comes before worker inspection, database
  persistence, scheduling, or execution routing
- Read-only WorkerInspectionService comes before worker CLI, database
  persistence, scheduling, or execution routing
- Worker source of truth is SQLite for durable profiles and current heartbeats;
  local files are bootstrap/import only, and discovery waits for
  federation/trust
- Minimal Worker Store comes before worker CLI, scheduling preview, routing,
  heartbeat history, or execution
- Read-only worker CLI comes before scheduling preview, routing, heartbeat
  history, discovery, or execution
- Storage-free scheduling preview comes before durable scheduling, routing,
  execution records, provider calls, or execution
- GovernanceDecision conversion comes before preview logging, durable
  assignments, scheduling enforcement, routing, or execution
- Opt-in preview logging has preceded the read-only scheduling preview CLI,
  durable assignments, scheduling enforcement, routing, or execution
- Read-only scheduling preview CLI has preceded a CLI `--log` option, durable
  assignments, scheduling enforcement, routing, or execution
- CLI preview logging comes before worker execution preflight, durable
  assignments, scheduling enforcement, routing, or execution
- Worker Execution Preflight comes before a preflight CLI, durable assignments,
  scheduling enforcement, routing, provider calls, or execution
- Read-only preflight CLI comes before preflight logging, durable assignments,
  scheduling enforcement, routing, provider calls, or execution
- Explicit preflight logging comes before durable assignment records,
  scheduling enforcement, routing, provider calls, or execution
- Model-only WorkerAssignment has preceded assignment storage, CLI assignment
  creation, scheduling enforcement, routing, provider calls, and execution
- Minimal WorkerAssignment Store comes before read-only assignment inspection,
  CLI assignment creation, scheduling enforcement, routing, provider calls, or
  execution
- Read-only WorkerAssignment inspection comes before CLI assignment creation,
  scheduling enforcement, routing, provider calls, or execution
- WorkerAssignment creation semantics come before an assignment validator, CLI
  assignment creation, status transitions, scheduling enforcement, routing,
  provider calls, or execution
- WorkerAssignmentValidator comes before CLI assignment creation, status
  transitions, scheduling enforcement, routing, provider calls, or execution
- WorkerAssignment creation audit semantics come before a creation service,
  CLI assignment creation, status transitions, scheduling enforcement, routing,
  provider calls, or execution
- WorkerAssignmentCreator comes before CLI assignment creation, status
  transitions, scheduling enforcement, routing, provider calls, or execution
- `worker-assignment-create` comes before assignment status transition commands,
  scheduling enforcement, routing, provider calls, or execution
- WorkerAssignment status transition semantics come before a transition
  validator, transition service, transition CLI, scheduling
  enforcement, routing, provider calls, or execution
- WorkerAssignmentStatusTransitionValidator comes before a transition service,
  transition CLI, scheduling enforcement, routing, provider calls, or
  execution
- WorkerAssignmentStatusTransitionService comes before transition CLI,
  scheduling enforcement, routing, provider calls, or execution
- `worker-assignment-transition` comes before scheduling enforcement,
  reservation, routing, provider calls, or execution
- Worker Scheduling Enforcement boundary comes before a read-only enforcement
  validator/service, reservation, routing, provider calls, or execution
- Worker storage repositories are domain-sliced before read-only assignment
  inspection, assignment creation, scheduling enforcement, routing, provider
  calls, or execution
- CI is established before continuing Worker Runtime logging, assignment,
  routing, provider, or execution work

### I. Resource Economy

- Resource grants beyond static limits
- Compute, attention, storage, and time budgets
- Per-room quotas
- Cost reporting before optimization
- No market mechanics until accounting is reliable
- Budgets and usage records before prices, credits, or markets

### J. Federation

- Exportable runtime snapshots
- Trust-scoped remote rooms
- Signed decision and meaning records
- Replication policy
- Conflict handling before autonomous synchronization

### K. Controlled Evolution

- Mutation proposals only in shadow mode
- Fitness comparisons against explicit tests
- Rollback and fossil records
- Human approval before activation
- No self-modification until traceability is boring and complete
- Mutation is never activation

### L. Human Governance

- Approval records before approval UI
- Review, escalation, and approval stay distinct
- Room-aware approval authority
- No agent self-approval
- Required evidence before approve/reject actions

### M. Product Surfaces

- CLI remains the primary operator surface
- Dashboard follows CLI semantics, not the other way around
- Human approval UI after approval records and guard summaries are stable
- Visual system maps after the architecture vocabulary stops shifting rapidly
- CLI command modules should be extracted as static structural boundaries
  before any dynamic command-cell routing exists
- The first static module boundaries are `pigenus/cli/worker_commands.py` and
  `pigenus/cli/meaning_commands.py`; worker-assignment command handling now
  has separate inspection and lifecycle boundaries. Later extraction
  candidates should be reviewed with the Philosophy Alignment Review before
  code movement

### N. Liquid Runtime

- Dynamic form proposals from known runtime inventory
- Shape previews before execution
- Guarded execution only after validation, guard decision, and trace
- No arbitrary capability invention
- No self-modification or hidden mutation

### O. Idea Harvest

- Harvest ideas from older or parallel WoltLab51 GENUS/PiGenus repositories
- Treat harvested ideas as source memory, not direct implementation authority
- Map each idea to a current architecture track before implementation
- Do not merge old architecture around the governed runtime
- Keep `docs/GITHUB_IDEA_HARVEST.md` as the quarantine and triage surface

### P. Internal Communication

- Communicate through typed, validatable meaning objects instead of loose prompts
- Keep free text embedded in structured, room-aware, guardable objects
- Preserve source, room, intent, truth status, sensitivity, and time reference
- Separate events, meaning objects, governance decisions, and audit logs
- Treat messages as conditions for action, not neutral data packets

### P2. Data Lifecycle

- Keep `docs/DATA_LIFECYCLE.md` as the map for event, meaning, memory,
  decision, audit, fossil, and future mutation lifecycles
- Ensure new data objects answer source, room/context, truth, sensitivity,
  creator, guard, decision, storage, inspection, and aging questions
- Do not add new storage surfaces without lifecycle and inspection clarity

### P3. Data Architecture

- Keep `docs/DATA_ARCHITECTURE.md` as the map for storage roles and
  performance boundaries
- Preserve SQLite as local governed runtime truth
- Treat graph, vector, blob, and cache layers as explicitly classified storage
  roles before implementation
- Keep hot-path data small, indexed where needed, and separate from large
  payloads
- Do not add worker persistence, graph edges, vector search, or blob storage
  before the source-of-truth boundary is documented

### Q. Vocabulary And Ontology Control

- Keep `docs/GENUS_VOCABULARY.md` as the central term map
- Distinguish implemented, documented, planned, and conceptual terms
- Stabilize language before adding schema, storage, or runtime behavior
- Update the glossary when a term's architecture boundary changes

### R. Documentation Maintenance

- Treat documentation as operational memory
- Check project control documents before every non-trivial commit
- Keep `docs/INDEX.md` as the entry point for architecture documentation
- Use `docs/FULL_CHECK.md` for complete change, release, PR, and external
  review checks
- Use `docs/PHILOSOPHY_ALIGNMENT_REVIEW_PROTOCOL.md` to classify fit,
  maturity, governance path, RuntimeShape risk, and overengineering risk before
  larger changes
- Update vocabulary when term meaning or implementation status changes
- Update decisions only for durable architecture constraints
- Keep documentation current without turning every commit into paperwork

### S. Architecture Contract

- Preserve the v0.3 governed runtime baseline during future work
- Require contracts, rooms, meaning, guards, decisions, traces, and tests for
  meaningful capability growth
- Keep workers, LLMs, agents, and evolution behind governance boundaries
- Use `docs/ARCHITECTURE_CONTRACT.md` as the contribution safety contract

### S2. Cellular Systemform

- Treat cells as smallest governable capability units, not merely small
  functions
- Use static module boundaries as temporary cell boundaries before dynamic
  runtime cells exist
- Keep CLI command modules small enough to become future command cells or
  organs
- Treat command modules above roughly 250 lines as a slicing review signal, not
  an automatic failure
- Do not introduce autonomous cell routing before contracts, membranes,
  traces, tests, and inspection are explicit

### T. Threat Model

- Keep `docs/THREAT_MODEL.md` as the safety risk map
- Review prompt/meaning injection, room bypass, capability escalation, stale
  memory, approval spoofing, log gaps, rogue workers, LLM trust, silent
  mutation, resource abuse, and documentation drift
- Add threat notes before adding powerful runtime surfaces

### U. Multimodal Systemform

- Keep `docs/MULTIMODAL_SYSTEMFORM.md` as the concept boundary for language,
  graph, state-field, visual, spatial, and action-based representations
- Treat LLMs as governed capabilities, not as the GENUS kernel
- Treat visual, spatial, embedding, or state-field content as meaning-bearing
  only when provenance, room, sensitivity, confidence, and guardability are
  explicit
- Do not add LLM orchestration, vector search, vision models, or sensor
  ingestion before Worker Runtime and meaning governance can host them safely

### V. Runtime Shapes

- Keep the Systemform Kernel stable while allowing future task-, device-, and
  deployment-specific runtime forms
- Start with documented RuntimeShape, DeploymentProfile, DeviceProfile,
  ShapePreview, ShapeValidator, and ShapeTrace concepts before implementation
- Treat ShapePreview as explanation only until validation, guard decision, and
  trace surfaces are explicit
- Do not activate dynamic runtime shapes without contracts, room/context
  boundary, resource policy, guard decision, inspection path, and tests
- Keep DeviceProfile and RuntimeShape planned until Worker Runtime can provide
  trustworthy worker, resource, privacy, and failure inputs

### W. Metabolic State Graph

- Keep `docs/GENUS_METABOLIC_STATE_GRAPH.md` as the concept boundary for
  graph-shaped diagnosis of state, dependencies, metabolic flows, resources,
  inhibition, activation, reflexes, and recovery
- Treat the graph as a derived view over current source-of-truth stores, not a
  second truth source
- Start with concept only, then derived in-memory projection, then read-only
  CLI/export, then optional materialized view or external graph database only
  if needed
- Do not force graph queries into hot paths
- Do not add graph schema, graph database, runtime cell routing, scheduling
  enforcement, worker execution, or mutation activation from this track

## Non-Goals For The Current Kernel Phase

- No LLM-first behavior
- No hidden mutation
- No dashboard-driven architecture
- No distributed execution before local governance is inspectable
- No vector search before deterministic meaning storage and retrieval are stable
- No free-form prompt bus between runtime components
