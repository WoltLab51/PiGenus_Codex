# PiGenus Decisions

This file captures durable architectural decisions. Keep entries short and
append-only unless a later decision explicitly supersedes an earlier one.

## D-001: Keep The Core Small

Decision:

PiGenus Core stays local, structured, and deterministic where possible.

Reason:

The core protects identity, memory, permissions, auditability, and context
boundaries. These are stability concerns, not places for early LLM magic.

## D-002: Durable Memory Belongs To The Core

Decision:

Cells may create `MemoryProposal` events, but only guarded proposals can become
persisted `MemoryObject` rows.

Reason:

This prevents cells from forming conflicting private truths. Cell-local state is
allowed, but it is operational state, not canonical memory.

## D-003: Guards Are Blocking Components

Decision:

Guard decisions are first-class events. A denied guard decision prevents the
downstream write or action.

Reason:

Safety cannot be advisory only. The runtime must be able to say no and leave an
audit trail explaining why.

## D-004: Context Boundaries Precede Memory Lifecycle

Decision:

Context validation and cell `allowed_contexts` are implemented before memory
aging, expiry, and review.

Reason:

Memory lifecycle rules are unsafe if the system does not first know which room a
memory belongs to.

## D-005: Checkpoints Must Update Project Control Files

Decision:

Stable phase commits update `CHANGELOG.md`, `BUILD_PLAN.md`, `STATUS.md`, and
the docs under `docs/` when architecture or durable decisions change.

Reason:

PiGenus should preserve its own development lineage. Future work should be able
to recover what changed, why it changed, what is stable, and what comes next.

## D-006: Specify Lifecycle Before Implementing It

Decision:

Phase 2 Memory Lifecycle is specified in `docs/PHASE_2_MEMORY_LIFECYCLE.md`
before implementation.

Reason:

Memory aging, expiry, and canonical protection are core trust behavior. The
rules should be explicit before code starts enforcing them.

## D-007: Expiry Changes Status, Not Rows

Decision:

Memory expiry does not delete memory rows. It applies deterministic status
transitions such as `active -> dead` or `dormant -> fossil`.

Reason:

PiGenus needs auditability and historical continuity. Removing memory
automatically would make it harder to explain why the system changed behavior.

## D-008: Inspection Commands Are Read-Only

Decision:

CLI commands that inspect storage, such as `memory-list`, must not mutate
memory, audit logs, or lifecycle state.

Reason:

Operators need safe visibility into PiGenus without accidentally changing the
system by looking at it.

## D-009: Add Migration Policy Before Migration Runner

Decision:

PiGenus documents SQLite migration rules before adding a migration runner.

Reason:

Schema evolution affects stored memory and audit history. The policy should be
clear before automation starts changing local databases.

## D-010: Record Schema Evolution In SQLite

Decision:

PiGenus records applied migrations in `schema_migrations` and routes
`Database.initialize()` through the migration runner.

Reason:

The database should carry its own schema lineage. Future runtime changes should
be explicit, idempotent, and inspectable.

## D-011: Schema Registry Uses Runtime Contracts

Decision:

The schema registry reads from the same event type and required-key constants
used by runtime validation.

Reason:

PiGenus should not maintain a second, drifting description of its own event
contracts.

## D-012: Decision Log Complements Events And Audit

Decision:

Important system decisions are recorded in `decision_logs` in addition to raw
events and audit logs.

Reason:

Events show flow, and audit logs show actions. Decision records make important
outcomes directly queryable and easier to explain.

## D-013: Cell Lifecycle Starts As Observation

Decision:

Cell lifecycle fields are explicit and inspectable, but passive. Phase 2.5
updates `last_used_at` for orchestrated cells and lists cells through a
read-only CLI; it does not mutate fitness or evolve cells.

Reason:

Cells should become observable runtime units before they become adaptive ones.
This preserves deterministic behavior while preparing the core for later
cell-management work.

## D-014: Context Inspection Is Read-Only

Decision:

Known contexts are exposed through a read-only registry and `context-list`.
Optional cell visibility reads an existing database only; it does not create a
missing database just to inspect context boundaries.

Reason:

Context boundaries protect rooms. Operators should be able to inspect those
rooms without changing storage or accidentally initializing runtime state.

## D-015: Permission Inspection Reads Engine Defaults

Decision:

Default permissions are exposed through a read-only registry that reads from
the same `PermissionEngine.default_allowed` mapping used by runtime checks.

Reason:

Permission visibility should not drift from enforcement. Inspection must show
what the core actually allows, without introducing policy editing or a second
permission source.

## D-016: Audit Inspection Is Passive

Decision:

Audit logs can be listed through a read-only CLI with small filters for actor,
action, and context. The inspection path does not modify audit rows or related
runtime storage.

Reason:

Audit exists to explain what happened. Operators need safe visibility into that
record before the system grows export formats, dashboards, or retention policy.

## D-017: Event Inspection Does Not Replay

Decision:

Stored events can be listed and inspected by ID through read-only CLI commands.
Inspection may show payload JSON, but it does not replay, mutate, export, or
reprocess events.

Reason:

Events are the runtime trace. Operators need to see that trace before PiGenus
adds replay or worker behavior, and viewing an event must remain a safe
operation.

## D-018: Runtime Overview Is A Summary, Not A Health Check

Decision:

`runtime-overview` summarizes current storage counts, known contexts, and
default permissions. It does not validate, repair, back up, export, or score
the runtime.

Reason:

Operators need one calm place to see what exists before deeper health checks or
backup workflows arrive. Summary and diagnosis stay separate.

## D-019: Health Check Diagnoses Without Repair

Decision:

`health-check` opens existing SQLite storage read-only and reports database
presence, required tables, and migration state. It returns a non-zero exit code
for unhealthy storage, but it does not initialize, migrate, repair, or back up
the database.

Reason:

Health checks must be trustworthy. A diagnostic command should not hide damage
by changing the thing it is checking.

## D-020: Phase 0 Hardens The Existing Prototype

Decision:

PiGenus Phase 0 does not replace the current runtime prototype. It formalizes,
hardens, and extends it through additive Systemform models and compatibility
adapters.

Reason:

The existing prototype already has passing tests, storage, events, cells,
memory, context boundaries, and inspection surfaces. Rebuilding would destroy
useful evidence. Hardening preserves the working core while making the deeper
GENUS ontology explicit.

## D-021: Systemform Adapters Are Deterministic And Side-Effect Free

Decision:

Adapters from `MemoryObject`, `CellSpec`, and `Context` into Systemform objects
are pure mappings. They do not persist data, mutate storage, run CLI commands,
or alter orchestration behavior.

Reason:

The bridge between the prototype vocabulary and the Systemform vocabulary must
be reviewable before it becomes enforceable. Pure adapters let tests prove the
mapping rules before contract validation, guard pipelines, or storage
migrations depend on them.

## D-022: Contract Validation Starts Storage-Free

Decision:

The first Systemform contract validator consumes in-memory `ActorIdentity`,
`Room`, `CellContract`, and optional `ResourceGrant` objects. It returns a
structured decision but does not persist data, mutate orchestration, or replace
the existing permission engine.

Reason:

The rule "no execution without a valid contract" needs to become executable
before it becomes operationally enforced. A storage-free validator makes the
policy surface testable without risking the current green runtime.

