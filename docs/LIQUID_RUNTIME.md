# Liquid Runtime

Liquid Runtime is a future GENUS concept. It is not part of the v0.3 governed
runtime implementation.

The idea is to let GENUS propose a temporary runtime form for a task without
hard-coding every workflow in advance. That form may include cells, context
frames, meaning objects, rooms, resources, and output contracts.

The core rule:

```text
No proposed form becomes real without validation, guard decision, and trace.
```

## Why This Exists

The v0.3 runtime gives PiGenus stable physics:

- rooms
- contexts
- meaning
- contracts
- guard decisions
- decision logs
- audit logs
- inspection surfaces
- backups

That stability is necessary, but not sufficient for later flexible capability
orchestration. Future GENUS should be able to ask:

- which cells are relevant now?
- which context stack applies now?
- which meaning objects matter now?
- which room boundaries constrain this task?
- which resources are available?
- which output shape is expected?
- which risks or guard families are involved?

Liquid Runtime is the layer that may eventually answer those questions by
proposing a task-specific shape.

## Safe Mental Model

Do not think:

```text
simulation = reality
```

Think:

```text
simulation -> proposal -> validation -> guard decision -> execution -> trace
```

A proposed form is only a candidate. It is not a permission, not a capability,
and not a fact.

## Future Concepts

These names are provisional:

- `FormProposal`: a proposed runtime shape
- `RuntimeShape`: the validated shape selected for a task
- `ShapePreview`: a dry-run explanation of what would happen
- `ShapeTrace`: ordered evidence for why a shape was proposed and selected
- `ShapeValidator`: deterministic checks before a proposal can run

## Required Inputs

A future form proposal should be built only from known, inspectable inputs:

- task intent
- actor identity
- available cells and capabilities
- cell contracts
- context stack
- rooms
- meaning objects
- resource grants
- sensitivity and truth status
- existing guard policy

No proposal should invent a new capability at runtime.

## Required Checks

Before a proposed shape can execute, it must pass:

- contract validation
- room/context compatibility
- permission checks
- resource checks
- guard pipeline evaluation
- trace generation

If any check blocks, the shape does not run. If any check escalates, the shape
waits for explicit approval or remains a preview.

## What This Is Not

Liquid Runtime is not:

- autonomous self-modification
- arbitrary agent spawning
- dynamic permission creation
- worker scheduling by another name
- LLM-only planning
- hidden mutation
- an excuse to bypass rooms, contracts, or guards

## First Safe Implementation Shape

The first implementation, when it happens, should be read-only:

```text
Task + known runtime inventory -> FormProposal -> ShapePreview
```

It should not execute. It should not persist new runtime state except an
explicit preview record if that is separately approved.

Only after preview behavior is deterministic and inspectable should the system
consider guarded execution.

## Relationship To v0.3

v0.3 is the stable governed runtime baseline.

Liquid Runtime comes later. It depends on v0.3 because dynamic shape formation
needs stable boundaries. The kernel is not a prison; it is the physics that
lets flexible forms appear safely.
