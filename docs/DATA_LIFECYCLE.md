# PiGenus Data Lifecycle

This document maps how core PiGenus data objects live, move, persist, age, and
become inspectable.

It is a documentation map, not a schema change.

## Core Rule

Data in PiGenus should not appear, move, become memory, or influence behavior
without a visible lifecycle.

The lifecycle should preserve:

```text
source -> context/room -> meaning -> guard -> decision -> storage -> inspection
```

## Current Lifecycle Map

The current v0.3 governed runtime uses this practical flow:

```text
UserInput / TaskRequest
-> Event
-> MemoryProposal
-> GuardDecision
-> MemoryStored
-> optional MemoryObject lifecycle
-> optional MeaningObject ingestion
-> optional MeaningStore inspection
-> DecisionLog / AuditLog / EventLog inspection
```

The Systemform target shape is:

```text
MeaningObject
-> Event
-> GuardPipeline
-> DecisionTrace
-> GovernanceDecision
-> optional MeaningStore
-> optional EventLog
-> optional AuditLog
-> optional MemoryObject
-> optional Fossil
```

## Object Lifecycles

### Event

Purpose:

Runtime trace of something requested, produced, or observed.

Lifecycle:

```text
created -> validated -> persisted -> listed/shown -> retained
```

Current storage:

- `events` table
- `EventRepository`
- `event-list`
- `event-show`

Boundary:

An event records runtime flow. It does not explain governance reasoning by
itself.

### MeaningObject

Purpose:

Structured semantic object carrying meaning, room, truth status, sensitivity,
confidence, provenance, source, and time metadata.

Lifecycle:

```text
created/adapted -> validated -> optionally guarded -> stored -> queried -> revised later
```

Current storage:

- `meaning_objects` table
- `MeaningRepository`
- `meaning-list`
- `meaning-show`

Boundary:

A MeaningObject is not automatically durable memory and is not raw text.

### MemoryObject

Purpose:

Durable local memory record managed by lifecycle rules.

Lifecycle:

```text
proposed -> guarded -> stored -> fresh/active/watch/stale/dormant/dead/fossil/canonical
```

Current storage:

- `memory_objects` table
- `MemoryRepository`
- memory lifecycle engine
- `memory-list`

Boundary:

MemoryObject is the current durable memory object. It can be adapted into a
MeaningObject, but it is not the full semantic communication layer.

### GovernanceDecision

Purpose:

Explanation of why a guard or governance result allowed, warned, blocked,
escalated, quarantined, revoked, or archived something.

Lifecycle:

```text
guard result -> decision record -> persisted -> inspected -> summarized
```

Current storage:

- decision log table
- `decision-list`
- `guard-decision-list`
- `guard-decision-summary`

Boundary:

A GovernanceDecision is not an event and not an audit log. It explains policy
reasoning.

### DecisionTrace

Purpose:

Ordered reasoning path for a guard or governance result.

Lifecycle:

```text
guard step -> ordered trace -> serialized in decision details -> inspected
```

Current storage:

- serialized inside governance decision details

Boundary:

Trace order matters. A trace should not become an unordered note field.

### EventLog

Purpose:

Chronological runtime event record.

Lifecycle:

```text
event persisted -> listed -> shown -> retained
```

Current storage:

- `events` table
- event inspection CLI

Boundary:

EventLog shows what flowed. It does not replace governance decisions or audit
logs.

### AuditLog

Purpose:

Append-only operational and safety-relevant record.

Lifecycle:

```text
action/lifecycle change -> audit record -> read-only inspection -> retained
```

Current storage:

- audit log repository/table
- `audit-list`

Boundary:

AuditLog records operational accountability. It is not the main event stream
and not the policy explanation.

### Fossil

Purpose:

Preserved inactive historical state.

Lifecycle:

```text
dormant/expired -> fossil -> retained for history -> not active truth
```

Current storage:

- `MemoryStatus.FOSSIL`
- memory lifecycle behavior

Future relation:

