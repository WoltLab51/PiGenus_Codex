# WorkerAssignment Scheduling Eligibility Logging

This document defines the semantics for future opt-in decision logging of
`WorkerAssignmentSchedulingEligibilityValidator` results.

It is a documentation-only boundary. It does not add runtime code, schemas,
migrations, CLI flags, audit behavior, scheduling enforcement, reservation,
routing, provider calls, execution logs, execution, RuntimeCell behavior,
CellRegistry behavior, or graph projection.

## Purpose

Eligibility logging answers one narrow operator question:

```text
Should this read-only scheduling eligibility result be persisted as decision
evidence for later review?
```

It does not answer:

```text
Should scheduling start?
Should capacity be reserved?
Should a provider receive work?
Has the worker executed anything?
Did the assignment complete?
```

The logged record is inspection evidence. It is not scheduling enforcement.

## Source And Family

Future logging should use a distinct decision source:

```text
source = "worker_assignment_scheduling_eligibility"
family = "worker_assignment_scheduling_eligibility"
rule_id = "worker_assignment_scheduling_eligibility"
```

This keeps assignment-level eligibility logging separate from:

- `worker_scheduling_preview`
- `worker_execution_preflight`
- future real scheduling enforcement
- future reservation
- future routing
- future execution records

Do not use `worker_scheduling_enforcement` for this first logging surface. The
current capability is eligibility inspection only.

## Logging Trigger

Logging must be explicit opt-in only.

Expected CLI shape for a later implementation:

```text
worker-assignment-scheduling-eligibility <assignment_id> --log
```

Without `--log`, the command must remain read-only and write nothing.

With `--log`, the command may write exactly one decision record and still must
not write audit rows, mutate assignments, reserve workers, route providers,
call providers, write execution logs, or execute work.

## Subject, Actor, Room, And Event

The logged decision should use:

- `subject_id`: the assignment ID being inspected
- `actor`: explicit CLI actor argument, with a safe default such as
  `worker_assignment_scheduling_eligibility_cli`
- `room_id`: the assignment's room when the assignment exists
- `event_id`: optional operator-supplied event ID

If the assignment does not exist, the implementation may either:

- not log missing-assignment results, or
- log them only with an explicit fallback room such as `room_developer`

The first code slice should prefer the smaller, safer rule:

```text
Do not log unknown assignments.
```

Unknown assignment output should stay inspectable on stdout, but not become a
durable governance decision until a clearer operator need exists.

## Outcome Mapping

`WorkerAssignmentSchedulingEligibilityOutcome` should map to governance
decision values as follows:

| Eligibility outcome | Future logged decision | Reason |
| --- | --- | --- |
| `allow_scheduling` | `allow` | `assignment_scheduling_eligible` |
| `deny_scheduling` | `block` | first deny reason |
| `require_review` | `escalate` | first review reason |
| `not_considered` | `warn` or no log | first not-considered reason |

Recommended first implementation:

```text
allow_scheduling -> allow
deny_scheduling -> block
require_review -> escalate
not_considered -> no persisted record
```

Reason:

`not_considered` often means the assignment is missing, pending, terminal, or
otherwise outside the scheduling-eligibility boundary. Persisting it as a
governance decision can make inspection noise look like policy action.

If a later operator workflow needs durable `not_considered` records, add that
as a separate decision with tests and documentation.

## Decision Details

The future logged record should preserve enough detail for review without
becoming execution state:

```text
details:
  family: worker_assignment_scheduling_eligibility
  assignment_id: ...
  outcome: allow_scheduling | deny_scheduling | require_review
  eligible: true | false
  reasons: [...]
  worker_id: ...
  capability: ...
  room_id: ...
  governance_decision_id: ...
  assignment_status: ...
  worker_status: ...
  heartbeat_status: ...
  decision_source: ...
  decision_type: ...
  trace:
    - name: worker_assignment_scheduling_eligibility
      family: worker_assignment_scheduling_eligibility
      decision: allow | block | escalate
      reason: ...
      details: ...
```

The record may reference the original `worker_execution_preflight` evidence,
but it must not replace that evidence or rewrite assignment state.

## Allowed Effects

Future opt-in logging may:

- run the existing read-only eligibility validator
- convert eligible, denied, or review results into one governance decision
- write exactly one decision record when `--log` is explicitly provided
- print the logged decision ID to the operator
- preserve outcome, reasons, worker, capability, room, and evidence IDs

## Forbidden Effects

Future opt-in logging must not:

- create WorkerAssignment intent
- mutate WorkerAssignment status
- write audit rows
- enforce scheduling
- reserve capacity
- route to providers
- call providers
- discover remote workers
- write execution logs
- store execution results
- execute work
- activate RuntimeCells
- update graph projections
- treat `assigned` as execution proof
- treat a logged eligibility decision as execution proof
- treat a worker as intelligence

## Test Requirements

The first implementation should add tests for:

- no `--log` remains read-only
- `allow_scheduling --log` writes exactly one decision record
- `deny_scheduling --log` writes exactly one decision record
- `require_review --log` writes exactly one decision record
- `not_considered --log` does not write a decision record in the first slice
- missing assignment with `--log` does not write a decision record
- assignment count remains unchanged
- audit count remains unchanged
- no execution fields or execution result records are created
- logged record source is `worker_assignment_scheduling_eligibility`
- logged record family is `worker_assignment_scheduling_eligibility`
- logged room comes from the assignment when the assignment exists

Full-suite verification is required for the code slice because it changes CLI
behavior and decision persistence.

## Stop Lines

This logging surface remains before scheduling enforcement.

Still not implemented:

- scheduling enforcement
- reservation
- provider routing
- provider calls
- execution logs
- execution
- graph projection
- RuntimeCell behavior
- dynamic cell routing
- trading or other high-risk live behavior

## Next Safe Implementation Slice

The next safe code slice may add:

```text
worker-assignment-scheduling-eligibility --log
```

Acceptance:

- explicit opt-in only
- one decision record for allow, deny, or review results
- no persisted record for unknown or not-considered results in the first slice
- no assignment mutation
- no audit write
- no scheduling, reservation, routing, provider calls, execution logs, or
  execution
