# Multimodal Systemform

This document records a future GENUS architecture principle: GENUS should not
be reduced to text-first reasoning.

The current PiGenus runtime is intentionally textual, structured, local, and
deterministic. That is correct for the governed kernel. Long term, GENUS may
need to combine language, structured meaning, graphs, state fields, time,
actions, and visual or spatial representations.

This is a concept boundary, not an implementation plan.

## Core Claim

Language is an interface and reasoning tool. It should not become the whole
internal world model.

GENUS should be able to support:

- structured meaning objects
- meaning graphs
- event dynamics
- context stacks
- runtime state fields
- visual or spatial representations
- action traces
- natural-language explanations

The target is not a prompt bus. The target is governed multimodal meaning.

## Language Models

Language models are useful for:

- abstraction
- planning
- explanation
- role understanding
- summarization
- semantic translation
- flexible communication

But language models can also produce:

- narrative coherence without truth
- plausible explanations without evidence
- inefficient token-heavy reasoning
- weak geometry or physical state handling
- hidden assumptions inside free text

In GENUS terms, an LLM should be a governed capability behind contracts, rooms,
meaning, resources, guards, and traces. It is not the kernel.

## Visual And Spatial Models

Visual or spatial models are useful for:

- scene structure
- pattern recognition
- geometry
- physical consistency
- dense world-state compression
- sensor-like inputs

But they can also be:

- harder to audit
- less precise in symbolic communication
- difficult to constrain
- opaque without structured traces

In GENUS terms, visual or spatial representations should become meaning-bearing
objects only when their provenance, confidence, room, sensitivity, and guard
path are explicit.

## Dynamic Meaning Fields

Future GENUS may need something closer to dynamic meaning fields than rigid
layer stacks.

Useful mental model:

```text
current state + goal + room + context + meaning + resources + constraints
-> proposed form
-> validation
-> guard decision
-> action or preview
-> trace
```

This is compatible with Liquid Runtime, but it does not remove governance.

Simulation is not permission. A predicted form is only a proposal until the
runtime validates it, guards it, and records the trace.

## Relationship To Internal Communication

Internal communication remains structured:

```text
MeaningObject -> Event -> GuardPipeline -> DecisionTrace -> GovernanceDecision
```

Multimodal content may appear as payload, reference, derived meaning, or future
state representation. It must still preserve:

- source
- provenance
- room
- truth status or confidence
- sensitivity
- time reference
- guardability
- inspection path

Free text, images, embeddings, graphs, and state fields should not bypass the
same governance rules.

## Relationship To Workers

Worker Runtime may eventually host multimodal capabilities:

- local CPU workers
- GPU workers
- camera or sensor workers
- embedding workers
- visual model workers
- LLM workers

That does not change the worker boundary:

```text
Worker = execution host
Cell = capability
Organ = capability composition
Agent = goal-directed coordinator
Character = social/personality surface
```

A multimodal worker is still only an execution host. The capability must still
be declared as a cell or organ, constrained by contracts, and governed by rooms,
resources, guards, decisions, and traces.

## Non-Goals

This document does not introduce:

- LLM orchestration
- vision model integration
- embedding storage
- vector search
- autonomous world modeling
- robot control
- sensor ingestion
- dashboard visualization
- hidden latent-state mutation

## Current Rule

The current runtime should stay boring and inspectable.

Future multimodal work may enrich meaning, but only if it strengthens the
governed runtime rather than replacing it with opaque model behavior.

## Conclusion

GENUS may eventually think less like a text chain and more like a governed
state-and-meaning environment.

Natural language remains important, but it should be one surface of GENUS, not
the entire internal substrate.
