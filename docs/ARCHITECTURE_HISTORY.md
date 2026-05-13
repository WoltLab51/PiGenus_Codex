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
