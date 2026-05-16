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

## Systemform Hardening v0.1

The important decision was:

```text
PiGenus is not rebuilt from scratch.
Phase 0 hardens the existing runtime prototype.
```

The system gained:

- GENUS Systemform and Phase 0 kernel documents in `docs/`
- `docs/SYSTEMFORM_GAP_ANALYSIS.md`
- Additive Systemform schema models for actors, rooms, meaning objects, cell
  contracts, resource grants, and governance decisions
- Deterministic adapters from current prototype concepts to Systemform concepts

Why it mattered:

The working runtime remains intact while the deeper GENUS ontology becomes
explicit. Current concepts such as `MemoryObject`, `CellSpec`, and `Context`
can continue to run as the compatibility layer until adapters and validators
are introduced in later hardening passes.

The adapter pass made that compatibility layer concrete:

- `MemoryObject -> MeaningObject`
- `CellSpec -> CellContract`
- `Context -> Room`

The adapters are side-effect free and do not change storage, CLI behavior, or
runtime orchestration.

## Contract Validator Minimal

The system gained:

- Storage-free `ContractValidator`
- `ContractValidationResult`
- Conversion from validator result to `GovernanceDecision`
- Tests for actor status, contract status, room scope, capabilities,
  permissions, resource grants, resource limits, and human-approval escalation

Why it mattered:

The Systemform rule "no execution without a valid contract" is now executable
without disturbing the current runtime. This creates a testable policy core
that can later be wired into guard pipelines or orchestration after room flow
rules are equally explicit.

## Room Flow Rules Minimal

The system gained:

- Storage-free `RoomFlowRules`
- Explicit room-to-room flow matrix
- Decisions for `allow`, `review`, `block`, and `allow_read`
- Sensitivity overrides for secret, private, family, financial, and child-related meaning
- Truth-status overrides for unsafe, contested, simulated, deprecated, and historical meaning

Why it mattered:

GENUS now has a small deterministic rule layer for semantic movement between
rooms. This is still not orchestration enforcement; it is a reviewable policy
surface that can be composed into a guard pipeline later.

## Guard Pipeline Minimal

The system gained:

- Storage-free `GuardPipeline`
- Ordered trace steps for contract validation and optional room flow
- Final decision precedence: block, then escalation, then allow
- Conversion from pipeline result to `GovernanceDecision`

Why it mattered:

Contract and room-flow policy are now composable without touching persistence
or the existing orchestrator. The kernel can explain which protective layer
made the final decision before any runtime enforcement is attempted.

## Guard Pipeline Runtime Preview

The system gained:

- Shadow-mode `GuardPipelineRuntimePreview`
- Runtime adaptation from `CellSpec` and `Context` into Systemform actor, room, and contract inputs
- Preview support for optional runtime `MemoryObject` or explicit `MeaningObject`
- Tests proving preview results do not mutate event, audit, memory, repository, or orchestrator behavior

Why it mattered:

The guard pipeline can now run against real runtime-shaped inputs without
enforcing decisions. This is the bridge between pure policy and operational
integration, and it preserves the existing green runtime while the policy layer
learns to observe real flows.

## Governance Decision Logging

The system gained:

- `GovernanceDecisionLogger`
- Conversion from Systemform `GovernanceDecision` to durable `DecisionRecord`
- Trace persistence through the existing `decision_logs` table
- Tests for allow, block, escalate, and ordered trace serialization

Why it mattered:

Policy decisions are now durable without changing orchestration behavior. This
gives GENUS an audit-ready path for comparing preview decisions with current
runtime behavior before any enforcement is enabled.

## Orchestrator Guard Preview

The system gained:

- Demo-orchestrator guard preview before memory writes
- Governance decision persistence for preview results
- Tests proving event flow and task execution continue unchanged

Why it mattered:

The policy layer now observes a real runtime path in warning mode. GENUS can
compare guard decisions with actual execution before any selective enforcement
is enabled.

## Selective Guard Enforcement

The system gained:

- Enforcement for hard `block` guard decisions
- Logged warning behavior for `review` and `escalate`
- Tests proving block stops execution while review/escalate remains non-blocking

Why it mattered:

GENUS now has its first narrow runtime enforcement point. Enforcement remains
conservative: only explicit blocks stop the write path, and human-review states
continue to be logged until an approval workflow exists.

## Human Approval Stub

The system gained:

- `HumanApprovalRecord`
- Approval statuses: `pending`, `approved`, `rejected`
- Approval persistence through the durable decision log
- Tests proving approval records do not alter current orchestrator flow

Why it mattered:

Review and escalation decisions now have a safe placeholder before richer
human-in-the-loop workflows exist. This keeps enforcement narrow while giving
future approval UI or CLI work a stable storage shape to build on.

## Meaning Store Minimal

The system gained:

- `meaning_objects` SQLite table
- Indexed query columns for room, type, truth status, and sensitivity
- `MeaningRepository` for add, get, list, and count
- Tests proving full `MeaningObject` JSON round-trips through storage

Why it mattered:

Systemform meaning now has a small durable home before vector search, LLM
integration, dashboards, or memory migration work begins. The store keeps the
complete semantic object intact while exposing only the first conservative query
surface needed by the local runtime.

## Snapshot/Backup Minimal

The system gained:

- `SnapshotBackupService`
- `backup-create` CLI command
- SQLite backup API based snapshot creation
- Missing-source and no-overwrite safety checks
- SQLite integrity check for created snapshots

Why it mattered:

Meaning Runtime work increases the value of local SQLite state. Before adding
richer retrieval or runtime integration, PiGenus now has a small operator-safe
way to preserve that state without running migrations, repairs, restore logic,
or remote backup workflows.

## Meaning Retrieval Queries Minimal

The system gained:

