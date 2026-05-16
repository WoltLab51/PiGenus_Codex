# GENUS Metabolic State Graph

This document defines the Metabolic State Graph as a conceptual architecture
view over GENUS metabolism, state, dependencies, flows, inhibition,
activation, resource use, and diagnosis.

It is not an implementation plan for a graph database.

It does not add schemas, migrations, runtime code, worker execution,
scheduling enforcement, or dynamic cell routing.

## Canonical Alignment

The Metabolic State Graph maps back to
`docs/GENUS_CANONICAL_SYSTEMFORM.md`.

It is an architectural view across:

- Stable Core / Variable Form
- MicroCell / Cell / CapabilityCell / GovernedCell / RuntimeCell
- Tissue / Organ / Organism / Character / Habitat
- Nervous System
- Immune System
- Metabolism
- Homeostasis
- Reflex / KillSwitch
- Quarantine
- Apoptosis
- Regeneration
- Ecology
- Controlled Evolution

The graph is a derived view. It must not become a second source of truth.

## Why Graph

GENUS is hierarchical, but not only hierarchical.

The hierarchy is useful:

```text
MicroCell -> Cell -> Organ -> Organism -> Character
```

But GENUS is also relational:

```text
cells activate, inhibit, consume, produce, depend on, govern, host, block,
recover, evolve, and fossilize each other
```

A tree can show containment. It cannot fully show metabolism, inhibition,
recovery, risk pressure, resource flow, worker health, room policy, guard
decisions, audit traces, and evolving dependencies.

The Metabolic State Graph gives GENUS a way to inspect those relations without
turning the runtime into a graph-first architecture.

## Core Idea

The Metabolic State Graph is a diagnostic and planning view showing:

- what exists
- what is active
- what consumes resources
- what produces meaning or output
- what is blocked
- what is degraded, stressed, or quarantined
- what depends on what
- what governs what
- what can recover from what
- what lives on which habitat or device

The graph can be used to reason about organisms, organs, workers, resource
pressure, guard decisions, safety reflexes, and lifecycle state.

It is initially conceptual. Later it may become a derived in-memory projection
from current stores. Even then, SQLite and the current runtime stores remain
the source of truth.

## Node Types

The graph may include these node types:

| Node Type | Meaning |
| --- | --- |
| MicroCell | Small responsibility-bearing capability boundary. |
| Cell | Smallest governable capability unit. |
| CapabilityCell | Cell exposing a reusable capability. |
| GovernedCell | CapabilityCell with contract, guard path, trace, and side-effect boundary. |
| RuntimeCell | Registered executable cell with lifecycle and inspection. |
| Tissue | Related cells sharing a domain responsibility. |
| Organ | Composed capability made from cells. |
| Organism | Coordinated runtime composition living in a habitat. |
| Character | Social organism with role, voice, memory, and relationship behavior. |
| Habitat | Runtime environment or device context where organisms live. |
| Worker | Execution host with profile, heartbeat, and constraints. |
| Room | Governed information/action boundary. |
| Contract | Declared capability and permission boundary. |
| Guard | Rule or evaluator that blocks, allows, escalates, or reviews. |
| Reflex | Fast protective response to known risk state. |
| KillSwitch | Strong reflex that disables or stops a risky path. |
| ResourceBudget | Allowed resource envelope. |
| ResourceUsage | Observed or projected consumption. |
| MeaningObject | Structured semantic object. |
| MemoryObject | Durable local memory record. |
| GovernanceDecision | Durable governance result. |
| DecisionTrace | Ordered explanation of decision reasoning. |
| AuditEvent | Operational accountability event. |
| Event | Typed runtime event. |
| State | Observable architecture or runtime state label. |
| LifecycleRecord | Status or lifecycle transition evidence. |
| MutationProposal | Proposed change, never activation by itself. |
| Fossil | Retired historical state, memory, or capability evidence. |

These node types are architectural vocabulary. They do not imply a current
Python class, table, graph schema, or migration.

## Edge Types

The graph may include these edge types:

| Edge Type | Meaning |
| --- | --- |
| contains | One boundary contains another. |
| composes | A larger capability is composed from smaller capabilities. |
| depends_on | One node requires another to be valid, present, or healthy. |
| consumes | A node consumes resource, input, signal, or meaning. |
| produces | A node produces output, meaning, decision, trace, audit, or state. |
| activates | One node activates or enables another. |
| inhibits | One node prevents or reduces another node's action. |
| governs | One node sets policy or decision constraints for another. |
| observes | One node watches state or evidence from another. |
| checked_by | One node is checked by a validator, guard, policy, or diagnostic view. |
| reads | One node reads another node or its store. |
| writes | One node writes another node or its store. |
| consumed_by | Inverse view of consumes for examples where input flow reads more clearly. |
| governed_by | Inverse view of governs for policy ownership. |
| inhibited_by | Inverse view of inhibits for blocked or constrained paths. |
| hosted_on | A cell, organ, organism, or worker lives on a habitat/device. |
| allowed_in | A node is allowed inside a room, context, or habitat. |
| blocked_by | A node is blocked by a guard, policy, state, reflex, or decision. |
| triggers | A node triggers a reflex, guard, transition, audit, or downstream signal. |
| transitions_to | A state or lifecycle record moves to another state. |
| recovers_from | A node can recover from another failed or degraded state. |
| quarantines | A node isolates another suspicious or unsafe node. |
| disables | A node disables another through kill switch, apoptosis, or policy. |
| derives_from | A node is derived from source data, meaning, memory, decision, or event. |
| evolves_to | A proposal or capability lineage evolves to another version. |
| fossilizes | A node becomes historical, retired, or fossil evidence. |

Edges are as important as nodes. In a metabolic graph, the important question
is often not "what exists?" but "what activates, blocks, consumes, produces,
or recovers what?"

## State Model

Graph nodes may carry observable state labels such as:

- idle
- ready
- active
- blocked
- degraded
- stressed
- overloaded
- quarantined
- disabled
- recovering
- retired
- fossil

States are observable runtime or architecture states. They are not necessarily
persisted yet.

A state label can come from existing stores, health checks, worker heartbeat
state, lifecycle records, decisions, audit events, future resource budgets, or
future derived diagnosis.

State labels must remain explainable. If the graph says a node is `blocked`,
`stressed`, `quarantined`, or `disabled`, it should eventually be able to show
the source decision, guard, reflex, resource budget, health signal, or audit
event behind that label.

## Metabolic Flows

GENUS metabolism is the movement and transformation of signal, meaning,
resources, risk, memory, audit, and trace.

A cell or organ can consume inputs/resources and produce outputs, meaning,
decisions, audit, traces, memory proposals, or downstream signals.

### Signal Metabolism

Signal metabolism describes how runtime signals move through the system.

Examples:

- a worker heartbeat refreshes worker readiness
- a guard result blocks a downstream action
- a reflex receives repeated failure signals and opens a circuit breaker
- a state transition changes a node from ready to blocked

### Meaning Metabolism

Meaning metabolism describes how structured meaning is created, transformed,
guarded, stored, retrieved, or rejected.

Examples:

- MemoryObject -> MeaningObject adaptation
- MeaningObject -> GuardPipeline -> GovernanceDecision
- MeaningObject -> MeaningStore
- untrusted meaning -> quarantine

### Resource Metabolism

Resource metabolism describes consumption, budgeting, pressure, and exhaustion.

Examples:

- a Worker consumes compute, memory, network, or time
- an Organ consumes a ResourceBudget
- a Habitat becomes overloaded
- a ResourceUsage node indicates budget pressure

### Risk Metabolism

Risk metabolism describes how risk enters, accumulates, is bounded, and is
reduced.

Examples:

- high sensitivity meaning increases room-crossing risk
- repeated failures increase circuit-breaker pressure
- a KillSwitch inhibits a risky execution path
- human approval reduces unresolved governance risk

### Memory Metabolism

Memory metabolism describes how observations become memory, age, stale,
retire, fossilize, or regenerate.

Examples:

- MemoryProposal -> guarded write -> MemoryObject
- active memory -> watch -> dormant -> fossil
- old memory becomes historical evidence, not active truth

### Audit / Trace Metabolism

Audit and trace metabolism describes how GENUS preserves evidence of decisions
and meaningful operational actions.

Examples:

- GuardPipeline -> DecisionTrace
- GovernanceDecision -> DecisionLog
- WorkerAssignmentCreator -> AuditLog
- status transition -> LifecycleRecord and AuditEvent

This flow makes diagnosis possible after the fact.

## Homeostasis

The graph helps GENUS detect homeostatic pressure.

It can show:

- resource exhaustion
- risk budget pressure
- overloaded workers
- degraded habitats
- stale signals
- blocked organs
- memory growth pressure
- governance bottlenecks
- unhealthy feedback loops

Homeostasis is not optimization. It is keeping GENUS inside safe operating
bounds.

For example, a future graph projection could show:

```text
TradingOrganism
-> consumes RiskBudget
-> hosted_on TradingHabitat
-> depends_on WorkerHeartbeat
-> blocked_by KillSwitch
-> governed_by TradingRoomPolicy
```

That view can explain why an organism should remain in shadow mode or why a
worker is no longer eligible for live work.

