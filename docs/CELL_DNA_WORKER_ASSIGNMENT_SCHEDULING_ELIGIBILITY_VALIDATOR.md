# WorkerAssignmentSchedulingEligibilityValidator Cell-DNA

This document applies `docs/CELL_DNA_PROTOCOL.md` to
`WorkerAssignmentSchedulingEligibilityValidator`, the second concrete
Cell-DNA frame after `WorkerAssignmentValidator`.

This document is documentation. The validator's current implementation remains
read-only and does not add schemas, migrations, new CLI behavior, implicit
logging behavior, scheduling behavior, worker execution, CellRegistry behavior,
or RuntimeCell behavior.

## Capability

Evaluate whether an existing assigned WorkerAssignment intent may be considered
eligible for future scheduling.

This capability answers:

```text
May this assigned WorkerAssignment intent be considered by a future scheduling
step?
```

It does not schedule anything.

## Maturity

```text
CapabilityCell / GovernedCellCandidate
```

Current implementation shape:

```text
pigenus.core.worker_assignment_scheduling_eligibility.WorkerAssignmentSchedulingEligibilityValidator
```

It is not a RuntimeCell.

## Inputs

Primary input:

- assignment id

Runtime data resolved from that id:

- WorkerAssignment intent
- assignment status
- worker id
- capability
- room id
- governance decision id
- required runtime
- sensitivity
- network requirement

## Outputs

Returns:

- `WorkerAssignmentSchedulingEligibilityResult`
- assignment id
- outcome
- `eligible` boolean
- stable reason codes
- details for operator/caller display

Outcomes:

- `allow_scheduling`
- `deny_scheduling`
- `require_review`
- `not_considered`

Current reasons include, but are not limited to:

- `assignment_scheduling_eligible`
- `assignment_unknown`
- `assignment_status_not_assigned`
- `assignment_status_terminal`
- `worker_unknown`
- `worker_degraded`
- `worker_not_considerable`
- `heartbeat_missing`
- `worker_capability_missing`
- `runtime_mismatch`
- `sensitivity_exceeded`
- `network_not_allowed`
- `governance_evidence_missing`
- `governance_evidence_not_preflight_allow`
- `evidence_worker_mismatch`
- `evidence_capability_mismatch`
- `evidence_runtime_mismatch`
- `evidence_sensitivity_mismatch`
- `evidence_network_requirement_mismatch`
- `evidence_room_mismatch`
- `heartbeat_review_stale`
- `heartbeat_hard_stale`
- `heartbeat_clock_invalid`
- `evidence_review_stale`
- `evidence_hard_stale`
- `evidence_clock_invalid`

## Reads

The validator may read:

- `WorkerAssignmentRepository`
- `WorkerRepository`
- worker profile
- current worker heartbeat
- `DecisionRepository`
- durable worker execution preflight governance evidence
- `WorkerFreshnessPolicyValidator`
- heartbeat and preflight evidence age labels returned by the freshness
  validator

## Writes

```text
none
```

`WorkerAssignmentSchedulingEligibilityValidator` is read-only.

## Allowed Effects

The validator may:

- perform read-only eligibility evaluation
- return `allow_scheduling`, `deny_scheduling`, `require_review`, or
  `not_considered`
- check assignment existence
- check assignment status
- check worker profile and current heartbeat state
- check capability, runtime, sensitivity, and network fit
- check governance evidence exists
- check governance evidence is a worker execution preflight allow decision
- check governance evidence matches the assignment
- check heartbeat and preflight evidence freshness through
  `WorkerFreshnessPolicyValidator`
- return stable reason codes
- return details for caller/operator use

## Forbidden Effects

The validator must not:

- mutate assignments
- create assignment intent
- transition assignment status
- write audit records
- write decision records
- log governance decisions
- enforce scheduling
- reserve capacity
- route to providers
- call providers
- execute work
- mutate worker profiles or heartbeats
- treat a worker as intelligence
- treat `assigned` status as execution proof
- call LLMs
- use graph projection as source of truth

## Trace / Audit Behavior

No trace, audit, or decision record is persisted by the validator itself.

It may return reasons, outcome, eligibility, and details that a CLI, caller, or
future governance surface can display or explicitly log later.

Any future persisted trace, audit, or decision behavior must be added through a
separate explicit maturity step.

## State / Lifecycle Assumptions

The validator assumes:

- only `assigned` WorkerAssignment intent can be considered for scheduling
- non-assigned pending intent is `not_considered`
- terminal statuses are `not_considered`
- degraded worker state requires review rather than immediate allow
- missing or non-considerable worker state denies scheduling consideration
- governance evidence must still match the assignment request
- review-stale heartbeat or preflight evidence requires review
- hard-stale heartbeat or preflight evidence denies scheduling consideration

It does not:

- move pending intent to assigned
- move assigned intent to running or completed
- create reservations
- enforce resource budgets
- create execution logs
- expire assignments
- revoke governance evidence
- inspect future scheduling queues

## Tests

Current and expected test coverage includes:

- eligible assigned intent returns `allow_scheduling`
- pending / non-assigned intent returns `not_considered`
- terminal status returns `not_considered`
- degraded worker returns `require_review`
- missing assignment returns `not_considered`
- stale or missing worker conditions deny scheduling consideration
- invalid governance evidence denies scheduling consideration
- hard-stale heartbeat denies scheduling consideration
- review-stale preflight evidence requires review
- hard-stale preflight evidence denies scheduling consideration
- reason codes remain stable
- no assignment writes occur during validation
- no audit writes occur during validation
- no decision writes occur during validation

Existing related tests:

- `tests/test_worker_assignment_scheduling_eligibility.py`
- `tests/test_worker_assignment_scheduling_eligibility_cli.py`

## Non-Goals

This Cell-DNA does not add:

- runtime code changes
- schemas
- migrations
- CellRegistry
- RuntimeCell implementation
- CLI behavior
- graph projection
- scheduling enforcement
- reservation
- provider routing
- provider calls
- execution
- logging behavior
- audit write
- decision logging
- human approval workflow
- resource budget enforcement
- evidence revocation beyond age-based freshness checks

## Next Possible Maturity

Next reasonable maturity:

```text
GovernedCell with explicit contract and returned trace shape
```

Promotion blockers:

- no explicit capability contract yet
- no explicit CellRegistry entry
- no dedicated inspection surface for validator trace shape
- no persisted trace decision for validator output
- no resource budget or reservation model
- no worker/habitat health model beyond current profile, heartbeat, and
  freshness labels
- no evidence revocation policy beyond age-based freshness checks

RuntimeCell maturity is later only. It requires CellRegistry, contract
validation, lifecycle, inspection, and explicit runtime execution boundaries.
