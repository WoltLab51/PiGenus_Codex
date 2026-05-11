# PiGenus Build Plan

This file is the living technical plan for PiGenus. Update it whenever a phase
is completed, renamed, split, or moved.

## Build Rule

Every checkpoint should leave the repository with:

- Passing tests
- Updated `CHANGELOG.md`
- Updated `STATUS.md`
- This build plan adjusted when the next step changes
- `docs/ARCHITECTURE_HISTORY.md` updated when the architecture changes
- `docs/DECISIONS.md` updated when a durable decision is made
- A Git commit
- A version tag for stable phase checkpoints

## Completed

### pigenus-v0.1-core

Phase 1 Core Runtime established the executable nucleus:

- Structured schemas
- SQLite storage
- Event bus
- Cell registry
- Permission engine
- Audit logger
- MVP cells
- CLI demo
- Core tests

### pigenus-v0.1.5-contracts

Phase 1.5 Core Contracts made core behavior more explicit:

- Known event types and required payload keys
- `MemoryProposal` before durable memory writes
- Guard decisions tied to the source proposal
- Separate `CellState` for operational cell-local state
- Invariant tests for direct-write rejection and cell-state separation

### pigenus-v0.1.6-contexts

Phase 1.6 Context Boundaries establishes minimal room separation:

- Structured context schema
- Known context names
- Event and memory context validation
- Cell `allowed_contexts` enforcement in the orchestrator
- Invariant tests for context rejection and preservation

### pigenus-v0.2-memory-lifecycle

Phase 2 Memory Lifecycle makes memory age, review, and protect itself without
adding external AI.

Specification:

- `docs/PHASE_2_MEMORY_LIFECYCLE.md`

Implemented scope:

- `review_due_at` and `expires_at` behavior
- Status transition rules
- `canonical` protection
- Memory review CLI
- Audit logs for memory status changes
- Tests for lifecycle invariants

### pigenus-v0.2.1-lifecycle-polish

Phase 2.1 hardens lifecycle ergonomics without adding intelligence:

- CLI command conventions and exit-code documentation
- Primitive SQLite migration policy
- Read-only memory listing command for inspection

### pigenus-v0.2.2-migrations

Phase 2.2 adds the smallest useful migration runner before future schema
evolution:

- `schema_migrations` table
- idempotent migration application
- smoke tests for fresh and existing databases
- no destructive migrations

### pigenus-v0.2.3-schema-registry

Phase 2.3 makes runtime contracts inspectable:

- event contract registry
- `schema-list` CLI
- tests that registry output matches runtime validation

### pigenus-v0.2.4-decision-log

Phase 2.4 makes important decisions queryable separately from raw events and
audit logs:

- `DecisionRecord` schema
- `decision_logs` SQLite table
- decision repository
- lifecycle decision recording
- read-only `decision-list` CLI

### pigenus-v0.2.5-cell-lifecycle

Goal: make cells observable as lifecycle-managed runtime units without adding
evolution.

Implemented scope:

- explicit cell lifecycle status handling
- update `last_used_at`
- simple fitness fields remain passive
- read-only cell listing CLI

Out of scope:

- LLM reasoning
- Dashboards
- Distributed workers
- Autonomous evolution
- Vector search

### pigenus-v0.2.6-context-inspection

Phase 2.6 makes known contexts inspectable without changing boundary behavior:

- read-only context registry
- `context-list` CLI
- optional allowed-cell display from an existing SQLite database
- tests proving context inspection does not create missing databases

### pigenus-v0.2.7-permission-inspection

Phase 2.7 makes built-in permissions inspectable before adding richer guard
behavior:

- read-only permission registry
- `permission-list` CLI
- tests tying inspection output to runtime permission defaults

### pigenus-v0.2.8-audit-inspection

Phase 2.8 makes audit logs safely inspectable:

- read-only `audit-list` CLI
- actor, action, and context filters
- tests proving audit inspection does not mutate storage

### pigenus-v0.2.9-event-inspection

Phase 2.9 makes stored events safely inspectable:

- read-only `event-list` CLI
- filters for event type, created-by cell, context, and limit
- read-only `event-show` CLI with JSON payload output
- clean error handling for unknown event IDs

### pigenus-v0.2.10-runtime-overview

Phase 2.10 provides one small operator overview of the local runtime:

- read-only runtime overview builder
- `runtime-overview` CLI
- counts for events, memory objects, cells, audit logs, and decision records
- known contexts and default permissions

### pigenus-v0.2.11-health-check

Phase 2.11 reports whether local runtime storage is structurally healthy:

- read-only health checker
- `health-check` CLI
- migration-state checks
- required-table checks
- non-zero exit for unhealthy storage

### pigenus-v0.2.21-human-approval-stub

Goal: formalize the GENUS Systemform kernel vocabulary without replacing the
existing runtime prototype, then prove deterministic mappings from the current
prototype contracts into that vocabulary and validate the first executable
contract, semantic room-flow, guard-pipeline, runtime preview, and governance
decision logging, orchestrator preview, selective enforcement, and approval
stub rules.

Implemented scope:

- GENUS Systemform document copied into `docs/`
- Phase 0 core kernel specification copied into `docs/`
- `docs/SYSTEMFORM_GAP_ANALYSIS.md`
- additive Systemform models for actors, rooms, meaning objects, cell contracts,
  resource grants, and governance decisions
- tests for the new models
- deterministic adapters for `MemoryObject -> MeaningObject`, `CellSpec -> CellContract`,
  and `Context -> Room`