- `meaning-list` CLI command
- Filters for room, type, truth status, and sensitivity
- Compact meaning rows for operator inspection
- Tests proving empty output, read-only behavior, and combined filters

Why it mattered:

The Meaning Store can now be inspected without reaching for SQLite directly.
Retrieval remains deliberately narrow: indexed filters only, no ranking, no
vector search, no LLM interpretation, and no dashboard behavior.

## Meaning Detail View Minimal

The system gained:

- `meaning-show` CLI command
- Deterministic JSON output for one stored `MeaningObject`
- Clean not-found behavior for unknown IDs
- Tests proving full object inspection and read-only behavior

Why it mattered:

Operators can now inspect a complete semantic object without opening SQLite or
adding export workflows. List stays compact for scanning; show provides the full
structured object for debugging and review.

## Meaning Runtime Ingestion Preview

The system gained:

- `MeaningIngestionPreview`
- `meaning-ingest-memory` CLI command
- Idempotent `MemoryObject -> MeaningObject` persistence
- Tests proving missing-memory behavior and no audit or decision side effects

Why it mattered:

Meaning Store is now reachable from actual runtime memory without changing the
orchestrator, lifecycle engine, or guard enforcement. The ingestion path is
explicit and reversible at the workflow level: operators choose when to bridge
durable memory into Systemform meaning.

## Runtime Overview Meaning Count

The system gained:

- `meaning_count` in `RuntimeOverview`
- `Meaning objects` line in `runtime-overview`
- Tests proving overview count and read-only behavior

Why it mattered:

Meaning Store is now part of the operator's first runtime glance. The overview
still stays intentionally small: it reports presence and volume without becoming
a search surface, dashboard, or semantic analysis tool.

## Context Boundary Room Metadata

The system gained:

- `room_id` on context boundary decisions
- `protection_level` on context boundary decisions
- Tests for room metadata on allowed and blocked contexts

Why it mattered:

The first context boundary only said whether a cell could process a context.
Boundary decisions now also carry the Systemform room identity behind that
context, which makes later logging, governance, and operator inspection easier
without changing enforcement behavior.

## Context Boundary Decision Logging Preview

The system gained:

- `ContextBoundaryDecisionLogger`
- `context-boundary-check` CLI command
- Optional `--log` persistence through the decision log
- Tests for conversion, preview output, opt-in logging, and missing cells

Why it mattered:

Operators can now preview a cell/context boundary decision and choose whether to
persist it. This keeps the default path read-only while giving governance work a
durable trace shape before automatic orchestration logging is considered.

## Context Boundary Decision Inspection

The system gained:

- `context-boundary-list` CLI command
- Filters for cell, context, room, and allowed status
- Tests for empty output, list output, filters, and read-only behavior

Why it mattered:

Persisted boundary decisions now have a focused inspection path instead of
being buried inside the general decision log. This keeps operator workflows
simple while leaving aggregation, exports, and dashboards for later.

## Guard Families Minimal

The system gained:

- `family` on guard pipeline results
- `family` on ordered guard trace steps
- Stable contract-validation families for actor, contract, room scope,
  capability, permission, resource, and approval outcomes
- Runtime preview and governance trace assertions for family propagation

Why it mattered:

Guard output can now be scanned by policy family without parsing individual
reason strings. This keeps the existing allow, escalate, and block behavior
unchanged while giving later operator inspection a cleaner shape.

## Guard Family Decision Log Surface

The system gained:

- `guard-decision-list` CLI command
- Filters for final guard decision and decision family
- Final family in governance decision record details
- Fallback family extraction from existing trace details

Why it mattered:

Logged guard decisions now have a focused operator view that can answer
"which family caused this?" without digging through serialized traces. This
keeps the durable decision log schema unchanged while making guard behavior
easier to inspect after demo or orchestrator runs.

## Roadmap Structure

The project gained:

- Architecture-track grouping in `BUILD_PLAN.md`
- Explicit ordering rationale for runtime, inspection, governance, and meaning
- Later tracks for workers, resource economy, federation, controlled evolution,
  and product surfaces

Why it mattered:

The checkpoint list had become accurate but hard to scan. Grouping it into
tracks preserves the small-test discipline while restoring the larger map of
what PiGenus is becoming and why the conservative order matters.

## GENUS Philosophy

The project gained:

- `docs/GENUS_PHILOSOPHY.md`
- A short statement of what GENUS is and is not
- Explicit principles for cells, meaning, control, evolution, and governance
- README reference to the philosophy document

Why it mattered:

The architecture now has enough internal shape that the "why" needs its own
home. Keeping philosophy separate from the build plan lets the plan describe
how PiGenus is built while the philosophy explains why it grows conservatively.

## Release Semantics

The project gained:

- Release arc definitions for `0.1.x` through `1.0`
- `0.2.x` documented as the kernel completion arc
- `pigenus-v0.3.0-governed-runtime` documented as the planned semantic cut
- A distinction between small checkpoint tags and larger release arcs

Why it mattered:

The `0.2.x` line had become a long sequence of useful checkpoints rather than
a clean semantic release scale. Naming the arcs now avoids pretending that
`0.2.35` and later tags are ordinary patch releases while preserving the
existing checkpoint history.

## Context Stack Ontology

The system gained:

- `ContextFrameType`
- `ContextFrame`
- `ContextStack`
- `docs/CONTEXT_MODEL.md`
- Tests for frame serialization, conflict rejection, stack composition, and
  duplicate frame handling

Why it mattered:

Rooms remain the existing governance, protection, and memory boundary, but they
no longer need to carry every contextual meaning. Context frames now describe
formal conditions around an action, and context stacks can later become the
task-level operating envelope without replacing actors, cells, organs, agents,
characters, or rooms.

## Guard Family Summary Minimal

The system gained:

