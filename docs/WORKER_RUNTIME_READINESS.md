# Worker Runtime Readiness

This document defines the readiness boundary for the `0.4.x` Worker Runtime
arc. It prepares worker concepts for later implementation without enabling
execution routing, remote work, LLM orchestration, federation, or autonomous
agents.

## Purpose

Worker Runtime exists to answer:

```text
Where can governed work run, under which constraints, and with which evidence?
```

It does not answer:

```text
What goal should be pursued?
What capability exists?
What should be believed?
Who may approve risk?
```

Those questions stay with agents, cells, meaning, rooms, contracts, guards,
and human governance.

## Core Boundary

```text
Worker = execution host
Cell = capability
Organ = capability composition
Agent = goal-directed coordinator
Character = social/personality surface
```

A worker may run cells later, but it is not a cell. A worker may host an agent
process later, but it is not an agent. A worker may be linked to a human-owned
machine, but it is not the human actor.

## Minimum Readiness Model

Before scheduling or execution exists, Worker Runtime should be able to model
these surfaces.

### Worker Identity

Stable identity for the execution host.

Candidate fields:

- `worker_id`
- `display_name`
- `worker_type`
- `owner_actor_id`
- `home_room_id`
- `created_at`
- `status`

Identity answers:

```text
Which execution host is this?
```

### Heartbeat

Freshness and liveness signal.

Candidate fields:

- `worker_id`
- `seen_at`
- `status`
- `runtime_version`
- `health_summary`

Heartbeat answers:

```text
Is this execution host currently visible and healthy enough to consider?
```

### Capability Profile

Declared execution inventory, not authorization.

Candidate fields:

- available cells
- supported runtimes
- supported tools
- operating system
- hardware hints
- network mode
- local paths or devices, if later allowed

Capability profile answers:

```text
What could this worker technically run?
```

It does not grant permission. Contracts, rooms, context stacks, resource
policies, and guards still decide whether the work may happen.

### Cost Profile

Expected cost and scarcity properties.

Candidate fields:

- compute class
- expected latency
- energy sensitivity
- monetary cost class
- local resource limits
- metering support

Cost profile answers:

```text
What does it cost or constrain to run work here?
```

### Privacy Profile

Data and exposure constraints.

Candidate fields:

- local-only flag
- network exposure level
- allowed sensitivity ceiling
- allowed room scope
- secret-handling support
- retention behavior

Privacy profile answers:

```text
What kinds of meaning or memory may safely reach this worker?
```

### Failure Semantics

Expected behavior when work cannot complete.

Candidate fields:

- timeout class
- retry policy
- partial-result policy
- lost-heartbeat policy
- failure audit requirement
- rollback or cleanup hint

Failure semantics answer:

```text
How does governed work fail without becoming silent or ambiguous?
```

## Safe Selection Rule

Later worker selection must be a governed decision, not a convenience lookup.

Before a worker can execute a task, the runtime should be able to prove:

- the worker identity is known
- heartbeat is fresh enough
- capability profile matches the requested cell or organ
- privacy profile is compatible with room, sensitivity, and context stack
- cost profile is compatible with resource grants or policies
- failure semantics are acceptable for the task risk
- guard pipeline allows execution
- the decision is traceable

## First Implementation Shape

The first implementation starts as model-only readiness:

```text
WorkerProfile
WorkerHeartbeat
```

After the model-only layer is stable, the next implementation should be
registration and inspection only:

```text
WorkerRegistry
worker-list
worker-show
```

No scheduling should be added until worker inspection is boring and tested.

No execution should be added until scheduling decisions are guardable,
persisted, and inspectable.

## Non-Goals

The readiness step must not introduce:

- remote code execution
- provider routing
- LLM gateway behavior
- autonomous agent spawning
- worker-to-worker federation
- dynamic permission creation
- trading or domain-specific execution
- dashboard-first worker management
- self-modifying worker behavior

## Relationship To Existing Governance

Worker Runtime extends the governed runtime baseline. It must not bypass:

- `Room`
- `ContextStack`
- `CellContract`
- `ResourceGrant`
- `GuardPipeline`
- `GovernanceDecision`
- `AuditLog`
- `EventLog`
- human approval semantics

The worker layer is allowed to make execution placement visible. It is not
allowed to make execution less accountable.

## Readiness Conclusion

The next safe step is not to run work on workers.

The current safe step is to define and test worker identity, heartbeat,
capability profile, cost profile, privacy profile, and failure semantics.

Inspection, storage, scheduling, and execution remain later steps.
