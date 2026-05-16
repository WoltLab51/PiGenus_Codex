# WorkerAssignmentCreator Cell-DNA

This document applies `docs/CELL_DNA_PROTOCOL.md` to
`WorkerAssignmentCreator`, the first write-capable responsible capability with
an applied Cell-DNA frame.

This is documentation only. It does not change runtime code, schemas,
migrations, CLI behavior, logging behavior, scheduling behavior, worker
execution, CellRegistry behavior, graph projection, or RuntimeCell behavior.

## Capability

Create governed WorkerAssignment intent from a validated request and matching
governance evidence.

This capability answers:

```text
Should this validated WorkerAssignment intent be persisted as a pending
assignment record?
```

It does not schedule, route, reserve, or execute work.

## Maturity

```text
CapabilityCell / GovernedCellCandidate
```

Current implementation shape:

```text
pigenus.core.worker_assignment_creator.WorkerAssignmentCreator
```

It is not a RuntimeCell.

## Inputs

Primary input:

- worker assignment creation request as a `WorkerAssignment`

Relevant fields:

- assignment id
- worker id
- capability
- room id
- governance decision id / evidence
- actor id / `created_by_actor_id`
- required runtime, when applicable
- sensitivity, when applicable
- network requirement, when applicable
- optional event id, when present
- optional context stack id, when present
- optional reason, when present

Supporting input:

- `WorkerAssignmentValidator`
- `WorkerAssignmentRepository`
- `AuditLogger`

## Outputs

Returns:

- `WorkerAssignmentCreationResult`
- created `WorkerAssignment` on success
- assignment id through the returned assignment
- audit id on success
- validation result
- validation errors / reason codes on rejection

Successful creation means:

```text
pending assignment intent was persisted
creation audit was written
no scheduling, routing, reservation, provider call, or execution occurred
```

## Reads

The creator may read indirectly through `WorkerAssignmentValidator`:

- `WorkerRepository` / worker profile lookup
- `DecisionRepository`
- durable `GovernanceDecision` / DecisionLog evidence

The creator directly uses:

- `WorkerAssignmentValidator`
- `WorkerAssignmentRepository`
- `AuditLogger`

It does not independently invent governance evidence.

## Writes

On success, the current implementation writes:

- exactly one durable `WorkerAssignment` record
- exactly one existing creation audit row via `AuditLogger`

On validation failure, it writes:

```text
none
```

No decision record is written by the creator.

## Allowed Effects

The creator may:

- validate assignment intent through `WorkerAssignmentValidator`
- reject invalid assignment intent with stable validation reasons
- persist one pending WorkerAssignment intent on success
- write the existing `worker_assignment_created` audit row on success
- return the created assignment, audit id, and validation result

## Forbidden Effects

The creator must not:

- execute worker tasks
- enforce scheduling
- reserve capacity
- route to providers
- call providers
- transition status beyond the initial assignment status supplied for creation
- write audit records other than the current creation audit row
- write decision records
- log governance decisions
- log eligibility decisions
- update graph projections
- activate RuntimeCells
- mutate worker profiles or heartbeats
- treat a worker as intelligence
- treat created or assigned WorkerAssignment status as execution proof
- call LLMs

## Trace / Audit Behavior

The creator does not persist a trace.

The current implementation does persist one creation audit row on success:

```text
action = worker_assignment_created
```

The audit records that the assignment intent was created. It is not execution
proof.

Governance evidence is referenced through the assignment's
`governance_decision_id`. The creator does not invent, derive, or log new
governance evidence.

## State / Lifecycle Assumptions

The creator assumes:

- assignment creation starts as durable intent
- valid creation requires matching preflight allow evidence
- created assignment intent is not scheduling
- created assignment intent is not reservation
- created assignment intent is not routing
- created assignment intent is not execution
- assigned status must never mean executed

The current creator does not:

- transition lifecycle state after creation
- decide scheduling eligibility
- check current worker heartbeat itself
- allocate resources
- open execution logs
- expire assignments
- revoke governance evidence

## Tests

Current and expected test coverage includes:

- successful creation writes one assignment record
- successful creation writes the existing creation audit row
- missing or unknown worker is rejected through validation
- missing governance evidence is rejected through validation
- invalid governance evidence is rejected through validation
- validator failure rejects creation
- rejected creation writes no assignment record
- rejected creation writes no audit row
- rejected creation writes no decision record
- stored assignment has no execution fields or execution result
- no unexpected writes occur beyond the assignment record and current creation
  audit row on success

Existing related tests:

- `tests/test_worker_assignment_creator.py`
- `tests/test_worker_assignment_create_cli.py`
- `tests/test_worker_assignment_store.py`

## Non-Goals

This Cell-DNA does not add:

- runtime code changes
- schemas
- migrations
- CLI behavior
- CellRegistry
- RuntimeCell implementation
- graph projection
- scheduling enforcement
- reservation
- provider routing
- provider calls
- execution
- decision logging
- eligibility logging
- new logging behavior
- human approval workflow
- resource budget enforcement
- evidence expiry or revocation

## Next Possible Maturity

Next reasonable maturity:

```text
GovernedCell with explicit contract and returned trace shape
```

Promotion blockers:

- no explicit capability contract yet
- no explicit CellRegistry entry
- no dedicated inspection surface for creator trace shape
- no persisted trace decision for creator output
- no resource budget or reservation model
- no evidence expiry or revocation policy

RuntimeCell maturity is later only. It requires CellRegistry, contract
validation, lifecycle, inspection, and explicit runtime execution boundaries.
