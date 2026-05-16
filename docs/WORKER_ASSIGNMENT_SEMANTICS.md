# Worker Assignment Semantics

This document defines when PiGenus may turn worker-readiness evidence into a
durable `WorkerAssignment` intent record.

It does not add a migration, scheduler, router, provider call, or execution
path.

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
- `WorkerAssignmentValidator`
- `WorkerAssignmentCreator`
- `worker-assignment-create`
- status transition semantics

Not implemented:

- status transition validator
- status transition service
- status transition commands
- worker reservation
- scheduling enforcement
- provider routing
- execution

## Evidence Rule

Assignment creation may use only matching allow evidence from Worker Execution
Preflight.

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

Assignment creation must prove that the requested assignment matches the
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

`worker-assignment-create` may create only:

```text
status = pending
```

It must not create `assigned` directly.

Rationale:

`pending` means governed assignment intent exists. `assigned` should later mean
that a separate activation or reservation boundary has accepted that intent.
Execution remains a later and separate lifecycle.

## Side-Effect Rule

Successful assignment creation must write:

- one `WorkerAssignment` record
- one `AuditLog` record

The audit record should use:

```text
action = "worker_assignment_created"
actor = assignment.created_by_actor_id
context = room-derived context for assignment.room_id where available
```

The audit details should include:

- `assignment_id`
- `worker_id`
- `capability`
- `room_id`
- `governance_decision_id`
- `status`

Assignment creation must not create or mutate a governance decision. The
governance decision is evidence for creation, not an output of creation.

It must not:

- create a worker
- create or mutate a governance decision
- create a routing record
- reserve capacity
- call a provider
- execute work
- store execution logs or execution results

Validation failure behavior remains intentionally narrow for the first creation
step: a failed validation must not create an assignment and must not write a
successful creation audit. A separate rejected-attempt audit can be decided
later if operator safety requires it.

## Implemented Validator

`WorkerAssignmentValidator` is a small service that checks:

- worker exists
- governance decision exists
- decision source is `worker_execution_preflight`
- decision result is `allow`
- decision family is `worker_execution_preflight`
- worker, capability, runtime, sensitivity, network, and room match
- requested initial status is `pending`

The repository may continue to enforce basic existence. The validator should
own semantic evidence checks before assignment intent is persisted.

The validator does not persist assignments. It only returns a validation
result.

## Implemented Creator

`WorkerAssignmentCreator` is a small service that:

1. validates the assignment with `WorkerAssignmentValidator`
2. persists exactly one pending `WorkerAssignment`
3. writes exactly one `worker_assignment_created` audit row
4. returns the created assignment and audit ID

It does not expose a CLI command.

`worker-assignment-create` is a thin CLI wrapper around this service. It does
not add scheduling, routing, reservation, provider calls, or execution.

## Status Transition Boundary

Status transitions describe assignment intent only. They do not prove that work
has started, reserve capacity, route to a provider, or store execution output.

Status meanings:

```text
pending
  Governed assignment intent exists, but it is not activated.

assigned
  A later activation or reservation boundary accepted the pending intent.
  This is still not execution proof.

rejected
  The pending intent was explicitly refused before activation.

cancelled
  The pending or assigned intent was withdrawn before execution.

expired
  The pending or assigned intent is no longer valid because time, evidence,
  room policy, worker state, or resource assumptions became stale.
```

Allowed transitions:

```text
pending  -> assigned
pending  -> rejected
pending  -> cancelled
pending  -> expired
assigned -> cancelled
assigned -> expired
```

Terminal states:

```text
rejected
cancelled
expired
```

Terminal states must not transition back into `pending` or `assigned`. If work
needs to be considered again after rejection, cancellation, or expiry, the
system should create a new assignment intent with fresh evidence instead of
reactivating the old record.

Forbidden transitions:

- `assigned -> pending`
- `assigned -> rejected`
- `rejected -> pending`
- `rejected -> assigned`
- `cancelled -> pending`
- `cancelled -> assigned`
- `expired -> pending`
- `expired -> assigned`

Same-status updates should be treated as no-ops unless a future command
explicitly supports metadata-only annotation. They should not create duplicate
status-change audit rows.

Transition side effects should be narrow:

- update the assignment status
- update `updated_at`
- preserve worker, capability, room, creator, and governance decision evidence
- write one audit row for successful status change
- avoid creating or mutating governance decisions
- avoid routing, reservation, provider calls, execution logs, or execution
  results

The future audit action should be:

```text
action = "worker_assignment_status_changed"
```

Audit details should include:

- `assignment_id`
- `worker_id`
- `capability`
- `room_id`
- `old_status`
- `new_status`
- `actor_id`
- `reason`, when provided

Future `pending -> assigned` activation may require additional governance or
approval evidence. If so, that evidence should be passed into the transition
boundary and referenced; the status transition itself should not silently create
the decision that authorizes it.

Out of scope for the next step:

- automatic status changes
- implicit assignment on scheduling preview
- assignment as execution proof
- execution result storage
- status transition commands
- status transition persistence implementation

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
