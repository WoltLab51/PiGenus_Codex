# WorkerAssignmentRoomContextRecheckValidator Cell-DNA

This document applies `docs/CELL_DNA_PROTOCOL.md` to the future
`WorkerAssignmentRoomContextRecheckValidator`.

The current implementation is read-only and repository-backed for existing
assignment, worker, and decision evidence. It does not add schemas,
migrations, CLI behavior, logging behavior, graph projection, RuntimeCell
behavior, CellRegistry behavior, scheduling enforcement, reservation, routing,
provider calls, execution logs, or execution.

## Capability

Evaluate whether an existing WorkerAssignment intent is still compatible with
its assignment room, worker home room, and supplied operating context before
future scheduling consideration.

This capability answers:

```text
Is this WorkerAssignment still valid for its governance room and context
envelope?
```

It does not answer:

```text
May scheduling proceed?
Should capacity be reserved?
Which provider should receive the work?
Should execution start?
```

Room/context recheck is one scheduling-readiness input, not scheduling
enforcement.

## Maturity

```text
CapabilityCell / GovernedCellCandidate
```

Current maturity is a read-only CapabilityCell implementation and
GovernedCellCandidate. RuntimeCell maturity is explicitly later.

Current implementation shape:

```text
pigenus.core.worker_assignment_room_context_recheck.WorkerAssignmentRoomContextRecheckValidator
```

RuntimeCell maturity is explicitly later.

## Inputs

Current first implementation inputs:

- assignment ID
- optional ContextStack supplied by caller
- optional ContextFrames supplied by caller
- optional source room ID if future payload movement is being evaluated
- optional target room ID if future payload movement is being evaluated

Runtime data resolved from assignment ID:

- WorkerAssignment intent
- assignment status
- WorkerAssignment room ID
- worker ID
- worker profile
- worker home room ID
- referenced preflight governance decision
- preflight evidence room ID

Inputs that do not exist yet must remain optional and explicit. Missing future
inputs should become stable reasons, not hidden permission.

## Outputs

Current output:

- `WorkerAssignmentRoomContextRecheckResult`
- assignment ID
- outcome
- context-compatible boolean
- stable reason codes
- details for caller/operator display

Suggested outcomes:

- `allow_context`
- `require_review`
- `deny_context`
- `not_considered`

Suggested initial reasons:

- `assignment_unknown`
- `assignment_status_not_considered`
- `room_missing`
- `room_evidence_mismatch`
- `worker_unknown`
- `worker_home_room_mismatch`
- `context_stack_missing`
- `context_stack_not_evaluated`
- `context_room_mismatch`
- `context_policy_mismatch`
- `room_flow_review_required`
- `room_flow_blocked`
- `high_risk_room_requires_approval`
- `room_context_recheck_passed`

Reason names may be refined before implementation. Once implemented and
tested, reason codes should remain stable.

## Reads

The current implementation may read:

- `WorkerAssignmentRepository`
- `WorkerRepository`
- `DecisionRepository`
- WorkerAssignment status and room ID
- WorkerProfile home room ID
- preflight decision source/type/family/details
- preflight evidence room ID
- supplied ContextStack and ContextFrames
- `RoomFlowRules` when source and target rooms imply meaning or payload flow

It should not own persistence for ContextStack, ContextFrame, Room, or policy
records in the first implementation.

## Writes

```text
none
```

The validator is read-only.

## Allowed Effects

The validator may:

- perform read-only room/context recheck
- verify assignment room is present
- verify preflight evidence room still matches assignment room
- compare worker home room and assignment room
- inspect supplied ContextStack / ContextFrames for room or policy conflicts
- evaluate RoomFlowRules only when source/target room movement is explicitly
  supplied
- return `allow_context`, `require_review`, `deny_context`, or
  `not_considered`
- return stable reason codes
- return details for caller/operator use

## Forbidden Effects

The validator must not:

- mutate WorkerAssignment
- create WorkerAssignment intent
- transition WorkerAssignment status
- write audit records
- write decision records
- log eligibility or enforcement results
- enforce scheduling
- reserve capacity
- route to providers
- call providers
- execute work
- create execution logs
- store execution results
- mutate worker profiles or heartbeats
- create ContextStack records
- create ContextFrame records
- create Room records
- create policy records
- use graph projection as source of truth
- become a RuntimeCell
- register itself in a CellRegistry

## Trace / Audit Behavior

No trace, audit, or decision record is persisted by the validator itself.

It may return:

- outcome
- reason codes
- assignment room ID
- worker home room ID
- evidence room ID
- context stack ID if supplied
- frame IDs or conflicting frame references if supplied
- room-flow decision if evaluated

Those returned details may be used by a caller or operator surface later, but
the validator itself must not create audit rows or governance decisions.

## State / Lifecycle Assumptions

The future validator assumes:

- assignment intent is not execution proof
- `assigned` is not scheduling permission
- room identity must be rechecked after assignment creation
- worker home room is a governance signal, not an execution grant
- missing ContextStack must not silently grant permission
- missing ContextStack also must not automatically block every current
  assignment path
- high-risk rooms may later require explicit ContextStack and approval inputs
- RoomFlowRules apply only when meaning, memory, task output, execution result,
  or audit-visible payload would cross rooms

It does not:

- move assignments between lifecycle states
- expire assignments
- create room policy
- create context stacks
- decide freshness
- decide resource or risk budget
- decide reservation
- decide execution

## Tests

Implemented tests:

- matching assignment room and preflight evidence room passes room identity
  check
- missing assignment returns `not_considered`
- non-considered assignment status returns `not_considered`
- mismatched evidence room denies room/context compatibility
- missing worker returns deny or not-considered according to final policy
- worker home room mismatch requires review
- missing ContextStack requires review and does not silently grant permission
- supplied ContextFrame room mismatch denies room/context compatibility
- supplied ContextFrame policy mismatch denies room/context compatibility
- RoomFlowRules review/block outcomes are carried as reasons when applicable
- no assignment writes occur during validation
- no audit writes occur during validation
- no decision writes occur during validation
- no context, room, or policy records are created
- no reservation, routing, provider, execution-log, or execution writes occur

## Non-Goals

This Cell-DNA does not add:

- runtime code
- schemas
- migrations
- persistence for ContextStack or ContextFrame
- room storage
- policy storage
- CLI inspection
- logging
- decision persistence
- audit persistence
- scheduling enforcement
- reservation
- routing
- provider calls
- execution
- heartbeat history
- resource/risk budget checks
- approval workflow
- RuntimeCell behavior
- CellRegistry behavior
- graph projection

## Next Possible Maturity

Current safe maturity:

```text
CapabilityCell with a read-only implementation and targeted tests.
```

The first implementation is narrow and repository-backed only for existing
assignment, worker, and decision evidence. ContextStack and ContextFrame inputs
are caller-supplied until a separate persistence and inspection plan exists.

Later maturity:

```text
GovernedCell with explicit contract and returned trace.
```

RuntimeCell maturity is only possible after CellRegistry, CellContract,
lifecycle inspection, runtime execution boundary, and operator inspection
surfaces exist.