## D-023: Room Flow Rules Start As A Fixed Matrix

Decision:

Room flow policy starts as a storage-free fixed matrix with deterministic
overrides for sensitive and unsafe meaning. Unknown room pairs require review
instead of default allow.

Reason:

Semantic movement between rooms is safety-critical. A small fixed matrix is
easier to audit than an editable policy engine, while conservative defaults
prevent silent cross-room leakage until a guard pipeline can combine all policy
decisions.

## D-024: Guard Pipeline Explains Before It Enforces

Decision:

The first guard pipeline composes storage-free contract validation and room
flow decisions into an ordered trace. It does not mutate storage, change CLI
behavior, or enforce decisions inside the current orchestrator.

Reason:

GENUS needs explainable policy composition before runtime enforcement. A
decision trace makes precedence and reasons inspectable, and it reduces the
risk of silently changing working behavior while the policy layer is still
young.

## D-025: Runtime Preview Runs In Shadow Mode

Decision:

Guard pipeline runtime preview adapts current runtime objects and returns a
decision trace, but it does not persist, publish, block, or alter orchestrator
execution.

Reason:

Policy should observe real runtime-shaped inputs before it controls them.
Shadow mode lets PiGenus compare policy decisions with current behavior while
keeping existing tests, demos, and storage semantics stable.

## D-026: Governance Decisions Use The Durable Decision Log

Decision:

Systemform `GovernanceDecision` results are persisted through the existing
`decision_logs` table as `DecisionRecord` entries. Their ordered traces live in
the record details.

Reason:

PiGenus already has a durable, inspectable decision log. Reusing it avoids a
new migration while making policy decisions queryable before orchestrator
integration or enforcement changes runtime behavior.

## D-027: Orchestrator Preview Logs But Does Not Enforce

Decision:

The demo orchestrator runs the guard preview before memory writes and persists
the resulting governance decision, but it does not stop or alter task execution.

Reason:

Runtime policy should be observed in the live path before it is allowed to
change behavior. Warning-mode logging gives PiGenus durable comparison data
while preserving the current deterministic demo flow.

## D-028: Selective Enforcement Blocks Only Hard Denials

Decision:

The first enforcement step stops only `block` governance decisions. `review`
and `escalate` remain logged warning states until a human approval workflow
exists.

Reason:

Hard denials are clear enough to enforce. Review and escalation need a human
approval model before they should stop runtime work, otherwise the system would
introduce ambiguous interruption without a resolution path.

## D-029: Human Approval Starts As A Stub

Decision:

Human approval starts as a durable placeholder with `pending`, `approved`, and
`rejected` states, persisted through the existing decision log. It does not add
UI, CLI commands, or enforcement changes.

Reason:

Review and escalation need a resolution model before they can safely control
runtime behavior. A small storage-backed stub creates that model without
expanding the user interface or complicating current guard enforcement.

## D-030: Meaning Store Starts As Plain SQLite Rows

Decision:

Systemform `MeaningObject` records are persisted in a local `meaning_objects`
table with the complete Pydantic JSON payload plus indexed columns for room,
type, truth status, and sensitivity. The first repository supports add, get,
list, and count only.

Reason:

Meaning Runtime needs durable semantic objects before richer retrieval exists.
Keeping the first store local and relational preserves inspectability, avoids
premature vector or LLM dependencies, and gives guard and room-flow work a
stable object source to build on later.

## D-031: Backups Are Local SQLite Snapshots First

Decision:

PiGenus creates local runtime backups with SQLite's backup API through a small
`SnapshotBackupService` and `backup-create` CLI command. The first workflow
creates a new snapshot file, refuses missing sources, refuses overwrites, and
checks snapshot integrity.

Reason:

Meaning Runtime makes the local database more valuable before the system has a
restore UI, scheduler, remote target, or retention policy. A boring local
snapshot path gives operators a safe checkpoint mechanism without expanding
storage semantics or pretending backup management is complete.

## D-032: Meaning Retrieval Starts As Indexed CLI Inspection

Decision:

Stored `MeaningObject` records are first exposed through a read-only
`meaning-list` CLI command with filters for room, type, truth status, and
sensitivity. Output stays compact and operator-readable.

Reason:

GENUS needs inspectable meaning before it needs semantic search. Starting with
indexed filters keeps retrieval deterministic, testable, and aligned with the
SQLite store while avoiding premature vector search, LLM ranking, dashboards,
or export workflows.

## D-033: Meaning Detail Inspection Uses Deterministic JSON

Decision:

One stored `MeaningObject` can be inspected through a read-only `meaning-show`
CLI command. The command returns the complete Pydantic JSON payload with stable
key ordering and a clean not-found error.

Reason:

The list view is intentionally compact and should remain scan-friendly. A
separate detail command gives operators the full semantic object for review and
debugging without adding edit behavior, exports, dashboards, or LLM summaries.

## D-034: Meaning Ingestion Starts As Explicit Memory Bridging

Decision:

Runtime-produced memory enters the Meaning Store first through an explicit
`MeaningIngestionPreview` service and `meaning-ingest-memory` CLI command. The
path uses the existing deterministic `MemoryObject -> MeaningObject` adapter and
is idempotent for repeated memory IDs.

Reason:

GENUS needs a real bridge from runtime artifacts to Systemform meaning, but
automatic ingestion would couple the orchestrator, memory lifecycle, and
governance layers too early. An explicit preview path proves persistence and
inspection while keeping enforcement and lifecycle behavior unchanged.

## D-035: Runtime Overview Reports Meaning Volume Only

Decision:

The runtime overview includes a `Meaning objects` count backed by
`MeaningRepository.count()`. It does not expose search, room breakdowns,
semantic summaries, or detail rendering.

Reason:

Operators need to know whether the Meaning Store is populated when inspecting
runtime health and shape. Keeping this to a count preserves the overview as a
small status surface while richer meaning inspection remains in dedicated
commands.

## D-036: Context Boundary Decisions Carry Room Metadata

Decision:

`ContextBoundaryDecision` includes the Systemform `room_id` and room
`protection_level` derived from the existing context-to-room adapter. The
allow/block decision remains based on the cell's allowed context names.

Reason:

Context boundaries are the runtime-facing form of room protection. Exposing room
metadata in the decision gives later logging and governance work a stable shape
without adding new policy or changing current orchestration behavior.

## D-037: Context Boundary Logging Is Explicit Preview First

Decision:

Context boundary decisions can be persisted through `ContextBoundaryDecisionLogger`
and the `context-boundary-check --log` CLI path. The default CLI check remains
read-only, and the orchestrator does not automatically log boundary checks.

Reason:

Boundary decisions are useful governance evidence, but automatic logging would
change runtime side effects across every orchestrated cell step. An explicit
preview path proves the durable record shape while preserving current
orchestration behavior.

## D-038: Boundary Decision Inspection Is Focused And Read-Only

Decision:

Logged context boundary decisions are exposed through a dedicated read-only
`context-boundary-list` CLI command with filters for cell, context, room, and
allowed status. The generic `decision-list` remains unchanged.

Reason:

Boundary decisions are operationally important enough to deserve focused
inspection, but not enough to justify new storage or dashboard work yet. A
filtered read-only command keeps review fast while preserving the existing
decision log as the durable source.

