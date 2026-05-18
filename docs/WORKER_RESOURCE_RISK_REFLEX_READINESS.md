# Worker Resource / Risk / Reflex Readiness

This document defines the next scheduling-readiness boundary after freshness
and room/context recheck: resource, risk, and reflex semantics.

This document started as documentation-only. The first implementation now adds
only a storage-free read-only validator:
`WorkerAssignmentResourceRiskReflexReadinessValidator`.

It still does not add schemas, migrations, CLI behavior, logging behavior,
graph projection, RuntimeCell behavior, CellRegistry behavior, scheduling
enforcement, reservation, routing, provider calls, execution logs, or
execution.

## Purpose

PiGenus can now create governed WorkerAssignment intent, transition assignment
status, inspect scheduling eligibility, evaluate freshness, and optionally
compose room/context recheck into eligibility.

That is still not enough for scheduling enforcement.

Before an assigned intent may reach any scheduling-enforcement validator,
PiGenus needs explicit semantics for:

- what resources would be consumed
- what risk would be introduced
- what reflexes can stop the path
- what remains missing before reservation, routing, provider calls, or
  execution

## Canonical Alignment

This document maps to:

- `docs/GENUS_CANONICAL_SYSTEMFORM.md`
- `docs/RESOURCE_ECONOMY.md`
- `docs/WORKER_SCHEDULING_ENFORCEMENT_READINESS_GAP_REVIEW.md`
- `docs/WORKER_ROOM_CONTEXT_ELIGIBILITY_INTEGRATION_CONSOLIDATION_REVIEW.md`

Canonical rule:

```text
No scheduling enforcement before resource, risk, and reflex semantics.
```

Resource readiness, risk readiness, and reflex readiness are scheduling inputs.
They are not scheduling, reservation, routing, provider calls, execution logs,
or execution.

## Current Runtime State

Implemented:

- `ResourceGrant` model
- contract resource limit checks
- guard family mapping for resource reasons
- WorkerProfile capability, runtime, sensitivity, and network limits
- WorkerHeartbeat current-state freshness checks
- WorkerAssignment freshness and room/context eligibility inputs
- storage-free read-only
  `WorkerAssignmentResourceRiskReflexReadinessValidator`

Not implemented:

- resource usage records
- resource reservation
- worker capacity reservation
- risk budget store
- reflex state store
- kill-switch runtime path
- circuit-breaker runtime path
- quarantine / recovery workflow for workers or assignments
- scheduling-enforcement validator
- worker execution

## Resource Readiness

Resource readiness answers:

```text
Is there enough explicit budget to consider this assignment for scheduling?
```

Resource readiness may later inspect:

- requested runtime
- requested capability
- room ID
- actor ID
- worker ID
- sensitivity
- network requirement
- worker cost profile
- worker current capacity
- resource grant
- recent resource usage
- room-level budget
- actor-level budget
- human review capacity

Initial resource categories:

- compute
- memory
- storage
- time
- network
- attention
- privacy budget
- money / external cost where relevant
- human review capacity

Suggested future resource outcomes:

```text
allow_resource
require_review
deny_resource
not_considered
```

Suggested future resource reason codes:

```text
resource_budget_missing
resource_budget_exhausted
resource_budget_review_required
resource_request_missing
resource_request_exceeds_grant
worker_capacity_unknown
worker_capacity_degraded
human_review_capacity_missing
resource_readiness_passed
```

Important boundary:

```text
Resource readiness is not reservation.
```

Allowing a resource check means only that the assignment may continue toward
future scheduling consideration. It does not reserve capacity, spend budget,
or start work.

## Risk Readiness

Risk readiness answers:

```text
Is the proposed scheduling consideration inside the allowed risk envelope?
```

Risk is not only security risk. It can include:

- privacy risk
- financial risk
- irreversible action risk
- network / external-system risk
- room-crossing risk
- unsafe output risk
- stale evidence risk
- degraded-worker risk
- high-sensitivity data risk
- human-trust / relationship risk

Suggested risk bands:

```text
low
medium
high
critical
unknown
```

Suggested future risk outcomes:

```text
allow_risk
require_review
deny_risk
not_considered
```

Suggested future risk reason codes:

```text
risk_budget_missing
risk_band_unknown
risk_band_requires_review
risk_band_denied
high_risk_room_requires_approval
external_effect_requires_review
irreversible_effect_blocked
sensitivity_risk_exceeded
risk_readiness_passed
```

Important boundary:

```text
Risk readiness is not human approval.
```

