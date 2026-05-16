# Architecture Convergence Review

This review aligns the current GENUS/PiGenus architecture after the Systemform,
Worker Runtime preparation, and Cellular Systemform work. It is not a feature
plan and not a refactor commit. It is a decision map for how the parts fit
together before the next cell-oriented code slice.

The goal is to prevent the project from growing by metaphor alone. GENUS may use
biological language, but every architecture move must still answer what exists,
what acts, what stores, what decides, what communicates, what runs where, and
what may become dynamic.

## Scope

This review covers:

- core anatomy / tissue map
- maturity levels from helper function to character
- transition rules between maturity levels
- current repository mapping
- runtime flow boundaries
- hot path vs governed path
- runtime shape / deployment shape boundary
- static vs dynamic boundary rules
- open decisions before further cell-oriented refactors

Out of scope:

- no runtime code changes
- no schema or migration changes
- no CLI command extraction
- no repository split
- no dynamic cell runtime
- no worker assignment activation or execution
- no worker execution
- no LLM, dashboard, federation, or evolution behavior

## Convergence Thesis

GENUS is converging toward this shape:

```text
Systemform Kernel
  identity + rooms + meaning + contracts + guards + decisions

Stable Core / Variable Runtime Shape
  the governed core remains stable while deployment-specific shape varies

Cellular Runtime Direction
  governable capabilities that can later become runtime cells and organs

Worker Runtime Direction
  execution hosts that run governed capabilities, not independent intelligence

Operator Surface
  deterministic CLI and inspection surfaces before dashboard or autonomy
```

The current codebase should not be restarted. It should be re-differentiated:
large coordination surfaces become static boundaries, static boundaries become
smaller capability units, and only mature capability units may later become
runtime cells.

## Runtime Shape / Deployment Shape

A RuntimeShape is a checked composition of available runtime surfaces for a
specific task, device, room, resource profile, and output surface.

It may include:

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

A RuntimeShape is not automatic dynamic behavior. It is a proposed or selected
form that must remain downstream of the stable core:

```text
identity
room/context boundary
meaning scope
contracts
guards
decision trace
governance decision
inspection path
```

Example future shapes:

- Pi Local Shape
- Developer Shape
- Server Shape
- Family Privacy Shape
- Sherlook Diagnostic Shape
- Learning Character Shape

### ShapePreview

A ShapePreview explains what form GENUS would take for a task before activating
that form. It may compare available cells, workers, resources, room policy, and
meaning scope, but it must not execute, assign, reserve, route providers, or
mutate state by itself.

### ShapeValidator

A ShapeValidator checks that a proposed shape preserves the stable core. It
should verify required cells, worker eligibility, context stack, room policy,
resource policy, output surface, and inspection path before any future
activation.

### ShapeTrace

A ShapeTrace records why a shape was considered acceptable, blocked, or
escalated. It is the trace surface that prevents variable form from becoming
hidden runtime improvisation.

Rule:

```text
No runtime shape activation without preview, validation, guard decision, and
trace.
```

## Core Anatomy

The following tissues are architecture categories, not mandatory Python modules
or runtime classes.

### Identity Tissue

Purpose: define who or what can be responsible.

Current surfaces:

- `ActorIdentity`
- `ActorType`
- `CellSpec`
- worker IDs in `WorkerProfile`
- future character or agent identities

Boundary:

Identity does not grant permission. It only makes responsibility addressable.

### Capability Tissue

Purpose: define what can be done.

Current surfaces:

- `CellSpec`
- `CellContract`
- capabilities
- permissions
- future CellType / CellInstance boundaries

Boundary:

Capability declaration is not authorization. Authorization requires contracts,
room/context scope, permissions, and guardability.

### Meaning Tissue

Purpose: carry inspectable semantics instead of loose text.

Current surfaces:

- `MeaningObject`
- `MeaningRepository`
- `meaning-list`
- `meaning-show`
- memory-to-meaning ingestion
- truth status
- sensitivity
- provenance

Boundary:

Meaning is not automatically memory and not automatically truth.

### Context And Governance Tissue

