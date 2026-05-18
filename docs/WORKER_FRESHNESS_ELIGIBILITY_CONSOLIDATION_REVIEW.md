# Worker Freshness Eligibility Consolidation Review

This review consolidates the first integration of
`WorkerFreshnessPolicyValidator` into
`WorkerAssignmentSchedulingEligibilityValidator`.

It does not add runtime behavior. It does not add CLI behavior, implicit
logging, scheduling enforcement, reservation, routing, provider calls,
execution logs, or execution.

## What Changed

Assigned-intent scheduling eligibility now evaluates freshness as one
read-only input.

The eligibility validator now:

- reads the current WorkerAssignment intent
- reads the current worker profile and current heartbeat
- reads the referenced worker execution preflight decision
- verifies that the governance evidence is a matching preflight allow decision
- passes assignment, heartbeat, evidence, and explicit `now` into
  `WorkerFreshnessPolicyValidator`
- adds freshness labels and ordered freshness reasons to the eligibility result
- still writes nothing

Freshness is only evaluated after the preflight evidence is structurally valid
and matches the assignment. Mismatched evidence fails at the evidence boundary
and does not receive a separate freshness interpretation.

## Philosophy Alignment

```text
Philosophy-Fit: green
Governance-Fit: green
Cellular-Fit: green
Worker-Boundary-Fit: green
RuntimeShape-Fit: green
Overengineering-Risk: low
Monolith-Risk: low
Recommendation: accept and pause before adding more scheduling power
```

Why green:

- stale worker state is no longer hidden behind a generic eligibility result
- preflight evidence age is checked before any future scheduling step
- `WorkerFreshnessPolicyValidator` remains storage-free and side-effect-free
- `WorkerAssignmentSchedulingEligibilityValidator` remains read-only
- worker remains an execution host, not intelligence
- `assigned` remains intent state, not execution proof

## Boundary Check

Still true after integration:

- no assignment mutation
- no audit write
- no implicit decision logging
- no scheduling enforcement
- no reservation
- no provider routing
- no provider calls
- no execution logs
- no execution

`worker-assignment-scheduling-eligibility --log` remains a separate explicit
operator action. Freshness integration does not make logging implicit and does
not change the logging source semantics.

## Result Semantics

Freshness can now affect the eligibility result:

- fresh heartbeat and fresh evidence preserve the normal eligibility outcome
- review-stale heartbeat or evidence can require review
- hard-stale heartbeat or evidence can deny scheduling consideration
- missing or invalid governance evidence blocks freshness evaluation
- mismatched governance evidence blocks freshness evaluation

This keeps evidence validity and evidence freshness separate:

```text
valid and matching evidence -> freshness may be evaluated
invalid or mismatched evidence -> deny at evidence boundary
```

## Test Evidence

Local verification at the time of this consolidation:

```text
317 passed
```

The current full-suite result is tracked in `STATUS.md`.

Targeted coverage includes:

- existing allow, deny, review, and not-considered eligibility cases
- hard-stale heartbeat denies scheduling consideration
- review-stale preflight evidence requires review
- hard-stale preflight evidence denies scheduling consideration
- mismatched preflight evidence skips freshness evaluation
- assignment count is unchanged
- decision count is unchanged
- audit count is unchanged

## Risks

Remaining risks are mostly future-facing:

- CLI output may eventually need to present freshness details more clearly
- eligibility logging may persist freshness-influenced results, but only when
  `--log` is explicit
- room/context policy can still change after assignment creation
- resource/risk budget inputs do not exist yet
- reflex, circuit-breaker, and kill-switch boundaries do not exist yet
- reservation still has no model
- enforcement logging semantics remain separate from eligibility logging

These are not bugs in the freshness integration. They are stop lines for the
next readiness boundary.

## Recommendation

Accept the integration as the current read-only eligibility boundary.

Do not add more eligibility logging or scheduling behavior immediately.

Next safe decision:

```text
Implement a storage-free read-only
WorkerAssignmentResourceRiskReflexReadinessValidator with targeted no-write
tests.
```

Why:

- freshness is now explicit
- WorkerAssignment room/context recheck semantics are now defined in
  `docs/WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK.md`
- the future validator's membrane is now explicit in
  `docs/CELL_DNA_WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK_VALIDATOR.md`
- the read-only validator now exists in
  `pigenus.core.worker_assignment_room_context_recheck`
- that validator is consolidated in
  `docs/WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK_CONSOLIDATION_REVIEW.md`
- the validator is now consumed by scheduling eligibility only when explicitly
  supplied by a caller
- that integration is consolidated in
  `docs/WORKER_ROOM_CONTEXT_ELIGIBILITY_INTEGRATION_CONSOLIDATION_REVIEW.md`
- resource, risk, and reflex readiness semantics now live in
  `docs/WORKER_RESOURCE_RISK_REFLEX_READINESS.md`
- the related Cell-DNA frame now lives in
  `docs/CELL_DNA_WORKER_ASSIGNMENT_RESOURCE_RISK_REFLEX_READINESS_VALIDATOR.md`

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
