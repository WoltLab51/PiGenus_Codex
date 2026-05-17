# Worker Scheduling Enforcement Readiness Gap Review

This review checks whether the current WorkerAssignment tissue is ready for the
first scheduling-enforcement validator.

It is documentation-only. It does not add runtime code, schemas, migrations,
CLI behavior, logging behavior, graph projection, RuntimeCell behavior,
CellRegistry behavior, reservation, routing, provider calls, execution logs, or
execution.

## Purpose

The current worker runtime can create governed assignment intent, move that
intent through a controlled lifecycle, inspect assigned-intent scheduling
eligibility, and optionally log eligibility decisions.

That is still not enough to enforce scheduling.

This review answers:

```text
What is missing before an assigned WorkerAssignment can be checked by a real
scheduling-enforcement boundary?
```

Current answer:

```text
Scheduling enforcement is not ready yet.
The next safe step is freshness semantics, not enforcement code.
```

## Current Ready Inputs

The current runtime has several useful inputs for a future enforcement check.

| Input | Current Status | Notes |
| --- | --- | --- |
| `WorkerAssignment` | Implemented | Durable governed intent with status, worker, capability, room, and evidence reference. |
| Assignment status graph | Implemented | `pending -> assigned/rejected/cancelled/expired`; `assigned -> cancelled/expired`; terminal states stay terminal. |
| Creation validation | Implemented | Requires known worker and matching `worker_execution_preflight` allow evidence. |
| Current worker profile | Implemented | Durable worker identity, capabilities, runtime, sensitivity, and network boundary. |
| Current worker heartbeat | Implemented | Latest heartbeat state with `seen_at`; freshness policy is now used by eligibility checks, but no heartbeat history exists. |
| Governance decision evidence | Implemented | Durable decision log can store preview, preflight, and eligibility decisions. |
| Scheduling eligibility validator | Implemented | Rechecks assigned intent against current worker and evidence state. |
| Eligibility logging | Implemented | Explicit `--log` writes one decision for allow, deny, or review results only. |
| Worker freshness validator | Implemented | Storage-free validator is wired into assigned-intent eligibility for heartbeat and preflight evidence age checks. |
| Tests | Implemented | Current full suite is tracked in `STATUS.md`. |

These inputs prove that a governed intent chain exists. They do not prove that
the intent is fresh, budgeted, approved, reservable, routeable, or executable.

## Gap Matrix

| Gap | Current State | Why It Matters | First Safe Treatment |
| --- | --- | --- | --- |
| Heartbeat freshness | Policy and read-only eligibility integration exist; no heartbeat history or enforcement exists. | A worker can be active in storage but too stale for scheduling. | Consolidate read-only behavior before enforcement code. |
| Evidence freshness | Policy and read-only eligibility integration exist; no revocation model exists. | Old preflight allow evidence may no longer be safe. | Keep expiry/review bands in eligibility; defer revocation and enforcement. |
| Room/context recheck | Read-only validator implemented and optionally wired into scheduling eligibility; no CLI, logging, or enforcement exists. | Room policy can change after assignment creation. | Consolidate read-only eligibility integration before CLI, logging, or enforcement code. |
| Resource/risk budget | Resource concepts exist, but no scheduling budget input. | Scheduling needs capacity and risk pressure, not only worker capability. | Define placeholder resource/risk inputs before reservation. |
| Reflex/circuit breaker | Canonical systemform defines reflexes, but worker runtime has no kill-switch path. | Enforcement must be stoppable before live behavior appears. | Define reflex and kill-switch boundary before any high-risk path. |
| Human approval thresholds | Human approval exists as a stub, but is not connected to worker scheduling. | Sensitive rooms or capabilities may need approval before scheduling. | Define threshold rules before high-risk scheduling. |
| Reservation distinction | No reservation model exists. | Enforcement must not silently become capacity reservation. | Keep enforcement read-only until reservation has a separate model. |
| Enforcement logging semantics | Eligibility logging exists; enforcement logging source is reserved. | Persisted enforcement records must not be confused with eligibility evidence. | Define later as a distinct source after readiness inputs exist. |
| No-execution proof | Eligibility tests prove no writes except explicit logging; enforcement has no tests yet. | First enforcement implementation must prove no scheduling, reservation, routing, or execution. | Require no-write/no-execution tests in the first code slice. |

## Freshness Was The First Missing Boundary

The first missing boundary identified by this review was freshness.

The current storage already has:

