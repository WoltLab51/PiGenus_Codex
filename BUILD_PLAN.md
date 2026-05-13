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
- `docs/INDEX.md` kept useful as the documentation entry point
- This build plan adjusted when the next step changes
- `docs/GENUS_VOCABULARY.md` checked when terms, statuses, or boundaries change
- `docs/DOCUMENTATION_MAINTENANCE.md` followed for documentation upkeep
- `docs/ARCHITECTURE_CONTRACT.md` preserved for non-trivial runtime changes
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
7. Treat internal communication as governed meaning flow, not loose prompts.
8. Add workers, resources, federation, and evolution only after the kernel can
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

The first semantic governed-runtime cut was
`pigenus-v0.3.0-governed-runtime`. The first post-release architecture-control
checkpoint is `pigenus-v0.3.1-architecture-control`.

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

- `pigenus-v0.3.1-architecture-control`: architecture-control checkpoint for
  documentation, vocabulary, internal communication, lifecycle, threat model,
  architecture contract, and full-check workflow

Next checkpoint:

- `pigenus-v0.3.2-post-release-runtime-verification`: verify health, runtime
  overview, migrations, inspection commands, backups, meaning queries, guard
  summaries, and read-only behavior before new runtime features

## Later Architecture Tracks

These are intentionally not current work. They become safer after guard,
meaning, inspection, and backup surfaces remain stable.

### H. Worker Interface

- Worker identity and heartbeat
- Capability declarations
- Cost and privacy profile
- Local-first worker registry
- Failure and timeout semantics
- Worker means execution host, not agent intelligence
- Cells carry capability, organs carry composition, agents carry goal direction

### I. Resource Economy

- Resource grants beyond static limits
- Compute, attention, storage, and time budgets
- Per-room quotas
- Cost reporting before optimization
- No market mechanics until accounting is reliable
- Budgets and usage records before prices, credits, or markets

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
- Mutation is never activation

### L. Human Governance

- Approval records before approval UI
- Review, escalation, and approval stay distinct
- Room-aware approval authority
- No agent self-approval
- Required evidence before approve/reject actions

### M. Product Surfaces

- CLI remains the primary operator surface
- Dashboard follows CLI semantics, not the other way around
- Human approval UI after approval records and guard summaries are stable
- Visual system maps after the architecture vocabulary stops shifting rapidly

### N. Liquid Runtime

- Dynamic form proposals from known runtime inventory
- Shape previews before execution
- Guarded execution only after validation, guard decision, and trace
- No arbitrary capability invention
- No self-modification or hidden mutation

### O. Idea Harvest

- Harvest ideas from older or parallel WoltLab51 GENUS/PiGenus repositories
- Treat harvested ideas as source memory, not direct implementation authority
- Map each idea to a current architecture track before implementation
- Do not merge old architecture around the governed runtime
- Keep `docs/GITHUB_IDEA_HARVEST.md` as the quarantine and triage surface

### P. Internal Communication

- Communicate through typed, validatable meaning objects instead of loose prompts
- Keep free text embedded in structured, room-aware, guardable objects
- Preserve source, room, intent, truth status, sensitivity, and time reference
- Separate events, meaning objects, governance decisions, and audit logs
- Treat messages as conditions for action, not neutral data packets

### P2. Data Lifecycle

- Keep `docs/DATA_LIFECYCLE.md` as the map for event, meaning, memory,
  decision, audit, fossil, and future mutation lifecycles
- Ensure new data objects answer source, room/context, truth, sensitivity,
  creator, guard, decision, storage, inspection, and aging questions
- Do not add new storage surfaces without lifecycle and inspection clarity

### Q. Vocabulary And Ontology Control

- Keep `docs/GENUS_VOCABULARY.md` as the central term map
- Distinguish implemented, documented, planned, and conceptual terms
- Stabilize language before adding schema, storage, or runtime behavior
- Update the glossary when a term's architecture boundary changes

### R. Documentation Maintenance

- Treat documentation as operational memory
- Check project control documents before every non-trivial commit
- Keep `docs/INDEX.md` as the entry point for architecture documentation
- Use `docs/FULL_CHECK.md` for complete change, release, PR, and external
  review checks
- Update vocabulary when term meaning or implementation status changes
- Update decisions only for durable architecture constraints
- Keep documentation current without turning every commit into paperwork

### S. Architecture Contract

- Preserve the v0.3 governed runtime baseline during future work
- Require contracts, rooms, meaning, guards, decisions, traces, and tests for
  meaningful capability growth
- Keep workers, LLMs, agents, and evolution behind governance boundaries
- Use `docs/ARCHITECTURE_CONTRACT.md` as the contribution safety contract

### T. Threat Model

- Keep `docs/THREAT_MODEL.md` as the safety risk map
- Review prompt/meaning injection, room bypass, capability escalation, stale
  memory, approval spoofing, log gaps, rogue workers, LLM trust, silent
  mutation, resource abuse, and documentation drift
- Add threat notes before adding powerful runtime surfaces

## Non-Goals For The Current Kernel Phase

- No LLM-first behavior
- No hidden mutation
- No dashboard-driven architecture
- No distributed execution before local governance is inspectable
- No vector search before deterministic meaning storage and retrieval are stable
- No free-form prompt bus between runtime components
