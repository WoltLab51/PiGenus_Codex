# Cellular Systemform

This document defines the cellular architecture philosophy for GENUS.

It is not a refactor plan by itself. It explains what a GENUS cell is, what is
not a cell, and how existing code should move toward cell-like structure
without weakening governance.

## Core Idea

A GENUS cell is not simply a small function.

A GENUS cell is the smallest responsible capability unit with its own boundary,
identity, contract, allowed effects, observable output, lifecycle, and tests.

GENUS does not decompose to the smallest line of code. It decomposes to the
smallest governable capability.

## Why Cells

Biological cells matter because they are living boundary units. They have a
membrane, identity, internal machinery, signal intake, signal output,
metabolism, rules, state, and participation in larger structures.

GENUS uses the cell metaphor in the same disciplined way:

```text
capability + boundary + contract + responsibility + lifecycle
```

This is why GENUS starts with cells before agents. An agent hides too much
behavior if the capabilities beneath it do not already have clear boundaries.

## What A Cell Is

A GENUS cell should be able to answer:

```text
Who am I?
What capability do I provide?
What may enter?
What may leave?
Which room or context may I act in?
Which permissions do I need?
Which side effects may I create?
Which decisions or traces explain my work?
How is my lifecycle managed?
Which tests prove my contract?
```

Current and future examples:

- a cell that reads a worker profile
- a cell that checks worker heartbeat freshness
- a cell that evaluates capability compatibility
- a cell that builds a preflight decision trace
- a cell that persists one explicit governance decision
- a cell that converts memory into meaning
- a cell that applies one guard family

## What Is Not A Cell

Small code is not automatically a cell.

Usually not cells:

- one `if` statement
- one formatting line
- one repository helper method
- one JSON serialization detail
- one print statement
- one ad hoc utility function

These can be parts of a cell, just as biological cells contain smaller
components. Turning every small implementation detail into a cell would create
bureaucracy instead of biology.

## When Cellular Architecture Is Worth It

Cellular Systemform is justified only when the system needs many capabilities,
many boundaries, many responsibilities, and strong inspectability.

It is useful when GENUS must support:

- many reusable capabilities
- sensitive rooms and contexts
- governed memory and meaning
- worker and device boundaries
- future agents or organs
- guardable communication
- lifecycle and deprecation behavior
- durable decisions and traces
- later controlled evolution

For a small single-purpose tool, this would be too much architecture.

## When It Is Too Much

Cellular architecture becomes harmful when it is used as decoration.

Warning signs:

- every helper gets a grand cell name
- every small function gets lifecycle and contract ceremony
- every change requires excessive documentation
- routing becomes harder to test than the capability itself
- files get smaller but responsibility stays hidden
- the biological metaphor starts making decisions instead of requirements

GENUS should not die by architecture poetry. The metaphor is useful only when
it improves boundaries, reuse, governance, inspection, or tests.

## Responsibility Test

Before making something cell-like, ask:

```text
Does this capability carry responsibility?
```

Responsibility means it does at least one meaningful thing:

- reads governed data
- writes governed data
- decides or blocks something
- moves meaning
- checks safety
- creates a decision
- changes memory
- coordinates a worker
- can be reused by another organ, agent, CLI, or runtime surface

If yes, it may deserve cell DNA.

If no, it should probably remain a normal function, helper, formatter, or
repository method.

Examples:

```text
WorkerExecutionPreflight = cell-worthy
RoomFlowGuard = cell-worthy
MeaningIngestion = cell-worthy
JSON indentation = helper
string concatenation = helper
boolean comparison = helper
```

## Cell DNA

Every mature GENUS cell should have some version of this DNA:

```text
CellIdentity
  id
  name
  type
  version
  status

CellPurpose
  capability
  reason to exist
  non-goals

CellContract
  input
  output
  permissions
  room/context scope
  resource expectations

CellMembrane
  accepted input
  allowed output
  sensitivity limits
  truth-status rules
  side-effect boundary

CellState
  temporary state
  lifecycle status
  last used time
  quality or fitness signals

CellEffects
  read-only behavior
  memory writes
  decision writes
  audit writes
  event publication

CellTrace
  decision
  reason
  source
  error
  guard or policy path

CellTests
  contract tests
  boundary tests
  side-effect tests
  lifecycle tests
```

This extends the existing architecture contract:

```text
contract + context + room + meaning + guard + decision + trace + test
```

## Cell Membrane

The membrane is more important than the code.

A GENUS cell is only a cell if its boundary is explicit:

- input contract
- output contract
- room or context boundary
- sensitivity boundary
- permission boundary
- side-effect boundary

Without a membrane, a small file can still become a hidden authority that
touches storage, logs, guards, CLI output, external APIs, and other cells
without review.

## Cell Nucleus

The nucleus of a GENUS cell is not just Python code.

