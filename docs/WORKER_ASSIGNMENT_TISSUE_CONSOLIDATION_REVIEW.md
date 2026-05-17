# WorkerAssignment Tissue Consolidation Review

This review consolidates the current WorkerAssignment tissue after opt-in
scheduling eligibility decision logging.

It is documentation-only. It does not add runtime code, schemas, migrations,
CLI behavior, logging behavior, scheduling enforcement, reservation, routing,
provider calls, execution logs, execution, RuntimeCell behavior, CellRegistry
behavior, or graph projection.

## Purpose

The WorkerAssignment tissue now has enough surface area to pause and ask:

```text
Is this still governed assignment intent, or has it started becoming
scheduling/execution by accident?
```

Current answer:

```text
It is still governed assignment intent.
It is not scheduling.
It is not reservation.
It is not routing.
It is not execution.
```

## Current Tissue Shape

The tissue is made of these bounded capabilities and operator surfaces.

| Surface | Role | Writes | Boundary |
| --- | --- | --- | --- |
| `WorkerAssignmentRepository` | Stores assignment intent and lifecycle state. | Assignment rows/status updates | Storage only, not policy. |
| `WorkerAssignmentValidator` | Checks matching preflight allow evidence. | None | Creation evidence check only. |
| `WorkerAssignmentCreator` | Creates pending assignment intent after validation. | One assignment row and one creation audit | Intent creation, not activation. |
| `worker-assignment-create` | Operator wrapper for creation. | Through creator only | Pending intent only. |
| `WorkerAssignmentStatusTransitionValidator` | Checks assignment lifecycle transitions. | None | Status graph check only. |
| `WorkerAssignmentStatusTransitionService` | Applies allowed lifecycle transitions. | Status/update mutation and one transition audit | Lifecycle only, not execution. |
| `worker-assignment-transition` | Operator wrapper for lifecycle transitions. | Through transition service only | Status updates only. |
| `WorkerAssignmentSchedulingEligibilityValidator` | Rechecks assigned intent before future scheduling consideration. | None | Eligibility only. |
| `WorkerAssignmentSchedulingEligibilityLogger` | Persists loggable eligibility outcomes. | One decision row for allow, deny, or review | Inspection evidence only. |
| `worker-assignment-scheduling-eligibility` | Operator inspection and explicit logging surface. | One decision row only with `--log` and loggable result | No mutation, scheduling, or execution. |

## Side-Effect Map

Allowed writes in the tissue are intentionally narrow:

| Action | Assignment write | Audit write | Decision write | Execution write |
| --- | --- | --- | --- | --- |
| Validate assignment creation | no | no | no | no |
| Create pending assignment | yes | yes | no | no |
| Validate status transition | no | no | no | no |
| Apply status transition | yes | yes | no | no |
| Inspect scheduling eligibility | no | no | no | no |
| Log scheduling eligibility | no | no | yes | no |

Important boundaries:

- assignment creation references governance evidence, but does not create it
- status transition writes audit, but does not create governance decisions
- eligibility logging writes governance decisions, but does not mutate
  assignments or audit
- `not_considered` eligibility results are not persisted in the current slice
- `assigned` remains intent lifecycle state, not execution proof

## Evidence Chain

The current governed chain is:

```text
worker-scheduling-preview
-> worker-execution-preflight --log
-> worker-assignment-create
-> worker-assignment-transition assigned
-> worker-assignment-scheduling-eligibility
-> optional worker-assignment-scheduling-eligibility --log
```

What this chain proves:

- a worker was known
- a worker had matching capability/runtime/sensitivity/network properties at
  preflight time
- assignment intent was created from matching allow evidence
- assignment intent entered the `assigned` lifecycle state
- eligibility can be rechecked against current worker and evidence state
- loggable eligibility results can be persisted for later review

What this chain does not prove:

- capacity was reserved
- a scheduler accepted the work
- a provider was selected
- a worker process received work
- execution started
- execution completed
- output is valid

## Test Evidence

The current local verification result is tracked in `STATUS.md`.

The relevant coverage proves:

- validation stays read-only
- creation writes pending assignment and creation audit only
- lifecycle transition writes status/update and transition audit only
- scheduling eligibility validation stays read-only
- `--log` writes one decision for allow, deny, or review results
- `--log` skips not-considered and unknown-assignment results
- assignment count remains stable during eligibility logging
- audit count remains stable during eligibility logging
- no execution fields, logs, routes, reservations, or results exist

## Philosophy Alignment

```text
Philosophy-Fit: green
Governance-Fit: green
Cellular-Fit: green
RuntimeShape-Fit: green
Worker-Boundary-Fit: green
Overengineering-Risk: low-medium
Monolith-Risk: medium
Recommendation: accept and pause before scheduling enforcement
```

Why green:

- every meaningful side effect is explicit
- every write-capable boundary has tests
- operator logging is opt-in
- decision logging is not enforcement
- workers remain execution hosts, not intelligence
- assignment remains intent, not execution

Why some risk remains:

- worker-assignment CLI surfaces now contain several related commands
- scheduling-adjacent language can easily drift into enforcement language
- resource, risk, and reflex inputs are not implemented yet
- heartbeat and evidence freshness are now read-only eligibility inputs, but
  not enforcement inputs
- future scheduling can become too powerful if introduced before those inputs

## Readiness For Scheduling Enforcement

The tissue is not ready for real scheduling enforcement yet.

Still missing before scheduling enforcement can safely exist:

- consolidation of heartbeat/evidence freshness as read-only eligibility input
- room/context-stack recheck at enforcement time
- resource or risk budget input
- reservation model
- reflex / circuit-breaker / kill-switch boundary
- human approval threshold rules for high-risk rooms or sensitivities
- explicit distinction between enforcement decision and reservation decision
- no-execution proof for the first enforcement implementation

The next scheduling-adjacent code, when it happens, should still be read-only
unless a separate review says otherwise.

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
- RuntimeCell implementation
- CellRegistry implementation
- graph projection
- dynamic cell routing
- trading or other high-risk live behavior

## Next Recommendation

Do not implement scheduling enforcement yet.

Next safe step from this review:

```text
Worker Scheduling Enforcement Readiness Gap Review
```

That review now lives in
`docs/WORKER_SCHEDULING_ENFORCEMENT_READINESS_GAP_REVIEW.md`. It answers what
minimal inputs must exist before the first read-only scheduling enforcement
validator can be built.

Focus:

- heartbeat freshness
- evidence freshness
- room/context recheck
- resource/risk budget placeholder
- reflex / circuit-breaker / kill-switch boundaries
- no-reservation and no-execution proof

The first later code slice should be a read-only validator only, not a
scheduler, reservation manager, router, provider gateway, execution log, or
execution engine.
