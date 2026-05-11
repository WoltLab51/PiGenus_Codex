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