## D-039: Guard Outcomes Carry Stable Families

Decision:

Guard pipeline results and ordered trace steps expose a `family` field. Contract
validation reasons map into stable families such as actor, contract, room
scope, capability, permission, resource, and approval. Room-flow decisions keep
their own `room_flow` family.

Reason:

Operators and later inspection surfaces need a quick way to understand which
class of policy produced a decision without parsing every low-level reason
string. Adding the family at the guard boundary preserves current behavior and
storage while making traces easier to scan and aggregate later.

## D-040: Guard Decisions Get A Focused Read-Only Surface

Decision:

Logged governance decisions produced by the guard pipeline are exposed through
`guard-decision-list`. The command filters by final decision and guard family,
and reads existing decision records without writing, migrating, or changing
enforcement.

Reason:

The generic `decision-list` should remain stable and compact. Guard decisions
now carry enough structure to deserve a focused inspection path, especially as
families become the primary operator-level explanation of why a guard allowed,
blocked, or escalated work.

## D-041: The Build Plan Is An Architecture Map

Decision:

`BUILD_PLAN.md` is organized by architecture tracks instead of repeated
linear "Current" checkpoint sections. Checkpoints remain small and versioned,
but the plan now shows Foundation Runtime, Memory Lifecycle, Operator Safety,
Systemform Kernel, Meaning Runtime, Context/Room Governance, Guard Families,
and later tracks.

Reason:

PiGenus has grown past a simple patch queue. The project still needs tiny,
testable commits, but operators and contributors also need a readable map of
why work happens in this order and which larger system concern each checkpoint
serves.

## D-042: GENUS Philosophy Is Documented Separately

Decision:

GENUS has a dedicated philosophy document at `docs/GENUS_PHILOSOPHY.md`. The
build plan remains the technical map for how PiGenus is built; the philosophy
document explains why GENUS favors structure, meaning, contracts, governance,
and controlled evolution.

Reason:

The project now touches runtime architecture, meaning, governance, inspection,
and future evolution. Those choices need a stable compass before worker,
resource, federation, and mutation tracks become active. Keeping the philosophy
short and separate prevents `BUILD_PLAN.md` from becoming a manifesto while
still making the deeper system principles explicit.

## D-043: Version Numbers Distinguish Checkpoints From Release Arcs

Decision:

PiGenus keeps the existing `0.2.x` checkpoint history, but documents it as the
kernel completion arc rather than a long sequence of semantic patch releases.
The next major semantic cut is planned as `pigenus-v0.3.0-governed-runtime`
after Guard Families, Meaning Runtime, and Context/Room Governance are stable
as one governed local runtime.

Reason:

The project has outgrown simple `0.2.x` patch semantics. Renumbering history
would create churn, but leaving the meaning implicit would make future tags
confusing. Explicit release arcs preserve the audit trail while making future
versioning easier to understand.

## D-044: Context Frames Are Conditions Around Actions

Decision:

PiGenus introduces additive `ContextFrameType`, `ContextFrame`, and
`ContextStack` Systemform models. `Room` remains the existing governance,
protection, and memory boundary. A context frame is one formal condition around
an action, and a context stack is the concrete operating envelope assembled
from frames.

Reason:

`Room` was becoming overloaded as the project approached the governed runtime
cut. The system needs a way to describe task conditions without confusing them
with actors, agents, characters, cells, organs, or rooms. Adding these concepts
as models first keeps the ontology explicit while avoiding a risky runtime,
storage, CLI, or migration rewrite.

## D-045: Guard Summaries Stay Read-Only And Derived

Decision:

PiGenus exposes `guard-decision-summary` as a read-only CLI command derived
from existing governance decision records. It groups decisions by final guard
decision and family, and reuses the same filters as `guard-decision-list`.

Reason:

The runtime needs operator-level accountability before it needs analytics
storage or dashboards. A derived summary gives immediate visibility into guard
behavior without adding migrations, new policy, enforcement changes, or a
second source of truth.

## D-046: v0.3 Is A Governed Runtime Cut

Decision:

`pigenus-v0.3.0-governed-runtime` is defined as a semantic release cut for the
local governed runtime. The cut should verify meaning, room/context governance,
guard families, decision logging, approval stubs, backup, health checks, and
operator inspection as one coherent local runtime.

Reason:

The project has enough kernel capability that continuing to add `0.2.x`
features risks blurring the release boundary. A readiness document defines what
is already ready, what remains, and what stays out of scope so v0.3 can be a
boring reliability milestone instead of a feature grab.

## D-047: v0.3.0 Freezes The Governed Runtime Baseline

Decision:

`pigenus-v0.3.0-governed-runtime` freezes the current local governed runtime
baseline. The release includes meaning persistence, room/context governance,
guard pipeline, guard families, decision logging, inspection surfaces, backup,
health checks, human approval stubs, documented ontology, and release
semantics.

Reason:

The kernel has reached a coherent governed-runtime shape. Cutting v0.3.0 now
creates a stable baseline before worker runtime, federation, LLM orchestration,
dashboard surfaces, and controlled evolution introduce larger design pressure.

## D-048: Liquid Runtime Is A Future Proposal Layer

Decision:

Liquid Runtime is documented as a future proposal and preview layer, not as a
v0.3 runtime feature. No proposed form becomes real without validation, guard
decision, and trace.

Reason:

Dynamic form formation may become important for flexible GENUS orchestration,
but uncontrolled dynamism would undermine the governed runtime baseline. The
concept stays useful only if it is constrained by known inventory, contracts,
rooms, context stacks, resources, guards, and explicit traces.

## D-049: Workers Carry Execution, Not Intelligence

Decision:

Worker Runtime treats workers as execution hosts with hardware, runtime,
capability, cost, privacy, network, status, and heartbeat profiles. Cells carry
capabilities, organs carry compositions of cells, and agents carry goal
direction.

Reason:

The next architecture arc risks confusing machines, functions, compositions,
and goal-directed actors. Separating worker, cell, organ, and agent semantics
keeps future scheduling and execution routing governed by the v0.3 runtime
instead of turning workers into unbounded autonomous agents.

## D-050: Resource Economy Starts With Accounting

Decision:

Resource Economy starts with explicit grants, usage records, summaries, and
room-scoped budgets. It does not start with internal markets, dynamic pricing,
credits, or autonomous budget changes.

Reason:

Future workers, liquid runtime shapes, agents, federation, and evolution will
all increase resource pressure. The first safety need is accountability: what
was consumed, by whom, in which room, under which grant, and why. Optimization
comes only after accounting is reliable.

## D-051: Human Approval Is A Governance Decision

Decision:

Human approval is treated as a governance decision, not a UI button. Review,
escalation, and approval remain distinct states. Approval authority should be
explicit, room-aware, and backed by evidence before any approve or reject action
is allowed.

Reason:

Future workers, resource changes, liquid runtime shapes, federation, and
evolution will create situations where automation must slow down. Approval
semantics need to exist before a rich approval UI, otherwise the UI becomes a
cosmetic confirmation layer over unclear policy.

## D-052: Mutation Is Never Activation

Decision:

Evolution Sandbox treats mutation as proposal, not active behavior. Mutations
must pass through shadow mode, explicit fitness comparison, trace, rollback
planning, fossil records, guard checks, and human approval before activation.