Evolution Sandbox may also use fossil records for rejected or replaced
mutations.

Boundary:

Fossil is not deletion. It is preserved inactive history.

### WorkerProfile

Purpose:

Durable local identity and capability envelope for a known execution host.

Lifecycle:

```text
created -> validated -> stored -> inspected later -> suspended/retired later
```

Current storage:

- `worker_profiles` table
- `WorkerRepository` in `pigenus/storage/worker_repositories.py`

Boundary:

A WorkerProfile describes where work may run later. It is not permission,
scheduling, routing, or execution.

### WorkerHeartbeat

Purpose:

Current liveness signal for a known worker.

Lifecycle:

```text
observed -> validated against known worker -> stored as latest/current -> replaced by fresher heartbeat
```

Current storage:

- `worker_heartbeats` table
- `WorkerRepository` in `pigenus/storage/worker_repositories.py`

Boundary:

The first heartbeat store keeps current state only. It is not heartbeat
history, health repair, scheduling, or execution proof.

### WorkerAssignment

Purpose:

Future durable intent that one governed capability is assigned to one worker.

Lifecycle:

```text
governance evidence -> validation -> pending assignment + audit -> assigned/rejected/cancelled/expired -> retained for inspection
```

Allowed status transitions:

```text
pending  -> assigned
pending  -> rejected
pending  -> cancelled
pending  -> expired
assigned -> cancelled
assigned -> expired
```

`rejected`, `cancelled`, and `expired` are terminal lifecycle states.

Current storage:

- `worker_assignments` table
- `WorkerAssignmentRepository` in `pigenus/storage/worker_repositories.py`
- `WorkerAssignmentCreator` for validated creation plus audit
- `worker-assignment-create` for CLI creation of pending assignment intent
- full `WorkerAssignment` JSON plus indexed worker, status, room, capability,
  and governance-decision columns

Boundary:

WorkerAssignment is not execution. It does not store start time, completion
time, execution result, provider route, reservation, or tool call state.
Assignment persistence requires a known worker and existing governance decision
evidence.
Successful assignment creation must also write a
`worker_assignment_created` audit row so creation of durable intent is
operationally accountable.

### MutationProposal

Purpose:

Future proposed change to behavior, policy, prompt, routing, or code.

Lifecycle:

```text
proposal -> shadow mode -> fitness comparison -> guard checks -> human approval -> activation or fossil
```

Current storage:

- not implemented
- documented in `docs/EVOLUTION_SANDBOX.md`

Boundary:

MutationProposal is never activation.

## Lifecycle Questions

Every new data object should answer:

```text
1. Where did it come from?
2. Which room or context does it belong to?
3. What truth status or confidence does it carry?
4. What sensitivity does it carry?
5. Which actor or cell created it?
6. Which guard or policy checked it?
7. Which decision explains it?
8. Which log or repository preserves it?
9. How can an operator inspect it?
10. When does it become stale, dormant, dead, fossil, or canonical?
```

## Current Gaps

The current runtime is intentionally minimal. Known lifecycle gaps:

- MeaningObject does not yet have a full review/expiry lifecycle.
- DecisionTrace is serialized inside decisions, not a first-class repository.
- ContextStack is ontology-only and not yet attached to task lifecycle.
- HumanApproval is a stub and does not yet enforce approval transitions.
- MutationProposal is documented but not implemented.
- Worker output lifecycle is documented but not implemented.
- Worker heartbeat history is not implemented.
- LLM output lifecycle is not implemented because LLMGateway is not present.

These are not bugs in v0.3. They are future work boundaries.

## Non-Goals

- No new database tables from this document
- No schema changes
- No vector search
- No automatic lifecycle mutation for MeaningObject
- No active mutation workflow
- No worker or LLM lifecycle implementation

## Current Conclusion

PiGenus data should remain explainable over time.

The system should be able to answer:

```text
What is this?
Where did it come from?
Why was it allowed?
Where was it stored?
How can it be inspected?
When does it stop being active truth?
```
