# Changelog

## Unreleased

- Added GENUS Systemform and Phase 0 kernel documents under `docs/`
- Added `docs/SYSTEMFORM_GAP_ANALYSIS.md`
- Added additive Systemform models for `ActorIdentity`, `Room`,
  `MeaningObject`, `CellContract`, `ResourceGrant`, and `GovernanceDecision`
- Added Systemform model tests without changing existing runtime storage or CLI
- Added deterministic Systemform adapters for `MemoryObject -> MeaningObject`,
  `CellSpec -> CellContract`, and `Context -> Room`
- Added Systemform adapter tests without adding persistence or CLI behavior
- Added storage-free `ContractValidator` for Systemform actor, room, contract,
  permission, capability, resource, and human-approval checks
- Added contract validator tests without changing orchestration enforcement
- Added storage-free room flow rules with deterministic allow, review, block, and
  allow-read decisions
- Added room flow tests for matrix behavior, sensitivity overrides, and truth-status overrides
- Added storage-free guard pipeline that composes contract validation and room flow decisions
- Added guard pipeline tests for allow, block precedence, escalation, and decision traces
- Added guard pipeline runtime preview for shadow-mode evaluation against adapted runtime objects
- Added preview tests proving allow, review, block, sensitivity override, truth-status override,
  trace order, and no orchestrator side effects
- Added governance decision logging through the existing durable decision log
- Added governance decision log tests for allow, escalate, block, and trace-order persistence
- Integrated guard runtime preview into the demo orchestrator in warning mode
- Added tests proving preview decisions are logged while demo execution continues
- Enabled selective guard enforcement for hard block decisions only
- Added tests proving block decisions stop execution while review/escalate remains warning-only
- Added human approval stub with pending, approved, and rejected statuses
- Added tests proving approval records persist without changing current flow
- Added SQLite-backed `MeaningRepository` for Systemform `MeaningObject` persistence
- Added `0004_meaning_objects` migration with indexes for room, type, truth status, and sensitivity
- Added meaning-store tests for serialization, retrieval, ordering, and filters
- Added local SQLite snapshot backup service using SQLite's backup API
- Added `backup-create` CLI command with missing-source, no-overwrite, and integrity checks
- Added backup tests for snapshot consistency and CLI behavior
- Added read-only `meaning-list` CLI command for stored Systemform meaning objects
- Added meaning-list filters for room, type, truth status, and sensitivity
- Added meaning-list tests for empty output, read-only behavior, and combined filters
- Added read-only `meaning-show` CLI command with deterministic JSON output
- Added meaning-show tests for full object inspection, missing IDs, and read-only behavior
- Added `MeaningIngestionPreview` for idempotent memory-to-meaning ingestion
- Added `meaning-ingest-memory` CLI command for explicit Meaning Store ingestion
- Added ingestion tests for service behavior, CLI behavior, missing memory, and no audit/decision side effects

## pigenus-v0.2.11-health-check

- Added read-only health checker for local SQLite runtime storage
- Added `health-check` CLI command
- Checked database presence, required tables, and recorded migration state
- Added non-zero health-check exit codes for unhealthy storage
- Added health-check tests for healthy and broken databases
- Verified: 75 tests passed

## pigenus-v0.2.10-runtime-overview

- Added read-only runtime overview builder
- Added `runtime-overview` CLI command
- Summarized events, memory objects, cells, audit logs, and decision records
- Included known contexts and default permissions in overview output
- Added runtime overview tests
- Verified: 70 tests passed

## pigenus-v0.2.9-event-inspection

- Added read-only `event-list` CLI command
- Added event filters for object type, created-by cell, context, and limit
- Added read-only `event-show` CLI command with readable JSON payload output
- Added clean error handling for unknown event IDs
- Added event inspection tests
- Verified: 67 tests passed

## pigenus-v0.2.8-audit-inspection

