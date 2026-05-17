# Worker Freshness Policy

This document defines freshness semantics for worker heartbeat state and worker
governance evidence before any scheduling-enforcement implementation exists.

It is documentation-only. It does not add runtime code, schemas, migrations,
CLI behavior, logging behavior, heartbeat history, reservation, routing,
provider calls, execution logs, execution, RuntimeCell behavior, CellRegistry
behavior, or graph projection.

## Purpose

Worker Freshness Policy answers one narrow question:

```text
Is the worker state and governance evidence recent enough to keep considering
an assigned WorkerAssignment for future scheduling?
```

It does not answer:

```text
Should a scheduler accept the work?
Has capacity been reserved?
Which provider should receive the work?
Has execution started?
Did execution succeed?
```

Freshness is a scheduling-readiness input, not scheduling itself.

## Current Source Fields

The current runtime already has enough timestamp fields to define policy
semantics without adding storage:

| Surface | Field | Meaning |
| --- | --- | --- |
| `WorkerHeartbeat` | `seen_at` | Last known liveness signal for a worker. |
| `GovernanceDecision` / `DecisionRecord` | `created_at` | Time the preflight or eligibility decision was persisted. |
| `WorkerAssignment` | `created_at` | Time assignment intent was created. |
| `WorkerAssignment` | `updated_at` | Time assignment lifecycle state was last updated. |

SQLite and existing repositories remain the source of truth. A future freshness
validator may read these fields, but this document does not create a new truth
store.

## Freshness Labels

Freshness checks should use a small stable vocabulary:

```text
fresh
review_stale
hard_stale
missing
clock_invalid
```

Definitions:

- `fresh`: recent enough to continue if all other checks pass.
- `review_stale`: old enough to require review or escalation, but not old
  enough to be a hard block by itself.
- `hard_stale`: too old for scheduling consideration.
- `missing`: required timestamp or source record does not exist.
- `clock_invalid`: timestamp appears to be in the future or otherwise cannot
  be compared safely.

Future validators should accept an explicit `now` value so tests remain
deterministic.

## Default Local Policy Candidates

These values are policy candidates for the local v0.4 worker preparation arc.
They are not active until implemented in a future read-only validator.

### Heartbeat Freshness

| Heartbeat age | Label | Future scheduling effect |
| --- | --- | --- |
| Missing heartbeat | `missing` | Deny / not considered. |
| Future timestamp beyond tolerated clock skew | `clock_invalid` | Require review or deny for high-risk rooms. |
| `0s` to `120s` | `fresh` | May continue if all other checks pass. |
| `>120s` to `600s` | `review_stale` | Require review. |
| `>600s` | `hard_stale` | Deny scheduling consideration. |

Rationale:

- local worker liveness should be recent before scheduling
- a short review band gives operators a visible warning zone
- anything older than ten minutes is too stale for execution-adjacent behavior

### Preflight Evidence Freshness

| Preflight evidence age | Label | Future scheduling effect |
| --- | --- | --- |
| Missing preflight evidence | `missing` | Deny / not considered. |
| Future timestamp beyond tolerated clock skew | `clock_invalid` | Require review or deny for high-risk rooms. |
| `0s` to `15m` | `fresh` | May continue if all other checks pass. |
| `>15m` to `60m` | `review_stale` | Require review. |
| `>60m` | `hard_stale` | Deny scheduling consideration. |

Rationale:

- execution preflight evidence is narrower than scheduling preview evidence
- it can remain useful longer than a heartbeat
- it should not silently authorize work hours later

### Assignment Lifecycle Freshness

Assignment lifecycle age is a supporting signal, not the first hard policy
input.

Future validators may use `WorkerAssignment.updated_at` to detect how long an
assignment has been in its current lifecycle state. Candidate defaults:

| Assigned-state age | Label | Future scheduling effect |
| --- | --- | --- |
| `0m` to `30m` | `fresh` | May continue if heartbeat and evidence are also fresh. |
| `>30m` to `120m` | `review_stale` | Require review. |
| `>120m` | `hard_stale` | Deny scheduling consideration or require explicit expiry/recreation. |

The first freshness validator may defer assignment-age enforcement if it only
has heartbeat and preflight evidence as inputs. If it does use assignment age,
it must treat `assigned` as intent state only, not execution proof.

## Worker Status Interaction

Freshness does not replace worker status checks.

Default interpretation:

| Worker profile / heartbeat state | Freshness interaction |
| --- | --- |
| `active` profile + `active` heartbeat | Freshness policy may allow continuation. |
| `degraded` profile or heartbeat | Fresh heartbeat still requires review. |
| `draft`, `offline`, `suspended`, or `retired` | Deny / not considered regardless of freshness. |
| Missing profile | Deny / not considered. |
| Missing heartbeat | Deny / not considered. |