- `guard-decision-summary` CLI command
- Summary counts grouped by final guard decision and family
- Filters for final decision and family before summarization
- Tests for output, filters, empty databases, and read-only behavior

Why it mattered:

Guard families are now inspectable both as individual records and as a small
operator summary. This improves accountability before scale without adding
analytics storage, migrations, dashboards, or new enforcement policy.

## v0.3 Governed Runtime Readiness

The project gained:

- `docs/V0_3_GOVERNED_RUNTIME_READINESS.md`
- A readiness definition for `pigenus-v0.3.0-governed-runtime`
- Explicit remaining work before the v0.3 tag
- Out-of-scope boundaries for workers, LLMs, dashboards, federation, and evolution
- Migration and ContextStack runtime rules before v0.3

Why it mattered:

The kernel completion arc is close enough to a semantic release that the next
step should be verification, not more feature drift. The readiness document
turns v0.3 into a governed release cut with explicit non-goals.

## v0.3 Governed Runtime

The project reached:

- `pigenus-v0.3.0-governed-runtime`
- local governed runtime semantics
- Meaning Store and meaning inspection
- room/context governance and additive ContextStack ontology
- guard pipeline, guard families, decision logging, and guard summaries
- selective hard-block enforcement and human approval stub records
- operator inspection, health checks, and local snapshot backups

Why it mattered:

This release marks the shift from a long `0.2.x` kernel completion arc into a
named governed runtime baseline. It is not a worker, federation, LLM, dashboard,
or evolution release. It is a boring reliability cut for the local GENUS core.

## Liquid Runtime Concept

The project gained:

- `docs/LIQUID_RUNTIME.md`
- A future concept for dynamic form proposals
- The rule that no proposed form becomes real without validation, guard
  decision, and trace
- Explicit non-goals around self-modification, arbitrary agent spawning, and
  bypassing rooms, contracts, or guards

Why it mattered:

GENUS may eventually need more flexible task-specific runtime shapes, but that
flexibility must sit above the v0.3 governed runtime instead of dissolving it.
Documenting the concept now keeps the idea available without turning it into an
immediate implementation commitment.

## Worker Runtime Concept

The project gained:

- `docs/WORKER_RUNTIME.md`
- A distinction between workers, cells, organs, and agents
- Worker Runtime as a future execution-host layer, not a source of intelligence
- A local-first and inspection-first implementation direction

Why it mattered:

Worker Runtime is likely the next large architecture pressure after v0.3. The
concept needs clean language before implementation so machines, capabilities,
compositions, and goal-directed actors do not collapse into one vague "agent"
idea.

## Resource Economy Concept

The project gained:

- `docs/RESOURCE_ECONOMY.md`
- Resource Economy as accounting before markets
- Room-scoped resource thinking
- Worker/resource relationship boundaries
- Attention, privacy, money, risk, and human review as possible resources

Why it mattered:

Workers and liquid runtime shapes will create pressure to spend compute,
attention, privacy, and money. Documenting Resource Economy now keeps the first
step boring: grants, usage records, and summaries before pricing, credits, or
market allocation.

## Human Governance Concept

The project gained:

- `docs/HUMAN_GOVERNANCE.md`
- Review, escalation, and approval distinctions
- Room-aware approval authority
- Required approval evidence
- Human approval as governance semantics before UI

Why it mattered:

PiGenus already has approval stub records, but future workers, resources,
liquid runtime shapes, federation, and evolution need stronger approval
semantics. Human Governance makes approval accountable before it becomes a
button.

## Evolution Sandbox Concept

The project gained:

- `docs/EVOLUTION_SANDBOX.md`
- Mutation as proposal, not activation
- Shadow mode and explicit fitness comparison
- Fossil and rollback requirements
- Human approval before activation

Why it mattered:

Evolution is the most dangerous later architecture track. Documenting it now
keeps adaptation inside governance: proposals, traces, tests, approval, fossils,
and rollback before anything becomes active behavior.

## GitHub Idea Harvest

The project gained:

- `docs/GITHUB_IDEA_HARVEST.md`
- A source list for older WoltLab51 GENUS/PiGenus repositories
- A rule that ideas may be harvested but architectures are not merged directly
- Initial mappings from `Genus`, `UrPi`, and `PiGenus_mistral` into future
  architecture tracks

Why it mattered:

GENUS has useful history outside the current repository. Capturing that history
keeps old ideas from being forgotten while protecting the governed runtime from
unplanned feature import, old architecture drift, or code copied around the
current contracts, guards, rooms, approvals, traces, and tests.

## Internal Communication Concept

The project gained:

- `docs/INTERNAL_COMMUNICATION.md`
- Internal communication as governed meaning flow
- A boundary between events, meaning objects, governance decisions, and audit
  logs
- A rule against free-form prompt buses between runtime components
- Future communication fields documented as target concepts, not current
  schema promises

Why it mattered:

The current runtime already has event flow, meaning objects, rooms, guards, and
decision traces, but the communication concept was distributed across those
pieces. Naming it explicitly protects future workers, organs, agents,
characters, and LLM gateways from bypassing the governed runtime through loose
text or hidden direct calls.

## GENUS Vocabulary

The project gained:

- `docs/GENUS_VOCABULARY.md`
- A central glossary for implemented, documented, planned, and conceptual terms
- Explicit boundaries for MeaningObject, Event, DecisionTrace, Cell, Organ,
  Agent, Character, Worker, LLMGateway, EvolutionSandbox, and related terms
- A rule that vocabulary can be valid before it is implemented

Why it mattered:

GENUS now has enough ontology that future builders need a shared dictionary.
The glossary prevents planned concepts from being mistaken for missing ideas,
while also preventing premature schema expansion just because a term exists in
the architecture vocabulary.

## Documentation Maintenance

The project gained:

- `docs/DOCUMENTATION_MAINTENANCE.md`
- A required documentation check for non-trivial changes
- Update triggers for vocabulary, decisions, status, changelog, build plan, and
  architecture history
- A minimal commit checklist for keeping docs current without over-updating

Why it mattered:

The project now has enough architecture memory that stale documentation would
become a safety problem. Documentation maintenance turns project docs into a
deliberate part of checkpoint quality instead of relying on memory or cleanup
later.

## Architecture Contract

The project gained:

- `docs/ARCHITECTURE_CONTRACT.md`
- Non-breaking rules for storage, events, meaning, rooms, contexts, contracts,
  guards, approval, workers, LLMs, evolution, and documentation
- A contribution checklist for non-trivial future changes
- The rule that capability must not bypass governance

Why it mattered:

The post-v0.3 phase will add pressure from workers, agents, LLM gateways,
product surfaces, federation, and eventually controlled evolution. The
architecture contract protects the governed runtime baseline so new capability
must grow through contracts, meaning, rooms, guards, decisions, traces, and
tests instead of around them.

## Documentation Index

The project gained:

- `docs/INDEX.md`
- A recommended reading order for new contributors and future Codex sessions
- A grouped map of core architecture, governance, operations, and future
  concept documents
- A before-building checklist that points to status, build plan, vocabulary,
  architecture contract, and documentation maintenance

Why it mattered:

The project now has enough documentation that discoverability matters. The
index turns the documentation set into a navigable system instead of a folder
of individually useful files.

## Threat Model

The project gained:

- `docs/THREAT_MODEL.md`
- A risk map for the current governed runtime and future architecture tracks
- Threats for meaning injection, room bypass, capability escalation, stale
  memory, approval spoofing, log gaps, rogue workers, unsafe LLM trust, silent
  mutation, resource abuse, and documentation drift
- A review checklist for future capability work

Why it mattered:

The next powerful surfaces will increase risk faster than the local v0.3 kernel
does. Threat modeling now keeps future workers, LLM gateways, federation,
resource policy, product surfaces, and evolution behind the same governance
posture that made the runtime inspectable in the first place.

## Data Lifecycle

The project gained:

- `docs/DATA_LIFECYCLE.md`
- A map for Event, MeaningObject, MemoryObject, GovernanceDecision,
  DecisionTrace, EventLog, AuditLog, Fossil, and future MutationProposal
- A lifecycle question checklist for future data objects
- Explicit gaps that are future work rather than v0.3 bugs

Why it mattered:

The runtime already persists events, memory, meaning, decisions, and audit
records. The lifecycle map makes their roles and aging behavior explicit before
more stores, workers, LLM outputs, and evolution proposals add new state.

## Full Check

The project gained:

- `docs/FULL_CHECK.md`
- Check levels for small documentation, concept/architecture, runtime, and
  release/checkpoint changes
- A bounded ChatGPT review role for conceptual review
- PR and merge review questions

Why it mattered:

PiGenus now has enough governance, documentation, and future architecture
surface that quality checks need to scale with risk. The full check makes small
work lightweight while keeping runtime, release, and baseline changes strongly
verified.

## v0.3.1 Architecture Control

The project reached:

- `pigenus-v0.3.1-architecture-control`
- a documentation index
- a GENUS vocabulary and ontology-control baseline
- an architecture contract
- internal communication, data lifecycle, and threat model documents
- documentation maintenance and full-check workflow
- explicit ChatGPT review boundaries

Why it mattered:

After `pigenus-v0.3.0-governed-runtime`, the project needed a stable control
layer before returning to runtime work. This checkpoint freezes the
architecture memory and review process so future verification, workers, LLM
gateways, federation, product surfaces, and evolution have to pass through the
same vocabulary, lifecycle, threat, and governance boundaries.

## Runtime Verification Migration Hardening

The project gained:

- `docs/RUNTIME_VERIFICATION.md`
- a first post-v0.3.1 runtime verification pass
- exclusive pending migration application inside `MigrationRunner.apply()`
- documentation of a concurrent migration version race found during CLI
  verification

Why it mattered:

The verification pass exercised real operator commands against the local
runtime and found a race in migration application. Hardening the migration
apply step keeps initialization idempotent even when multiple runtime commands
start near the same time.

## v0.3.2 Runtime Verification

The project reached:

- `pigenus-v0.3.2-post-release-runtime-verification`
- migration apply hardening
- documented runtime verification
- health and runtime overview verification
- backup integrity verification
- read-only inspection verification with unchanged database hash
- full test suite verification with 187 passing tests

Why it mattered:

This checkpoint proved the post-v0.3.1 runtime remained inspectable and stable
after the architecture-control phase. It closed the verification loop before
the project moves toward Worker Runtime preparation.

## Worker Runtime Readiness

The project gained:

- `docs/WORKER_RUNTIME_READINESS.md`
- a v0.4 readiness boundary for worker identity, heartbeat, capability profile,
  cost profile, privacy profile, and failure semantics
- an explicit rule that registration and inspection precede scheduling
- an explicit rule that scheduling precedes execution

Why it matters:

Worker Runtime is the first post-v0.3 arc that can move governed work toward
different machines, processes, or providers. Defining readiness first keeps
workers accountable as execution hosts and prevents worker implementation from
becoming remote execution, LLM routing, federation, or autonomous agent behavior
by accident.

## Multimodal Systemform Concept

The project gained:

- `docs/MULTIMODAL_SYSTEMFORM.md`
- a future boundary for language, meaning graphs, runtime state fields, visual
  or spatial representations, embeddings, and action traces
- an explicit rule that LLMs are governed capabilities, not the GENUS kernel
- an explicit rule that multimodal content must preserve provenance, room,
  sensitivity, confidence or truth status, guardability, and inspection

Why it matters:

GENUS should not accidentally become text-only just because early runtime work
is textual and structured. The multimodal concept keeps the long-term direction
open while protecting the governed runtime from opaque model state, loose
prompt communication, or untraceable latent behavior.

## Worker Model-Only Readiness

The system gained:

- `WorkerType`
- `WorkerStatus`
- `WorkerProfile`
- `WorkerHeartbeat`
- tests for profile serialization, liveness records, deterministic list
  de-duplication, and required identity fields

Why it mattered:

Worker Runtime now has its first code shape without adding storage, CLI,
scheduling, routing, provider calls, or execution. This keeps the v0.4 arc
inside the same additive discipline used for Systemform hardening: define and
test the ontology before it can affect runtime behavior.

## Worker Registry Storage-Free

The system gained:

- `WorkerRegistry`
- registration and lookup for `WorkerProfile`
- latest-heartbeat tracking for known workers
- deterministic profile and heartbeat listing
- filters for worker status, worker type, and heartbeat status
- `is_considerable()` for active profile plus active heartbeat checks

Why it mattered:

Worker Runtime now has an inspectable in-memory shape before storage or CLI
exists. This keeps worker identity and liveness testable without introducing
database migrations, scheduling decisions, provider routing, or execution.

## Worker Inspection Read-Only

The system gained:

- `WorkerInspection`
- `WorkerInspectionService`
- read-only worker rows combining profile and heartbeat state
- filters for profile status, worker type, and considerable state
- show behavior for one known worker
- tests for missing heartbeat handling

Why it mattered:

Worker Runtime now has an operator-facing inspection shape before CLI or
storage exists. This lets the project design future `worker-list` and
`worker-show` commands around tested read-only semantics instead of wiring a
command directly to improvised state.

## Data Architecture And Summary Cleanup

The project gained:

- `docs/DATA_ARCHITECTURE.md`
- `docs/GENUS_ARCHITECTURE_SUMMARY.md`
- an explicit distinction between data lifecycle, migration policy, and storage
  architecture
- a cleaned Build Plan current step before worker persistence or CLI work

Why it mattered:

The project already had lifecycle and migration documents, but performance and
database-design questions needed a separate storage-role map. This cleanup
prevents duplicate documents while making the next worker source-of-truth
decision easier to make.

## Worker Source Of Truth Policy

The project decided:

- durable worker profiles belong in SQLite
- current worker heartbeat state belongs in SQLite-backed storage
- heartbeat history may become append-only/audit-style later
- local worker files are bootstrap/import only
- discovery waits for federation, trust, signatures, remote rooms, and privacy
  boundaries

Why it mattered:

Worker CLI and persistence should not read from invented demo workers, hidden
defaults, local config as truth, or network scans. Naming SQLite as the worker
source of truth gives the next migration a clear target while keeping remote
execution and discovery out of scope.

## Worker Store Minimal

The system gained:

- migration `0005_worker_store`
- `worker_profiles`
- `worker_heartbeats`
- `WorkerRepository`
- tests for profile persistence, profile filters, current heartbeat freshness,
  heartbeat filters, and unknown-worker heartbeat rejection
- health-check coverage for worker store tables

Why it mattered:

Worker Runtime now has durable local truth for known execution hosts and their
current liveness without adding CLI, scheduling, routing, discovery, heartbeat
history, provider calls, or execution. This keeps worker persistence aligned
with the v0.3 governed runtime contract.

## Worker CLI Read-Only

The system gained:

- `worker-list`
- `worker-show`
- filters for worker status, type, owner, home room, and considerable state
- stable JSON detail output for one worker
- tests proving list/show behavior and read-only inspection

Why it mattered:

Worker Runtime now has a safe operator surface for known execution hosts. The
commands read from the SQLite Worker Store and expose current heartbeat state
without creating workers, recording heartbeats, scheduling work, discovering
remote workers, or executing tasks.

## Worker Scheduling Preview

The system gained:

- `WorkerSchedulingRequest`
- `WorkerSchedulingPreview`
- `WorkerSchedulingCandidate`
- `WorkerSchedulingPreviewService`
- suitability reasons for missing capability, missing runtime, missing active
  heartbeat/profile, network unavailability, and sensitivity limits
- tests proving preview ordering, explanations, and no registry mutation

Why it mattered:

GENUS can now ask "which worker could host this?" without scheduling anything.
This creates the first explainable placement layer while preserving the strict
boundary: preview is not assignment, routing, provider call, discovery, or
execution.

## Worker Scheduling Preview Governance Conversion

The system gained:

- conversion from `WorkerSchedulingPreview` to `GovernanceDecision`
- allow decisions when candidate workers are available
- block decisions when no suitable worker exists
- worker-scheduling family details
- request metadata, candidate details, recommended worker ID, and trace-like
  candidate steps
- tests proving decision-log compatibility without persistence

Why it mattered:

Worker placement reasoning now has the same governance shape as other policy
surfaces. The conversion is intentionally storage-free, so the runtime can
review and test scheduling reasoning before deciding whether previews should be
logged.

## Worker Scheduling Preview Logging

The system gained:

- `WorkerSchedulingPreviewLogger`
- opt-in persistence through the existing decision log
- source `worker_scheduling_preview` for logged preview decisions
- allow/block preview logging tests
- proof that previewing remains non-persistent unless the logger is called

Why it mattered:

Worker placement reasoning can now be made durable when an operator or future
runtime surface explicitly asks for it. The logger does not introduce
scheduling tables, assignments, reservations, provider calls, routing, or
execution; it only preserves the governance-shaped explanation.

## Worker Scheduling Preview CLI

The system gained:

- read-only `worker-scheduling-preview`
- capability, runtime, sensitivity, and network requirement inputs
- printed preview decision, reason, recommended worker, and candidate reasons
- tests for empty databases, constrained previews, and unchanged decision/audit
  logs

