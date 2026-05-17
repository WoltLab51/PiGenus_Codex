# Cellular Inventory Review

This review executes Arc A from `docs/CANONICAL_IMPLEMENTATION_PLAN.md`.

It checks the initial cellular inventory against the current codebase and
identifies which existing surfaces are ready for lightweight Cell-DNA framing
before any further worker power is added.

This is a docs-only review. It does not change runtime code, schemas,
migrations, CLI behavior, worker execution, scheduling enforcement, graph
implementation, trading behavior, or dynamic runtime-cell routing.

## Method

Reviewed code surfaces:

- `pigenus/core/guard_pipeline.py`
- `pigenus/core/governance_decision_log.py`
- `pigenus/core/meaning_ingestion.py`
- `pigenus/core/orchestrator.py`
- `pigenus/core/worker_assignment_validator.py`
- `pigenus/core/worker_assignment_creator.py`
- `pigenus/core/worker_assignment_status_transition_validator.py`
- `pigenus/core/worker_assignment_status_transition.py`
- `pigenus/core/worker_assignment_scheduling_eligibility.py`
- `pigenus/storage/repositories.py`
- `pigenus/storage/worker_repositories.py`
- `pigenus/cli/worker_assignment_commands.py`
- `pigenus/cli/worker_assignment_inspection_commands.py`
- `pigenus/cli/worker_assignment_lifecycle_commands.py`
- current worker-assignment tests

Review questions:

- What does the component read?
- What does it write?
- Does it make a decision, mutate state, or only format/route?
- Does it already have a clear membrane?
- Does it remain deterministic and testable?
- Does it preserve the no-execution Worker Runtime boundary?
- Is it a Function, MicroCell, CapabilityCell, GovernedCell candidate, Tissue,
  OperatorSurface, StorageBoundary, or later RuntimeCell/Organ?

## Summary Judgment

The initial inventory in `docs/CANONICAL_IMPLEMENTATION_PLAN.md` matches the
current code shape.

Most current components are not yet RuntimeCells. That is correct. PiGenus has
several strong GovernedCell candidates and several static operator/storage
boundaries, but it should not promote them into dynamic runtime cells until
Cell-DNA, contracts, inspection, lifecycle, and tests are explicit.

Current fit:

```text
philosophy fit: green
worker boundary fit: green
cellular fit: green-yellow
runtime-cell readiness: not yet
storage/source-of-truth fit: green
monolith risk: medium
overengineering risk: low-medium
next safe step: Cell-DNA construction protocol
```

## Code-Checked Inventory Notes

| Surface | Current Shape | Code-Checked Notes | Review Result |
| --- | --- | --- | --- |
| `GuardPipeline` | Tissue | Composes contract validation and room-flow checks, returns ordered trace, does not persist by itself. | Keep as immune/governance tissue. Do not force it into one cell. |
| `GovernanceDecisionLogger` | GovernedCellCandidate | Converts `GovernanceDecision` into durable `DecisionRecord` and writes through `DecisionRepository`. | Strong Cell-DNA candidate because it writes governance evidence. |
| `MeaningIngestionPreview` | GovernedCellCandidate | Reads memory, adapts to meaning, writes only if the target meaning row does not exist. | Strong candidate for meaning-metabolism Cell-DNA. |
| `SimpleOrchestrator` | OrganLater | Coordinates primitive cells, context checks, guard preview, decision logging, memory write, and events. | Keep deterministic. Do not let it become an autonomous agent loop. |
| `WorkerAssignmentRepository` | StorageBoundary | Stores assignment intent, validates worker/decision existence, updates status. | Correct storage boundary; semantic validation belongs outside. |
| `WorkerAssignmentValidator` | GovernedCellCandidate | Read-only validation against worker existence, pending status, preflight allow evidence, and matching request fields. | Best first Cell-DNA candidate because membrane is clear and writes are forbidden. |
| `WorkerAssignmentCreator` | GovernedCellCandidate | Uses validator, writes pending assignment and one audit row on success. | Cell-worthy, but should get Cell-DNA after validator frame exists. |
| `WorkerAssignmentStatusTransitionValidator` | MicroCell / CapabilityCell candidate | Read-only status transition validation with stable reason codes. | Small responsible capability; can remain lightweight. |
| `WorkerAssignmentStatusTransitionService` | GovernedCellCandidate | Applies validated lifecycle transition and writes audit on success. | Cell-worthy lifecycle control point; not execution proof. |
| `WorkerAssignmentSchedulingEligibilityValidator` | GovernedCellCandidate | Read-only assigned-intent eligibility check; tests prove no assignment, decision, or audit writes. | Strong candidate, but logging should wait for Cell-DNA protocol. |
| Worker assignment CLI router | OperatorSurface | Dispatches inspection vs lifecycle command modules; no domain policy. | Keep thin. |
| Worker assignment inspection CLI | OperatorSurface | `list` and scheduling eligibility inspection; no writes. | Correct operator surface. |
| Worker assignment lifecycle CLI | OperatorSurface | Wraps creator and transition service; writes only through services. | Correct for now; do not let CLI own policy. |
| Shared repositories | StorageBoundary | Still contains several storage domains, but worker storage has been sliced out. | Continue slicing only when pressure returns. |
| Worker storage module | StorageBoundary | Contains worker profiles, current heartbeats, assignment intent. | Acceptable domain boundary for v0.4. |
| Primitive runtime cells in `pigenus/cells` | RuntimeCellLater | Existing MVP cells are executable, but predate canonical Cell-DNA maturity. | Review before promotion; do not use as template for dynamic routing yet. |

