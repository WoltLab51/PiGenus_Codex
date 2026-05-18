# Cell-DNA Protocol

This document defines the lightweight Cell-DNA frame used to describe
cell-shaped responsible capabilities before any RuntimeCell implementation
exists.

It is documentation and protocol only.

It does not introduce:

- RuntimeCell behavior
- CellRegistry behavior
- dynamic cell routing
- schemas
- migrations
- CLI commands
- graph projection
- scheduling enforcement
- execution
- logging behavior

## Purpose

GENUS is cell-first, but PiGenus should not become RuntimeCell-first.

Cell-DNA is the small description frame that makes a responsible capability
legible before it gains more maturity. It names the membrane:

```text
what comes in
what comes out
what it reads
what it writes
what it may do
what it must never do
how it is tested
what maturity it may reach next
```

The goal is to prevent hidden capability growth while keeping the ceremony
small enough for validators, services, and static cell boundaries.

## Scope Rule

Cell ceremony scales with responsibility.

Not every helper needs Cell-DNA. MicroCells may remain lightweight when they are
small, deterministic, local, and have no durable side effects.

Responsible capabilities should get a Cell-DNA frame before further maturity
when they:

- make a meaningful decision
- validate governance evidence
- write durable state
- write audit or decision records
- move Meaning or Memory
- change lifecycle state
- prepare worker assignment, scheduling, routing, or execution
- may later become a GovernedCell, RuntimeCell, or part of an Organ

## Maturity Labels

Use the current maturity label honestly. Do not promote by naming.

```text
Function
MicroCell
CapabilityCell
GovernedCellCandidate
GovernedCell
RuntimeCellLater
RuntimeCell
Tissue
OrganLater
Organ
OperatorSurface
StorageBoundary
```

Most current PiGenus surfaces are not RuntimeCells. That is expected.

## Cell-DNA Frame

Use this frame for new responsible capabilities and for existing candidates as
they mature:

```text
Capability:
Maturity:
Inputs:
Outputs:
Reads:
Writes:
Allowed effects:
Forbidden effects:
Trace / audit behavior:
State / lifecycle assumptions:
Tests:
Non-goals:
Next possible maturity:
```

## Field Guidance

### Capability

Name the smallest governable responsibility.

Good:

```text
Validate WorkerAssignment creation evidence.
```

Too broad:

```text
Manage workers.
```

Too small:

```text
Compare one worker id string.
```

### Maturity

State the current level, not the desired final form.

Examples:

```text
MicroCell
CapabilityCell
GovernedCellCandidate
OperatorSurface
StorageBoundary
RuntimeCellLater
```

### Inputs

List the explicit request shape, objects, ids, context, room, and evidence the
capability receives.

### Outputs

List return objects, result statuses, reason codes, traces, emitted events, or
operator-visible rows.

### Reads

List repositories, stores, in-memory registries, configuration, worker profiles,
decision evidence, meaning objects, memory objects, or policies read by the
capability.

### Writes

List all durable writes. If the capability is read-only, say:

```text
none
```

For write-capable capabilities, list every allowed durable write explicitly.
If existing code already writes audit, name that audit write directly. Do not
hide audit, decision, lifecycle, graph, or execution side effects under a broad
"writes state" phrase.

### Allowed Effects

Describe what the capability may do. Keep this narrow.

### Forbidden Effects

Describe explicit stop lines. Include future temptations where relevant:

- no hidden writes
- no audit write
- no decision logging
- no assignment creation
- no status transition
- no scheduling enforcement
- no reservation
- no provider routing
- no execution
- no graph truth
- no LLM judgement

### Trace / Audit Behavior

Clarify whether the capability persists trace/audit data or only returns reason
codes for a caller to use.

### State / Lifecycle Assumptions

State whether the capability is stateless, whether it assumes current state,
which lifecycle states are accepted, and which states remain out of scope.

### Tests

List the proof expected before the capability can mature:

- happy path
- missing input
- invalid evidence
- reason stability
- no-write proof
- audit/decision proof when writes are allowed
- no execution proof for worker surfaces

### Non-Goals

State what this capability must not become.

### Next Possible Maturity

Name the next reasonable promotion, not the whole future.

Examples:

```text
GovernedCell with explicit contract and returned trace.
RuntimeCell only after CellRegistry, contract validation, lifecycle, and
inspection exist.
```

## Promotion Rules

A Cell-DNA frame does not grant new runtime power.

To promote a capability, a later change must explicitly add the missing pieces:

- contract
- inspection surface
- tests
- trace shape
- lifecycle/status handling
- guard or policy path where needed
- audit/decision behavior where needed
- rollback or recovery path where needed

RuntimeCell promotion additionally requires explicit RuntimeCell infrastructure
and is out of scope for the current Worker Runtime preparation arc.

## Applied Frames

Current applied Cell-DNA frames:

```text
docs/CELL_DNA_WORKER_ASSIGNMENT_VALIDATOR.md
docs/CELL_DNA_WORKER_ASSIGNMENT_SCHEDULING_ELIGIBILITY_VALIDATOR.md
docs/CELL_DNA_WORKER_ASSIGNMENT_CREATOR.md
docs/CELL_DNA_WORKER_ASSIGNMENT_STATUS_TRANSITION_SERVICE.md
docs/CELL_DNA_WORKER_FRESHNESS_POLICY_VALIDATOR.md
docs/CELL_DNA_WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK_VALIDATOR.md
docs/CELL_DNA_WORKER_ASSIGNMENT_RESOURCE_RISK_REFLEX_READINESS_VALIDATOR.md
```

They describe the first candidates identified by
`docs/CELLULAR_INVENTORY_REVIEW.md`.
