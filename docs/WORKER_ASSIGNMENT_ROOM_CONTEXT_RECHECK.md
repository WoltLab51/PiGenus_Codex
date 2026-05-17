# WorkerAssignment Room / Context Recheck

This document defines room and context recheck semantics for future
WorkerAssignment scheduling consideration.

It is documentation-only. It does not add runtime code, schemas, migrations,
CLI behavior, logging behavior, graph projection, RuntimeCell behavior,
CellRegistry behavior, scheduling enforcement, reservation, routing, provider
calls, execution logs, or execution.

## Purpose

WorkerAssignment now has a governed intent chain:

```text
preflight evidence
-> assignment intent
-> lifecycle transition
-> scheduling eligibility inspection
-> freshness-integrated eligibility
```

That chain still is not enough for scheduling enforcement.

The next boundary is room and context recheck:

```text
Is the assignment still valid for its room and operating context at the moment
future scheduling consideration would happen?
```

This must be checked before any scheduling-enforcement validator, reservation,
routing, provider call, execution log, or execution can exist.

## Canonical Definitions

`Room` remains the governance, protection, and memory boundary.

`ContextFrame` is one condition around an action.

`ContextStack` is the concrete operating envelope assembled from frames.

`WorkerAssignment.room_id` identifies the room under which the assignment
intent was created. It is not a permanent grant to schedule or execute.

`WorkerProfile.home_room_id` identifies the worker's registered home or
governance room. It is not proof that the worker may execute every assignment
in that room.

## Core Rule

Room and context must be rechecked at scheduling-consideration time.

Assignment creation proves that the original preflight evidence matched the
assignment request. It does not prove that the room, context, worker posture,
or policy is still valid later.

Future scheduling consideration must not rely only on:

- `WorkerAssignment.status = assigned`
- a previously logged preflight allow decision
- a previously logged eligibility decision
- a worker being currently active
- a room ID string being present

Those are inputs, not permission.

## Recheck Inputs

A future read-only room/context recheck may inspect:

- WorkerAssignment ID
- WorkerAssignment status
- WorkerAssignment room ID
- worker ID
- worker home room ID
- worker capability request
- referenced preflight governance decision
- current room policy, when available
- current ContextStack, when available
- relevant ContextFrames, when available
- current room-flow rules if meaning would cross rooms
- current guard / decision evidence, when explicitly provided

The first implementation may be conservative and use only the inputs that
already exist. Missing future inputs should produce stable review or
not-considered reasons rather than hidden allow behavior.

## Required Checks

A future recheck should answer these questions in order:

1. Does the WorkerAssignment exist?
2. Is it in a status that may be considered?
3. Does it have a non-empty `room_id`?
4. Does the referenced preflight evidence still carry the same `room_id`?
5. Does the current worker profile exist?
6. Does the worker's home room conflict with the assignment room?
7. If a ContextStack is provided, is it compatible with the assignment room?
8. If ContextFrames reference rooms or policies, do they contradict the
   assignment room?
9. If work would move meaning between rooms, do RoomFlowRules allow, review,
   or block that movement?
10. If the room is high-protection or high-risk, are review / approval
    thresholds still unresolved?

The first read-only validator does not need to solve every future check. It
must make unsupported checks visible instead of silently treating them as
allowed.

## Suggested Outcomes

Room/context recheck should use the same broad outcome family as other worker
readiness checks:

```text
allow_context
require_review
deny_context
not_considered
```

Suggested initial reason codes:

```text
assignment_unknown
assignment_status_not_considered
room_missing
room_evidence_mismatch
worker_unknown
worker_home_room_mismatch
context_stack_missing
context_stack_not_evaluated
context_room_mismatch
context_policy_mismatch
room_flow_review_required
room_flow_blocked
high_risk_room_requires_approval
room_context_recheck_passed
```

Reason names may be refined before implementation, but they must stay stable
once tests and operator output depend on them.

## Worker Home Room Semantics

Worker home room is a governance signal, not an execution grant.

If `worker.home_room_id` differs from `assignment.room_id`, the first safe
treatment is review, not automatic deny or allow. Some future configurations
may intentionally run shared workers across rooms, but that must be policy,
not accident.

Suggested first behavior:

```text
same room -> continue
different known rooms -> require_review
missing worker home room -> require_review
unknown worker -> deny / not considered through worker checks
```

## ContextStack Semantics

ContextStack is implemented as ontology but is not yet persisted or attached
to WorkerAssignment lifecycle.

Therefore:

- missing ContextStack must not imply permission
- missing ContextStack also must not block every current WorkerAssignment path
  by default
- first room/context recheck may report `context_stack_not_evaluated`
- high-risk rooms may later require an explicit ContextStack before scheduling
  consideration

This keeps current WorkerAssignment behavior compatible while making the
future gap visible.

## RoomFlow Semantics

RoomFlowRules govern movement between rooms, especially meaning movement.

WorkerAssignment room/context recheck is not automatically a room flow. If no
meaning or output is crossing a room boundary, the recheck should not invent a
room-flow decision.

RoomFlowRules become relevant when future scheduling consideration would move
meaning, memory, task output, execution result, or audit-visible payload from
one room to another.

## Side Effects

Room/context recheck must be read-only at first.

It must not:

- mutate WorkerAssignment
- transition WorkerAssignment status
- write audit rows
- write governance decisions
- log eligibility or enforcement results
- reserve capacity
- route providers
- call providers
- write execution logs
- execute work
- update graph projections
- create ContextStack records
- create Room records
- create policy records

## Relationship To Freshness

Freshness answers:

```text
Are the heartbeat and preflight evidence recent enough?
```

Room/context recheck answers:

```text
Is the assignment still valid for its governance room and operating context?
```

Both are scheduling-readiness inputs. Neither one is scheduling enforcement by
itself.

## Future Validator Shape

The first read-only implementation is:

```text
WorkerAssignmentRoomContextRecheckValidator
```

Current first shape:

- Maturity: `CapabilityCell / GovernedCellCandidate`
- Inputs: assignment ID, optional ContextStack / ContextFrame data, explicit
  current room policy inputs where available
- Reads: WorkerAssignmentRepository, WorkerRepository, DecisionRepository,
  optional context inputs supplied by caller
- Writes: none
- Output: stable outcome, ordered reasons, details
- Forbidden effects: no assignment mutation, no audit write, no decision
  logging, no scheduling enforcement, no reservation, no routing, no provider
  call, no execution

The Cell-DNA frame for that validator now lives in
`docs/CELL_DNA_WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK_VALIDATOR.md`.

The first implementation consolidation now lives in
`docs/WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK_CONSOLIDATION_REVIEW.md`.

## Validator Test Expectations

Current and future tests should prove:

- matching assignment room and evidence room passes the room identity check
- mismatched evidence room denies or requires review according to final policy
- worker home room mismatch requires review
- missing context stack does not silently allow high-risk rooms
- context frame room mismatch is visible
- room flow review/block outcomes are carried as reasons when applicable
- no assignment writes
- no audit writes
- no decision writes
- no reservation, routing, provider, execution-log, or execution writes

## Current Recommendation

Accept this semantics document as the current room/context boundary.

Next safe step:

```text
Decide whether and how to wire WorkerAssignmentRoomContextRecheckValidator
into assigned-intent scheduling eligibility as a read-only input.
```

Still not next:

- worker execution
- scheduling enforcement
- reservation
- provider routing
- provider calls
- execution logs
- execution results
- remote worker discovery
- heartbeat history
- graph projection
- RuntimeCell implementation
- CellRegistry implementation
- dynamic cell routing
- trading or other high-risk live behavior