Why it mattered:

Operators can now inspect worker placement reasoning from the command line
without creating a scheduling assignment or durable decision. The command reads
from the SQLite Worker Store, builds only temporary in-memory preview state, and
does not expose preview logging yet.

## Worker Scheduling Preview CLI Logging

The system gained:

- `worker-scheduling-preview --log`
- `--actor`, `--room`, and optional `--event-id` metadata for logged previews
- decision-log persistence through `WorkerSchedulingPreviewLogger`
- tests proving no logging without the flag and exactly one governance decision
  with the flag

Why it mattered:

The operator can now turn a placement preview into durable governance evidence
without creating scheduling assignments or execution records. This keeps the
transition from inspection to accountability explicit and reviewable.

## Worker Execution Preflight

The system gained:

- `WorkerExecutionPreflightRequest`
- `WorkerExecutionPreflightCheck`
- `WorkerExecutionPreflightResult`
- `WorkerExecutionPreflightService`
- ordered checks for known worker, considerable state, capability, runtime,
  sensitivity, and network access
- conversion to a log-compatible `GovernanceDecision`

Why it mattered:

PiGenus can now ask whether one specific worker appears eligible for a proposed
execution before assignment or execution exists. This makes execution
eligibility governable without adding scheduling tables, reservations, provider
routing, or task execution.

## Worker Execution Preflight CLI

The system gained:

- read-only `worker-execution-preflight`
- worker ID, capability, runtime, sensitivity, and network requirement inputs
- printed allow/block decision and ordered preflight checks
- tests proving no decision or audit persistence

Why it mattered:

Operators can now inspect execution eligibility for one worker from the command
line before logging, assignment, routing, or execution exists. This gives the
Worker Runtime a visible safety check without making workers active executors.

## GitHub Actions CI

The system gained:

- `.github/workflows/ci.yml`
- CI runs on push and pull requests to `main`
- manual `workflow_dispatch`
- Python 3.12 setup
- editable install with development dependencies
- `python -m pytest`

Why it mattered:

The test suite is now large enough that local verification should not be the
only safety signal. CI gives pushed changes and future pull requests an
external repeatable test run without changing runtime behavior.

## Architecture Fitness Review

The project gained:

- `docs/ARCHITECTURE_FITNESS_REVIEW.md`
- measured CLI and repository hotspots
- a responsibility map for `pigenus/cli/main.py` and
  `pigenus/storage/repositories.py`
- a test-coupling review for CLI subprocess, SQLite, audit, decision, and
  worker-store interactions
- a recommended first structural cut: worker CLI command module extraction

Why it mattered:

PiGenus has reached the point where the next quality improvement is not more
policy, more worker behavior, or more documentation volume. The next risk is
operator-surface coordination accumulating inside one CLI file. The fitness
review lets the project move toward cell-like module boundaries without
turning that into dynamic runtime routing or a risky rewrite.

## Worker CLI Module Boundary

The system gained:

- `pigenus/cli/worker_commands.py`
- worker CLI parser registration outside `pigenus/cli/main.py`
- worker-list, worker-show, worker-scheduling-preview, and
  worker-execution-preflight command handling outside the main CLI entry point
- preservation of existing worker CLI behavior, output, and side-effect rules

Why it mattered:

This is the first static module boundary produced from the architecture fitness
review. It moves PiGenus a little closer to cell-like structure while staying
fully deterministic: no dynamic routing, no new commands, no worker execution,
and no storage changes.

## Worker Execution Preflight Logging

The system gained:

- `WorkerExecutionPreflightLogger`
- explicit `worker-execution-preflight --log`
- actor, room, and optional event metadata for logged preflights
- tests proving allow logging, block logging, and no implicit persistence

Why it mattered:

Execution preflight is the closest current Worker Runtime surface to future
execution. Making it optionally durable creates governance evidence before
assignments or execution exist, while the explicit `--log` boundary preserves
read-only inspection as the default.

## Worker Assignment Model Shape

The system gained:

- `WorkerAssignment`
- `WorkerAssignmentStatus`
- model tests proving governance evidence is required
- model tests proving assignment does not contain execution result fields

Why it mattered:

Worker assignment is the first future step where placement can become durable
runtime intent. Defining the shape before storage or CLI creation keeps the
worker arc governed: assignment must be downstream of evidence, and assignment
still remains separate from execution.

## GENUS And PiGenus Naming Boundary

The project clarified:

- GENUS is the broader governed systemform and architecture
- PiGenus is the local Python reference runtime distribution for GENUS
- PiGenus is edge-friendly but not Raspberry-Pi-only
- the `pigenus` package, repository history, CLI, migrations, and checkpoint
  names remain stable for the current arc

Why it mattered:

The project is now clearly building GENUS while preserving PiGenus as the
working runtime implementation. This avoids a risky rename while keeping the
architecture open for other device classes and future runtime distributions.

## Cellular Systemform

The project gained:

- `docs/CELLULAR_SYSTEMFORM.md`
- a formal definition of GENUS cells as governed capability units
- Cell DNA, membrane, nucleus, metabolism, organ, immune-system, and
  nervous-system framing
- a static cell boundary rule for CLI and service slicing
- a 250-line fitness signal for operator command modules

Why it mattered:

The cell idea is now a first-class architecture philosophy instead of only a
metaphor. This lets PiGenus keep refactoring toward cell-like structure without
turning every function into a cell or introducing dynamic runtime routing too
early.

## Stable Core And Variable Runtime Shapes

The project clarified:

- the Systemform Kernel remains stable across future runtime forms
- RuntimeShape is a checked composition, not spontaneous dynamic behavior
- DeploymentProfile, DeviceProfile, ShapePreview, ShapeValidator, and
  ShapeTrace are documented/planned terms