Purpose: decide whether meaning or action may proceed.

Current surfaces:

- `Room`
- `ContextFrame`
- `ContextStack`
- `ContextBoundaryEngine`
- `ContractValidator`
- `RoomFlowRules`
- `GuardPipeline`
- guard families
- `GovernanceDecision`
- decision traces
- human approval stubs

Boundary:

Governance is not a UI layer and not an afterthought. It is the immune system of
GENUS.

### Memory Tissue

Purpose: make durable memory explicit, aging, and inspectable.

Current surfaces:

- `MemoryObject`
- memory lifecycle statuses
- review and expiry rules
- fossils
- audit and decision records for lifecycle changes

Boundary:

Memory is not a cache, not all meaning, and not all events.

### Event And Trace Tissue

Purpose: show what happened and why.

Current surfaces:

- `Event`
- `EventRepository`
- `EventBus`
- decision logs
- audit logs
- guard traces
- context-boundary decisions

Boundary:

EventLog, AuditLog, and GovernanceDecision remain distinct surfaces.

### Resource Tissue

Purpose: constrain compute, storage, time, network, privacy, and cost.

Current surfaces:

- `ResourceGrant`
- worker cost profiles
- worker privacy profiles
- future resource accounting

Boundary:

Resource policy starts with accounting and limits, not markets or optimization.

### Worker Interface Tissue

Purpose: connect governed capabilities to execution hosts.

Current surfaces:

- `WorkerProfile`
- `WorkerHeartbeat`
- `WorkerRepository`
- `WorkerRegistry`
- `WorkerInspectionService`
- `WorkerSchedulingPreviewService`
- `WorkerExecutionPreflightService`
- `WorkerAssignment`
- `WorkerAssignmentRepository`

Boundary:

Worker means execution host, not intelligence. Workers do not bypass rooms,
contracts, guards, decisions, approval, resource policy, or auditability.

### Operator And Inspection Tissue

Purpose: make the runtime observable before it becomes more capable.

Current surfaces:

- CLI commands
- read-only inspection commands
- health check
- runtime overview
- backup creation
- architecture and status docs

Boundary:

Operator surfaces are not the runtime core. They expose and inspect governed
state.

## Maturity Ladder

Every component should be classifiable at one of these levels.

### Function

A helper with no independent architecture responsibility.

Examples:

- simple string formatting
- JSON indentation
- small value conversion
- pure predicates without durable meaning

Rule:

Do not inflate simple helpers into cells.

### Service

A unit of domain logic with meaningful behavior, but not yet full Cell DNA.

Examples:

- `WorkerExecutionPreflightService`
- `WorkerSchedulingPreviewService`
- `MeaningIngestionPreview`

Rule:

Services may be cell-worthy, but a service is not automatically a cell.

### StaticCellBoundary

A static code boundary that groups related behavior and prepares later cell-like
structure while keeping execution deterministic.

Examples:

- `pigenus/cli/worker_commands.py`
- future `pigenus/cli/meaning_commands.py`

Rule:

Static boundaries are transitional. They should reveal responsibilities, not
hide new mini-monoliths.

### GovernedCell

A capability with explicit identity, purpose, input, output, allowed effects,
lifecycle, trace, and tests.

Current status:

Mostly a target maturity level. Some services are candidates, but they should
not be promoted casually.

Rule:

A governed cell is a declared architecture unit, not just a class name.

### RuntimeCell

A registered executable cell in the runtime with lifecycle, contract validation,
permission checks, and execution boundary.

Current status:

Current MVP cells exist, but broader dynamic runtime-cell behavior is not yet a
general architecture pattern.

Rule:

Do not introduce dynamic runtime cell discovery or routing before contracts,
membranes, traces, tests, and inspection are explicit.

### Organ

A composed capability made from multiple cells.

Examples:

- future `WorkerReadinessOrgan`
- future `MeaningIngestionOrgan`
- future `SherlookLightOrgan`

Rule:

An organ is not a folder. It is a coordinated capability with input, output,
policy, and trace expectations.

### Agent

A goal-directed coordinator that uses cells and organs.