The nucleus is its identity and contract:

- `CellSpec`
- `CellContract`
- capabilities
- permissions
- lifecycle
- version
- tests

The code is one implementation of the cell. Later, the same cell capability may
have different implementations for local, remote, optimized, sandbox, or test
runtime profiles.

## Cell Metabolism

Cells consume, transform, and produce.

A GENUS cell should be explicit about:

- what it reads
- what it computes
- what it emits
- what it may persist
- what it must never mutate
- what trace it leaves

Example:

```text
WorkerExecutionPreflightCell

Consumes:
  worker_id
  capability
  required_runtime
  sensitivity
  network_required

Reads:
  WorkerProfile
  WorkerHeartbeat

Produces:
  WorkerExecutionPreflightResult
  ordered checks
  log-compatible GovernanceDecision

Optional effect:
  one DecisionRecord only through explicit logging

Never:
  assignment
  reservation
  provider route
  execution
```

## Cells, Organs, Agents, Characters

GENUS grows through composition:

```text
Cell -> Organ -> Agent -> Character
```

Definitions:

- Cell: smallest responsible capability unit
- Tissue: related cells with a shared domain
- Organ: coordinated capability made from multiple cells
- Agent: goal-directed coordinator using organs or cells
- Character: agent-facing identity with voice, role, relationships, and memory

An organ is not a folder. It is a composed capability.

Example future organ:

```text
WorkerReadinessOrgan
  WorkerProfileReadCell
  WorkerHeartbeatReadCell
  WorkerConsiderableCheckCell
  CapabilityMatchCell
  SensitivityLimitCell
  NetworkRequirementCell
  PreflightDecisionBuildCell
  OptionalDecisionLogCell
```

## Immune System

GENUS safety is not an add-on. It is the immune system.

Current immune surfaces include:

- contracts
- permissions
- room flow rules
- guard pipeline
- human approval
- quarantine concepts
- audit logs
- decision traces

A capability without governance is not a free cell in GENUS. It is an unsafe
growth risk.

## Nervous System

Cells do not communicate through hidden prompt strings or private direct calls
for meaningful actions.

GENUS communication should move through governed signals:

```text
MeaningObject
Event
GuardPipeline
DecisionTrace
GovernanceDecision
EventLog
AuditLog
MeaningStore
```

Natural language may be a payload, but it is not the communication boundary by
itself.

## Memory

Not every signal becomes memory.

GENUS keeps these distinct:

```text
Event != MemoryObject
MeaningObject != MemoryObject
Observation != Truth
LLM output != Knowledge
```

Healthy memory flow is selective:

```text
observation -> meaning -> guard -> memory -> lifecycle -> fossil or refresh
```

## Evolution

Biology does not mean uncontrolled mutation.

GENUS may eventually evolve, but only through:

- mutation proposals
- shadow mode
- explicit fitness comparison
- tests
- guard checks
- human approval
- rollback
- fossil records

Mutation is never activation. Simulation is never execution.

## Existing Code Transformation

The current code should not be rewritten from scratch. It should be
re-differentiated.

The path is:

```text
large coordination file
-> static domain module
-> smaller command/service boundaries
-> explicit cell-like contracts
-> later runtime cells or organs
```

Current examples:

- `pigenus/cli/main.py` remains the deterministic CLI entry point
- `pigenus/cli/worker_commands.py` is a first static cell boundary
- future CLI modules should stay small enough to become command cells or organs
- worker storage repositories have split into a dedicated domain module
- remaining repository domains may split later before new persistence surfaces
  become too dense

## Static Cell Boundary Rule

Static module boundaries are the bridge from ordinary software structure to
runtime cells.

Rule:

```text
CLI modules are temporary static cell boundaries.
They should remain small enough to later become command cells or organs.
```

Fitness signal:

```text
If an operator command module grows beyond roughly 250 lines,
create a follow-up slicing decision.
```

This is not a hard law. It is a signal that a module may be collecting too many
responsibilities.

## Current Non-Goals

Cellular Systemform does not currently mean:

- dynamic cell runtime
- autonomous cell routing
- agent swarm behavior
- hidden self-organization
- LLM-driven command dispatch
- repository split in the same step as every CLI extraction
- rewriting the whole runtime

## Red Lines

Cellular Systemform must preserve these red lines:

```text
No cell without clear use.
No dynamic behavior without trace.
No capability without contract.
No architecture that makes tests slower than the insight it creates.
```

These rules keep cellular design practical. GENUS should become more
cell-shaped only where that improves accountability.

## Conclusion

GENUS is a cognitive operating environment whose smallest living architecture
unit is not the agent and not the function.

Its smallest living architecture unit is the governed capability cell.

Healthy GENUS growth means:

```text
bounded cells
observable signals
governed composition
testable organs
accountable agents
controlled evolution
```