Reason:

GENUS may eventually need adaptation, but uncontrolled adaptation would erase
accountability. Keeping mutation separate from activation allows the system to
compare, reject, preserve, or approve changes without turning experimentation
into hidden self-modification.

## D-053: Harvest Ideas, Do Not Merge Architectures

Decision:

Ideas from older or parallel WoltLab51 GENUS/PiGenus repositories may be
harvested into documentation, decisions, and future work packages, but their
architecture and code are not merged directly into the current PiGenus governed
runtime.

Reason:

The older repositories preserve useful product, worker, operations, deployment,
and assistant ideas. Directly importing them would risk bypassing the current
Systemform vocabulary, room/context boundaries, guard pipeline, approval
semantics, decision logs, and tests. Harvesting keeps the memory without
weakening the kernel.

## D-054: Internal Communication Uses Governed Meaning Objects

Decision:

GENUS internal communication is defined as governed meaning flow. Components
communicate through typed events, `MeaningObject` records, decision traces, and
persisted governance decisions instead of a free-form prompt bus. Natural
language remains allowed only as payload inside structured, room-aware,
guardable objects.

Reason:

Workers, organs, agents, characters, LLM gateways, and Liquid Runtime proposals
will all increase internal communication pressure. Without a communication
boundary, the runtime would drift toward hidden prompts and direct component
calls. Meaning-based communication preserves source, room, truth status,
sensitivity, provenance, time, guardability, and operator inspection.

## D-055: Vocabulary Precedes Architecture Expansion

Decision:

GENUS keeps a central vocabulary glossary that distinguishes implemented,
documented, planned, and conceptual terms. Future work should use the glossary
to preserve term meanings before adding schema, storage, runtime behavior, or
renames.

Reason:

Several GENUS concepts are valid architecture vocabulary before they exist as
runtime classes. Without a glossary, later implementation work may either treat
planned concepts as absent or prematurely force them into code. Vocabulary
control lets the project grow without confusing current runtime contracts with
future ontology.

## D-056: Documentation Is Operational Memory

Decision:

PiGenus treats documentation maintenance as part of the checkpoint process.
Non-trivial runtime or architecture changes must check the relevant project
control documents, especially changelog, status, build plan, vocabulary,
decisions, architecture history, and topic-specific concept documents.

Reason:

GENUS now depends on a growing ontology, release map, governance posture, and
future-track boundary set. If documentation drifts, future builders may rely on
stale assumptions and accidentally weaken the governed runtime. Documentation
upkeep preserves system memory without requiring every small cleanup to touch
every document.

## D-057: Capability Must Not Bypass Governance

Decision:

Future PiGenus capability growth must preserve the governed runtime contract.
Meaningful extensions must pass through contracts, contexts, rooms, meaning,
guards, decisions, traces, tests, and documentation maintenance instead of
bypassing them through direct calls, prompt buses, undocumented storage changes,
or hidden autonomy.

Reason:

The v0.3 governed runtime baseline exists to make intelligence-shaped work
observable, bounded, testable, and accountable. Workers, LLMs, agents, product
surfaces, federation, and evolution would weaken the system if they could route
around contracts, rooms, guard decisions, approval, auditability, or tests.

## D-058: Documentation Needs A Stable Entry Point

Decision:

PiGenus keeps `docs/INDEX.md` as the stable entry point for architecture
documentation. It should point readers toward philosophy, vocabulary, build
plan, status, architecture contract, documentation maintenance, and the main
topic-specific concept documents.

Reason:

The documentation set has become large enough that correctness alone is not
enough. Future builders need a predictable reading path so they can understand
the governed runtime baseline, vocabulary, rules, and non-goals before making
changes.

## D-059: Threat Modeling Precedes Powerful Runtime Surfaces

Decision:

PiGenus keeps a threat model for current and future security and governance
risks. Powerful runtime surfaces such as workers, LLM gateways, federation,
resource allocation, product dashboards, and controlled evolution should be
reviewed against this model before implementation.

Reason:

The governed runtime exists to make capability accountable. Future power will
increase risks around meaning injection, room boundary bypass, capability
escalation, stale memory, approval spoofing, log gaps, rogue workers, unsafe
LLM trust, silent mutation, and resource abuse. Naming threats early lets the
project harden deliberately instead of reacting after capability expands.

## D-060: Data Needs A Visible Lifecycle

Decision:

PiGenus keeps a data lifecycle map for events, meaning objects, memory objects,
governance decisions, decision traces, event logs, audit logs, fossils, and
future mutation proposals. New data objects should define source,
room/context, truth or confidence, sensitivity, creator, guard, decision,
storage, inspection, and aging behavior before becoming runtime surfaces.

Reason:

The governed runtime depends on being able to explain how information enters,
moves, persists, ages, and stops being active truth. Without a visible data
lifecycle, future stores, workers, LLM outputs, and evolution proposals could
create hidden state that bypasses inspection and governance.

## D-061: Full Checks Scale With Change Risk

Decision:

PiGenus uses a layered full-check process. Small documentation changes require
light checks, while concept, runtime, release, PR, and baseline changes require
progressively deeper documentation, architecture, threat, lifecycle, test, and
repository checks. ChatGPT may be used for bounded conceptual review, but Codex
remains responsible for repository truth and implementation.

Reason:

One checklist for every change would either be too weak for releases or too
heavy for small documentation edits. A layered check keeps the project
disciplined without making ordinary work painful. External discussion is useful
when bounded, but it must be translated back into the actual repository state.

## D-062: Pending Migration Application Is Exclusive

Decision:

`MigrationRunner.apply()` performs pending migration application under an
immediate SQLite transaction. Reading applied versions, executing pending
migration statements, recording migration versions, and committing the result
belong to one exclusive apply step.

Reason:

Runtime verification found that parallel CLI commands could attempt to apply a
pending migration at the same time and both record the same
`schema_migrations.version`. Exclusive migration application preserves
idempotent initialization without changing the schema or adding a new
migration.

## D-063: Worker Runtime Starts With Readiness

Decision:

The `0.4.x` Worker Runtime arc starts with readiness semantics before runtime
execution. PiGenus must define worker identity, heartbeat, capability profile,
cost profile, privacy profile, and failure semantics before adding worker
scheduling, remote execution, LLM provider routing, or autonomous agent
spawning.

Reason:

Workers increase the runtime's execution power. If worker routing begins before
identity, liveness, capability inventory, privacy limits, resource cost, and
failure behavior are explicit, the governed runtime could lose traceability at
the exact point where work leaves the simple local path. Readiness-first keeps
workers as accountable execution hosts rather than hidden intelligence or
unbounded capability.

## D-064: Multimodal Meaning Must Stay Governed

Decision:

GENUS may later use language models, meaning graphs, state fields, visual or
spatial models, embeddings, sensor-like inputs, and action traces, but these
representations must enter the runtime as governed meaning. Language is an
interface and reasoning tool, not the whole GENUS kernel.

Reason:

Pure text systems can produce coherent narratives without enough grounding,
while visual, spatial, and latent representations can become powerful but hard
to audit. GENUS should be able to grow toward multimodal world modeling without
creating hidden model state, prompt buses, or untraceable capability. Every
future representation still needs provenance, room, sensitivity, confidence or
truth status, guardability, decisions, and inspection.

