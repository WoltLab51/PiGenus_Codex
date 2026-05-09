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