- shape activation remains out of scope until preview, validation, guard
  decision, trace, inspection, and tests exist

Why it mattered:

GENUS can move toward device- and function-specific forms without losing kernel
accountability. This connects Cellular Systemform, Liquid Runtime, Worker
Runtime, and the Architecture Convergence Review into one map instead of
letting each concept drift independently.

## Philosophy Alignment Review Protocol

The project gained:

- `docs/PHILOSOPHY_ALIGNMENT_REVIEW_PROTOCOL.md`
- a full review template for non-trivial changes
- quick-review questions for smaller architecture checks
- fit ratings for philosophy, governance, cellular maturity, and RuntimeShape
  boundaries
- risk checks for monolith drift, documentation drift, premature dynamics, and
  overengineering

Why it mattered:

GENUS now has a repeatable way to test whether future changes still match its
philosophy. This keeps the growing architecture map useful without turning every
change into either intuition-only work or excessive documentation ceremony.

## Meaning CLI Module Boundary

The system gained:

- `pigenus/cli/meaning_commands.py`
- meaning-list, meaning-show, and meaning-ingest-memory parser registration
  outside `pigenus/cli/main.py`
- meaning command handling outside the main CLI entry point
- preservation of existing meaning CLI behavior, output, and side-effect rules

Why it mattered:

This was the first code move selected through the Philosophy Alignment Review
Protocol. It reduced operator-surface monolith risk without changing meaning
storage, ingestion semantics, governed paths, assignments, routing, or
execution.

## Worker Assignment Store

The system gained:

- migration `0006_worker_assignments`
- `worker_assignments` local SQLite table
- `WorkerAssignmentRepository`
- tests for roundtrip, filters, unknown-worker rejection, and
  missing-governance-evidence rejection

Why it mattered:

WorkerAssignment moved from model-only shape to minimal governed persistence.
The store captures assignment intent only after worker and governance decision
evidence already exist, keeping assignment separate from scheduling
enforcement, reservation, provider routing, and execution.

## Worker Storage Repository Boundary

The system gained:

- `pigenus/storage/worker_repositories.py`
- `WorkerRepository` and `WorkerAssignmentRepository` outside the shared
  repository module
- preserved compatibility through `pigenus.storage.repositories`

Why it mattered:

The WorkerAssignment Store was the right feature boundary, but it increased
storage-module density. Splitting worker repositories into their own storage
domain keeps Worker Runtime growth reviewable before assignment inspection,
scheduling enforcement, routing, or execution appears.

## Worker Assignment Inspection CLI

The system gained:

- `pigenus/cli/worker_assignment_commands.py`
- `worker-assignment-list`
- filters by worker, status, room, capability, and governance decision
- read-only tests proving assignment inspection does not create decisions or
  audit logs

Why it mattered:

Assignment intent became inspectable before assignment creation, scheduling
enforcement, routing, provider calls, or execution. Keeping this command in its
own static CLI boundary avoids growing the existing worker command module while
preserving the current no-execution Worker Runtime boundary.

## Worker Assignment Semantics

The system gained:

- `docs/WORKER_ASSIGNMENT_SEMANTICS.md`
- a matching-evidence rule for assignment creation
- the requirement that only `worker_execution_preflight` allow decisions may
  create assignment intent
- the rule that initial assignment creation may create only `pending` records

Why it mattered:

WorkerAssignment moved from inspectable storage toward a future creation path
without opening that path yet. The semantics now make clear that assignment is
durable governed intent, not scheduling enforcement, reservation, routing, or
execution.

## Worker Assignment Validator

The system gained:

- `pigenus/core/worker_assignment_validator.py`
- read-only validation of matching preflight allow evidence
- tests for allow, block, scheduling-preview evidence, worker mismatch,
  capability mismatch, room mismatch, non-pending status, and missing evidence

Why it mattered:

The validator makes assignment creation semantics executable without adding a
creation command. It keeps semantic checks outside the repository and preserves
the no-scheduling, no-routing, no-execution Worker Runtime boundary.

## Worker Assignment Creation Audit

The system gained:

- a documented audit requirement for future successful assignment creation
- the `worker_assignment_created` audit action boundary
- D-094 recording that creation must not create decisions, routing, or execution

Why it mattered:

Assignment creation will be the first durable operational step after validation.
Requiring audit before adding a creator keeps that step accountable while
preserving the distinction between governance evidence and operational action.

## Worker Assignment Creator

The system gained:

- `pigenus/core/worker_assignment_creator.py`
- service-only validated assignment creation
- `worker_assignment_created` audit logging on success
- tests proving success writes assignment plus audit, invalid input writes
  neither, and no extra governance decision is created

Why it mattered:

Assignment creation became executable but not operator-facing. The service
keeps the future CLI small while preserving the current no-scheduling,
no-routing, no-execution Worker Runtime boundary.

## Worker Assignment Create CLI

The system gained:

- `worker-assignment-create`
- CLI creation of pending worker assignment intent through
  `WorkerAssignmentCreator`
- validation-failure output with no assignment or audit writes
- tests proving successful CLI creation writes one assignment and one audit row
  without creating extra decisions

Why it mattered:

Assignment creation became operator-facing without moving policy into CLI code.
The command remains a thin wrapper around the creator service and still does
not activate assignment status, schedule, route, call providers, or execute.

## Worker Assignment Status Transition Semantics

The system gained:

- explicit allowed WorkerAssignment status transitions
- terminal-state rules for `rejected`, `cancelled`, and `expired`
- a future `worker_assignment_status_changed` audit boundary
- D-097 recording that status transitions are intent lifecycle, not execution
  proof

Why it mattered:

Assignment creation now exists, so the next risk is accidental activation.
Documenting the status graph before adding validators, services, or commands
keeps `assigned` separate from execution and preserves the Worker Runtime
boundary.