## D-065: Worker Models Do Not Execute

Decision:

The first Worker Runtime implementation step adds only model-level
`WorkerProfile` and `WorkerHeartbeat` Systemform schemas. These models describe
execution hosts and liveness signals, but they do not create storage,
inspection commands, scheduling, provider routing, remote execution, or task
execution.

Reason:

Worker identity and heartbeat must become testable before workers can become
runtime infrastructure. Keeping the first step model-only preserves the v0.3
governed runtime while preparing a clear shape for future WorkerRegistry and
inspection work.

## D-066: Worker Registry Starts Storage-Free

Decision:

The first `WorkerRegistry` is storage-free. It registers `WorkerProfile`
objects, records the latest known `WorkerHeartbeat` for known workers, provides
deterministic list and filter behavior, and can say whether a worker is
currently considerable. It does not persist workers, add CLI commands, schedule
tasks, route capabilities, call providers, or execute work.

Reason:

Worker Registry is the bridge from worker ontology to operator inspection and
later scheduling. Starting storage-free keeps the behavior easy to test and
review before migrations, CLI surfaces, or execution placement create durable
runtime obligations.

## D-067: Worker Inspection Is Read-Only

Decision:

Worker inspection starts as a read-only service over an existing
`WorkerRegistry`. It produces inspectable rows for profile status, worker type,
latest heartbeat status, last-seen time, considerable status, available cells,
supported runtimes, and network access. It does not add persistence, CLI wiring,
scheduling, routing, provider calls, health repair, or execution.

Reason:

The project needs a stable inspection shape before deciding how operators will
load or view workers. A read-only service keeps the output testable without
pretending worker data is durable or inventing default workers.

## D-068: Storage Roles Must Be Explicit

Decision:

PiGenus distinguishes storage roles before adding new persistence surfaces.
SQLite remains the local governed runtime source of truth. Future graph,
vector, blob, cache, derived view, or external capability stores must be named
as such before implementation and must not silently become truth.

Reason:

Performance pressure will grow as GENUS adds workers, dynamic agent shapes,
multimodal meaning, and richer retrieval. Without explicit storage roles, the
runtime could confuse truth, indexes, caches, payloads, and audit evidence.
That would make the system harder to optimize and harder to explain.

## D-069: Worker Source Of Truth Is SQLite

Decision:

Durable Worker Runtime identity belongs in SQLite. The planned worker store
uses SQLite for `WorkerProfile` records and SQLite-backed current
`WorkerHeartbeat` state. Local files may be used later for bootstrap or import,
but not as runtime truth after import. Worker discovery is out of scope until
federation, trust, signatures, remote rooms, and privacy boundaries exist.

Reason:

Workers are security-relevant execution hosts. Treating worker data as ad hoc
configuration or network-discovered fact would weaken governance before worker
scheduling or execution even begins. SQLite matches the existing local governed
runtime: inspectable, migratable, testable, and compatible with read-only CLI
surfaces.

## D-070: Worker Store Persists Identity And Current Heartbeat Only

Decision:

The first Worker Store migration adds `worker_profiles` and `worker_heartbeats`.
`worker_profiles` persists full `WorkerProfile` JSON with indexed identity,
type, status, owner, home room, sensitivity, network, and timestamps.
`worker_heartbeats` persists only the latest/current `WorkerHeartbeat` per
worker. It does not store heartbeat history, scheduling assignments, execution
records, provider calls, discovery state, or remote worker state.

Reason:

Worker identity and current liveness need a durable local truth before
read-only worker CLI or scheduling preview can be honest. Keeping the first
store limited prevents persistence from quietly becoming execution
infrastructure.

## D-071: Worker CLI Is Read-Only Inspection

Decision:

`worker-list` and `worker-show` are read-only inspection commands over the
SQLite Worker Store. They can list and show known worker profiles, latest
heartbeat state, and considerable status. They do not create workers, record
heartbeats, schedule work, route capabilities, discover workers, call
providers, or execute tasks.

Reason:

Operators need visibility into known worker state before the system can safely
preview scheduling. Keeping the first CLI read-only preserves the source-of-
truth boundary and avoids turning inspection into worker management or
execution.

## D-072: Scheduling Preview Does Not Schedule

Decision:

Worker Scheduling Preview is storage-free candidate suitability reasoning. It
can explain whether known workers appear suitable for a requested capability
under simple constraints such as active heartbeat, capability inventory,
runtime support, sensitivity limit, and network availability. It does not
reserve workers, persist assignments, route capabilities, call providers,
discover workers, or execute tasks.

Reason:

GENUS needs to understand placement before it performs placement. A preview
layer makes worker selection criteria testable and inspectable without creating
durable scheduling semantics or execution side effects too early.

## D-073: Scheduling Preview Governance Conversion Is Not Persistence

Decision:

Worker Scheduling Preview may convert a preview result into a
`GovernanceDecision` with worker-scheduling family details, request metadata,
candidate suitability, and trace-like candidate steps. This conversion is
storage-free and does not persist the decision by itself.

Reason:

The project needs governance-shaped placement reasoning before it starts
logging, assigning, or executing worker tasks. Keeping conversion separate from
persistence allows later preview logging to reuse the existing decision-log
path without making every preview a durable runtime event too early.

## D-074: Scheduling Preview Logging Is Opt-In

Decision:

Worker Scheduling Preview may be persisted through a
`WorkerSchedulingPreviewLogger`, which converts the preview to a
`GovernanceDecision` and stores it through the existing decision log with
source `worker_scheduling_preview`. This persistence is explicit opt-in only.
Previewing or converting a preview still does not write by itself.

Reason:

Operators need a durable explanation path for placement reasoning before real
scheduling exists, but making every preview automatically durable would blur
inspection, reasoning, and runtime action. Opt-in logging keeps preview
accountable without creating assignments, reservations, provider routing, or
execution semantics.

## D-075: Scheduling Preview CLI Is Read-Only

Decision:

`worker-scheduling-preview` is a read-only CLI surface over the SQLite Worker
Store. It builds an in-memory worker registry from stored profiles and current
heartbeats, runs `WorkerSchedulingPreviewService`, and prints the resulting
allow/block preview, recommendation, and candidate reasons. Its default path
does not persist decisions.

Reason:

Operators should be able to inspect placement reasoning before the runtime has
durable scheduling, assignments, or execution. Keeping the first CLI read-only
preserves the distinction between seeing a possible placement and creating a
runtime action or governance record.

## D-076: Scheduling Preview CLI Logging Is Explicit

Decision:

`worker-scheduling-preview` may persist one preview decision only when `--log`
is provided. Logged previews use `WorkerSchedulingPreviewLogger`, the existing
decision log, and explicit metadata from `--actor`, `--room`, and optional
`--event-id`. Without `--log`, the command remains read-only.

Reason:

Preview logging is useful evidence, but it is still a write. Requiring an
explicit flag and governance metadata keeps operator inspection separate from
durable accountability records while avoiding new scheduling, assignment,
reservation, routing, provider, or execution behavior.

## D-077: Package Version Tracks Active Development Arc

Decision:

`pyproject.toml` uses the active package-development version. After the
`pigenus-v0.3.2-post-release-runtime-verification` checkpoint, mainline Worker
Runtime preparation uses package version `0.4.0.dev0` until a future stable
v0.4 release is cut.

Reason:

Keeping the package version at `0.2.0` while the repository status and build
plan describe v0.3/v0.4 work creates avoidable confusion. A PEP 440 dev
version makes the distinction explicit: v0.3.2 is the latest stable checkpoint;
v0.4.0 is the current preparation arc; worker execution is still not enabled.

## D-078: Worker Execution Preflight Is Not Execution

Decision:

Worker Execution Preflight checks one known worker against a proposed execution
request before any assignment, reservation, routing, provider call, or task
execution exists. The first implementation is storage-free and produces an
ordered check trace plus a log-compatible `GovernanceDecision`.

Reason:

GENUS needs to make execution eligibility inspectable before it makes execution
possible. Preflight separates "this worker appears allowed for these
conditions" from "this worker has been assigned work" or "this worker is
running work", preserving the governance-first Worker Runtime boundary.

## D-079: Worker Execution Preflight CLI Is Read-Only

Decision:

`worker-execution-preflight` is a read-only CLI surface for checking one worker
against a proposed capability, runtime, sensitivity, and network requirement.
It reads the SQLite Worker Store, builds temporary in-memory preview state, and
prints ordered preflight checks. It does not expose logging yet.

Reason:

Operators need to inspect execution eligibility before any execution path
exists. Keeping the first preflight CLI read-only preserves the distinction
between eligibility, durable governance evidence, assignment, and actual work.

## D-080: GitHub Actions Runs The Test Suite

Decision:

PiGenus uses GitHub Actions CI to run the Python test suite on push and pull
request events for `main`, plus manual dispatch. The first CI workflow uses
Python 3.12, installs the package with development dependencies, and runs
`python -m pytest`.

Reason:

The repository has grown beyond a purely local prototype. Local test runs remain
required before commits, but CI gives every pushed change a repeatable external
verification path and makes future PRs safer to review.

## D-081: Architecture Fitness Review Precedes Structural Refactor

Decision:

PiGenus records an architecture fitness review before slicing large runtime
coordination files such as the CLI entry point or storage repository module.
The first review identifies `pigenus/cli/main.py` as the next structural
extraction target and recommends a worker CLI command module boundary before
dynamic cell routing or repository splitting.

Reason:

PiGenus should move toward cell-like structure deliberately. Measuring hotspots,
responsibilities, and test coupling first keeps refactors behavior-preserving
and prevents a conceptual "cell architecture" discussion from turning into an
unsafe runtime rewrite.

## D-082: Worker Execution Preflight Logging Is Explicit

Decision:

`worker-execution-preflight` may persist one governance decision only when
`--log` is provided. Logged preflights use `WorkerExecutionPreflightLogger`,
the existing decision log, and explicit metadata from `--actor`, `--room`, and
optional `--event-id`. Without `--log`, the command remains read-only. This
supersedes the initial no-logging limit recorded in D-079 while preserving the
same no-execution boundary.

Reason:

Execution preflight is closer to future worker execution than scheduling
preview. Operators need an explicit way to make eligibility evidence durable
before assignments or execution exist, but implicit logging would blur
inspection and persistence. Requiring `--log` keeps the transition from
read-only eligibility check to durable governance record visible and auditable.

## D-083: Worker Assignment Shape Precedes Assignment Creation

Decision:

PiGenus defines `WorkerAssignment` and `WorkerAssignmentStatus` as model-only
Systemform schemas before adding worker assignment storage, CLI creation,
scheduling enforcement, routing, provider calls, or execution. A worker
assignment must reference a governance decision ID, but it does not contain
execution start time, completion time, or execution result fields.

Reason:

Assignment is the first point where worker placement can become durable runtime
intent. Its record shape must be clear before the system can create
assignments. Requiring governance evidence keeps assignment downstream of
scheduling and preflight decisions, while excluding execution fields preserves
the boundary between "this worker is assigned" and "this worker is running
work."

## D-084: PiGenus Is A GENUS Runtime Distribution

Decision:

GENUS is the broader governed systemform and architecture. PiGenus is the local
Python reference runtime distribution for GENUS. The current repository and
package keep the `pigenus` name during the Worker Runtime preparation arc, and
no repo, package, import, CLI, migration, or checkpoint rename is performed as
part of this naming clarification.

Reason:

The project is conceptually building GENUS, not a Raspberry-Pi-only product.
At the same time, the current codebase, tests, migrations, CLI, and checkpoint
history already use PiGenus as the local runtime identity. Clarifying the
relationship preserves stable engineering surfaces while making room for GENUS
to run on different devices or future runtime distributions.

## D-085: Cells Are Governed Capability Units

Decision:

GENUS defines a cell as the smallest responsible capability unit with identity,
boundary, contract, allowed effects, observable output, lifecycle, and tests.
Static CLI or service modules may act as temporary cell boundaries while the
runtime remains deterministic. Operator command modules that grow beyond
roughly 250 lines should trigger a follow-up slicing decision.

Reason:

The project should become more cellular without jumping into dynamic cell
routing too early. Treating cells as governed capability units preserves the
GENUS philosophy of cells before agents, while the static boundary rule keeps
ordinary software modules from becoming new small monoliths.

## D-086: GENUS Uses Stable Core And Variable Runtime Shapes

Decision:

GENUS keeps the Systemform Kernel stable while allowing future runtime shapes to
vary by device, function, resource profile, room policy, worker availability,
capability set, context stack, meaning scope, and output surface. RuntimeShape,
DeploymentProfile, DeviceProfile, ShapePreview, ShapeValidator, and ShapeTrace
are documented/planned concepts only until separate implementation decisions
add schemas, storage, CLI, or runtime behavior.

Reason:

This lets GENUS run as a local Pi-style runtime, developer runtime, server
runtime, privacy runtime, diagnostic runtime, or future character/agent runtime
without rewriting the core or bypassing governance. Variable form is useful
only if it stays downstream of identity, rooms, meaning, contracts, guards,
decisions, traces, inspection, and tests.

## D-087: Philosophy Alignment Reviews Gate Non-Trivial Changes

Decision:

PiGenus uses `docs/PHILOSOPHY_ALIGNMENT_REVIEW_PROTOCOL.md` as the repeatable
fit check for non-trivial changes. Larger work should classify philosophy fit,
governance fit, cellular maturity, RuntimeShape impact, hot-path versus
governed-path behavior, worker boundaries, documentation drift, monolith risk,
verification needs, and overengineering risk before implementation or commit.

Reason:

GENUS now has enough philosophy, ontology, governance, worker, cellular, and
runtime-shape language that informal judgement alone can drift. A repeatable
protocol keeps new work aligned with the stable core while avoiding both early
dynamic behavior and architecture ceremony that does not improve inspection,
tests, reuse, or governance.

## D-088: Meaning CLI Boundary Follows Alignment Review

Decision:

The first applied Philosophy Alignment Review chooses Meaning CLI extraction as
the next structural step before WorkerAssignment storage. The extraction creates
`pigenus/cli/meaning_commands.py` as a StaticCellBoundary for meaning-list,
meaning-show, and meaning-ingest-memory command handling. It does not promote
MeaningIngestionPreview to a GovernedCell or RuntimeCell, and it does not add
new commands, storage, migrations, assignments, routing, provider calls, or
execution.

