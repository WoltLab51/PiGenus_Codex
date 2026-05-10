# Systemform Gap Analysis

> Status: working draft
> Date: 2026-05-10
> Scope: first Systemform hardening pass for the existing PiGenus runtime prototype

## Core Decision

PiGenus is not being rebuilt from scratch.

The current repository is a working runtime prototype with green tests. Phase 0 now means
Systemform hardening of that existing core: formalize the kernel concepts, add missing domain
models, and keep the current runtime behavior stable while the deeper GENUS ontology becomes
executable.

## Current State

The current PiGenus runtime already provides:

- Pydantic schemas for events, memory objects, cells, cell state, context, and decision records.
- SQLite persistence for events, memory objects, cells, cell state, audit logs, and decision logs.
- A deterministic local event flow.
- A cell registry.
- A permission engine.
- A context boundary engine.
- A memory lifecycle engine.
- Audit logging.
- Read-only CLI inspection commands.
- A minimal migration runner.
- A health check command.
- A deterministic demo orchestrator.
- Test coverage for the existing runtime invariants.

The existing runtime terms are intentionally small and practical. They should remain compatible
until the Systemform layer is mature enough to take over selected responsibilities.

## Target State

The GENUS Systemform target introduces explicit kernel concepts:

- `ActorIdentity`
- `Room`
- `MeaningObject`
- `CellContract`
- `ResourceGrant`
- `GovernanceDecision`
- `Event`
- `AuditRecord`

The target model is stricter than the current prototype:

- Actors have stable identity, lifecycle status, provenance, and optional reputation linkage.
- Rooms are explicit governance and isolation objects, not only string contexts.
- Meaning objects are the primary semantic information unit before durable memory.
- Cell contracts define allowed capabilities, permissions, obligations, risks, resources, and
  governance policy.
- Resource grants make compute, storage, token, event, and attention budgets explicit.
- Governance decisions become structured, inspectable results rather than only event payloads or
  audit details.

## Existing Building Blocks

The current codebase already maps to several Systemform concepts:

| Systemform concept | Existing prototype block | Notes |
|---|---|---|
| Event | `pigenus.schemas.events.Event` | Already structured and validated by known event types. |
| MeaningObject | `pigenus.schemas.memory.MemoryObject` | Current memory object is durable memory, not the full semantic object. |
| Room | `pigenus.schemas.context.Context` | Current context is a light room boundary by name. |
| CellContract | `pigenus.schemas.cells.CellSpec` | Current cell spec declares IO, permissions, allowed contexts, and lifecycle metadata. |
| GovernanceDecision | `DecisionRecord` and `GuardDecision` events | Decision records and guard payloads exist, but no explicit governance decision model yet. |
| ResourceGrant | None | Resource limits are not explicit runtime objects yet. |
| ActorIdentity | None | Cells have IDs, but actors are not modeled as first-class identities yet. |
| AuditRecord | `audit_logs` table and `AuditRepository` | Audit is durable, but the schema is still implementation-specific. |

## Missing Models

This hardening pass should add the following models without deleting or replacing existing models:

- `ActorIdentity`
- `Room`
- `MeaningObject`
- `CellContract`
- `ResourceGrant`
- `GovernanceDecision`

The models should initially live as additive Pydantic contracts. They should not require storage
migrations, CLI changes, or orchestration rewrites in this first pass.

## Compatibility Strategy

The existing runtime remains the compatibility layer:

- `MemoryObject` remains the durable memory record.
- `CellSpec` remains the registered executable cell description.
- `Context` remains the event and memory boundary used by current code.
- Existing SQLite migrations remain forward-only and unchanged.
- Existing CLI commands remain stable.
- Existing tests must stay green.

The first adapter pass introduces deterministic, side-effect-free mappings:

- `MemoryObject -> MeaningObject`
- `CellSpec -> CellContract`
- `Context -> Room`

Those adapters are tested before any storage migration attempts to persist the new objects.

## Migration Strategy

Phase 0 hardening should proceed in small, reversible steps:

1. Add Systemform documents and gap analysis.
2. Add additive domain models and tests.
3. Add compatibility adapters.
4. Add a contract validator that consumes `ActorIdentity`, `Room`, `CellContract`, and
   `ResourceGrant`.
5. Add room flow rules.
6. Add a general guard pipeline.
7. Only then consider SQLite tables for actors, rooms, meaning objects, contracts, grants, and
   governance decisions.

No existing migration should be edited after it has shipped. New storage shape must arrive through
new forward-only migrations.

## Risks

- Naming drift: current terms such as `Context` and `MemoryObject` can diverge from Systemform
  terms if adapters are not introduced soon.
- Over-scoping: adding storage, CLI, validators, room flow rules, and guard pipelines in one commit
  would make review harder and increase regression risk.
- False completeness: adding models alone does not make the runtime contract-safe; validation and
  guard execution still need later work.
- Data migration risk: persisting the new objects before adapters are proven could lock in a weak
  schema too early.
- Governance ambiguity: `GovernanceDecision`, existing `DecisionRecord`, and guard events need a
  clear relationship before dashboards, exports, or advanced policy work are added.

## Completed Hardening Steps

The repository now has:

- Additive Systemform models.
- Deterministic adapters from prototype contracts to Systemform contracts.
- A storage-free contract validator for actor, room, contract, capability, permission, resource,
  and human-approval checks.
- Storage-free room flow rules for semantic movement between rooms.
- A storage-free guard pipeline with ordered decision traces.
- A shadow-mode runtime preview that runs the guard pipeline against adapted runtime objects.
- Governance decision logging through the existing durable decision log.

The validator proves the first executable Systemform rule:

```text
No execution without actor, room, contract, permission, and resource context.
```

## Immediate Next Step

Add Orchestrator Guard Preview. It should call the shadow-mode preview from the orchestrator,
persist the preview decision, and keep task execution unchanged.
