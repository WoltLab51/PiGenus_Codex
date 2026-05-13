# GENUS Internal Communication Layer

This document defines internal communication as a core GENUS concept. It is a
concept and architecture boundary document, not a new runtime feature by
itself.

## Core Rule

GENUS components do not communicate primarily through loose prompts or blind
raw text.

They communicate through typed, validatable meaning objects, governed events,
decision traces, and persisted decisions.

Free text is allowed, but it must sit inside a structured, inspectable,
room-aware object.

## Purpose

Internal communication is the nervous system of GENUS.

It connects cells, organs, agents, characters, workers, rooms, guards, memory,
and governance without letting them call each other freely or pass unbounded
information around the runtime.

The goal is not rigid module wiring. The goal is governed semantic flow:

```text
context + room + actor + contract + meaning + guard + trace -> action
```

## Communication Shape

GENUS communication is hybrid.

### Machine-Readable

Every important communication should be inspectable by code:

- Stable schemas
- Stable IDs
- Explicit types
- Source references
- Room references
- Contracts
- Validation
- Guard checks
- Event logs
- Decision logs

### Semantically Rich

The payload may carry natural language, but the language is not the whole
message:

- Summaries
- Reasons
- Uncertainties
- Hypotheses
- Sources
- Provenance
- Relationships to other meaning objects
- Suggested follow-up actions

### Dynamic

Internal communication should support dynamic runtime formation without
becoming chaotic:

- Context matters
- Momentum matters
- Goal matters
- Room matters
- Current Systemform matters
- Guard outcome matters

This is compatible with the Liquid Runtime idea: future runtime shapes may be
proposed dynamically, but no proposed form becomes real without validation,
guard decision, trace, and approval where required.

## Meaning Objects As Communication Carriers

The current PiGenus `MeaningObject` already provides the core semantic carrier:

- `id`
- `type`
- `content`
- `source`
- `provenance`
- `room_id`
- `truth_status`
- `confidence`
- `sensitivity`
- `revision`
- `parent_ids`
- `valid_from`
- `valid_until`
- `created_by`
- `created_at`

This is enough for the current governed runtime.

Future communication-specific fields may be added only through a separate
schema and migration plan. Candidate concepts include:

- target scope
- intent
- causal links
- required capabilities
- guard trace references
- suggested actions
- response expectations
- delivery state

These are target concepts, not implicit fields in the current runtime.

## Events, Meanings, And Decisions

Internal communication uses distinct surfaces:

### Event

An event is the runtime trace of something that happened or was requested.
Events are typed, contextual, persisted, and inspectable.

### MeaningObject

A meaning object is the semantic object being communicated, stored, inspected,
guarded, or remembered.

### GovernanceDecision

A governance decision explains why a movement, action, or escalation was
allowed, warned, blocked, escalated, or otherwise classified.

### Audit Log

An audit log records operational facts that must remain append-only.

These surfaces should not collapse into one generic message table.

## Communication Rule

No cell should blindly forward raw information as if it were neutral.

Relevant communication must carry at least:

- Source
- Room
- Intent or action context
- Truth status
- Sensitivity
- Time reference
- Enough provenance to inspect where it came from

The current runtime already enforces parts of this through events, contexts,
meaning objects, room flow rules, guard decisions, and decision logs. Future
work should make intent, target scope, and causal links more explicit.

## Taxonomy Boundary

Communication must preserve the Systemform taxonomy:

```text
Cell -> Organ -> Agent -> Character
```

- Cell: smallest reusable capability
- Organ: composed group of cells
- Agent: goal-directed coordinator using capabilities
- Character: social and personal surface with relationship memory
- Worker: execution host, not intelligence itself
- Room: governed information and action boundary
- ContextFrame: condition around an action
- ContextStack: concrete operating envelope for a task

A message is not automatically an actor.
A context is not automatically an agent.
A worker is not automatically a character.

## Relation To Existing Runtime

The current runtime already contains the foundations:

- Event bus
- Structured events
- Meaning Store
- Meaning inspection
- Memory-to-meaning adapter
- Cell contracts
- Room flow rules
- Guard pipeline
- Guard decision logging
- Context boundaries
- Audit logs

This document does not replace those pieces. It names the architecture they are
forming together.

## Phase Placement

The current and future placement is:

- Phase 0/v0.3 baseline: IDs, types, TruthStatus, Sensitivity, Room context,
  MeaningObject, Event, DecisionRecord, Guard Trace
- Phase 1: richer Meaning Runtime and retrieval
- Phase 2: Cell Registry, cell contracts, organ contracts, and IO schemas
- Phase 3: worker-facing communication and guarded task delivery
- Later: semantic compression, graph-based meaning links, dynamic internal
  language, and Liquid Runtime proposal communication

This is not an additional feature track that competes with the kernel. It is
the communication principle that keeps later features from becoming prompt
spaghetti.

## Non-Goals

- No free-form prompt bus
- No direct cell-to-cell hidden calls
- No bypassing rooms, guards, or contracts
- No schema migration only to satisfy speculative fields
- No LLM-native internal language before deterministic meaning objects remain
  stable
- No dashboard-first communication model

## Current Conclusion

GENUS should communicate internally through structured meaning, not loose text.

The message is not just a data packet. It is a condition for action.

That means every future communication layer must preserve:

```text
meaning + provenance + room + truth + sensitivity + time + guardability
```

Only then can GENUS stay dynamic without becoming opaque.