- Added read-only `audit-list` CLI command
- Added audit filters for actor, action, and context
- Added repository filter support for audit listing
- Added audit inspection tests
- Verified: 61 tests passed

## pigenus-v0.2.7-permission-inspection

- Added minimal read-only permission registry
- Added `permission-list` CLI command
- Exposed built-in default permissions from the runtime permission engine
- Added permission inspection tests
- Verified: 57 tests passed

## pigenus-v0.2.6-context-inspection

- Added minimal read-only context registry
- Added `context-list` CLI command
- Added optional allowed-cell inspection for existing databases
- Ensured `context-list --show-cells` does not create missing databases
- Added context inspection tests
- Verified: 54 tests passed

## pigenus-v0.2.5-cell-lifecycle

- Added cell lifecycle migration `0003_cell_lifecycle`
- Made cell status, fitness, creation time, and last-used time explicit in SQLite
- Added cell repository listing and `last_used_at` update support
- Updated the orchestrator to mark executed cells as used
- Added read-only `cell-list` CLI command with status filtering
- Added cell lifecycle tests
- Verified: 50 tests passed

## pigenus-v0.2.4-decision-log

- Added `DecisionRecord` schema
- Added `decision_logs` SQLite table through migration `0002_decision_logs`
- Added decision repository
- Added lifecycle decision recording for status changes
- Added read-only `decision-list` CLI command
- Added decision log tests
- Verified: 45 tests passed

## pigenus-v0.2.3-schema-registry

- Added minimal schema registry for event contracts
- Added `schema-list` CLI command
- Added tests tying registry output to runtime event validation
- Cleaned current status and build-plan phase layout
- Verified: 41 tests passed

## pigenus-v0.2.2-migrations

- Added minimal SQLite migration runner
- Added `schema_migrations` table
- Moved initial table creation into `0001_initial_schema`
- Made `Database.initialize()` apply migrations idempotently
- Added migration smoke tests for fresh, repeated, and existing databases
- Verified: 36 tests passed

## pigenus-v0.2.1-lifecycle-polish

- Added read-only `memory-list` CLI command
- Added status and context filters for memory listing
- Added CLI conventions and exit-code documentation
- Added SQLite migration policy documentation
- Added tests proving `memory-list` does not mutate storage
- Verified: 33 tests passed

## pigenus-v0.2-memory-lifecycle

- Bumped package version to `0.2.0`
- Added Phase 2 Memory Lifecycle implementation specification
- Added deterministic `MemoryLifecycleEngine`
- Added memory lifecycle service with status persistence and audit logging
- Added repository support for memory listing, due lifecycle lookup, and status updates
- Added `memory-review` CLI with deterministic `--now`
- Implemented review due and expiry rules without automatic deletion
- Protected `canonical` memory from automatic lifecycle changes
- Added lifecycle invariant tests
- Added architecture history and decision log documents
- Updated project-control rules for future checkpoints
- Verified: 29 tests passed

## pigenus-v0.1.6-contexts

- Added Phase 1.6 minimal context boundaries
- Added structured context schema with known context names
- Added context boundary checks before orchestrated cell execution
- Added invariant tests for context rejection and proposal context preservation
- Added `BUILD_PLAN.md` and `STATUS.md` as living project control documents
- Verified: 20 tests passed

## pigenus-v0.1.5-contracts

- Added Phase 1.5 Core Contracts
- Formalized known event types and required payload keys
- Added `MemoryProposal` as the required path before durable memory writes
- Added separate `CellState` storage for operational cell-local state
- Hardened guard decision payloads with blocking-cell metadata
- Verified: 14 tests passed

## pigenus-v0.1-core

- Implemented Phase 1 Core Runtime
- Added structured schemas, SQLite storage, event bus, registry, permissions, audit logger
- Added MVP cells and simple orchestrator
- Added CLI demo
- Added Phase-1 hardening tests
- Verified: 9 tests passed
