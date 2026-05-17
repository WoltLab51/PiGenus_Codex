# Worker Scheduling Enforcement Boundary

This document defines the boundary between worker assignment lifecycle and any
future scheduling behavior.

It does not add a migration, service, CLI command, reservation, provider route,
execution log, or execution path.

## Purpose

Worker Scheduling Enforcement answers one narrow question:

```text
May this assigned WorkerAssignment be considered by a future scheduler now?
```

It does not answer:

```text
Which worker is best?
Should capacity be reserved?
Which provider should receive work?
Has execution started?
Did execution succeed?
```

Those are later boundaries.

## Current Sequence

The safe Worker Runtime sequence is:

```text
worker-scheduling-preview
-> worker-execution-preflight --log
-> worker-assignment-create
-> worker-assignment-transition assigned
-> future scheduling enforcement
-> future reservation
-> future routing
-> future execution
```

The important invariant:

```text
assigned is necessary for scheduling consideration.
assigned is not sufficient for scheduling execution.
```

`assigned` means assignment intent has moved through the allowed lifecycle
graph. It does not prove that the worker is still healthy, that evidence is
fresh, that resources are available, that room policy still allows the work, or
that a provider may be called.

## Enforcement Inputs

A future enforcement check should be able to inspect:

- the stored `WorkerAssignment`
- the assignment status
- the original `worker_execution_preflight` allow decision
- the current `WorkerProfile`
- the current `WorkerHeartbeat`
- capability and runtime compatibility
- sensitivity and network requirements
- room and context-stack constraints
- relevant guard and room-flow outcomes
- relevant resource policy or resource grant, when implemented
- optional human approval evidence, when risk requires it
- freshness limits for evidence and heartbeat state

The first implementation is intentionally named
`WorkerAssignmentSchedulingEligibilityValidator` rather than
`WorkerSchedulingEnforcementValidator` because it only checks eligibility. It
does not enforce scheduling.

## Minimum Rules

Scheduling enforcement must reject consideration when:

- the assignment does not exist
- the assignment is not `assigned`
- the assignment is terminal: `rejected`, `cancelled`, or `expired`
- the referenced worker does not exist
- the referenced governance decision does not exist
- the evidence is not an allow decision from `worker_execution_preflight`
- the worker no longer has the required capability
- the required runtime no longer matches
- the sensitivity exceeds the worker limit
- network access is required but no longer allowed
- heartbeat state is missing or stale beyond policy
- room, context, guard, or resource policy blocks the work

Scheduling enforcement may require review when:

- evidence is old but not expired by hard policy
- room policy requires human approval
- resource policy is ambiguous
- worker state is degraded but not blocked
- sensitivity or network exposure is near a configured boundary

## Outcomes

A future result should use stable outcome and reason vocabulary. Candidate
outcomes:

```text
allow_scheduling
deny_scheduling
require_review
not_considered
```

Candidate reasons:

```text
assignment_scheduling_eligible
assignment_unknown
assignment_status_not_assigned
assignment_status_terminal
governance_evidence_missing
governance_evidence_not_preflight_allow
evidence_worker_mismatch
evidence_capability_mismatch
evidence_runtime_mismatch
evidence_sensitivity_mismatch
evidence_network_requirement_mismatch
evidence_room_mismatch
worker_unknown
worker_not_considerable
worker_degraded
worker_capability_missing
runtime_mismatch
sensitivity_exceeded
network_not_allowed
heartbeat_missing
heartbeat_stale
room_policy_blocked
guard_blocked
resource_policy_blocked
human_approval_required
```

The exact model can be smaller, but it should stay deterministic and
inspectable.

## Side-Effect Boundary

The first scheduling enforcement implementation should not write anything.

Opt-in eligibility logging writes one `GovernanceDecision` with a
distinct source:

```text
source = "worker_assignment_scheduling_eligibility"
```

