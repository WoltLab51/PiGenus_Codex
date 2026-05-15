# Philosophy Alignment Review Protocol

This protocol checks whether a PiGenus change still fits the GENUS philosophy.

Use it for non-trivial code, architecture, vocabulary, runtime, worker,
cellular, storage, governance, or documentation changes. It is not a runtime
feature and not a blocker for small wording fixes.

## Purpose

GENUS should grow without drifting away from its core posture:

```text
observable
bounded
testable
accountable
governed
```

The protocol exists to catch:

- philosophy drift
- governance bypass
- premature dynamic behavior
- unclear cell maturity
- documentation drift
- new mini-monoliths
- architecture ceremony without practical value

## Review Output

Every full alignment review should end with:

```text
Philosophy Fit: green / yellow / red
Governance Fit: green / yellow / red
Cellular Fit: green / yellow / red
RuntimeShape Fit: green / yellow / red
Overengineering Risk: low / medium / high
Monolith Risk: low / medium / high
Recommendation: accept / sharpen / stop

Plausible: yes / no / partly
Consistent: yes / no / partly
Complete: yes / no / partly
```

## 1. Philosophy Alignment

Question:

```text
Does the change strengthen the GENUS philosophy?
```

GENUS is not a single AI agent, chatbot wrapper, dashboard-first product, or
autonomous swarm. It is a governed environment for digital capabilities,
meaning, memory, agents, workers, and decisions.

Green when the change strengthens:

- observability
- boundedness
- testability
- accountability
- meaning before raw text
- contracts before capability growth
- governance before autonomy
- accountability before scale

Yellow when useful behavior exists but boundaries or terms are unclear.

Red when the change introduces hidden decisions, early autonomy, trusted raw LLM
output, or capability without governance and traceability.

## 2. Stable Core / Variable Form

Question:

```text
Does the change preserve the stable core?
```

Stable core:

```text
identity + rooms + meaning + contracts + guards + decisions + traces
```

Variable form may include:

- cells
- organs
- workers
- device profiles
- resource policies
- interfaces
- deployment profiles
- output surfaces

Green when form changes and the core remains stable.

Yellow when the core is extended with a decision, tests, and documentation.

Red when the stable core is silently changed, bypassed, or weakened.

## 3. Cellular Systemform

Question:

```text
What maturity level does this component actually have?
```

Allowed maturity labels:

- Function
- Service
- StaticCellBoundary
- GovernedCell
- RuntimeCell
- Organ
- Agent
- Character

Required statement for new non-trivial components:

```text
This component is currently:
It must not yet be:
Next possible maturity level:
```

Examples:

```text
WorkerExecutionPreflightService
Currently: Service / GovernedCell candidate
Must not yet be: RuntimeCell
Next possible maturity level: GovernedCell after explicit Cell DNA
```

Green when the maturity label is honest and bounded.

Yellow when the component is cell-worthy but lacks explicit membrane, contract,
trace, or lifecycle.

Red when ordinary code is renamed as a cell, or a service becomes dynamic
runtime behavior without the required cell boundary.

## 4. Governance Path

Question:

```text
Is this hot-path behavior or governed-path behavior?
```

Hot path is allowed for low-risk local work:

- formatting
- sorting
- temporary display
- enum conversion
- small helper functions

Governed path is required when the change:

- moves meaning
- writes memory
- writes decisions
- writes audit logs
- crosses rooms or contexts
- checks safety
- coordinates workers
- creates assignment intent
- changes lifecycle state
- touches LLM, remote worker, federation, or evolution surfaces

Green when the correct path is chosen.

Yellow when path classification needs a decision.

Red when meaningful action happens in the hot path.

## 5. RuntimeShape / DeploymentShape

Question:

```text
Does the change imply a runtime shape?
```

RuntimeShape is a checked composition of:

- available cells
- active organs
- workers
- device profile
- deployment profile
- room policy
- context stack
- resource policy
- meaning scope
- output surface

Hard rule:

```text
No runtime shape activation without preview, validation, guard decision, and
trace.
```

Green when shape behavior remains previewed, validated, and traceable.

Yellow when the concept is useful but validator or trace is not defined yet.

Red when a shape becomes implicitly active.

## 6. Static Versus Dynamic Boundary

Question:

```text
Does this introduce dynamic behavior too early?
```

Allowed now:

- static module boundaries
- explicit services
- explicit CLI handlers
- explicit repositories
- opt-in logging
- model-only future shapes
- deterministic tests and CI

Not allowed yet:

- autonomous cell routing
- dynamic command-cell discovery
- self-organizing organs
- LLM-dispatched internal commands
- agent-driven runtime mutation
- worker execution
- remote worker discovery
- implicit decision logging
- assignment creation without governance review

Green when the change stays explicit and deterministic.

Yellow when dynamic behavior is preview-only and non-activating.

Red when dynamic activation appears without validation, trace, and governance.

## 7. Worker Boundary

Question:

```text
Is a worker still treated as an execution host?
```

Allowed current worker surfaces:

- WorkerProfile
- WorkerHeartbeat
- WorkerInspection
- WorkerSchedulingPreview
- WorkerExecutionPreflight
- model-only WorkerAssignment

Still out of scope:

- real execution
- provider routing
- remote discovery
- autonomous worker decisions
- implicit assignment creation

Green when the worker remains a host.

Yellow when the change approaches assignment or scheduling and needs governance
review.

Red when the worker behaves like an agent or bypasses guards.

## 8. Documentation Drift

