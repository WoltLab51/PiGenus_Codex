# Cell-DNA Consolidation Review

This review consolidates the first three applied Cell-DNA frames before the
project creates more frames or adds opt-in scheduling eligibility decision
logging.

Reviewed source documents:

- `docs/CELL_DNA_PROTOCOL.md`
- `docs/CELL_DNA_WORKER_ASSIGNMENT_VALIDATOR.md`
- `docs/CELL_DNA_WORKER_ASSIGNMENT_SCHEDULING_ELIGIBILITY_VALIDATOR.md`
- `docs/CELL_DNA_WORKER_ASSIGNMENT_CREATOR.md`

This is docs-only. It does not change runtime code, schemas, migrations, CLI
behavior, decision logging, eligibility logging, audit behavior, scheduling
enforcement, reservation, routing, provider calls, execution, RuntimeCell
behavior, CellRegistry behavior, or graph projection.

## 1. Does The Protocol Help?

Yes.

The protocol makes responsible capability boundaries clearer in the places
that matter most:

- inputs are explicit instead of implied by service signatures
- outputs are named as result objects, outcomes, ids, reason codes, or audit ids
- reads are separated from writes
- writes are narrow enough to review
- allowed effects are small and testable
- forbidden effects catch future temptation before it becomes code
- trace/audit behavior is no longer mixed into general "side effects"
- tests become proof of the membrane, not just behavior checks
- next maturity is bounded instead of aspirational

The three frames show that Cell-DNA is useful before RuntimeCell exists. It
does not make services dynamic. It makes them inspectable as possible future
cells.

Most useful fields so far:

- Writes
- Forbidden effects
- Trace / audit behavior
- Tests
- Next possible maturity

These fields prevent hidden worker execution, hidden scheduling, hidden audit
or decision writes, and accidental RuntimeCell language.

## 2. Is The Protocol Too Heavy?

Partly.

The full frame is appropriate for write-capable or governance-sensitive
capabilities. It may be too verbose for MicroCells and very small
CapabilityCells.

Fields that can become redundant for lightweight read-only candidates:

- State / lifecycle assumptions
- Non-goals
- long failure-reason inventories
- long promotion blocker lists

The protocol should stay available in full, but future use should scale:

```text
MicroCell:
  use compact frame

CapabilityCell:
  use compact frame plus Trace/Audit when relevant

GovernedCellCandidate:
  use full frame

Write-capable capability:
  use full frame and name every durable write explicitly
```

The current `docs/CELL_DNA_PROTOCOL.md` is light enough if the project treats
optional fields as optional for low-risk cells.

## 3. Are The Three Examples Consistent?

Yes, with one useful distinction.

| Frame | Maturity | Writes | Trace/Audit | Main Boundary |
| --- | --- | --- | --- | --- |
| `WorkerAssignmentValidator` | CapabilityCell / GovernedCellCandidate | none | none persisted | validation evidence only |
| `WorkerAssignmentSchedulingEligibilityValidator` | CapabilityCell / GovernedCellCandidate | none | none persisted | scheduling consideration only |
| `WorkerAssignmentCreator` | CapabilityCell / GovernedCellCandidate | one assignment and existing creation audit on success | audit exists, no trace | durable assignment intent creation |

Consistency check:

- maturity labels match
- read/write boundaries are clear
- forbidden effects consistently block execution, scheduling enforcement,
  reservation, routing, provider calls, RuntimeCell activation, and graph truth
- audit/trace language distinguishes "returns reasons" from "persists audit"
- no-execution language is explicit in all three
- next possible maturity is consistently `GovernedCell with explicit contract
  and returned trace shape`
- RuntimeCell remains later and blocked on CellRegistry, contract validation,
  lifecycle, inspection, and runtime execution boundaries

The useful distinction is that `WorkerAssignmentCreator` is write-capable. Its
frame correctly documents that the current code already writes one assignment
record and one creation audit row on success. That proves the protocol can
handle write-capable cells without hiding writes.

