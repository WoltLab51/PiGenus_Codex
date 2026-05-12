# v0.3 Governed Runtime Readiness

This document defines what must be true before PiGenus cuts the semantic
release `pigenus-v0.3.0-governed-runtime`.

The goal is not to add broad capability. The goal is to prove that the local
runtime can store meaning, apply governance, explain decisions, preserve
boundaries, and remain inspectable.

## Target Definition

`pigenus-v0.3.0-governed-runtime` means:

- local GENUS runtime
- Meaning Store
- room and context governance
- guard pipeline and guard families
- governance decision logging
- human approval placeholder
- selective enforcement for hard blocks
- backup and health checks
- operator inspection surfaces
- documented ontology and release semantics

It does not mean:

- worker runtime
- LLM orchestration
- autonomous agents
- vector search
- federation
- dashboard
- trading execution
- controlled evolution

## Already Ready

### Runtime Nucleus

- deterministic event flow
- SQLite-backed storage
- event, memory, cell, cell-state, audit, decision, and meaning repositories
- cell registry
- permission engine
- context boundary engine
- demo orchestrator

### Memory And Meaning

- memory lifecycle rules
- canonical memory protection
- meaning object model
- SQLite-backed Meaning Store
- meaning list/detail inspection
- explicit memory-to-meaning ingestion preview
- meaning count in runtime overview

### Governance And Guards

- Systemform actor, room, contract, resource, meaning, and governance models
- deterministic adapters from prototype objects into Systemform concepts
- contract validator
- room-flow rules
- guard pipeline with ordered traces
- guard runtime preview
- governance decision logging
- selective enforcement for hard blocks
- human approval stub
- guard decision family classification
- guard decision list and summary inspection

### Context And Room Model

- existing `Context -> Room` adapter remains compatible
- context boundary decisions expose room ID and protection level
- context boundary decisions can be preview-logged explicitly
- context boundary decisions can be inspected read-only
- additive `ContextFrame` and `ContextStack` ontology exists
- `Room` remains the governance, protection, and memory boundary

### Operator Safety

- read-only CLI inspection commands
- health check
- local SQLite snapshot backup
- changelog, status, decisions, architecture history, philosophy, and build map
- full test suite currently verifies runtime invariants

## Remaining Before v0.3.0

These are the only recommended remaining items before the semantic cut:

1. Ensure all current `0.2.x` work is merged into the release branch.
2. Run the full test suite on the release branch.
3. Create one final local snapshot backup of a sample runtime database.
4. Confirm the CLI inspection set is documented in `docs/CLI_CONVENTIONS.md`.
5. Confirm `CHANGELOG.md` has a `pigenus-v0.3.0-governed-runtime` section.
6. Tag `pigenus-v0.3.0-governed-runtime`.

Optional but useful before the tag:

- run the demo orchestrator once and inspect generated guard decisions
- run `runtime-overview`
- run `health-check`
- run `guard-decision-summary`

## Explicitly Out Of Scope

Do not add these before `pigenus-v0.3.0-governed-runtime`:

- worker registry
- worker scheduling
- LLM gateway
- provider routing
- character registry
- agent registry
- trading-specific logic
- DnD-specific logic
- legal expert agents
- vector search
- dashboard
- federation
- autonomous mutation
- evolution sandbox
- full human approval UI

These belong to later release arcs.

## Migration Rules Before v0.3.0

No breaking migration should be introduced before the `v0.3.0` cut.

Allowed:

- additive documentation
- additive read-only inspection
- additive model-only ontology
- bug fixes that preserve existing storage and CLI behavior

Not allowed:

- deleting or renaming `Room`
- replacing legacy `Context`
- removing `Context -> Room`
- changing event flow semantics
- changing existing CLI output without tests
- changing guard enforcement rules without an explicit decision
- replacing storage layout for existing tables

## ContextStack Runtime Rule

`ContextFrame` and `ContextStack` are currently ontology-only.

They may become runtime-relevant only after `v0.3.0` if all of these are true:

- existing room behavior stays compatible
- existing context boundary behavior stays compatible
- a migration plan exists if persistence is needed
- CLI inspection exists before runtime enforcement
- tests prove old context and room flows still pass
- documentation explains how TaskEnvelope uses the stack

Until then:

- `Room` is the runtime boundary
- `Context` remains the legacy runtime context
- `ContextFrame` is one condition around an action
- `ContextStack` is a future operating envelope

## v0.3.0 Cut Criteria

Cut `pigenus-v0.3.0-governed-runtime` when:

- full test suite passes
- working tree is clean
- release branch is up to date
- build plan points beyond v0.3.0
- changelog contains the v0.3.0 release section
- tag is created and pushed

The release is successful when PiGenus remains boring, inspectable, and local.
The point of v0.3.0 is not more magic. It is governed runtime reliability.
