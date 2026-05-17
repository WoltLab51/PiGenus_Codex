# WorkerFreshnessPolicyValidator Cell-DNA

This document applies the lightweight Cell-DNA protocol to
`WorkerFreshnessPolicyValidator`.

The current implementation is storage-free and read-only. It does not add
schemas, migrations, CLI behavior, logging behavior, heartbeat history,
scheduling enforcement, reservation, routing, provider calls, execution logs,
execution, RuntimeCell behavior, CellRegistry behavior, or graph projection.

## Capability

Evaluate worker heartbeat freshness and governance evidence freshness for a
WorkerAssignment scheduling-readiness check.

The capability answers:

```text
Are the heartbeat and preflight evidence fresh, review-stale, hard-stale,
missing, or clock-invalid?
```

It does not answer:

```text
May scheduling proceed?
Should capacity be reserved?
Should assignment state change?
Should a provider receive work?
Should execution start?
```

Freshness is one input to future scheduling enforcement, not enforcement
itself.

## Maturity

```text
CapabilityCell / GovernedCellCandidate
```

Current maturity is a storage-free read-only CapabilityCell implementation and
GovernedCellCandidate. RuntimeCell maturity is explicitly later.

## Inputs

Current first implementation inputs:

- `WorkerAssignment`
- current `WorkerHeartbeat` or `None`
- referenced preflight `DecisionRecord` / `GovernanceDecision` evidence
- explicit `now` timestamp for deterministic evaluation
- optional policy thresholds from `docs/WORKER_FRESHNESS_POLICY.md`

Inputs are passed explicitly by the caller. The validator does not query
storage in the first slice.

## Outputs

Current outputs:

- heartbeat freshness label:
  - `fresh`
  - `review_stale`
  - `hard_stale`
  - `missing`
  - `clock_invalid`
- evidence freshness label with the same vocabulary
- optional assignment-age freshness label
- ordered reason codes
- derived recommendation:
  - continue
  - require review
  - deny freshness
  - not considered

The output should be deterministic and stable enough for later enforcement
validators to consume.

## Reads

The first implementation reads only input objects it is given:

- `WorkerAssignment.created_at`
- `WorkerAssignment.updated_at`
- `WorkerHeartbeat.seen_at`
- `WorkerHeartbeat.status`
- preflight decision `created_at`
- preflight decision source/type/family only if needed to confirm evidence
  shape
- freshness thresholds from policy or explicit configuration

It does not directly read repositories in the first slice.

## Writes

```text
none
```

## Allowed Effects

- classify heartbeat freshness
- classify preflight evidence freshness
- optionally classify assignment lifecycle freshness
- return stable freshness labels
- return stable reason codes
- expose enough detail for a caller, CLI, or later enforcement validator to
  explain the result

## Forbidden Effects

The validator must not:

- mutate `WorkerAssignment`
- expire assignments automatically
- mutate worker profiles
- mutate worker heartbeats
- create heartbeat history
- write audit rows
- write governance decisions
- log eligibility or enforcement results
- create assignments
- change assignment status
- schedule work
- enforce scheduling
- reserve capacity
- route providers
- call providers
- call tools
- write execution logs
- store execution results
- execute work
- update a graph projection
- become a RuntimeCell
- register itself in a CellRegistry

## Trace / Audit Behavior

The validator persists nothing.

It may return:

- labels
- reason codes
- compared timestamps
- effective thresholds
- `now`

Those returned details may be used by a caller or operator surface later, but
the validator itself must not create audit rows or governance decisions.

## State / Lifecycle Assumptions

- The validator is stateless.
- It does not own worker lifecycle.
- It does not own assignment lifecycle.
- It does not decide terminal assignment transitions.
- It does not repair clock skew.
- It does not turn `assigned` into execution proof.
- It assumes `now` is supplied explicitly for deterministic tests.
- It treats freshness as a prerequisite signal, not as final scheduling
  permission.

## Tests

Implemented tests for the first implementation:

- fresh heartbeat and fresh evidence returns fresh labels
- missing heartbeat returns `missing`
- review-stale heartbeat returns `review_stale`
- hard-stale heartbeat returns `hard_stale`
- missing evidence returns `missing`
- review-stale evidence returns `review_stale`
- hard-stale evidence returns `hard_stale`
- future heartbeat timestamp returns `clock_invalid`
- future evidence timestamp returns `clock_invalid`
- degraded heartbeat or profile remains review-oriented even when timestamp is
  fresh if profile input is included in the slice
- explicit `now` makes tests deterministic
- no assignment mutation
- no decision writes
- no audit writes
- no heartbeat writes
- no reservation, routing, provider, execution log, or execution writes

## Non-Goals

This Cell-DNA and implementation do not add:

- storage reads
- repository wiring
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
- automatic assignment expiry
- RuntimeCell behavior
- CellRegistry behavior
- graph projection

## Next Possible Maturity

Current safe maturity:

```text
CapabilityCell with a read-only implementation and targeted tests.
```

The first implementation is storage-free and repository-free. It accepts
explicit inputs and returns a deterministic result.

Later maturity:

```text
GovernedCell with explicit contract and returned trace.
```

RuntimeCell maturity is only possible after CellRegistry, CellContract,
lifecycle inspection, runtime execution boundary, and operator inspection
surfaces exist.
