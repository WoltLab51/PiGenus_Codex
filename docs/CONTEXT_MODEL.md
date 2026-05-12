# Context Model

PiGenus keeps `Room` as the existing governance, protection, and memory
boundary. The context model adds a smaller concept beside it:

- `Room`: where information and work are governed
- `ContextFrame`: one formal condition around an action
- `ContextStack`: the concrete operating envelope assembled from frames

This is additive. It does not delete, rename, or replace `Room`, the legacy
`Context -> Room` adapter, existing CLI commands, migrations, event flow, guard
decisions, audit logs, or Meaning Runtime behavior.

## Core Rule

Context frames are conditions around an action. They are not actors, agents,
characters, cells, or organs.

The thing that acts remains an actor, cell, organ, agent, or later character.
The context stack only describes the operating conditions of a task.

## Room

`Room` remains the existing Systemform boundary for governance, protection, and
memory placement. A room can represent a protected working area such as
`room_private`, `room_trading`, or `room_developer`.

Rooms are still used by existing guard, context boundary, room-flow, meaning,
and decision-log behavior.

## ContextFrame

`ContextFrame` describes one condition around an action. A frame can reference
a room or policy, but it does not replace either one.

Initial frame types:

- `domain`
- `governance`
- `data`
- `execution`
- `learning`
- `capability`
- `resource`
- `time`
- `audit`

Frames may define capability/source allow and deny lists, truth requirements,
sensitivity level, risk level, execution mode, learning mode, and audit level.
Internal allow/deny conflicts are rejected deterministically.

## ContextStack

`ContextStack` combines frame IDs into one operating envelope for a task.
Duplicate frame IDs are de-duplicated while preserving first-seen order.

Example:

```text
Room:
  room_trading

ContextFrames:
  domain: crypto
  execution: trade_republic_readonly
  learning: shadow_mode
  governance: live_money_protected
  audit: full_trace

ContextStack:
  robert_crypto_trade_republic_shadow
```

The stack is the task envelope's context. It is not the actor, agent,
character, cell, or organ.

## Not In This Checkpoint

This checkpoint does not add persistence, CLI commands, worker scheduling, LLM
orchestration, vector search, trading-specific logic, character registry, agent
registry, dashboard behavior, federation, or evolution.

Those can be built later once the ontology remains stable and existing runtime
boundaries continue to pass unchanged.