Reason:

Meaning CLI extraction reduces operator-surface monolith risk while preserving
the stable core. WorkerAssignment storage remains important, but it touches
storage, migrations, and governed worker intent, so it should stay a separate
decision after this behavior-preserving CLI boundary.

## D-089: Worker Assignment Store Requires Governance Evidence

Decision:

PiGenus adds a minimal SQLite `worker_assignments` table and
`WorkerAssignmentRepository` as the storage step before pending creation,
scheduling enforcement, reservation, routing, provider call, or execution.
Persisting a `WorkerAssignment` requires both a known worker profile and an
existing governance decision record. The repository supports add, get, list,
and count only.

Reason:

Assignment is durable worker placement intent and belongs in the governed path.
Persisting it without requiring worker and governance evidence would let the
runtime create unsupported intent. Keeping the first store small makes the
future assignment boundary inspectable while preserving the no-execution rule.

## D-090: Worker Storage Repositories Are Domain-Sliced

Decision:

PiGenus moves `WorkerRepository` and `WorkerAssignmentRepository` into
`pigenus/storage/worker_repositories.py` while preserving the existing
`pigenus.storage.repositories` import surface. The change does not alter SQL,
migrations, CLI behavior, worker assignment behavior, scheduling, routing,
provider calls, or execution.

Reason:

Adding WorkerAssignment persistence made the shared repository module a storage
hotspot. Splitting the worker storage domain reduces monolith pressure before
read-only assignment inspection or further Worker Runtime behavior is added,
while keeping compatibility for existing callers and tests.

## D-091: Worker Assignment Inspection Is Read-Only

Decision:

PiGenus adds `worker-assignment-list` as a read-only CLI inspection surface for
stored `WorkerAssignment` records. The command supports filtering by worker,
status, room, capability, and governance decision. It does not create
assignments, decisions, audit logs, scheduling enforcement, reservations,
routing, provider calls, execution logs, or execution results.

Reason:

WorkerAssignment persistence should become inspectable before assignment
creation exists. This keeps worker intent observable while preserving the
current boundary: assignment records are durable governed intent, not execution
or routing.

## D-092: Worker Assignment Creation Requires Matching Preflight Allow Evidence

Decision:

WorkerAssignment creation requires matching `allow` evidence from
`worker_execution_preflight`. A generic decision record, scheduling preview
decision, blocked decision, escalated decision, or unstructured reason is not
sufficient. The requested assignment must match worker, capability, runtime
when present, sensitivity when present, network requirement, and room. Initial
creation may create only `pending` assignment intent.

Reason:

Assignment creation is the first durable step from inspection toward action.
It must remain narrower than scheduling preview and separate from assignment
activation, routing, provider calls, and execution. Defining the rule before
implementing the validator and creation command kept Worker Runtime growth
observable and accountable.

## D-093: Worker Assignment Validator Enforces Matching Evidence

Decision:

PiGenus adds `WorkerAssignmentValidator` as a read-only semantic validator
before assignment intent can be created. The validator checks that
a candidate `WorkerAssignment` references a known worker, an existing
`worker_execution_preflight` governance decision, an `allow` result, the
`worker_execution_preflight` family, matching worker, capability, runtime,
sensitivity, network requirement, room, and initial `pending` status.

Reason:

The repository enforces basic existence; it should not own the richer evidence
semantics. A separate validator keeps assignment creation accountable while
preserving the boundary: no scheduling enforcement, no reservation, no routing,
no provider calls, and no execution.

## D-094: Worker Assignment Creation Must Be Audited

Decision:

Future successful WorkerAssignment creation must write exactly one pending
`WorkerAssignment` record and one `worker_assignment_created` audit row. The
audit row should use the assignment creator as actor, a room-derived context
where available, and details containing assignment ID, worker ID, capability,
room ID, governance decision ID, and status. Assignment creation must not create
or mutate governance decisions, scheduling records, reservations, routes,
provider calls, execution logs, or execution results.

Reason:

Creating assignment intent is an operationally meaningful act even though it is
not execution. Audit makes that act accountable without confusing it with the
governance decision that authorized it. Keeping audit separate from decision
evidence preserves the distinction between policy reasoning and operational
action.

## D-095: Worker Assignment Creator Stays Service-Only

Decision:

PiGenus adds `WorkerAssignmentCreator` as a service-only creation boundary. It
uses `WorkerAssignmentValidator`, persists exactly one pending
`WorkerAssignment`, and writes exactly one `worker_assignment_created` audit row
for valid assignments. Invalid assignments do not create assignments or
successful creation audit rows. At this step, the creator is not exposed
through a CLI command and does not create governance decisions, schedule,
reserve, route, call providers, write execution logs, or execute work.

Reason:

Creation semantics should be executable before they become operator-facing. A
service-only boundary lets tests prove validation, persistence, audit, and
no-decision side effects before `worker-assignment-create` is exposed.

## D-096: Worker Assignment Create CLI Is Service-Backed

Decision:

PiGenus adds `worker-assignment-create` as a thin CLI wrapper around
`WorkerAssignmentCreator`. The command creates pending assignment intent only
after validator approval, writes the creator's `worker_assignment_created`
audit row, and returns a clean rejection when validation fails. It does not
create governance decisions, activate assignment status, schedule, reserve,
route, call providers, write execution logs, or execute work.

Reason:

The creation path is now safe to expose because validation and creation
semantics are already tested as services. Keeping the CLI as a wrapper prevents
operator-surface code from owning assignment policy and preserves the Worker
Runtime boundary.

## D-097: Worker Assignment Status Transitions Are Explicit

Decision:

PiGenus defines WorkerAssignment status transitions before implementing a
transition validator, transition service, or transition CLI commands. The
allowed transitions are `pending -> assigned`, `pending -> rejected`,
`pending -> cancelled`, `pending -> expired`, `assigned -> cancelled`, and
`assigned -> expired`. `rejected`, `cancelled`, and `expired` are terminal
states. A status transition must preserve the original worker, capability,
room, creator, and governance evidence, write a future
`worker_assignment_status_changed` audit row on successful change, and must not
create governance decisions, schedule, reserve, route, call providers, write
execution logs, or execute work.

Reason:

Assignment creation is now operator-facing, so the next risk is accidental
activation semantics. Defining the status graph first keeps assignment
lifecycle accountable and prevents `assigned` from being confused with
execution proof.

## D-098: Worker Assignment Status Transition Validator Is Read-Only

Decision:

PiGenus adds `WorkerAssignmentStatusTransitionValidator` as a read-only service
that checks documented WorkerAssignment status transitions without mutating or
persisting assignments. It accepts a current `WorkerAssignment`, a target
status, and optional actor/reason metadata for traceability. It returns stable
reason codes for valid edges, no-op requests, terminal-state reactivation,
undocumented edges, and unknown target statuses. It does not write audit rows,
create governance decisions, schedule, reserve, route, call providers, write
execution logs, or execute work.

Reason:

The status graph should become executable before any transition service or CLI
command can change durable state. A read-only validator makes the lifecycle
testable while preserving the current no-transition, no-execution boundary.

## D-099: Unreleased Changelog Uses Grouped Arc Summaries

