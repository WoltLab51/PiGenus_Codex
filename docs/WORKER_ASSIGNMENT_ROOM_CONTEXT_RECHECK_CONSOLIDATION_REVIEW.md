# WorkerAssignment Room / Context Recheck Consolidation Review

This review consolidated the first read-only
`WorkerAssignmentRoomContextRecheckValidator` implementation before it was
wired into scheduling eligibility, exposed through CLI, logged, or used by any
future scheduling-enforcement boundary.

It is documentation-only. It does not add runtime code, schemas, migrations,
CLI behavior, logging behavior, graph projection, RuntimeCell behavior,
CellRegistry behavior, scheduling enforcement, reservation, routing, provider
calls, execution logs, or execution.

## Implemented Surface

The current implementation is:

```text
pigenus.core.worker_assignment_room_context_recheck.WorkerAssignmentRoomContextRecheckValidator
```

It checks whether an already assigned WorkerAssignment intent still appears
compatible with its room and caller-supplied operating context.

Inputs:

- assignment ID
- optional `ContextStack`
- optional `ContextFrame` list
- optional source room ID
- optional target room ID

Reads:

- `WorkerAssignmentRepository`
- `WorkerRepository`
- `DecisionRepository`
- optional `RoomFlowRules` supplied at construction time

Writes:

- none

Outputs:

- `allow_context`
- `require_review`
- `deny_context`
- `not_considered`
- ordered reason codes
- details for operator / caller use

## Philosophy Alignment

```text
Philosophy-Fit: green
Governance-Fit: green
Cellular-Fit: green
Worker-Boundary-Fit: green
RuntimeShape-Fit: green
Overengineering-Risk: low
Monolith-Risk: low
Recommendation: accept, then decide whether to wire read-only into eligibility
```

Why this fits:

- It keeps `assigned` separate from execution proof.
- It treats worker room, assignment room, context, and room-flow state as
  current scheduling-readiness inputs, not permanent grants.
- It is a CapabilityCell / GovernedCellCandidate shaped validator, not a
  RuntimeCell.
- It is read-only and has no operator surface yet.
- It strengthens scheduling-readiness without enabling scheduling.

## Boundary Confirmation

The validator does not:

- mutate WorkerAssignment state
- transition assignment status
- create WorkerAssignments
- write audit events
- write governance decisions
- log eligibility or enforcement results
- reserve capacity
- route providers
- call providers
- create execution logs
- execute work
- persist ContextStacks, ContextFrames, Rooms, RoomFlowRules, or policies
- update a graph projection
- activate RuntimeCells or dynamic routing

These boundaries are part of the acceptance criteria for this consolidation.

## Result Semantics

`allow_context` means:

- assignment exists
- assignment status is `assigned`
- assignment room and referenced governance evidence align
- worker exists
- worker home room does not conflict with assignment room
- supplied ContextStack / ContextFrames do not contradict the assignment
  room or capability
- supplied RoomFlowRules do not require review or block the explicit
  source/target flow

`require_review` means:

- a worker home room mismatch exists
- the ContextStack was not supplied / not evaluated
- RoomFlowRules require review for the supplied source/target room movement

`deny_context` means:

- governance evidence room conflicts with assignment room
- the worker is missing for an otherwise existing assignment
- a ContextFrame contradicts assignment room or capability
- RoomFlowRules block the supplied source/target room movement

`not_considered` means:

- the assignment does not exist
- the assignment exists but is not in `assigned` status

## Test Evidence

Targeted verification for the implementation covered:

```text
.venv\Scripts\python.exe -m pytest tests\test_worker_assignment_room_context_recheck.py tests\test_worker_assignment_scheduling_eligibility.py
-> 26 passed
```

Full suite verification for the implementation covered:

```text
.venv\Scripts\python.exe -m pytest
-> 328 passed
```

The targeted tests cover:

- matching assignment room, evidence room, worker home room, and context
- unknown assignment
- non-assigned assignment status
- evidence-room mismatch
- worker home-room mismatch
- unknown worker after assignment exists
- missing ContextStack
- ContextFrame room mismatch
- ContextFrame capability policy mismatch
- RoomFlow review
- RoomFlow block
- no-write proof for assignments, decisions, and audit

## Remaining Gaps

This consolidation does not claim scheduling readiness is complete.

Known gaps after the first implementation consolidation:

- no CLI inspection for room/context recheck
- wired into scheduling eligibility only when explicitly supplied by the
  caller; no default CLI or logging path uses it yet
- no persisted ContextStack / ContextFrame attachment to WorkerAssignment
- no room policy store
- no high-risk room approval policy
- no resource budget, risk budget, reflex, or kill-switch boundary
- no reservation boundary
- no scheduling-enforcement validator
- no worker execution path

These gaps are intentional. The validator is one scheduling-readiness input,
not scheduling permission.

## Recommendation

Accept the read-only `WorkerAssignmentRoomContextRecheckValidator` as the next
small readiness boundary.

Do not add CLI, logging, scheduling enforcement, reservation, routing,
provider calls, execution logs, or execution from this review.

Next safe step:

```text
Consolidate the read-only room/context scheduling eligibility integration.
```

The current integration must continue to:

- remain read-only
- not change assignment status
- not create audit events
- not create governance decisions unless a separate explicit logging decision
  exists
- not imply scheduling enforcement
- not reserve, route, call providers, create execution logs, or execute work
- keep missing context visible as review / not-ready evidence rather than
  hidden permission

## Stop Lines

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
