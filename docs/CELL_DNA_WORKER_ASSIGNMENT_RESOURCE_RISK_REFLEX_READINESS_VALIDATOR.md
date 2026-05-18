# WorkerAssignmentResourceRiskReflexReadinessValidator Cell-DNA

This document applies `docs/CELL_DNA_PROTOCOL.md` to the future
`WorkerAssignmentResourceRiskReflexReadinessValidator`.

It is documentation-only. It does not add runtime code, schemas, migrations,
CLI behavior, logging behavior, graph projection, RuntimeCell behavior,
CellRegistry behavior, scheduling enforcement, reservation, routing, provider
calls, execution logs, or execution.

## Capability

Evaluate whether an assigned WorkerAssignment intent has enough explicit
resource, risk, and reflex readiness to remain a candidate for future
scheduling enforcement.

This capability answers:

```text
Are resource budget, risk budget, and protective reflex boundaries explicit
enough to keep this assignment in readiness consideration?
```

It does not answer:

```text
May scheduling proceed?
Has capacity been reserved?
Which provider should receive the work?
Should execution start?
```

Resource/risk/reflex readiness is one scheduling-readiness input, not
scheduling enforcement.

## Maturity

```text
CapabilityCell / GovernedCellCandidate
```

Current maturity is documentation-only. RuntimeCell maturity is explicitly
later.

Planned implementation shape:

```text
pigenus.core.worker_assignment_resource_risk_reflex_readiness.WorkerAssignmentResourceRiskReflexReadinessValidator
```

## Inputs

Future first implementation inputs:

- assignment ID
- explicit resource readiness policy / thresholds
- explicit risk readiness policy / thresholds
- explicit reflex readiness policy / required boundaries

Runtime data resolved from assignment ID:

- WorkerAssignment intent
- assignment status
- worker ID
- capability
- room ID
- required runtime
- sensitivity
- network requirement
- created-by actor ID
- referenced governance evidence ID

Optional future inputs:

- ResourceGrant
- resource request
- worker cost profile
- worker capacity signal
- room-level budget signal
- actor-level budget signal
- risk band
- risk budget
- human approval threshold signal
- circuit-breaker state
- kill-switch state
- quarantine state
- abort path availability
- recovery path availability

Inputs that do not exist yet must remain optional and explicit. Missing future
inputs should become stable reasons, not hidden permission.

## Outputs

Future output:

- `WorkerAssignmentResourceRiskReflexReadinessResult`
- assignment ID
- outcome
- readiness boolean
- stable reason codes
- details for caller/operator display

Suggested broad outcomes:

- `allow_readiness`
- `require_review`
- `deny_readiness`
- `not_considered`

Suggested resource reasons:

- `resource_budget_missing`
- `resource_budget_exhausted`
- `resource_budget_review_required`
- `resource_request_missing`
- `resource_request_exceeds_grant`
- `worker_capacity_unknown`
- `worker_capacity_degraded`
- `human_review_capacity_missing`
- `resource_readiness_passed`

Suggested risk reasons:

- `risk_budget_missing`
- `risk_band_unknown`
- `risk_band_requires_review`
- `risk_band_denied`
- `high_risk_room_requires_approval`
- `external_effect_requires_review`
- `irreversible_effect_blocked`
- `sensitivity_risk_exceeded`
- `risk_readiness_passed`

Suggested reflex reasons:

- `reflex_boundary_missing`
- `kill_switch_missing`
- `kill_switch_active`
- `circuit_breaker_open`
- `quarantine_active`
- `abort_path_missing`
- `recovery_path_missing`
- `reflex_review_required`
- `reflex_readiness_passed`

Reason names may be refined before implementation. Once implemented and
tested, reason codes should remain stable.

## Reads

A future first implementation may read:

- `WorkerAssignmentRepository`
- WorkerAssignment status and assignment fields
- explicit resource/risk/reflex policy inputs supplied by the caller
- optional ResourceGrant or resource request inputs supplied by the caller
- optional worker capacity / cost profile inputs supplied by the caller
- optional risk band / approval-threshold inputs supplied by the caller
- optional circuit-breaker, kill-switch, quarantine, abort, or recovery
  signals supplied by the caller