- `WorkerHeartbeat.seen_at`
- `WorkerAssignment.created_at`
- `WorkerAssignment.updated_at`
- `GovernanceDecision.created_at`

The runtime now defines and tests:

- when a heartbeat is fresh
- when a heartbeat requires review
- when a heartbeat is too stale to consider
- when preflight evidence is fresh
- when preflight evidence requires review
- when preflight evidence is too stale to consider
- whether degraded worker state changes freshness tolerance

Still unresolved:

- whether freshness thresholds become room-specific, capability-specific, or
  resource-policy-specific
- evidence revocation beyond age bands
- heartbeat history beyond current heartbeat state

That policy and a storage-free validator now exist, and assigned-intent
eligibility consumes them read-only. Enforcement still must not appear until
the remaining resource, risk, reflex, approval, reservation, and no-execution
boundaries are explicit.

## Scheduling Enforcement Must Stay Separate

Scheduling enforcement should eventually answer:

```text
May this assigned intent enter scheduling consideration now?
```

It must still not answer:

```text
Has capacity been reserved?
Which provider receives the work?
Has execution started?
Did execution produce output?
```

The first enforcement implementation, when the remaining gaps are closed,
should remain
read-only:

- read assignment
- read current worker
- read current heartbeat
- read governance evidence
- evaluate freshness policy
- evaluate room/resource/reflex placeholders where available
- return ordered reasons
- write nothing

## Minimal First Enforcement Validator, Later

Do not build this yet.

When ready, the first validator should be small and storage-read-only. It should
probably be named around the assignment boundary, for example:

```text
WorkerAssignmentSchedulingEnforcementValidator
```

Its initial Cell-DNA should state:

- Maturity: `CapabilityCell / GovernedCellCandidate`
- Inputs: assignment ID plus configured freshness policy
- Outputs: allow, deny, review, or not-considered result with stable reasons
- Reads: assignment, worker profile, current heartbeat, governance decision
- Writes: none
- Forbidden effects: no assignment mutation, no audit write, no decision
  logging, no reservation, no routing, no provider call, no execution
- Tests: allow/review/deny, stale heartbeat, stale evidence, missing evidence,
  no-write proof, no-execution proof

Eligibility logging should not be reused as enforcement logging. A later
enforcement logger needs a distinct source after the first validator is stable.

## Philosophy Alignment

```text
Philosophy-Fit: green
Governance-Fit: green
Cellular-Fit: green
RuntimeShape-Fit: green
Worker-Boundary-Fit: green
Overengineering-Risk: low
Monolith-Risk: low
Recommendation: do not implement enforcement yet; define freshness first
```

Why green:

- the review preserves the worker-as-host boundary
- `assigned` remains intent state, not execution proof
- enforcement remains separate from reservation, routing, and execution
- freshness is treated as explicit policy rather than hidden code behavior
- no new source of truth is introduced

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
- graph projection
- RuntimeCell implementation
- CellRegistry implementation
- dynamic cell routing
- trading or other high-risk live behavior

## Recommendation

Do not implement scheduling enforcement yet.

Next safe step:

```text
Consolidate the read-only room/context scheduling eligibility integration.
```

The current policy and implementation now live in
`docs/WORKER_FRESHNESS_POLICY.md`,
`docs/CELL_DNA_WORKER_FRESHNESS_POLICY_VALIDATOR.md`,
`pigenus.core.worker_freshness_policy`, and
`pigenus.core.worker_assignment_scheduling_eligibility`.

They define and test:

- heartbeat freshness bands
- evidence freshness bands
- hard-stale vs review-stale behavior
- default thresholds for local worker preparation
- how freshness interacts with degraded workers
- how future rooms, resources, and risk policy may override thresholds
- no-write expectations for freshness-integrated eligibility

The freshness integration is consolidated in
`docs/WORKER_FRESHNESS_ELIGIBILITY_CONSOLIDATION_REVIEW.md`.

Room/context recheck semantics now live in
`docs/WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK.md`. The corresponding Cell-DNA
frame now lives in
`docs/CELL_DNA_WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK_VALIDATOR.md`. The
read-only validator now exists in
`pigenus.core.worker_assignment_room_context_recheck`. The implementation is
consolidated in
`docs/WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK_CONSOLIDATION_REVIEW.md`.
The validator is now wired into scheduling eligibility only when explicitly
supplied by a caller. Next, PiGenus should consolidate that integration without
adding CLI, logging, scheduling enforcement, reservation, routing, provider
calls, execution logs, or execution.
Scheduling enforcement remains later.