- tests for the adapter mappings
- storage-free contract validator
- tests for actor, contract, room, capability, permission, resource, and human-approval checks
- storage-free room flow rules
- tests for room matrix behavior, sensitivity overrides, and truth-status overrides
- storage-free guard pipeline
- tests for ordered traces, allow, escalation, and block precedence
- shadow-mode guard runtime preview against adapted runtime objects
- tests for allow, review, block, sensitivity override, truth-status override, trace order,
  and no orchestrator side effects
- governance decision logging through the existing durable decision log
- tests for allow, escalate/review, block, and trace-order persistence
- demo orchestrator guard preview in warning mode
- tests proving preview decisions are logged while demo execution continues
- selective guard enforcement for hard block decisions only
- tests proving block stops execution and review/escalate stays warning-only
- human approval stub with pending, approved, and rejected states
- tests proving approval records persist without changing current flow

Out of scope:

- CLI changes
- human approval UI

## Current

### pigenus-v0.2.22-meaning-store-minimal

Goal: persist and retrieve Systemform `MeaningObject` records as the start of Meaning Runtime.

Implemented scope:

- SQLite migration for meaning objects
- repository for add/get/list
- queries by room, type, truth status, and sensitivity
- tests for serialization and retrieval filters

Out of scope:

- CLI changes
- vector search
- LLM integration
- dashboard
- export behavior

## Current

### pigenus-v0.2.23-snapshot-backup-minimal

Goal: define a boring local safety path for preserving SQLite runtime state before
larger Meaning Runtime features arrive.

Implemented scope:

- SQLite backup service using the SQLite backup API
- `backup-create` CLI command
- missing-source and no-overwrite safety checks
- integrity check for created snapshots
- tests for repository-independent backup behavior and CLI behavior

Out of scope:

- restore workflow
- remote backup targets
- scheduling
- compression
- retention cleanup

## Current

### pigenus-v0.2.24-meaning-retrieval-queries

Goal: expose the first operator-safe Meaning Store lookup path without adding
vector search, LLM ranking, or dashboard behavior.

Implemented scope:

- read-only `meaning-list` CLI command
- filters by room, type, truth status, and sensitivity
- compact operator output for ID, type, room, truth status, sensitivity, and summary
- tests for empty output, read-only behavior, and combined filters

Out of scope:

- detail view
- vector search
- LLM ranking
- dashboard
- export behavior

## Current

### pigenus-v0.2.25-meaning-detail-view

Goal: inspect one stored `MeaningObject` by ID with deterministic JSON output.

Implemented scope:

- read-only `meaning-show` CLI command
- deterministic JSON output for full `MeaningObject`
- clean not-found error for unknown IDs
- tests for JSON output, not-found behavior, and read-only behavior

Out of scope:

- editing
- export files
- semantic search
- LLM summarization
- dashboard detail page

## Current

### pigenus-v0.2.26-meaning-ingestion-preview

Goal: create a narrow path for runtime-produced semantic objects to enter the
Meaning Store without changing guard enforcement or memory lifecycle behavior.

Implemented scope:

- `MeaningIngestionPreview` service
- `meaning-ingest-memory` CLI command
- deterministic `MemoryObject -> MeaningObject` ingestion through existing adapters
- idempotent behavior for repeated memory ingestion
- tests for service behavior, CLI behavior, missing memory, and no audit/decision side effects

Out of scope:

- automatic orchestrator ingestion
- guard enforcement changes
- memory lifecycle changes
- LLM extraction
- mutation or revision workflows

## Current

### pigenus-v0.2.27-runtime-overview-meaning-count

Goal: include Meaning Store counts in the existing runtime overview without
turning overview into a search or dashboard surface.

Implemented scope:

- `RuntimeOverview` includes `meaning_count`
- `runtime-overview` CLI prints `Meaning objects`
- tests prove builder count, CLI output, and read-only behavior

Out of scope:

- meaning search
- meaning detail rendering
- dashboard widgets
- per-room breakdowns

## Current

### pigenus-v0.2.28-changelog-release-sections

Goal: split the overloaded `Unreleased` changelog into checkpoint sections before
opening a PR or merging.

Implemented scope:

- moved Systemform and Meaning Runtime changes out of overloaded `Unreleased`
- added checkpoint sections from `pigenus-v0.2.12` through `pigenus-v0.2.27`
- preserved concise verified test counts for each checkpoint

Out of scope:

- code changes
- release tags
- PR creation

## Completed

### pigenus-v0.2.29-context-boundary-room-metadata

Goal: expand context boundary decisions with explicit Systemform room metadata
without changing allowed/blocked behavior.

Implemented scope:

- context boundary decisions include `room_id`
- context boundary decisions include `protection_level`
- existing context allow/block behavior remains unchanged
- tests cover allowed and blocked contexts with room metadata

Out of scope:

- new context names
- new enforcement policy
- room-flow integration changes
- persistence changes

## Current

### pigenus-v0.2.30-context-boundary-decision-logging-preview

Goal: optionally persist context boundary decisions for operator inspection
without changing orchestration behavior.

Implemented scope:

- `ContextBoundaryDecisionLogger`
- `context-boundary-check` CLI command
- default read-only preview behavior
- optional `--log` persistence into the decision log
- tests for record conversion, CLI preview, CLI logging, and missing cells

Out of scope:

- automatic orchestrator logging
- enforcement changes
- new context policy
- dashboard inspection

## Next

### Context Boundary Decision Inspection

Goal: expose persisted context boundary decisions through a focused read-only
inspection path without changing existing decision-list behavior.

## Later

- Guard families
- Worker interface
- Controlled cell evolution
