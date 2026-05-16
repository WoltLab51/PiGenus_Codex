# GENUS Canonical Systemform

This document is the current source of truth for GENUS orientation.

Older blueprints, local notes, sketches, external discussions, and concept
documents remain useful as source memory only when they map back to this
canonical systemform. They may inform future work, but they must not drive
implementation by themselves.

## Conflict Rule

If another document conflicts with `docs/GENUS_CANONICAL_SYSTEMFORM.md`, this
canonical systemform wins until the conflict is resolved.

Resolution means one of:

- update the older document to map to the canonical systemform
- explicitly supersede the older statement with a durable decision
- record the older material as history or source memory only

No implementation should follow an older, conflicting direction without first
mapping it to this document.

## What GENUS Is

GENUS is a bio-cybernetic operating systemform.

It is a governed environment where digital capabilities, meaning, memory,
workers, rooms, decisions, organs, organisms, and future characters can exist,
communicate, act, recover, and evolve under inspectable control.

GENUS is closer to a cognitive operating environment than to a single
application. Its durable goal is not to appear intelligent first. Its first
duty is to make intelligence-shaped work observable, bounded, testable, and
accountable.

PiGenus is the local Python reference runtime distribution for GENUS. It is the
current executable kernel and operator surface. PiGenus is edge-friendly and
can run on small devices, but GENUS itself is not limited to Raspberry Pi
hardware or this repository.

## What GENUS Is Not

GENUS is not:

- a single AI agent
- chatbot-first
- dashboard-first
- LLM-first
- an autonomous swarm
- a hidden prompt bus
- a worker execution fabric without physiology
- mutation-as-activation
- a project where every helper becomes a heavy RuntimeCell

Workers are execution hosts, not intelligence.

Organs are composed capabilities, not folders.

Organisms live on devices or habitats.

Characters are social organisms with role, voice, memory, and relationship
behavior. They are not merely chat personas and not the root of the
architecture.

## Stable Core, Variable Form

GENUS keeps a stable core and allows variable forms around that core.

The stable core is:

- identity
- rooms
- meaning
- contracts
- guards
- decisions
- traces
- auditability
- lifecycle
- inspection
- tests

The variable form may change by:

- available cells
- active organs
- organisms
- workers
- habitats and devices
- deployment profile
- resource policy
- room policy
- context stack
- meaning scope
- output surface

Variable form is not spontaneous autonomy. A future variable form must be
previewed, validated, governed, traced, inspected, and tested before it can
act.

## Cell Principle

Every meaningful control point in GENUS should be treated as a cell-shaped
capability boundary.

This does not mean every helper function becomes a heavy runtime object. Cell
ceremony scales with responsibility.

The rule is:

```text
More responsibility -> stronger membrane, contract, trace, and lifecycle.
Less responsibility -> lighter ceremony.
```

A responsible capability is cell-worthy when it:

- decides something
- writes governed state
- moves meaning
- changes memory or lifecycle
- checks safety
- coordinates workers
- can affect resources
- can cross rooms or contexts
- may later be reused inside an organ

Small helpers may remain plain functions. A formatting helper or local boolean
comparison does not need a cell lifecycle. A worker eligibility check,
assignment creator, guard validator, meaning ingester, or resource limiter
does.

## Cell Maturity Ladder

GENUS uses a maturity ladder instead of forcing every capability to become a
RuntimeCell immediately.

### MicroCell

A MicroCell is a very small, responsibility-bearing capability boundary. It
has a clear input, output, and forbidden effects, but may not yet have a full
runtime identity or registry entry.

Use MicroCell thinking for small validators, mappers, filters, formatters with
semantic responsibility, and other reusable control points.

### Cell

A Cell is the smallest governable capability unit.

It has:

- identity
- boundary
- purpose
- input and output
- allowed effects
- forbidden effects
- tests

### CapabilityCell

A CapabilityCell is a cell that exposes a concrete capability for reuse.

It should define:

- capability name
- capability contract
- required inputs
- produced outputs
- compatible rooms or context scopes
- expected resource profile where relevant

### GovernedCell

A GovernedCell is a CapabilityCell that participates in GENUS governance.

It must define:

- contract
- membrane
- guard path
- trace output
- audit or decision behavior when relevant
- allowed and forbidden side effects
- tests proving the boundary

### RuntimeCell

A RuntimeCell is a registered executable cell in a runtime.

It additionally needs:

- runtime identity
- registry entry
- lifecycle
- inspection surface
- execution boundary
- health/status signal
- compatibility with worker or habitat constraints when relevant

RuntimeCells are not current default implementation targets. PiGenus may first
build Services, Validators, Repositories, CLI modules, and StaticCellBoundaries
as cell-ready structures.

## Tissue

A Tissue is a related group of cells that share a domain responsibility.

Canonical tissues include:

- Identity Tissue
- Meaning Tissue
- Governance Tissue
- Memory Tissue
- Capability Tissue
- Worker / Execution Tissue
- Resource Tissue
- Operator Tissue
- Storage Tissue
- Safety / Immune Tissue

Tissue is not merely a package name. It is a responsibility region.

## Organ

An Organ is a composed capability made from cells.

An organ is not a folder and not automatically an agent. It has a purpose,
input/output contract, internal cells, allowed effects, failure behavior, and
inspection path.

Examples of future organ classes:

- WorkerInspectionOrgan
- MeaningIngestionOrgan
- GuardEvaluationOrgan
- SherlookDiagnosticOrgan
- ResourceBudgetOrgan

## Organism

An Organism is a coordinated runtime composition that can live in a habitat.

It may contain cells, tissues, organs, memory scope, resource limits, and
operator surfaces. An organism has a deployment shape and must preserve the
stable core. It is not automatically autonomous.

Future examples:

- LocalDeveloperOrganism
- FamilyPrivacyOrganism
- PiEdgeOrganism
- DiagnosticOrganism
- LearningCharacterOrganism

## Character

A Character is a social organism.

It adds:

- role
- voice
- relationship memory
- durable interaction style
- social accountability
- identity continuity

Characters may use agents later, but they are not the base architecture.
Characters must remain downstream of identity, meaning, rooms, contracts,
guards, decisions, traces, and approval thresholds.

## Habitat / Device

A Habitat is the environment where an organism lives and acts.

A Device is a concrete local host or machine inside a habitat.

Habitats and devices provide:

- compute
- storage
- network access
- sensors or tools where available
- privacy constraints
- failure modes
- resource limits
- operator access

PiGenus is currently a local runtime distribution that can run inside one
habitat. Future GENUS forms may live across multiple habitats, but federation
must wait for trust, signatures, replication policy, and conflict handling.

## Nervous System

The GENUS nervous system is the governed communication path.

Canonical flow:

```text
MeaningObject
-> Event
-> GuardPipeline
-> DecisionTrace
-> GovernanceDecision
-> optional MeaningStore / EventLog / AuditLog
```

The nervous system carries structured meaning, not loose prompts. Free text is
allowed as payload only when embedded in inspectable meaning objects, events,
decisions, or traces.

Hidden prompt buses are non-canonical.

## Immune System

The GENUS immune system protects the organism from unsafe action, unsafe
meaning movement, capability escalation, stale memory, rogue workers, prompt
or meaning injection, and uncontrolled mutation.

Immune components include:

- contracts
- room policies
- guard pipeline
- room-flow rules
- human approval thresholds
- audit logs
- decision traces
- quarantine
- kill switches
- rollback and recovery paths

Governance is not an add-on. It is physiology.

## Metabolism / Resource Economy

Metabolism is how GENUS consumes, transforms, budgets, and releases resources.

Resources include:

- compute
- memory
- storage
- time
- attention
- network access
- money or energy where relevant
- human approval capacity