Current status:

Documented, not active runtime direction.

Rule:

Agents come after cells and organs. Starting with agents hides too much behavior.

### Character

An agent-facing identity with role, voice, relationship memory, and long-term
interaction behavior.

Current status:

Future concept.

Rule:

Characters require stable memory, identity, governance, and relationship
boundaries first.

## Transition Rules

Use these rules before promoting a component.

### Function To Service

Promote when:

- logic becomes reusable domain behavior
- behavior needs direct tests
- output carries domain meaning

Do not promote when:

- it is only formatting, small conversion, or a local predicate

### Service To StaticCellBoundary

Promote when:

- a domain area collects several related responsibilities
- the current file becomes harder to inspect
- tests already cover behavior and side effects
- extraction can preserve command names, output, storage, and exit codes

Do not promote when:

- the extraction only moves mess into a new file

### StaticCellBoundary To GovernedCell

Promote when the candidate has:

- clear identity
- explicit input and output
- allowed effects
- room/context assumptions
- trace or decision behavior
- lifecycle expectation
- contract and boundary tests

Do not promote when:

- the module still mixes parser, storage, formatting, decision, and business
  logic without an explicit membrane

### GovernedCell To RuntimeCell

Promote only when:

- registration exists
- contract validation exists
- execution boundary exists
- lifecycle status exists
- inspection path exists
- tests prove failure and side-effect behavior

Do not promote when:

- dynamic behavior would make execution harder to explain than the static path

### Cells To Organ

Promote when:

- multiple cells repeatedly cooperate to provide one larger capability
- the composition has a stable input and output
- the composition needs its own contract or trace

Do not promote when:

- the folder structure merely groups files by theme

## Current Repository Mapping

| Surface | Current Maturity | Notes |
| --- | --- | --- |
| `pigenus/cli/main.py` | Operator dispatcher | Deterministic entry point; should shrink through static boundaries, not become dynamic router yet. |
| `pigenus/cli/worker_commands.py` | StaticCellBoundary | First static cell boundary; useful but not yet a runtime cell or organ. |
| `pigenus/cli/worker_assignment_commands.py` | StaticCellBoundary | Assignment inspection and pending-intent creation boundary; not status activation, routing, or execution. |
| `WorkerExecutionPreflightService` | Service / governed-cell candidate | Cell-worthy because it checks capability, sensitivity, network, and worker state, but should not be treated as final cell architecture yet. |
| `WorkerExecutionPreflightLogger` | Service / governed-cell candidate | Persists one explicit governance decision; candidate for later logging cell. |
| `WorkerSchedulingPreviewService` | Service / governed-cell candidate | Explains candidate suitability but does not schedule. |
| `WorkerRepository` | Worker storage adapter | Source-of-truth access in `pigenus/storage/worker_repositories.py`, not a cell by itself. |
| `WorkerAssignmentRepository` | Worker storage adapter | Durable assignment-intent storage in `pigenus/storage/worker_repositories.py`, not execution or routing. |
| `MeaningRepository` | Storage adapter | Meaning persistence, not a cell by itself. |
| `MeaningIngestionPreview` | Service / governed-cell candidate | Converts memory to meaning with explicit behavior. |
| `GuardPipeline` | Governance service / immune tissue | Cell-worthy family surface, but currently best understood as core governance tissue. |
| `RoomFlowRules` | Governance service | Deterministic policy tissue. |
| `ContextBoundaryEngine` | Governance service | Checks context boundary; not operator surface. |
| `SimpleOrchestrator` | Deterministic runtime coordinator | Should not become an autonomous agent. |
| `pigenus/storage/repositories.py` | Shared storage compatibility surface | Worker repositories have been domain-sliced; remaining domains may split later before new execution/resource stores. |
| `docs/CELLULAR_SYSTEMFORM.md` | Philosophy / cell rulebook | Defines cellular architecture but does not decide every component mapping. |

## Runtime Flow Boundaries

GENUS needs two explicit flow classes.

### Hot Path

The hot path is for local, internal, low-risk operations that do not carry
meaning, move rooms, write governed state, or make decisions.

