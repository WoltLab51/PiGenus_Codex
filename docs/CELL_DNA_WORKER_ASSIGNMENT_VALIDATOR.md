# WorkerAssignmentValidator Cell-DNA

This document applies `docs/CELL_DNA_PROTOCOL.md` to
`WorkerAssignmentValidator`, the first Cell-DNA candidate selected by
`docs/CELLULAR_INVENTORY_REVIEW.md`.

This is documentation only. It does not change runtime code, schemas,
migrations, CLI behavior, logging behavior, scheduling behavior, worker
execution, CellRegistry behavior, or RuntimeCell behavior.

## Capability

Validate whether a worker assignment creation request has acceptable evidence
before assignment intent is persisted.

This capability answers:

```text
May this WorkerAssignment intent be created from the supplied preflight
governance evidence?
```

It does not create the assignment.

## Maturity

```text
CapabilityCell / GovernedCellCandidate
```

Current implementation shape:

```text
pigenus.core.worker_assignment_validator.WorkerAssignmentValidator
```

It is not a RuntimeCell.

## Inputs

Primary input:

- worker assignment creation request / assignment intent fields as a
  `WorkerAssignment`

Relevant fields:

- assignment id
- worker id
- capability
- room id
- governance evidence / decision id
- required runtime
- sensitivity
- network requirement
- pending assignment status

## Outputs

Returns:

- `WorkerAssignmentValidationResult`
- `valid` boolean
- stable reason codes
- details containing assignment id, worker id, decision id, decision source,
  and decision type when available

Successful validation currently returns:

```text
worker_assignment_valid
```

Failure reasons include, but are not limited to:

- `worker_unknown`
- `assignment_status_must_be_pending`
- `governance_decision_unknown`
- `evidence_type_invalid`
- `evidence_source_invalid`
- `evidence_decision_not_allow`
- `evidence_family_invalid`
- `evidence_governance_decision_missing`
- `evidence_details_missing`
- `evidence_request_missing`
- `worker_mismatch`
- `capability_mismatch`
- `runtime_mismatch`
- `sensitivity_mismatch`
- `network_requirement_mismatch`
- `room_mismatch`

## Reads

The validator may read:

- `WorkerRepository` / worker profile lookup
- `DecisionRepository`
- durable `GovernanceDecision` / DecisionLog evidence

The current code does not read existing WorkerAssignment state from
`WorkerAssignmentRepository`.

## Writes

```text
none
```

`WorkerAssignmentValidator` is read-only.

## Allowed Effects

The validator may:

- perform pure/read-only validation
- check that the worker exists
- require pending assignment status before creation
- check that governance evidence exists
- check that evidence is a worker execution preflight allow decision
- check that evidence fields match the requested assignment
- return stable reason codes
- return details for caller/operator use

## Forbidden Effects

The validator must not:

- create assignment intent
- update assignment status
- write audit records
- write decision records
- log governance decisions
- enforce scheduling
- reserve capacity
- route to providers
- execute work
- mutate worker profiles or heartbeats
- treat a worker as intelligence
- treat `assigned` status as execution proof
- call LLMs
- use graph projection as source of truth

## Trace / Audit Behavior

No trace, audit, or decision record is persisted by the validator itself.

It may return reasons and details that a caller, CLI, service, or future
governance surface can present or log explicitly.

Any future persisted trace or audit behavior must be added outside this
validator or through an explicitly documented maturity step.

## State / Lifecycle Assumptions

The validator assumes:

- assignment creation starts from `pending`
- assignment evidence comes from a durable decision record
- the evidence source is `worker_execution_preflight`
- the evidence decision is `allow`
- the assignment request must match the preflight evidence

It does not:

- transition assignment lifecycle state
- decide scheduling eligibility
- decide worker readiness for execution
- inspect current heartbeat state
- expire evidence
- revoke evidence

## Tests

Current and expected test coverage includes:

- valid evidence is accepted
- missing or unknown worker is rejected
- missing governance evidence is rejected
- invalid governance evidence is rejected
- non-allow preflight evidence is rejected
- wrong evidence source or family is rejected
- mismatched worker, capability, runtime, sensitivity, network, or room is
  rejected
- reason codes remain stable
- no assignment writes occur when validation fails through creator/CLI paths
- no audit writes occur when validation fails through creator/CLI paths
- no decision writes occur during validator execution

Existing related tests:

- `tests/test_worker_assignment_validator.py`
- `tests/test_worker_assignment_creator.py`
- `tests/test_worker_assignment_create_cli.py`

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
- execution
- logging behavior
- human approval workflow
- evidence expiry or revocation

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
- no evidence expiry or revocation policy

RuntimeCell maturity is later only. It requires CellRegistry, contract
validation, lifecycle, inspection, and explicit runtime execution boundaries.