Question:

```text
Which documents must change for the repository to remain truthful?
```

Update matrix:

```text
New term -> docs/GENUS_VOCABULARY.md
New durable rule -> docs/DECISIONS.md
New current truth -> STATUS.md
New roadmap/order -> BUILD_PLAN.md
New architecture history -> docs/ARCHITECTURE_HISTORY.md
New safety boundary -> docs/ARCHITECTURE_CONTRACT.md or docs/THREAT_MODEL.md
New cell/form boundary -> docs/CELLULAR_SYSTEMFORM.md or docs/ARCHITECTURE_CONVERGENCE_REVIEW.md
```

Green when affected documents are updated or explicitly checked.

Yellow when only a minor reference is missing.

Red when a term, rule, status, or boundary changed but docs did not.

## 9. Code Shape / Monolith Risk

Questions:

```text
Does a module grow beyond roughly 250 lines?
Does it mix parser, storage, business logic, formatting, and governance?
Does it hide more than one architecture responsibility?
Was one large block only moved into a new file?
```

Green when responsibility is clear and the cut is useful.

Yellow when a module grows but the tradeoff is understood.

Red when a new mini-monolith appears.

## 10. Verification

Question:

```text
What check level matches the risk?
```

Guidance:

```text
Docs-only -> git diff --check and relevant doc review
CLI change -> CLI tests and full suite
Storage change -> migration, repository, and health tests
Governance change -> allow/block/escalate and trace tests
Meaning change -> roundtrip, filters, read-only behavior, provenance
Worker change -> no execution, no assignment, no implicit logging, decision compatibility
RuntimeShape change -> preview-only, validator, trace, no activation
```

Green when verification matches risk.

Yellow when coverage is narrow but acceptable.

Red when behavior changed without tests.

## 11. Overengineering

Questions:

```text
Is a helper being inflated into a cell?
Does the change need the new terms it introduces?
Does the structure improve boundaries, reuse, governance, inspection, or tests?
Is routing becoming harder to test than the capability itself?
Is documentation larger than the insight it creates?
```

Green when structure solves a real problem.

Yellow when the concept is useful but should be smaller.

Red when architecture is being added for its own sake.

## Full Review Template

```text
# GENUS Philosophy Alignment Review

## 1. Change / Commit / PR
Name:
Area:
Kind:
- Docs
- Code
- CLI
- Storage
- Governance
- Worker
- Meaning
- RuntimeShape
- Cell/Organ
- Other

## 2. Short Verdict
Philosophy Fit:
Governance Fit:
Cellular Fit:
RuntimeShape Fit:
Overengineering Risk:
Monolith Risk:
Recommendation:

## 3. Architecture Surfaces
Stable Core:
Variable Form:
Identity Tissue:
Capability Tissue:
Meaning Tissue:
Governance Tissue:
Memory Tissue:
Worker Interface Tissue:
Operator Tissue:

## 4. Maturity Classification
New/changed component:
Current maturity:
Must not yet be:
Next possible maturity:

## 5. Hot Path vs Governed Path
Hot Path affected:
Governed Path affected:
Reason:

## 6. Stable Core / Variable Form
Does the core remain stable?
What form may vary?
Is ShapePreview/ShapeValidator/ShapeTrace needed?

## 7. Governance
Who decides?
Which guard or policy applies?
Is there a DecisionTrace?
Is there a GovernanceDecision?
Is logging explicit or implicit?

## 8. Meaning / Memory
Is meaning moved?
Is memory written?
Are TruthStatus, Sensitivity, or Provenance affected?
Is lifecycle affected?

## 9. Worker / Runtime
Is a worker affected?
Does the worker remain only an execution host?
Is assignment, execution, or routing introduced?
Is everything preview-only?

## 10. Documentation
Checked/updated:
- STATUS.md
- BUILD_PLAN.md
- CHANGELOG.md
- docs/GENUS_VOCABULARY.md
- docs/DECISIONS.md
- docs/ARCHITECTURE_HISTORY.md
- docs/ARCHITECTURE_CONTRACT.md
- docs/CELLULAR_SYSTEMFORM.md
- docs/ARCHITECTURE_CONVERGENCE_REVIEW.md
- docs/THREAT_MODEL.md
- other:

## 11. Tests / Checks
Required:
Executed:
Not executed, because:

## 12. Risks
Monolith Risk:
Overengineering Risk:
Governance Bypass Risk:
Documentation Drift Risk:
Premature Dynamics Risk:
Performance Risk:

## 13. Decision
Accept:
Sharpen:
Stop:
Next sensible step:

## 14. Closure
Plausible:
Consistent:
Complete:
```

## Quick Review

When a full template is too much, check these seven questions:

```text
1. Does GENUS remain stable core + variable form?
2. Is the capability covered by contract, governance, trace, or tests?
3. Is this truly a cell/boundary, or just renamed code?
4. Was dynamic behavior introduced too early?
5. Do workers remain execution hosts?
6. Are Meaning, Memory, Event, Decision, and Audit still distinct?
7. Are docs and tests proportional to risk?
```

If any answer is red, stop and sharpen the change before building more.

## Current Use

Use this protocol before:

- the next Meaning CLI StaticCellBoundary extraction
- any WorkerAssignment repository or CLI step
- any service-to-cell promotion
- any RuntimeShape or DeviceProfile implementation
- any LLM, worker execution, federation, dashboard, or evolution work

This protocol should make GENUS easier to inspect, not harder to change.