## Reflexes

Reflexes use graph state to protect the runtime quickly.

Examples:

- KillSwitch blocks a path.
- CircuitBreaker stops repeated failures.
- Quarantine isolates a cell, worker, organ, meaning object, or runtime shape.
- Apoptosis retires or disables unsafe units.
- Regeneration revalidates and restores after failure.

Reflexes should be explicit and inspectable. A future graph view should be able
to show what triggered a reflex, what it inhibited, what it quarantined, and
what recovery path remains.

## Source Of Truth Rule

SQLite and current runtime stores remain the source of truth.

The Metabolic State Graph is initially:

- a derived architectural view
- a diagnostic model
- a planning model
- a future projection

It must not become a second truth source.

A graph projection may derive from:

- events
- memory objects
- meaning objects
- decision records
- audit logs
- worker profiles
- worker heartbeats
- worker assignments
- lifecycle state
- future resource records

If derived graph state conflicts with source storage, the source storage wins
until the projection is rebuilt or corrected.

## Future Implementation Stages

### Stage 0: Concept Only

Current stage.

The graph exists only as architecture language and planning vocabulary.

### Stage 1: Derived In-Memory Graph Projection

Build an in-memory projection from existing stores.

No graph database. No schema migration. No second source of truth.

### Stage 2: CLI Inspection / Graph Export

Expose read-only graph inspection or export.

Examples:

- graph summary
- dependency export
- blocked-path view
- worker/habitat diagnostic view
- post-run audit graph

### Stage 3: Optional Materialized Graph View

Persist a rebuildable derived view only if inspection performance requires it.

The materialized graph must remain downstream of source storage and must be
rebuildable.

### Stage 4: Optional External Graph Database

Use an external graph database only if the derived view becomes too large,
complex, or slow for local inspection and planning.

This is not current work.

## Performance Rule

Graph queries must not be forced into hot paths.

Use graph mainly for:

- planning
- inspection
- diagnosis
- scheduling preview
- organism/habitat analysis
- dependency analysis
- post-run audit/review

Hot runtime paths should continue to use direct stores, simple indexes,
validated contracts, and explicit services unless a later decision proves a
graph view is safe, necessary, and bounded.

## Non-Goals

This document does not add:

- Neo4j implementation
- graph database
- graph schema migration
- runtime cell routing
- execution
- worker scheduling enforcement
- trading behavior
- autonomous organism behavior
- mutation activation
- hidden prompt bus

The Metabolic State Graph is not a new control plane yet. It is a future
diagnostic and planning view.

## Example A: WorkerAssignmentSchedulingEligibility Flow

Conceptual graph:

```text
WorkerAssignment
-> depends_on Worker
-> depends_on GovernanceDecision
-> checked_by SchedulingEligibilityValidator
-> produces EligibilityResult
-> no writes
-> no audit
-> no execution
```

Graph interpretation:

- `WorkerAssignment` depends on the known worker and governance evidence.
- `SchedulingEligibilityValidator` observes the assignment, worker, and
  decision records.
- The validator produces an eligibility result.
- The current flow does not write decisions, audit logs, reservations,
  execution logs, or execution results.

This maps to the current Worker Runtime boundary: assigned intent may become
eligible for future scheduling consideration, but it is never execution proof.

## Example B: Future High-Risk TradingOrganism

Conceptual graph:

```text
MarketSignal
-> consumed_by SignalValidationCell
-> produces ValidatedSignal
-> consumed_by RiskBoundaryCell
-> inhibited_by KillSwitch
-> governed_by TradingRoomPolicy
-> consumes RiskBudget
-> hosted_on TradingHabitat
-> must remain shadow/dry-run until high-risk execution requirements are met
```

Graph interpretation:

- `MarketSignal` is not trusted action input by itself.
- `SignalValidationCell` must produce a validated signal with provenance.
- `RiskBoundaryCell` checks room policy, budget, and risk pressure.
- `KillSwitch` can inhibit the trading path.
- `TradingRoomPolicy` governs what the organism may inspect or do.
- `RiskBudget` limits exposure.
- `TradingHabitat` supplies device/resource constraints.
- Live behavior is forbidden until the high-risk execution rule from
  `docs/GENUS_CANONICAL_SYSTEMFORM.md` is satisfied.

No trading behavior is implemented by this document.

## Current Conclusion

The Metabolic State Graph gives GENUS a way to think beyond hierarchy without
abandoning the stable core.

It makes dependencies, flows, inhibition, activation, resource pressure,
homeostasis, reflexes, and recovery visible as a future diagnostic surface.

For now, it remains conceptual and derived. SQLite and current runtime stores
remain the source of truth.