## 4. Minimum Cell-DNA Frame

Future candidates should use this compact required subset:

```text
Capability:
Maturity:
Inputs:
Outputs:
Reads:
Writes:
Allowed effects:
Forbidden effects:
Tests:
Next possible maturity:
```

Optional fields:

```text
Trace / audit behavior:
State / lifecycle assumptions:
Non-goals:
```

Guidance:

- Make Trace / audit behavior required when a capability returns a trace,
  writes audit, writes decisions, or may later add logging.
- Make State / lifecycle assumptions required when assignment, memory, worker,
  approval, or lifecycle status is involved.
- Make Non-goals required when the feature is close to execution, scheduling,
  routing, providers, LLMs, graph projection, mutation, or high-risk behavior.

## 5. Next Runtime Decision

Two options are plausible.

### Option A: Opt-In Eligibility Decision Logging

Description:

Add explicit logging for scheduling eligibility results. This would persist a
decision record when an operator opts in.

Fit:

- philosophy fit: good if logging stays explicit and inspectable
- governance risk: medium, because eligibility is scheduling-adjacent
- write risk: medium, because it adds a new durable decision write
- runtime risk: low-medium if it remains logging-only
- documentation need: medium; decision semantics must be named before code
- test need: high; must prove opt-in only, no assignment mutation, no audit
  surprise, no scheduling enforcement, no reservation, no routing, no execution

Should happen now?

Not yet.

It can happen soon, but only after its semantics are framed. The eligibility
result must be clearly described as:

```text
loggable inspection evidence
not scheduling enforcement
not assignment state
not reservation
not routing
not execution
```

### Option B: WorkerAssignmentStatusTransitionService Cell-DNA

Description:

Document the existing write-capable lifecycle service that applies validated
assignment status transitions and writes audit.

Fit:

- philosophy fit: strong; lifecycle state is a meaningful control point
- governance risk: medium, but already implemented and test-covered
- write risk: medium, because it mutates assignment status and writes audit
- runtime risk: low if documented only
- documentation need: medium; it should distinguish lifecycle status from
  execution proof
- test need: already mostly covered; review should map existing tests to the
  membrane

Should happen now?

Yes.

This should be the next Cell-DNA frame before eligibility decision logging. It
documents an existing write-capable lifecycle boundary and reinforces the rule:

```text
assigned does not mean executed
```

## 6. Recommendation

Recommendation:

```text
Document WorkerAssignmentStatusTransitionService Cell-DNA first.
Do not implement eligibility decision logging yet.
```

Reason:

The protocol is useful enough and not too heavy when scaled by responsibility.
The first three frames are consistent. But before adding a new decision logging
write, the project should document the existing assignment lifecycle write
path. That gives the WorkerAssignment tissue a complete shape:

```text
validate creation evidence
create intent
transition lifecycle status
inspect scheduling eligibility
```

Eligibility decision logging may follow after the review confirms:

- eligibility result semantics are stable
- persisted logging is opt-in
- logging is not scheduling enforcement
- logging does not mutate assignment state
- logging does not create reservation
- logging does not route to providers
- logging does not call providers
- logging does not execute work

## 7. Stop Lines

Current stop lines remain:

- no worker execution
- no scheduling enforcement
- no reservation
- no provider routing
- no provider calls
- no trading behavior
- no RuntimeCell implementation
- no CellRegistry
- no graph projection
- no dynamic cell routing

## Conclusion

Cell-DNA should continue.

Use the compact required frame by default. Use the full frame when a capability
writes durable state, touches lifecycle, writes audit or decisions, approaches
worker scheduling, or could later become a GovernedCell or RuntimeCell.

Next safe step:

```text
Add WorkerAssignmentStatusTransitionService Cell-DNA.
```

## Follow-Up

The recommended lifecycle-changing frame is now documented in:

```text
docs/CELL_DNA_WORKER_ASSIGNMENT_STATUS_TRANSITION_SERVICE.md
```

Eligibility decision logging remains out of scope until a separate decision
and implementation slice.
