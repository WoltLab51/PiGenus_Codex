# PiGenus Build Plan

This file is the living technical map for PiGenus. It keeps the small
checkpoints, but groups them by architectural intent so the project stays
readable as GENUS grows.

The guiding philosophy lives in `docs/GENUS_PHILOSOPHY.md`. This build plan
describes how PiGenus grows; the philosophy explains why it grows in this
order.

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

## Why This Order

PiGenus should become more capable only after it becomes more observable and
governable. The ordering is intentionally boring:

1. Build a deterministic runtime nucleus.
2. Make memory and storage lifecycle behavior explicit.
3. Add read-only inspection and backup surfaces before larger features.
4. Formalize Systemform models and adapters without replacing the prototype.
5. Add guard, governance, and approval layers before autonomous behavior.
6. Persist and inspect meaning before semantic search or LLM extraction.
7. Add workers, resources, federation, and evolution only after the kernel can
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

The planned semantic cut is `pigenus-v0.3.0-governed-runtime`. It should happen
after the current `0.2.x` kernel arc proves Guard Families, Meaning Runtime, and
Context/Room Governance as one stable governed runtime.

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

Current checkpoint:

- `pigenus-v0.2.39-v0-3-readiness-check`: document what remains before
  `pigenus-v0.3.0-governed-runtime`

Next checkpoint:

- `pigenus-v0.3.0-governed-runtime`: semantic release cut after final branch
  verification, changelog section, and release tag

## Later Architecture Tracks

These are intentionally not current work. They become safer after guard,
meaning, inspection, and backup surfaces remain stable.

### H. Worker Interface

- Worker identity and heartbeat
- Capability declarations
- Cost and privacy profile
- Local-first worker registry
- Failure and timeout semantics

### I. Resource Economy

- Resource grants beyond static limits
- Compute, attention, storage, and time budgets
- Per-room quotas
- Cost reporting before optimization
- No market mechanics until accounting is reliable

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

### L. Product Surfaces

- CLI remains the primary operator surface
- Dashboard follows CLI semantics, not the other way around
- Human approval UI after approval records and guard summaries are stable
- Visual system maps after the architecture vocabulary stops shifting rapidly

## Non-Goals For The Current Kernel Phase

- No LLM-first behavior
- No hidden mutation
- No dashboard-driven architecture
- No distributed execution before local governance is inspectable
- No vector search before deterministic meaning storage and retrieval are stable
