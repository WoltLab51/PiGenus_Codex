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

## Source Of Truth Policy

Worker data must not come from hidden defaults or network discovery.

The planned source of truth for durable worker identity is SQLite:

```text
worker_profiles
```

The planned source of truth for current worker liveness is also SQLite-backed,
but heartbeats have different semantics:

```text
worker_heartbeats = latest/current liveness signal
worker_heartbeat_history = optional later audit or telemetry history
```

A local file may be used later as an import or bootstrap format, but it should
not be treated as runtime truth after import.

Discovery is explicitly out of scope until federation, trust, signatures,
remote rooms, and privacy boundaries exist.

This means `worker-list` and `worker-show` should eventually read from a
governed SQLite worker store, not from invented demo workers, ad hoc config, or
network scans.

## First Implementation Shape

The first implementation starts as model-only readiness:

```text
WorkerProfile
WorkerHeartbeat
```

After the model-only layer is stable, the next implementation starts as a
storage-free registry:

```text
WorkerRegistry
```

After the storage-free registry is stable, the next implementation should be
read-only inspection service:

```text
WorkerInspection
WorkerInspectionService
```

After the inspection service is stable, the first CLI reads from the SQLite
Worker Store:

```text
worker-list
worker-show
```

No scheduling should be added until worker inspection is boring and tested.

Before real scheduling, PiGenus may use storage-free scheduling preview:

```text
WorkerSchedulingRequest
WorkerSchedulingPreview
```

Scheduling preview explains which known workers appear suitable for a requested
capability under simple constraints. It does not reserve, assign, route, or
execute work.

Scheduling preview may convert its result into a `GovernanceDecision` so the
reasoning shape is compatible with later decision logging. This conversion does
not persist by itself.

Scheduling preview may be logged explicitly through
`WorkerSchedulingPreviewLogger`, which writes the governance-shaped preview to
the existing decision log with source `worker_scheduling_preview`. Logging is
opt-in; plain preview and conversion remain non-persistent.

The first scheduling preview CLI is read-only:

```text
worker-scheduling-preview
```

It reads worker profiles and current heartbeats from SQLite, builds temporary
in-memory preview state, prints candidate suitability, and does not expose
logging unless `--log` is provided.

With `--log`, the command writes exactly one governance decision record through
`WorkerSchedulingPreviewLogger`. The logged record requires explicit actor and
room metadata and may include an event ID. This is still not scheduling.

After scheduling preview is inspectable, PiGenus may use storage-free execution
preflight:

```text
WorkerExecutionPreflightRequest
WorkerExecutionPreflightResult
```

Execution preflight checks one specific worker against known-worker state,
considerable status, capability, runtime, sensitivity, and network constraints.
It may produce a log-compatible `GovernanceDecision`, but it does not assign,
reserve, route, call providers, persist by itself, or execute work.

Execution preflight may be logged explicitly through
`WorkerExecutionPreflightLogger`, which writes the governance-shaped preflight
result to the existing decision log with source `worker_execution_preflight`.
Logging is opt-in; plain preflight and conversion remain non-persistent.

No execution should be added until scheduling decisions are guardable,
persisted, and inspectable.

After preflight logging is explicit, PiGenus may define the first model-only
assignment shape:

```text
WorkerAssignment
WorkerAssignmentStatus
```

A worker assignment is durable intent to place a capability on a worker later.
It must reference governance decision evidence, but it does not start work,
reserve capacity, route providers, call tools, or store execution results.
Assignment creation remains out of scope until a separate storage and
inspection plan exists.

## Non-Goals

The readiness step must not introduce:

- remote code execution
- assignment creation from CLI or runtime paths
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

Read-only CLI inspection is now the current operator surface. Storage-free
scheduling preview, governance-decision conversion, and opt-in preview logging
are the current preparation surfaces. `worker-scheduling-preview` exposes that
reasoning to operators. With `--log`, it may create a decision record, but it
still does not create assignments.

Storage-free Worker Execution Preflight is now the current execution-readiness
surface. It checks eligibility, not execution.

The first preflight CLI is read-only unless `--log` is provided:

```text
worker-execution-preflight
```

It exposes ordered execution eligibility checks for one worker. With `--log`,
the command writes exactly one governance decision record through
`WorkerExecutionPreflightLogger`. The logged record requires explicit actor and
room metadata and may include an event ID. This is still not assignment,
reservation, routing, provider access, or execution.

Model-only WorkerAssignment now defines the later assignment record shape. It
does not create assignment storage or assignment commands.

Assignment storage, scheduling, and execution remain later steps.