Risk readiness may require approval, but it does not grant approval by itself.
Approval remains a separate governance surface.

## Reflex Readiness

Reflex readiness answers:

```text
Can the system stop, pause, isolate, or abort the path if known unsafe
conditions appear?
```

Reflexes are protective responses. They must be explicit and inspectable.

Initial reflex classes:

- `CircuitBreaker`: stops repeated failures or repeated risky attempts
- `KillSwitch`: stops or disables a risky path immediately
- `Quarantine`: isolates a worker, assignment, meaning object, cell, or organ
- `AbortPath`: stops a running or pending path before it becomes worse
- `RecoveryPath`: defines how to revalidate, restore, or roll back after
  failure

Suggested future reflex outcomes:

```text
allow_reflex
require_review
deny_reflex
not_considered
```

Suggested future reflex reason codes:

```text
reflex_boundary_missing
kill_switch_missing
kill_switch_active
circuit_breaker_open
quarantine_active
abort_path_missing
recovery_path_missing
reflex_review_required
reflex_readiness_passed
```

Important boundary:

```text
Reflex readiness is not execution control.
```

Before execution exists, reflex readiness defines which protective boundaries
must exist. Later, execution code must honor those boundaries explicitly.

## Combined Readiness

A future read-only readiness validator may combine these domains as:

```text
WorkerAssignment
-> freshness eligibility
-> room/context eligibility
-> resource readiness
-> risk readiness
-> reflex readiness
-> scheduling-enforcement candidate
```

The first combined semantics should use the broad worker-readiness outcome
family:

```text
allow
require_review
deny
not_considered
```

Combination rule:

- any `deny_*` blocks readiness
- any `require_review` requires review
- any `not_considered` keeps the assignment outside consideration
- only all allow/pass outcomes may allow future enforcement consideration

This is still not scheduling enforcement.

## Future Validator Shape

The first validator is now implemented as read-only and small:

```text
WorkerAssignmentResourceRiskReflexReadinessValidator
```

Current shape:

- Maturity: `CapabilityCell / GovernedCellCandidate`
- Inputs: assignment ID plus explicit resource/risk/reflex policy inputs
- Outputs: allow, deny, review, or not-considered result with stable reasons
- Reads: assignment plus explicit resource/risk/reflex inputs supplied by the
  caller
- Writes: none
- Forbidden effects: no assignment mutation, no audit write, no decision
  logging, no reservation, no routing, no provider call, no execution
- Tests: allow/review/deny/not-considered, missing inputs, no-write proof, and
  no-execution proof

## Relationship To Scheduling Enforcement

Scheduling enforcement remains later.

A future enforcement validator must not exist until the following are explicit:

- freshness input
- room/context input
- resource readiness input
- risk readiness input
- reflex readiness input
- human approval threshold rules where required
- no-write and no-execution proof

Scheduling enforcement still must not reserve capacity, route providers, call
providers, create execution logs, or execute work.

## Relationship To Resource Economy

`docs/RESOURCE_ECONOMY.md` remains the broad topic-authoritative document for
resource accounting.

This document is narrower:

```text
What resource/risk/reflex semantics must exist before WorkerAssignment
scheduling enforcement?
```

The first resource economy implementation may later add read-only accounting.
This document does not require that implementation before it is explicitly
planned.

## Non-Goals

This document does not add:

- resource usage records
- resource stores
- risk stores
- reflex stores
- schema migrations
- CLI commands
- eligibility logging changes
- scheduling enforcement
- reservation
- provider routing
- provider calls
- execution logs
- execution
- high-risk trading behavior
- RuntimeCell implementation
- dynamic cell routing

## Recommendation

Accept resource, risk, and reflex readiness as the next semantic boundary
before scheduling enforcement.

Next safe step:

```text
Consolidate the storage-free read-only
WorkerAssignmentResourceRiskReflexReadinessValidator before wiring it into
scheduling eligibility, CLI, logging, scheduling enforcement, reservation,
routing, provider calls, execution logs, or execution.
```

The Cell-DNA frame for that future validator now lives in
`docs/CELL_DNA_WORKER_ASSIGNMENT_RESOURCE_RISK_REFLEX_READINESS_VALIDATOR.md`.

Still not next:

- worker execution
- scheduling enforcement
- reservation
- provider routing
- provider calls
- execution logs
- execution results
- remote worker discovery
- graph projection
- RuntimeCell implementation
- CellRegistry implementation
- dynamic cell routing
- trading or other high-risk live behavior
