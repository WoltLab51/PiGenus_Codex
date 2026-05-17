# WorkerAssignmentStatusTransitionService Cell-DNA

This document applies `docs/CELL_DNA_PROTOCOL.md` to
`WorkerAssignmentStatusTransitionService`, the first lifecycle-changing
WorkerAssignment capability with an applied Cell-DNA frame.

This is documentation only. It does not change runtime code, schemas,
migrations, CLI behavior, logging behavior, eligibility logging, decision
logging, scheduling behavior, worker execution, CellRegistry behavior, graph
projection, or RuntimeCell behavior.

## Capability

Apply a validated WorkerAssignment status transition.

This capability answers:

```text
Should this WorkerAssignment lifecycle status move from its current status to
the requested target status?
```

It does not schedule, reserve, route, call providers, or execute work.

## Maturity

```text
CapabilityCell / GovernedCellCandidate
```

Current implementation shape:

```text
pigenus.core.worker_assignment_status_transition.WorkerAssignmentStatusTransitionService
```

It is not a RuntimeCell.

## Inputs

Primary inputs:

- assignment id
- target status
- actor id
- optional reason

Resolved runtime input:

- current WorkerAssignment state

Supporting input:

- `WorkerAssignmentStatusTransitionValidator`
- `WorkerAssignmentRepository`
- `AuditLogger`

The transition validator receives actor and reason values and returns the
transition validation result.

## Outputs

Returns:

- `WorkerAssignmentStatusTransitionResult`
- updated WorkerAssignment on success
- audit id on success
- validation result
- validation errors / reason codes on rejection

Successful transition means:

```text
assignment lifecycle status was updated
updated_at was changed
status-change audit was written
no scheduling, reservation, routing, provider call, or execution occurred
```

## Reads

The service may read:

- `WorkerAssignmentRepository`
- current WorkerAssignment state
- `WorkerAssignmentStatusTransitionValidator`
- actor id supplied by caller
- reason supplied by caller, when present

It does not read worker heartbeat, scheduling queues, provider state, graph
state, or execution state.

## Writes

On success, the current implementation writes:

- exactly one WorkerAssignment status/update mutation
- `updated_at`
- exactly one existing audit event through `AuditLogger`

The audit action is:

```text
worker_assignment_status_changed
```

On rejected transition, missing assignment, unknown target status, terminal
transition, invalid transition, or no-op transition, it writes:

```text
none
```

No decision record is written by this service.

## Allowed Effects

The service may:

- load one WorkerAssignment by id
- validate a requested status transition
- apply a documented status transition
- update lifecycle status
- update `updated_at`
- write the existing status-change audit event on successful real transition
- return stable transition reasons
- return the updated assignment and audit id on success

Documented valid transitions:

- `pending -> assigned`
- `pending -> rejected`
- `pending -> cancelled`
- `pending -> expired`
- `assigned -> cancelled`
- `assigned -> expired`

## Forbidden Effects

The service must not:

- create WorkerAssignment intent
- enforce scheduling
- log eligibility decisions
- reserve capacity
- route to providers
- call providers
- execute worker tasks
- write execution results
- activate RuntimeCells
- update graph projections
- mutate worker profiles or heartbeats
- mutate anything beyond the transition boundary
- invent GovernanceDecision records
- treat assigned status as execution proof
- call LLMs

## Trace / Audit Behavior

The service does not persist a trace.

The current implementation does persist one audit event on successful real
transition.

The audit must describe:

- assignment id
- worker id
- capability
- room id
- old status
- new status
- actor id
- reason, when provided

No GovernanceDecision is invented by this service.

Rejected transitions, missing assignment, unknown target status, terminal
transition, invalid transition, and no-op transition do not write audit.

## State / Lifecycle Assumptions

Allowed transitions follow the documented WorkerAssignment lifecycle.

Terminal states stay terminal:

- `rejected`
- `cancelled`
- `expired`

No-op / same-status transitions are rejected as:

```text
status_transition_noop
```

Invalid undocumented transitions are rejected as:

```text
status_transition_not_allowed
```

Unknown target statuses are rejected as:

```text
target_status_unknown
```

Assigned is still not execution proof.

The service does not:

- create assignments
- decide scheduling eligibility
- create reservation records
- open execution logs
- write execution results
- complete work
- prove that work ran

## Tests

Current and expected test coverage includes:

- allowed `pending -> assigned`
- allowed `pending -> rejected`
- allowed `pending -> cancelled`
- allowed `pending -> expired`
- allowed `assigned -> cancelled`
- allowed `assigned -> expired`
- terminal transition blocked
- invalid transition blocked
- no-op transition blocked
- unknown target status blocked
- missing assignment rejected
- exactly one audit event on successful real transition
- no audit on rejected transition
- no audit on no-op transition
- no audit on missing assignment
- no decision write by this service
- no execution fields or execution results

Existing related tests:

- `tests/test_worker_assignment_status_transition_validator.py`
- `tests/test_worker_assignment_status_transition.py`
- `tests/test_worker_assignment_transition_cli.py`

## Non-Goals

This Cell-DNA does not add:

- runtime code changes
- schemas
- migrations
- CLI behavior
- logging behavior
- eligibility logging
- decision logging
- scheduling enforcement
- reservation
- provider routing
- provider calls
- execution
- execution results
- CellRegistry
- RuntimeCell implementation
- graph projection
- human approval workflow
- resource budget enforcement
- lifecycle edges beyond the documented transition graph

## Next Possible Maturity

Next reasonable maturity:

```text
GovernedCell with explicit contract and returned trace shape
```

Promotion blockers:

- no explicit capability contract yet
- no explicit CellRegistry entry
- no dedicated lifecycle inspection surface for transition trace shape
- no persisted trace decision for transition output
- no resource budget or reservation model
- no execution boundary exists

RuntimeCell maturity is later only. It requires CellRegistry, CellContract,
lifecycle inspection, and explicit runtime execution boundary.