Examples:

- formatting a line
- sorting local rows
- converting enum values for display
- building a temporary list for output

Rules:

- keep it simple
- avoid unnecessary governance ceremony
- keep it testable where useful
- do not persist or move meaning from the hot path

### Governed Path

The governed path is required when an operation:

- moves meaning
- writes memory
- writes decisions
- writes audit logs
- crosses rooms or contexts
- checks safety
- coordinates workers
- creates durable assignment intent
- changes lifecycle state
- uses LLM, remote worker, federation, or future evolution surfaces

Required surfaces may include:

```text
TaskEnvelope / explicit input
Context or ContextStack
MeaningObject where semantics are carried
GuardPipeline or specific guard service
DecisionTrace
GovernanceDecision where policy is decided
optional EventLog / AuditLog / MeaningStore / MemoryStore
```

Rule:

Do not push every helper into the governed path. Do not let any meaningful
capability bypass the governed path.

## Static Versus Dynamic Boundaries

### Allowed Now

- static module boundaries
- explicit services
- explicit CLI handlers
- explicit repositories
- explicit logging via opt-in flags
- model-only future shapes before storage or execution
- deterministic tests and CI

### Not Allowed Yet

- autonomous cell routing
- dynamic command-cell discovery
- self-organizing organs
- LLM-dispatched internal commands
- agent-driven runtime mutation
- worker execution
- remote worker discovery
- implicit decision logging
- assignment creation without storage and governance review

### Later Possible

Later dynamic behavior may be allowed only after:

- cell identity is explicit
- cell contract is explicit
- membrane / side effects are explicit
- trace is explicit
- inspection path exists
- tests prove allow, block, failure, and side effects
- human approval exists where escalation or activation needs it

## Current Open Decisions

These are deliberately unresolved.

1. WorkerAssignment has gained a minimal SQLite repository and read-only
   `worker-assignment-list` inspection before pending creation was exposed.
2. Meaning CLI extraction has been chosen and implemented as the next
   StaticCellBoundary; worker command internals remain stable for now.
3. When should a service become an official GovernedCell rather than a
   cell-worthy service?
4. Should the remaining non-worker repositories split by storage domain before
   adding further execution or resource stores?
5. What is the first true Organ candidate: WorkerReadinessOrgan,
   MeaningIngestionOrgan, or SherlookLightOrgan?
6. What minimal CellSpec/CellContract additions are needed before general
   RuntimeCell behavior can exist?
7. Which traces belong in hot-path tests and which require durable
   GovernanceDecision records?
8. What must remain impossible even after dynamic cells exist?

## Non-Goals

This convergence review does not approve:

- a rewrite of the repository
- a dynamic cell runtime
- agent-first planning
- LLM-first orchestration
- autonomous worker execution
- implicit assignment creation
- repository splitting in the same step as every CLI extraction
- treating every service as a cell
- treating every helper as a cell

## Practical Next Step

The first Philosophy Alignment Review chose the Meaning CLI extraction over
WorkerAssignment storage because it reduced operator-surface monolith risk
without changing storage, runtime behavior, assignments, routing, or execution.

Before the next code refactor, choose one narrow path:

```text
Option A: Define WorkerAssignment status transition semantics before activation commands.
Option B: Slice worker_commands.py internally if it exceeds the practical
          review threshold.
Option C: Extract decision/guard CLI as a StaticCellBoundary.
```

Recommended order:

1. Keep WorkerAssignment creation separate from activation and execution.
2. Apply the Philosophy Alignment Review before choosing storage or more
   operator-surface slicing.
3. Do not promote any service to GovernedCell or RuntimeCell in the same commit.
4. Run the full test suite after any code movement.

## Conclusion

GENUS is converging toward a governed capability organism, but the safe path is
not to make everything dynamic.

The safe path is:

```text
stable kernel
-> explicit anatomy
-> maturity levels
-> static boundaries
-> governed cells
-> organs
-> agents
-> controlled evolution
```

The next builds should use this map to avoid both monolith drift and cellular
overengineering.