## Worker Assignment Status Transition Validator

The system gained:

- `pigenus/core/worker_assignment_status_transition_validator.py`
- read-only checks for allowed WorkerAssignment status transitions
- stable reason codes for valid edges, no-ops, terminal reactivation,
  undocumented edges, and unknown targets
- tests proving the validator does not mutate assignment state

Why it mattered:

The documented status graph became executable without adding persistence,
audit writing, transition commands, routing, or execution. This keeps the next
Worker Runtime step service-shaped and testable before any operator command can
change durable assignment status.

## Worker Assignment Status Transition Service

The system gained:

- `pigenus/core/worker_assignment_status_transition.py`
- `WorkerAssignmentRepository.update`
- service-only validated assignment status updates
- `worker_assignment_status_changed` audit logging on success
- tests proving success writes one status update plus audit, invalid input
  writes neither, missing assignments are rejected cleanly, and no governance
  decision is created

Why it mattered:

WorkerAssignment lifecycle can now move under a service boundary without
exposing operator commands or execution. This keeps status changes auditable
while preserving the line between assignment intent, scheduling, routing, and
actual work.

## Worker Assignment Transition CLI

The system gained:

- `worker-assignment-transition`
- CLI status updates through `WorkerAssignmentStatusTransitionService`
- tests proving successful transition writes one assignment update and audit
  row without creating decisions
- tests proving invalid and missing assignments do not write audits or status
  changes

Why it mattered:

Assignment lifecycle became operator-facing without moving transition policy
into CLI code. The command is still only lifecycle status management; it does
not schedule, reserve, route, call providers, or execute work.

## Worker Scheduling Enforcement Boundary

The system gained:

- `docs/WORKER_SCHEDULING_ENFORCEMENT.md`
- D-102 recording that `assigned` is necessary but not sufficient for future
  scheduling consideration
- explicit separation between assignment lifecycle, scheduling enforcement,
  reservation, routing, provider calls, and execution

Why it mattered:

After `worker-assignment-transition`, assignment status became operator-facing.
The scheduling enforcement boundary prevents `assigned` from becoming hidden
runtime permission and keeps the next Worker Runtime step read-only before any
real scheduling or execution behavior exists.

## GENUS Canonical Systemform

The project gained:

- `docs/GENUS_CANONICAL_SYSTEMFORM.md`
- a canonical bio-cybernetic operating systemform orientation
- a conflict rule for older blueprints, sketches, and concept documents
- explicit cell maturity language from MicroCell through RuntimeCell
- physiology language for nervous system, immune system, metabolism,
  homeostasis, reflexes, kill switches, quarantine, apoptosis, regeneration,
  ecology, and controlled evolution
- a high-risk execution rule requiring room policy, budgets, health,
  contracts, guards, reflexes, kill switch, audit, approval thresholds,
  recovery path, and shadow/dry-run evidence before live behavior

Why it mattered:

GENUS now has one alignment source above the many useful topic documents. This
keeps older material available as source memory while preventing agent-first,
LLM-first, dashboard-first, hidden prompt-bus, premature worker-execution, or
mutation-as-activation directions from quietly driving implementation.

## GENUS Metabolic State Graph

The project gained:

- `docs/GENUS_METABOLIC_STATE_GRAPH.md`
- a graph-shaped diagnostic view for cells, tissues, organs, organisms,
  habitats, workers, rooms, guards, resources, meaning, decisions, lifecycle,
  reflexes, recovery, mutation proposals, and fossils
- node and edge vocabulary for activation, inhibition, dependency, governance,
  resource use, lifecycle transitions, quarantine, recovery, evolution, and
  fossilization
- a staged future path from concept-only to derived in-memory projection,
  read-only CLI/export, optional materialized view, and optional external graph
  database only if needed
- a source-of-truth rule preserving SQLite and current runtime stores as the
  canonical state

Why it mattered:

The canonical systemform made GENUS bio-cybernetic. The Metabolic State Graph
adds the relational lens: not just what contains what, but what consumes,
produces, blocks, activates, governs, recovers, and stresses what. It gives
future diagnosis and planning a precise map without introducing graph storage,
runtime routing, worker execution, or a second truth source.

## Canonical Implementation Plan

The project gained:

- `docs/CANONICAL_IMPLEMENTATION_PLAN.md`
- a practical bridge from canonical systemform and metabolic graph concepts to
  next build cycles
- future arcs for cellular inventory, Cell-DNA protocol, Worker Runtime
  consolidation, graph projection preview, resource/homeostasis/reflex
  foundations, RuntimeCell/organ preparation, habitat/device profiles, and
  high-risk execution readiness as concept-only
- an initial cellular inventory classifying current runtime and operator
  surfaces by maturity, reads, writes, allowed effects, forbidden effects, and
  next possible maturity

Why it mattered:

The canonical documents define the organism. The implementation plan keeps the
next work practical: classify what already exists, add Cell-DNA discipline to
new responsible capabilities, and consolidate Worker Runtime before any
execution, graph implementation, trading behavior, dynamic cells, or autonomous
organisms are considered.

## Cellular Inventory Review

The project gained:

- `docs/CELLULAR_INVENTORY_REVIEW.md`
- code-checked validation of the initial cellular inventory
- explicit distinction between current services, storage boundaries, operator
  surfaces, tissues, GovernedCell candidates, and later RuntimeCells/organs
- first recommended Cell-DNA candidates, starting with
  `WorkerAssignmentValidator`
- a next-step recommendation to define Cell-DNA before adding more Worker
  Runtime behavior

Why it mattered:

The canonical systemform now has a practical checkpoint against the actual
codebase. GENUS stays cell-first, but PiGenus does not jump into RuntimeCell
ceremony, scheduling enforcement, worker execution, graph implementation, or
autonomous organism behavior before the membranes are clear.
