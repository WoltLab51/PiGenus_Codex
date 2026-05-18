# Worker Room / Context Eligibility Integration Consolidation Review

This review consolidates the read-only composition of
`WorkerAssignmentRoomContextRecheckValidator` into
`WorkerAssignmentSchedulingEligibilityValidator`.

It is documentation-only. It does not add runtime code, schemas, migrations,
CLI behavior, logging behavior, graph projection, RuntimeCell behavior,
CellRegistry behavior, scheduling enforcement, reservation, routing, provider
calls, execution logs, or execution.

## Implemented Surface

The current composition is:

```text
WorkerAssignmentSchedulingEligibilityValidator
  + optional WorkerAssignmentRoomContextRecheckValidator
  + optional caller-supplied ContextStack / ContextFrames / room-flow inputs
```

The integration is opt-in:

- if no room/context recheck validator is supplied, scheduling eligibility
  keeps its previous behavior
- if a room/context recheck validator is supplied, the caller may also pass
  ContextStack, ContextFrames, source room, and target room inputs
- the scheduling eligibility validator maps the room/context result into its
  own outcome and reasons
- no CLI path supplies the room/context validator yet
- no logger path was added or changed

## Outcome Mapping

Room/context outcomes map into scheduling eligibility as follows:

```text
allow_context
-> continue normal scheduling eligibility evaluation

require_review
-> require_review

deny_context
-> deny_scheduling

not_considered
-> not_considered
```

Reason codes from the room/context validator are preserved in the scheduling
eligibility result. The `details["room_context"]` payload records the
room/context outcome, reasons, and details for caller/operator use.

## Philosophy Alignment

```text
Philosophy-Fit: green
Governance-Fit: green
Cellular-Fit: green
Worker-Boundary-Fit: green
RuntimeShape-Fit: green
Overengineering-Risk: low
Monolith-Risk: low
Recommendation: accept and pause before new effects
```

Why this fits:

- It composes two responsible CapabilityCell / GovernedCellCandidate surfaces
  without promoting either one to RuntimeCell.
- It strengthens scheduling readiness while staying below scheduling
  enforcement.
- It keeps old eligibility behavior unchanged unless the new validator is
  explicitly supplied.
- It treats missing context as visible review evidence instead of hidden
  permission.
- It preserves the worker boundary: workers remain execution hosts, not
  intelligence.

## Boundary Confirmation

The integration does not:

- mutate WorkerAssignment state
- create WorkerAssignments
- transition assignment status
- write audit events
- write governance decisions
- implicitly log eligibility or room/context results
- expose new CLI behavior
- persist ContextStacks, ContextFrames, Rooms, RoomFlowRules, or policies
- reserve capacity
- route providers
- call providers
- create execution logs
- execute work
- activate RuntimeCells or dynamic cell routing

The existing scheduling eligibility logger remains explicit and opt-in. If a
caller later passes an eligibility result containing `room_context` details to
that logger, the result details may be included in the governance decision
payload through the existing logging path. This review does not add any new
implicit logging path.

## Test Evidence

Targeted verification covered:

```text
.venv\Scripts\python.exe -m pytest tests\test_worker_assignment_scheduling_eligibility.py tests\test_worker_assignment_room_context_recheck.py tests\test_worker_assignment_scheduling_eligibility_cli.py
-> 39 passed
```

Full suite verification covered:

```text
.venv\Scripts\python.exe -m pytest
-> 332 passed
```

The new integration tests prove:

- old scheduling eligibility still allows assigned current worker intent
  when no room/context validator is supplied
- matching room/context keeps allow possible
- missing ContextStack maps to `require_review`
- ContextFrame policy mismatch maps to `deny_scheduling`
- room/context `not_considered` maps to scheduling `not_considered`
- assignment count remains unchanged
- decision count remains unchanged
- audit count remains unchanged

## Remaining Gaps

This integration is still not scheduling readiness completion.

Known gaps:

- no CLI surface for passing ContextStack / ContextFrames into eligibility
- no default room/context validator in the CLI path
- no persisted ContextStack / ContextFrame attachment to WorkerAssignment
- no room policy store
- no resource budget or risk budget
- no reflex / circuit breaker / kill-switch boundary
- no high-risk approval threshold
- no reservation boundary
- no scheduling-enforcement validator
- no worker execution path

The current integration is intentionally a composition of read-only validators,
not a move toward execution.

## Recommendation

Accept the read-only integration as the current WorkerAssignment scheduling
readiness boundary.

Do not add room/context CLI exposure or eligibility logging changes yet. The
system lacks persisted ContextStack attachment, room policy storage,
resource/risk budget semantics, and reflex boundaries. Exposing more operator
surface before those exist would make the path look more mature than it is.

Next safe decision:

```text
Implement a storage-free read-only
WorkerAssignmentResourceRiskReflexReadinessValidator with targeted no-write
tests.
```

Resource, risk, and reflex readiness semantics now live in
`docs/WORKER_RESOURCE_RISK_REFLEX_READINESS.md`.
The Cell-DNA frame now lives in
`docs/CELL_DNA_WORKER_ASSIGNMENT_RESOURCE_RISK_REFLEX_READINESS_VALIDATOR.md`.

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