Freshness can only make a valid worker state stale. It cannot make an invalid
worker state valid.

## Evidence Scope

For WorkerAssignment scheduling enforcement, the authoritative evidence remains
the original matching `worker_execution_preflight` allow decision referenced by
`WorkerAssignment.governance_decision_id`.

`worker_assignment_scheduling_eligibility` decision records are inspection
evidence. They may help operators review what was checked, but they must not
replace the original preflight evidence or become execution proof.

## Outcome Mapping

A later read-only enforcement validator should map freshness into scheduling
outcomes conservatively:

| Freshness result | Candidate outcome |
| --- | --- |
| Required record missing | `not_considered` or `deny_scheduling`, depending on whether assignment exists. |
| Any hard-stale required input | `deny_scheduling`. |
| Any review-stale required input | `require_review`. |
| Clock invalid | `require_review` by default; `deny_scheduling` for high-risk rooms later. |
| All required inputs fresh | Continue to the next enforcement checks. |

Freshness alone should not produce final `allow_scheduling`. It is only one
required input alongside assignment status, worker capability, runtime,
sensitivity, network, room/context, guard, resource, reflex, and approval
checks.

## Reason Vocabulary

Future validators should keep reason codes stable. Candidate reasons:

```text
heartbeat_missing
heartbeat_clock_invalid
heartbeat_fresh
heartbeat_review_stale
heartbeat_hard_stale
evidence_missing
evidence_clock_invalid
evidence_fresh
evidence_review_stale
evidence_hard_stale
assignment_age_fresh
assignment_age_review_stale
assignment_age_hard_stale
```

Positive `*_fresh` reasons may be omitted from operator output if the result
would become noisy. Negative and review reasons should be visible.

## Clock Skew Rule

A future validator should compare timestamps against an explicit `now`.

If a timestamp is in the future, the validator should not silently treat it as
fresh. Small future skew may become `review_stale` / `clock_invalid`; large
future skew should block or require review. The first implementation should
avoid automatic repair.

## No Side Effects

Freshness evaluation must not:

- mutate `WorkerAssignment`
- expire assignments automatically
- write audit rows
- write governance decisions
- create reservations
- route providers
- call tools
- write execution logs
- execute work

If freshness suggests an assignment should expire, expiry must remain an
explicit lifecycle transition or later service boundary.

## First Future Validator Shape

Do not build this in this document.

The first code slice now introduces a read-only validator:

```text
WorkerFreshnessPolicyValidator
```

Current first slice:

- accepts assignment, heartbeat, preflight decision, and explicit `now`
- evaluates heartbeat freshness
- evaluates preflight evidence freshness
- optionally reports assignment lifecycle freshness
- returns labels and ordered reasons
- writes nothing
- includes no CLI at first

Implemented tests for that slice:

- fresh heartbeat and fresh evidence
- missing heartbeat
- review-stale heartbeat
- hard-stale heartbeat
- missing evidence
- review-stale evidence
- hard-stale evidence
- clock-invalid timestamp
- degraded worker remains review even when fresh
- no assignment mutation
- no decision writes
- no audit writes
- no reservation, routing, provider, or execution writes

## Relationship To Scheduling Enforcement

This policy is the next input required by
`docs/WORKER_SCHEDULING_ENFORCEMENT_READINESS_GAP_REVIEW.md`.

The storage-free `WorkerFreshnessPolicyValidator` is now wired into
assigned-intent scheduling eligibility. That integration evaluates heartbeat
and preflight evidence age read-only, returns freshness reasons through the
eligibility result, and still adds no CLI behavior, implicit logging,
reservation, routing, provider calls, execution logs, or execution behavior.

That integration is consolidated in
`docs/WORKER_FRESHNESS_ELIGIBILITY_CONSOLIDATION_REVIEW.md`.
Any future freshness exposure or persisted logging must remain explicit and
separate from scheduling, reservation, routing, provider calls, execution logs,
and execution behavior. WorkerAssignment room/context recheck semantics now
live in `docs/WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK.md`; the read-only
validator is consolidated in
`docs/WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK_CONSOLIDATION_REVIEW.md`.
The next readiness decision is whether and how to wire that validator into
assigned-intent scheduling eligibility as a read-only input.

The validator Cell-DNA frame lives in
`docs/CELL_DNA_WORKER_FRESHNESS_POLICY_VALIDATOR.md`.

## Stop Lines

Still not next:

- worker execution
- scheduling enforcement implementation
- reservation
- provider routing
- provider calls
- execution logs
- execution results
- remote worker discovery
- heartbeat history
- automatic assignment expiry
- graph projection
- RuntimeCell implementation
- CellRegistry implementation
- dynamic cell routing
- trading or other high-risk live behavior