## Confirmed Boundaries

Worker Runtime remains preparation-only:

- no worker execution
- no scheduling enforcement
- no reservation
- no provider routing
- no remote worker discovery
- no graph implementation
- no dynamic RuntimeCell routing
- no autonomous organism behavior
- no treating `assigned` WorkerAssignment status as execution proof

Storage remains the current source of truth:

- SQLite repositories write canonical runtime records.
- The Metabolic State Graph remains a future derived view.
- No graph database or graph schema exists.

Operator surfaces remain operator surfaces:

- CLI modules may route, inspect, and call services.
- CLI modules should not own policy.
- Writes must stay service-backed.

## First Cell-DNA Candidates

Recommended order:

1. `WorkerAssignmentValidator`
2. `WorkerAssignmentSchedulingEligibilityValidator`
3. `WorkerAssignmentCreator`
4. `WorkerAssignmentStatusTransitionService`
5. `MeaningIngestionPreview`
6. `GovernanceDecisionLogger`

Reasoning:

- Start with read-only validators because their membranes are easiest to prove.
- Add write-capable services only after the Cell-DNA frame is settled.
- Keep operator modules as static boundaries until service membranes are clear.
- Do not promote any component to RuntimeCell yet.

## Recommended Next Build Slice

Next safe slice:

```text
Arc B: Cell-DNA Construction Protocol
```

Goal:

Define a lightweight, reusable Cell-DNA frame for new responsible
capabilities, then apply it first to `WorkerAssignmentValidator`.

The frame should capture:

```text
Capability:
Maturity:
Input:
Output:
Reads:
Writes:
Allowed effects:
Forbidden effects:
Trace / audit:
Tests:
Promotion blocker:
```

Acceptance:

- docs-only first
- no runtime code changes
- no schemas or migrations
- no CLI additions
- no worker execution
- no scheduling enforcement
- no graph implementation
- no dynamic RuntimeCell routing
- no treating the frame as heavy RuntimeCell ceremony

## Risks

### RuntimeCell Too Early

The code has executable MVP cells, but the canonical systemform is newer than
that early runtime shape. Promoting current services directly to RuntimeCell
would skip contract, lifecycle, inspection, and registry questions.

Mitigation:

Use `GovernedCellCandidate` and Cell-DNA frames before RuntimeCell behavior.

### Operator Surface Growth

Worker assignment command handling is now sliced into router, inspection, and
lifecycle modules. The split is healthy, but future commands could make the
operator surface thick again.

Mitigation:

Keep CLI modules thin and service-backed. Split again only when responsibility,
not just line count, demands it.

### Storage Semantics Becoming Policy

Repositories enforce source-of-truth existence and persistence, but they should
not become policy engines.

Mitigation:

Keep semantic evidence checks in validators/services and keep repositories as
storage boundaries.

## Conclusion

Arc A is complete enough to move forward.

The next safe move is not more worker behavior. It is a small Cell-DNA
construction protocol and one first applied frame for
`WorkerAssignmentValidator`.

That keeps GENUS cell-first without becoming RuntimeCell-first.

## Follow-Up

The first application target is now documented in:

```text
docs/CELL_DNA_WORKER_ASSIGNMENT_VALIDATOR.md
```

The second application target validates the protocol beyond assignment
creation evidence:

```text
docs/CELL_DNA_WORKER_ASSIGNMENT_SCHEDULING_ELIGIBILITY_VALIDATOR.md
```

The first write-capable application target documents assignment intent creation
and its existing audit write:

```text
docs/CELL_DNA_WORKER_ASSIGNMENT_CREATOR.md
```

The lifecycle-changing application target documents status updates and their
existing audit write:

```text
docs/CELL_DNA_WORKER_ASSIGNMENT_STATUS_TRANSITION_SERVICE.md
```

The protocol source is:

```text
docs/CELL_DNA_PROTOCOL.md
```
