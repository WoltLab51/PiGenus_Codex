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
