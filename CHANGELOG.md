# Changelog

## Unreleased

- Added `docs/LIQUID_RUNTIME.md` as a future concept document
- Added Liquid Runtime as a later architecture track in `BUILD_PLAN.md`
- Recorded `D-048: Liquid Runtime Is A Future Proposal Layer`
- Added `docs/WORKER_RUNTIME.md` as a future concept document
- Clarified Worker, Cell, Organ, and Agent boundaries
- Recorded `D-049: Workers Carry Execution, Not Intelligence`
- Added `docs/RESOURCE_ECONOMY.md` as a future concept document
- Clarified budgets and usage accounting before market mechanics
- Recorded `D-050: Resource Economy Starts With Accounting`
- Added `docs/HUMAN_GOVERNANCE.md` as a future concept document
- Clarified review, escalation, approval, authority, and required evidence
- Recorded `D-051: Human Approval Is A Governance Decision`
- Added `docs/EVOLUTION_SANDBOX.md` as a future concept document
- Clarified proposal, shadow mode, fitness comparison, fossils, rollback, and approval before activation
- Recorded `D-052: Mutation Is Never Activation`
- Added `docs/GITHUB_IDEA_HARVEST.md` to capture ideas from older WoltLab51 GENUS/PiGenus repositories without merging architectures
- Recorded `D-053: Harvest Ideas, Do Not Merge Architectures`
- Added `docs/INTERNAL_COMMUNICATION.md` as a core concept document for governed meaning-based communication
- Recorded `D-054: Internal Communication Uses Governed Meaning Objects`

## pigenus-v0.3.0-governed-runtime

- Cut the first semantic governed runtime release
- Includes Systemform models, adapters, contract validation, room-flow rules, guard pipeline, and selective hard-block enforcement
- Includes Meaning Store, meaning inspection, explicit memory-to-meaning ingestion, and runtime overview meaning counts
- Includes governance decision logging, guard decision family inspection, guard decision summaries, and human approval stub records
- Includes context boundary room metadata, boundary decision logging preview, boundary decision inspection, and additive ContextFrame/ContextStack ontology
- Includes operator safety surfaces for health checks, backups, event/audit/decision/cell/context/permission inspection, and runtime overview
- Includes GENUS philosophy, release semantics, v0.3 readiness documentation, architecture history, and durable decisions
- Explicitly excludes workers, LLM orchestration, autonomous agents, vector search, federation, dashboard, trading execution, and controlled evolution
- Verified: 187 tests passed

## pigenus-v0.2.39-v0-3-readiness-check

- Added `docs/V0_3_GOVERNED_RUNTIME_READINESS.md`
- Documented what is ready, what remains, and what is out of scope before `pigenus-v0.3.0-governed-runtime`
- Documented migration limits and ContextStack runtime rules before the v0.3 cut
- Recorded `D-046: v0.3 Is A Governed Runtime Cut`
- Verified: 187 tests passed

## pigenus-v0.2.38-guard-family-summary-minimal

- Added read-only `guard-decision-summary` CLI command
- Added guard decision summary grouping by final decision and family
- Added summary filters for final decision and family
- Added tests for summary output, filters, empty databases, and read-only behavior
- Verified: 187 tests passed

## pigenus-v0.2.37-context-stack-ontology

- Added additive `ContextFrameType`, `ContextFrame`, and `ContextStack` Systemform models
- Added deterministic validation for context frame allow/deny conflicts and stack duplicate frame IDs
- Added `docs/CONTEXT_MODEL.md` to explain Room vs ContextFrame vs ContextStack
- Documented `D-044: Context Frames Are Conditions Around Actions`
- Verified: 184 tests passed

## pigenus-v0.2.36-release-semantics

- Documented release semantics for `0.1.x` through `1.0`
- Defined `0.2.x` as the kernel completion arc
- Defined planned `pigenus-v0.3.0-governed-runtime` semantic cut
- Recorded `D-043: Version Numbers Distinguish Checkpoints From Release Arcs`
- Verified: 179 tests passed

## pigenus-v0.2.35-genus-philosophy

- Added `docs/GENUS_PHILOSOPHY.md` as a short system philosophy document
- Added README reference to the GENUS philosophy
- Documented `D-042: GENUS Philosophy Is Documented Separately`
- Clarified GENUS as a cognitive operating environment in `docs/GENUS_PHILOSOPHY.md`
- Added `Accountability before scale` to the core principles
- Added `BUILD_PLAN.md` reference to the philosophy document
- Verified: 179 tests passed

## pigenus-v0.2.34-roadmap-structure

- Restructured `BUILD_PLAN.md` into architecture tracks instead of repeated checkpoint headings
- Added an explicit "Why This Order" section for the runtime/governance sequence
- Added later architecture tracks for workers, resource economy, federation, controlled evolution, and product surfaces
- Verified: 179 tests passed

## pigenus-v0.2.33-guard-family-decision-log-surface

- Added read-only `guard-decision-list` CLI command for logged guard governance decisions
- Added guard decision filters for final decision and decision family
- Persisted final guard family into governance decision records without a schema migration
- Added guard decision inspection tests for output, filters, empty databases, and read-only behavior
- Verified: 179 tests passed

## pigenus-v0.2.32-guard-families-minimal

- Added stable `family` classification to guard pipeline results and trace steps
- Added contract-validation family mapping for actor, contract, room scope, capability, permission, resource, and approval outcomes
- Added guard family assertions for runtime preview and governance trace serialization
- Verified: 176 tests passed

