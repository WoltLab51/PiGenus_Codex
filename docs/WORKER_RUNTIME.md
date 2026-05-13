# Worker Runtime

Worker Runtime is a future GENUS architecture track. It is not part of the
v0.3 governed runtime implementation.

The purpose of this document is to separate four concepts that are easy to mix:

```text
Worker = execution place
Cell = capability
Organ = capability composition
Agent = goal-directed coordinator
```

## Core Distinction

Workers carry execution. Cells carry capability. Organs carry composition.
Agents carry goal direction.

This means a worker is not automatically intelligent. A worker is the machine,
process, device, or runtime environment that can execute known capabilities
under governance.

## Worker

A worker is an execution host with a known profile.

Examples:

- a Raspberry Pi
- a local PC
- a Python process
- a server
- a GPU machine
- a future external provider

Worker properties may include:

- `worker_id`
- hardware profile
- runtime profile
- supported operating systems
- available tools
- available cells
- capability limits
- cost profile
- privacy level
- network access
- status
- heartbeat

A worker answers:

```text
Where can this run, under which constraints?
```

## Cell

A cell is one bounded capability or function.

Examples:

- `log_reader`
- `memory_writer`
- `meaning_ingester`
- `guard_checker`
- `summary_writer`

A cell answers:

```text
What can be done?
```

Cells remain governed by contracts, rooms, permissions, resources, and audit
requirements.

## Organ

An organ is a coordinated composition of cells.

Example:

```text
LogAnalysisOrgan =
  log_reader
  pattern_detector
  explanation_writer
  meaning_writer
```

An organ answers:

```text
Which capabilities work together as one functional unit?
```

An organ is not a machine. It may run on one worker or be distributed later,
but that is an execution decision, not its identity.

## Agent

An agent is a goal-directed coordinator that uses cells or organs to complete a
task.

Example:

```text
DiagnosticsAgent:
  goal = explain why the runtime became unstable
  organ = LogAnalysisOrgan
  room = room_developer
  context_stack = diagnostics_readonly_full_trace
```

An agent answers:

```text
Who or what is pursuing this goal?
```

Agents must not imply unrestricted autonomy. They remain actors under contracts
and guard decisions.

## Relationship To Rooms And ContextStack

`Room` remains the governance, protection, and memory boundary.

`ContextStack` describes the operating envelope for a task.

Worker selection must respect both:

- the room where work is allowed
- the context stack describing the task conditions
- the contracts governing the actor, cell, organ, or agent
- the resource grants available for execution

## Safe Execution Rule

No worker should execute a capability unless all of these are true:

- the worker is known and healthy
- the cell capability is known
- the actor or agent has a valid contract
- the room permits the action
- the context stack is compatible
- resource limits are available
- guard decision allows execution
- the execution can be traced

## Not In The First Worker Runtime

Do not start Worker Runtime with:

- arbitrary remote code execution
- opaque provider routing
- autonomous agent spawning
- dynamic permission creation
- trading execution
- federation
- self-modifying workers

The first worker runtime should be boring: local-first, inspectable, heartbeat
based, and governed by existing contracts.

## First Safe Implementation Shape

When implemented, Worker Runtime should start as inspection and registration:

```text
WorkerProfile
WorkerRegistry
worker-list
worker-show
heartbeat status
capability inventory
```

Only after that should scheduling or execution routing be considered.

## Relationship To v0.3

v0.3 provides the governed runtime baseline.

Worker Runtime comes later because execution across machines or processes
increases risk. The right order is:

```text
governed local runtime -> worker inventory -> worker routing -> worker execution
```

The worker layer must extend the v0.3 governance model, not bypass it.