Decision:

PiGenus keeps the `CHANGELOG.md` `Unreleased` section grouped by scan-friendly
categories once an arc grows beyond a few bullets: `Added`, `Changed`,
`Documented`, `Verified`, and `Not Yet Implemented`. `Unreleased` keeps only
the latest verified test result, summarizes related micro-commits at
capability or architecture-arc level, and leaves detailed decision history in
`docs/DECISIONS.md` and narrative context in `docs/ARCHITECTURE_HISTORY.md`.

Reason:

The v0.4 Worker Runtime preparation arc made the changelog useful as raw
construction history but hard to read as a changelog. A grouped summary keeps
release notes durable and operator-readable without losing detailed reasoning
from the decision log, architecture history, status file, or git history.

## D-100: Worker Assignment Status Transition Service Is Service-Only

Decision:

PiGenus adds `WorkerAssignmentStatusTransitionService` as a service-only
boundary for applying validated WorkerAssignment status transitions. The
service loads a stored assignment, delegates graph checks to
`WorkerAssignmentStatusTransitionValidator`, updates only `status` and
`updated_at`, and writes exactly one `worker_assignment_status_changed` audit
row on successful change. Invalid transitions, unknown assignments, and
unknown target statuses do not update assignments or write audit rows. The
service does not expose a CLI command, create governance decisions, schedule,
reserve, route, call providers, write execution logs, or execute work.

Reason:

Status changes are operationally meaningful but still not execution. A
service-only transition boundary makes lifecycle updates accountable and
testable before any operator command can change assignment status.

## D-101: Worker Assignment Transition CLI Is Service-Backed

Decision:

PiGenus adds `worker-assignment-transition` as a thin CLI wrapper around
`WorkerAssignmentStatusTransitionService`. The command accepts one assignment
ID, one target status, and optional actor/reason metadata. It delegates
validation, persistence, and audit to the service, prints either the applied
status change plus audit ID or stable rejection reasons, and does not create
governance decisions, schedule, reserve, route, call providers, write execution
logs, or execute work.

Reason:

The status transition service is already validated and audited. Exposing it as
a small operator command makes assignment lifecycle observable without moving
policy into CLI code or turning assignment status into execution.

## D-102: Assigned WorkerAssignments Require Scheduling Enforcement

Decision:

PiGenus defines a Worker Scheduling Enforcement boundary before implementing
real scheduling, reservation, routing, provider calls, execution logs, or
execution. `assigned` WorkerAssignment status is necessary for future
scheduling consideration, but it is not sufficient to run work. A future
enforcement check must revalidate current worker state, heartbeat freshness,
capability and runtime compatibility, sensitivity, network requirements, room
and context constraints, guard or room-flow outcomes, resource policy when
available, and any required human approval evidence. The first implementation
should be read-only and must not mutate assignments, create reservations,
route providers, write execution records, or execute work.

Reason:

`worker-assignment-transition` makes `assigned` operator-facing, so the next
risk is treating lifecycle status as runtime permission. A separate scheduling
enforcement boundary keeps assignment intent, scheduling consideration,
reservation, routing, and execution distinct and inspectable.

## D-103: Project Control Documents Have Explicit Roles

Decision:

PiGenus keeps project-control documents role-specific to reduce documentation
drift. `BUILD_PLAN.md` is the roadmap and sequencing map, `STATUS.md` is the
current repository truth, `CHANGELOG.md` records what changed,
`docs/DECISIONS.md` records durable rules, `docs/GENUS_VOCABULARY.md` owns
term boundaries, `docs/ARCHITECTURE_HISTORY.md` explains why the architecture
changed, and topic documents own detailed semantics for their area. Detailed
lifecycle rules should live in focused topic documents and be referenced from
broader maps instead of repeated in full.

Reason:

The v0.4 Worker Runtime preparation arc made the same worker lifecycle details
appear in multiple control documents. Explicit roles keep documentation useful
without turning roadmap, status, changelog, and topic documents into competing
sources of truth.

## D-104: GENUS Canonical Systemform Is The Alignment Source Of Truth

Decision:

GENUS keeps `docs/GENUS_CANONICAL_SYSTEMFORM.md` as the current source of truth
for overall systemform orientation. Older blueprints, local notes, sketches,
external discussions, and concept documents remain useful only as history or
source memory unless they map back to the canonical systemform. If another
document conflicts with the canonical systemform, the canonical systemform wins
until the conflict is resolved.

Reason:

GENUS now has enough philosophy, cellular language, worker boundaries,
RuntimeShape direction, resource concepts, safety language, and future
evolution vocabulary that parallel documents can drift. A single canonical
alignment document keeps future implementation pointed at the same
bio-cybernetic operating systemform without rewriting older history or
mistaking source memory for implementation authority.

## D-105: GENUS Metabolic State Graph Is A Derived Diagnostic View, Not A Second Source Of Truth

Decision:

GENUS defines the Metabolic State Graph as a conceptual architecture view over
cells, organs, organisms, habitats, workers, rooms, contracts, guards,
reflexes, resources, meaning, memory, decisions, traces, audit events,
lifecycle states, mutation proposals, and fossils. The graph may later become a
derived in-memory projection, read-only export, materialized view, or external
graph database only if needed. SQLite and current runtime stores remain the
source of truth.

Reason:

GENUS is hierarchical and relational. A tree can show cells becoming organs and
organisms, but it cannot explain activation, inhibition, resource pressure,
homeostasis, dependencies, quarantine, recovery, or governance bottlenecks.
The graph gives future planning and diagnosis a precise vocabulary while
preventing graph state from becoming hidden policy, hot-path routing, worker
execution, or a second truth source.

## D-106: Worker Freshness Policy Precedes Scheduling Enforcement

Decision:

PiGenus defines Worker Freshness Policy semantics before implementing any
scheduling-enforcement validator. Heartbeat freshness and preflight evidence
freshness must use explicit labels such as `fresh`, `review_stale`,
`hard_stale`, `missing`, and `clock_invalid`. Future validators must not invent
hidden timing rules, mutate assignments, create audit or decision records,
reserve capacity, route providers, write execution logs, or execute work.

Reason:

The WorkerAssignment tissue can now create intent, transition lifecycle state,
inspect eligibility, and explicitly log eligibility decisions. The next risk is
using stale heartbeat or stale preflight evidence as if it were live authority.
Freshness policy keeps future enforcement deterministic, testable, and
reviewable before any scheduling power appears.

## D-107: WorkerAssignment Room And Context Recheck Precedes Scheduling Enforcement

Decision:

PiGenus defines WorkerAssignment room/context recheck semantics before
implementing any scheduling-enforcement validator. Future scheduling
consideration must recheck assignment room identity, worker home room
compatibility, and ContextStack / ContextFrame compatibility where available.
RoomFlowRules apply only when meaning, memory, task output, execution result,
or other payload would cross rooms. The first recheck implementation must be
read-only and must not mutate assignments, write audit or decision records,
reserve capacity, route providers, write execution logs, or execute work.

Reason:

WorkerAssignment creation proves that original preflight evidence matched the
assignment request. It does not prove that the room, context, worker posture,
or policy is still valid later. A separate room/context recheck keeps room
governance, future ContextStack envelopes, and room-flow policy visible before
any scheduling power appears.
