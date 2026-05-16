# Worker Assignment Semantics

This document defines when PiGenus may turn worker-readiness evidence into a
durable `WorkerAssignment` intent record.

It does not add a CLI command, validator, migration, scheduler, router,
provider call, or execution path.

## Purpose

`WorkerAssignment` is durable governed intent:

```text
this worker may be considered assigned to this capability under this evidence
```

It is not execution.

Assignment creation is the first step that turns a preview or preflight result
into stored intent. Because of that, creation must be stricter than read-only
inspection and stricter than generic decision-log existence.

## Current Boundary

Already implemented:

- `WorkerAssignment` model
- `WorkerAssignmentStatus`
- `WorkerAssignmentRepository`
- `worker_assignments` SQLite table
- read-only `worker-assignment-list`

Not implemented:

- `WorkerAssignmentValidator`
- `worker-assignment-create`
- assignment status transitions
- worker reservation
- scheduling enforcement
- provider routing
- execution

## Evidence Rule

Future assignment creation may use only matching allow evidence from Worker
Execution Preflight.

Allowed evidence:

```text
DecisionRecord.source == "worker_execution_preflight"
DecisionRecord.decision_type == "governance_decision"
DecisionRecord.details["decision"] == "allow"
DecisionRecord.details["family"] == "worker_execution_preflight"
```

Not sufficient:

- a generic existing decision record
- a scheduling-preview decision by itself
- a blocked preflight decision
- an escalated or review decision
- a human-readable reason without structured request details

Reason:

Scheduling Preview explains candidate suitability across workers. Execution
Preflight checks one concrete worker against one concrete capability request.
Assignment intent should be derived from the narrower evidence.

## Matching Rule

Future assignment creation must prove that the requested assignment matches the
preflight decision evidence.

The assignment must match:

- `worker_id`
- `capability`
- `required_runtime`, when present
- `sensitivity`, when present
- `network_required`
- `room_id`

The current preflight decision stores request details under:

```text
DecisionRecord.details["governance_decision"]["details"]["request"]
```

and worker identity under:

```text
DecisionRecord.details["governance_decision"]["details"]["worker_id"]
```

Room identity comes from the governance decision context and `room_id` carried
through the logged preflight decision.

## Creation Rule

Future `worker-assignment-create` may create only:

```text
status = pending
```

It must not create `assigned` directly.

Rationale:

`pending` means governed assignment intent exists. `assigned` should later mean
that a separate activation or reservation boundary has accepted that intent.
Execution remains a later and separate lifecycle.

## Side-Effect Rule

Future assignment creation may write one `WorkerAssignment` record.

It must not:

- create a worker
- create or mutate a governance decision
- create a routing record
- reserve capacity
- call a provider
- execute work
- store execution logs or execution results

Audit behavior is intentionally unresolved. It should be decided before a
creation command is implemented.

## Future Validator

The next code step should be a small `WorkerAssignmentValidator` or equivalent
service that checks:

- worker exists
- governance decision exists
- decision source is `worker_execution_preflight`
- decision result is `allow`
- decision family is `worker_execution_preflight`
- worker, capability, runtime, sensitivity, network, and room match
- requested initial status is `pending`

The repository may continue to enforce basic existence. The validator should
own semantic evidence checks before any CLI creation command exists.

## Status Transition Boundary

Future status transitions should be explicit and tested.

Initial candidate transitions:

```text
pending -> assigned
pending -> rejected
pending -> cancelled
pending -> expired
assigned -> cancelled
assigned -> expired
```

Out of scope for the next step:

- automatic status changes
- implicit assignment on scheduling preview
- assignment as execution proof
- execution result storage

## Rule Of Thumb

Assignment creation is allowed only when the system can answer:

```text
Which worker?
Which capability?
Which room?
Which preflight allow decision?
Which request details?
Why is this still only intent, not execution?
```

If any answer is missing, the assignment should not be created.