The detailed logging semantics live in
`docs/WORKER_ASSIGNMENT_SCHEDULING_ELIGIBILITY_LOGGING.md`. The source
`worker_scheduling_enforcement` is reserved for a later enforcement boundary
after scheduling, reservation, routing, provider, and execution stop lines are
revisited.

Even with eligibility logging, this boundary must not:

- create assignments
- mutate assignment status implicitly
- reserve capacity
- route to providers
- call tools
- write execution logs
- store execution results
- execute work

If enforcement decides an assignment is stale, expiry should remain an explicit
status transition or service boundary, not a hidden side effect of a scheduling
check.

## Relationship To Existing Boundaries

```text
Scheduling Preview
  Explains possible workers before assignment intent exists.

Execution Preflight
  Checks one worker and can provide allow evidence for assignment creation.

WorkerAssignment
  Stores governed intent, not execution.

WorkerAssignment Status Transition
  Moves assignment intent through a controlled lifecycle.

Scheduling Enforcement
  Rechecks whether assigned intent may enter future scheduling.

Reservation
  Future capacity hold. Not implemented.

Routing
  Future provider or worker handoff. Not implemented.

Execution
  Future work run. Not implemented.
```

## Implemented First Check

The first code step is a read-only validator, not a scheduler:

```text
WorkerAssignmentSchedulingEligibilityValidator
```

It:

- accepts an assignment ID and reads current assignment, worker, heartbeat, and
  governance evidence state
- evaluates heartbeat and preflight evidence age through
  `WorkerFreshnessPolicyValidator`
- returns stable allow, deny, review, or not-considered outcomes
- explains every reason in order
- writes no decisions, audits, assignments, reservations, routes, or execution
  records
- includes tests proving no storage mutation

This remains an eligibility check, not scheduling enforcement.

## Implemented CLI Inspection

`worker-assignment-scheduling-eligibility` exposes the validator as a read-only
operator command.

It prints:

- assignment ID
- outcome
- eligible yes/no
- ordered reasons
- worker, capability, room, and governance decision IDs where available

It does not:

- write audit rows
- mutate assignments
- schedule
- reserve
- route
- call providers
- write execution logs
- execute work

With explicit `--log`, it may write one decision record for `allow_scheduling`,
`deny_scheduling`, or `require_review` results. It does not log
`not_considered` results in the first slice.

## Cycle Consolidation

The first eligibility slice and opt-in logging slice are sufficient for the
current WorkerAssignment tissue:

- the validator does not schedule, reserve, route, or execute
- eligibility logging is explicit and does not mutate assignments or audit
- reason codes are stable for the currently implemented worker inputs
- the CLI inspection surface reports the same validator outcome without writes
  unless `--log` is explicit
- heartbeat and preflight evidence freshness are now read-only eligibility
  inputs
- room policy, guard outcomes, resource policy, reflexes, and human approval
  remain future inputs because those scheduling-enforcement surfaces do not
  exist yet
- `docs/WORKER_ASSIGNMENT_TISSUE_CONSOLIDATION_REVIEW.md` consolidates the
  current WorkerAssignment tissue before further scheduling work

Next decision:

```text
WorkerAssignmentRoomContextRecheckValidator consolidation
```

Readiness gaps are documented in
`docs/WORKER_SCHEDULING_ENFORCEMENT_READINESS_GAP_REVIEW.md`.
Heartbeat and governance evidence freshness semantics are documented in
`docs/WORKER_FRESHNESS_POLICY.md` and are now used by assigned-intent
scheduling eligibility. That integration is consolidated in
`docs/WORKER_FRESHNESS_ELIGIBILITY_CONSOLIDATION_REVIEW.md`. Scheduling
enforcement remains later. Room/context recheck semantics now live in
`docs/WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK.md`, and the read-only validator
now exists in `pigenus.core.worker_assignment_room_context_recheck`. The next
safe step is consolidation before wiring, CLI, logging, scheduling
enforcement, reservation, routing, provider calls, execution logs, or
execution.

Not next:

```text
real scheduling
reservation
routing
provider calls
execution logs
execution
```