## pigenus-v0.2.31-context-boundary-decision-inspection

- Added read-only `context-boundary-list` CLI command
- Added filters for cell, context, room, and allowed status
- Added context boundary inspection tests for empty output, read-only behavior, and filters
- Verified: 176 tests passed

## pigenus-v0.2.30-context-boundary-decision-logging-preview

- Added `ContextBoundaryDecisionLogger` for optional boundary decision persistence
- Added `context-boundary-check` CLI command with optional `--log`
- Added context boundary logging tests for record conversion, CLI preview, CLI logging, and missing cells
- Verified: 167 tests passed

## pigenus-v0.2.29-context-boundary-room-metadata

- Added Systemform room metadata to context boundary decisions
- Added context boundary tests for room ID and protection level on allow/block decisions
- Verified: 167 tests passed

## pigenus-v0.2.28-changelog-release-sections

- Split overloaded `Unreleased` changelog into explicit checkpoint sections
- Added sections from `pigenus-v0.2.12` through `pigenus-v0.2.27`
- Verified: 167 tests passed

## pigenus-v0.2.27-runtime-overview-meaning-count

- Added Meaning Store object count to runtime overview
- Added runtime-overview tests for meaning count and read-only behavior
- Verified: 167 tests passed

## pigenus-v0.2.26-meaning-ingestion-preview

- Added `MeaningIngestionPreview` for idempotent memory-to-meaning ingestion
- Added `meaning-ingest-memory` CLI command for explicit Meaning Store ingestion
- Added ingestion tests for service behavior, CLI behavior, missing memory, and no audit/decision side effects
- Verified: 167 tests passed

## pigenus-v0.2.25-meaning-detail-view

- Added read-only `meaning-show` CLI command with deterministic JSON output
- Added meaning-show tests for full object inspection, missing IDs, and read-only behavior
- Verified: 161 tests passed

## pigenus-v0.2.24-meaning-retrieval-queries

- Added read-only `meaning-list` CLI command for stored Systemform meaning objects
- Added meaning-list filters for room, type, truth status, and sensitivity
- Added meaning-list tests for empty output, read-only behavior, and combined filters
- Verified: 159 tests passed

## pigenus-v0.2.23-snapshot-backup-minimal

- Added local SQLite snapshot backup service using SQLite's backup API
- Added `backup-create` CLI command with missing-source, no-overwrite, and integrity checks
- Added backup tests for snapshot consistency and CLI behavior
- Verified: 156 tests passed

## pigenus-v0.2.22-meaning-store-minimal

- Added SQLite-backed `MeaningRepository` for Systemform `MeaningObject` persistence
- Added `0004_meaning_objects` migration with indexes for room, type, truth status, and sensitivity
- Added meaning-store tests for serialization, retrieval, ordering, and filters
- Verified: 151 tests passed

## pigenus-v0.2.21-human-approval-stub

- Added human approval stub with pending, approved, and rejected statuses
- Added tests proving approval records persist without changing current flow
- Stabilized human approval decision timestamp ordering
- Verified: 147 tests passed

## pigenus-v0.2.20-selective-guard-enforcement

- Enabled selective guard enforcement for hard block decisions only
- Added tests proving block decisions stop execution while review/escalate remains warning-only
- Verified: 142 tests passed

## pigenus-v0.2.19-orchestrator-guard-preview

- Integrated guard runtime preview into the demo orchestrator in warning mode
- Added tests proving preview decisions are logged while demo execution continues
- Verified: 135 tests passed

## pigenus-v0.2.18-governance-decision-logging

- Added governance decision logging through the existing durable decision log
- Added governance decision log tests for allow, escalate, block, and trace-order persistence
- Verified: 132 tests passed

## pigenus-v0.2.17-guard-runtime-preview

- Added guard pipeline runtime preview for shadow-mode evaluation against adapted runtime objects
- Added preview tests proving allow, review, block, sensitivity override, truth-status override,
  trace order, and no orchestrator side effects
- Verified: 127 tests passed

## pigenus-v0.2.16-guard-pipeline

- Added storage-free guard pipeline that composes contract validation and room flow decisions
- Added guard pipeline tests for allow, block precedence, escalation, and decision traces
- Verified: 120 tests passed

## pigenus-v0.2.15-room-flow-rules

- Added storage-free room flow rules with deterministic allow, review, block, and
  allow-read decisions
- Added room flow tests for matrix behavior, sensitivity overrides, and truth-status overrides
- Verified: 113 tests passed

## pigenus-v0.2.14-contract-validator

- Added storage-free `ContractValidator` for Systemform actor, room, contract,
  permission, capability, resource, and human-approval checks
- Added contract validator tests without changing orchestration enforcement
- Verified: 96 tests passed

## pigenus-v0.2.13-systemform-adapters

- Added deterministic Systemform adapters for `MemoryObject -> MeaningObject`,
  `CellSpec -> CellContract`, and `Context -> Room`
- Added Systemform adapter tests without adding persistence or CLI behavior
- Verified: 83 tests passed

## pigenus-v0.2.12-systemform-models

- Added GENUS Systemform and Phase 0 kernel documents under `docs/`
- Added `docs/SYSTEMFORM_GAP_ANALYSIS.md`
- Added additive Systemform models for `ActorIdentity`, `Room`,
  `MeaningObject`, `CellContract`, `ResourceGrant`, and `GovernanceDecision`
- Added Systemform model tests without changing existing runtime storage or CLI
- Verified: 75 tests passed

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