The first implementation should not own persistence for resource usage, risk
budgets, reflex state, kill switches, quarantine records, or recovery paths.

## Writes

```text
none
```

The validator must be read-only.

## Allowed Effects

The validator may:

- perform read-only resource readiness evaluation
- perform read-only risk readiness evaluation
- perform read-only reflex readiness evaluation
- return `allow_readiness`, `require_review`, `deny_readiness`, or
  `not_considered`
- return stable reason codes
- return details for caller/operator use
- make missing resource/risk/reflex inputs visible
- treat missing critical safety boundaries as review or deny reasons according
  to explicit policy

## Forbidden Effects

The validator must not:

- mutate WorkerAssignment
- create WorkerAssignment intent
- transition WorkerAssignment status
- write audit records
- write decision records
- log readiness, eligibility, or enforcement results
- enforce scheduling
- reserve capacity
- spend budget
- route to providers
- call providers
- execute work
- create execution logs
- store execution results
- mutate worker profiles or heartbeats
- create ResourceGrant records
- create resource usage records
- create risk budget records
- create reflex state records
- activate or clear kill switches
- open or close circuit breakers
- quarantine or unquarantine anything
- trigger abort or recovery paths
- use graph projection as source of truth
- become a RuntimeCell
- register itself in a CellRegistry

## Trace / Audit Behavior

No trace, audit, decision, or readiness record is persisted by the validator
itself.

It may return:

- outcome
- reason codes
- assignment ID
- worker ID
- room ID
- capability
- resource readiness details
- risk readiness details
- reflex readiness details

Those returned details may be used by a caller or operator surface later, but
the validator itself must not create audit rows or governance decisions.

## State / Lifecycle Assumptions

The future validator assumes:

- assignment intent is not execution proof
- `assigned` is not scheduling permission
- resource readiness is not reservation
- risk readiness is not human approval
- reflex readiness is not execution control
- missing critical resource/risk/reflex inputs must not silently allow
  scheduling readiness
- existing freshness and room/context readiness are upstream scheduling inputs
- scheduling enforcement remains later

It does not:

- decide freshness
- decide room/context compatibility
- create or mutate resource grants
- create reservations
- approve high-risk work
- trigger human approval workflows
- trigger kill switches
- trigger quarantine
- trigger abort or recovery
- decide provider routing
- decide execution

## Tests

Future tests should prove:

- missing assignment returns `not_considered`
- non-assigned assignment status returns `not_considered`
- matching resource/risk/reflex inputs allow readiness
- missing resource budget returns review or deny according to explicit policy
- exhausted resource budget denies readiness
- unknown risk band requires review
- denied risk band denies readiness
- active kill switch denies readiness
- open circuit breaker denies readiness
- active quarantine denies readiness
- missing abort or recovery path requires review for high-risk contexts
- reason codes remain stable
- no assignment writes occur during validation
- no audit writes occur during validation
- no decision writes occur during validation
- no resource, risk, reflex, kill-switch, quarantine, abort, or recovery
  records are created or mutated
- no reservation, routing, provider, execution-log, or execution writes occur

## Non-Goals

This Cell-DNA does not add:

- runtime code
- schemas
- migrations
- resource usage records
- resource stores
- risk stores
- reflex stores
- kill-switch implementation
- circuit-breaker implementation
- quarantine implementation
- abort or recovery workflow
- CLI inspection
- logging
- decision persistence
- audit persistence
- scheduling enforcement
- reservation
- routing
- provider calls
- execution
- high-risk trading behavior
- RuntimeCell behavior
- CellRegistry behavior
- graph projection

## Next Possible Maturity

Current safe maturity:

```text
Documented Cell-DNA only.
```

Next reasonable maturity:

```text
Read-only CapabilityCell implementation with targeted no-write tests.
```

Promotion blockers:

- no explicit resource readiness policy object yet
- no explicit risk readiness policy object yet
- no explicit reflex readiness policy object yet
- no source of truth for resource usage or reservation
- no source of truth for risk budget state
- no source of truth for kill-switch, circuit-breaker, or quarantine state
- no human approval threshold integration
- no scheduling-enforcement validator
- no reservation model
- no execution boundary

RuntimeCell maturity is later only. It requires CellRegistry, contract
validation, lifecycle, inspection, and explicit runtime execution boundaries.