The Resource Economy begins with accounting, budgets, limits, and review. It
does not begin with credits, internal markets, or dynamic prices.

## Homeostasis

Homeostasis is the ability to keep the runtime inside safe operating bounds.

It requires:

- current health signals
- resource budgets
- failure semantics
- room and context constraints
- heartbeat freshness
- stale-state detection
- degradation modes
- inspection surfaces

Homeostasis comes before high-risk execution.

## Reflex / Kill Switch

A Reflex is a fast protective response triggered by known risk conditions.

A KillSwitch is the strongest reflex. It stops or disables a risky path
without waiting for a complex planning loop.

Examples of future reflexes:

- stop worker execution when heartbeat is stale
- block room crossing when sensitivity is too high
- halt repeated failed attempts
- abort execution when resource budget is exceeded
- disable an organ after unsafe output

Reflexes must be explicit, tested, inspectable, and reversible where possible.

## Quarantine

Quarantine isolates suspicious meaning, workers, cells, organs, memories, or
runtime shapes.

Quarantine means:

- do not treat as trusted active capability or knowledge
- preserve evidence
- keep inspection possible
- require review, repair, expiry, or rejection before reactivation

Quarantine is not deletion.

## Apoptosis

Apoptosis is controlled shutdown of an unsafe, obsolete, or failed capability
path.

In GENUS, apoptosis may retire or disable:

- a cell
- an organ
- a worker route
- a memory path
- a runtime shape
- a failed experiment

Apoptosis must leave traceable evidence. It is not silent disappearance.

## Regeneration

Regeneration is controlled recovery after failure, quarantine, or apoptosis.

It may restore capability through:

- rollback
- replacement
- revalidation
- rehydration from backup
- rebuilding derived state
- redeploying a safer runtime shape

Regeneration requires evidence that the recovered path is safe enough to use.

## Ecology

GENUS ecology is the interaction between cells, organs, organisms, habitats,
resources, rooms, workers, and humans over time.

Ecology asks:

- which capabilities dominate?
- which become stale?
- which should be retired?
- which relationships are symbiotic?
- which behaviors create resource pressure?
- which habitats are safe for which organisms?

Ecology is not uncontrolled swarm behavior. It is the long-term governed
interaction of many bounded parts.

## Controlled Evolution

GENUS may evolve only under controlled conditions.

Controlled evolution means:

- proposal before activation
- shadow mode before live behavior
- tests before acceptance
- fitness comparison before promotion
- human approval where required
- rollback before risk
- fossils for retired paths
- audit and trace throughout

Mutation is never activation.

## High-Risk Execution Rule

No high-risk organ may be activated without:

- room policy
- resource/risk budget
- worker/habitat health
- capability contract
- guard decision path
- reflexes / circuit breakers
- kill switch
- audit and trace
- human approval thresholds where required
- rollback, abort, or recovery path
- shadow mode or dry-run evidence before live behavior

High-risk execution includes anything that can spend money, affect private or
regulated information, call external providers, route work to workers, mutate
runtime state, write durable decisions, change lifecycle state, or perform
irreversible action.

## Non-Canonical Directions

The following directions are non-canonical unless explicitly remapped to this
systemform and accepted through later decisions:

- agent-first architecture
- LLM-first orchestration
- dashboard-first architecture
- high-risk execution without physiology
- worker execution before resource/risk/reflex/kill-switch boundaries
- dynamic cell routing before contracts, membranes, traces, tests, and
  inspection
- mutation as activation
- hidden prompt buses
- treating WorkerAssignment `assigned` status as execution proof
- treating a worker as intelligence
- treating every helper as a heavy RuntimeCell

## Implementation Posture

PiGenus should continue to build in small, testable, boring steps.

For each new responsible capability, use a lightweight Cell-DNA frame before
implementation:

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
```

The implementation may remain a Function, Service, Validator, Repository, CLI
module, or StaticCellBoundary until there is a clear reason to promote it.

The canonical direction is cell-first, not RuntimeCell-first.
