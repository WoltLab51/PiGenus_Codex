# GENUS Architecture Summary

This is the compact map of the current PiGenus/GENUS architecture. It points to
the detailed documents instead of replacing them.

## What GENUS Is

GENUS is not a single AI agent.

It is a governed environment for digital capabilities, meaning, memory,
workers, agents, characters, and decisions.

Its first duty is to make intelligence-shaped work observable, bounded,
testable, and accountable.

## Current PiGenus Baseline

The current repository is a local governed runtime. It includes:

- structured events
- SQLite persistence
- memory lifecycle
- Meaning Store
- Systemform models and adapters
- rooms and context boundaries
- ContextFrame and ContextStack ontology
- cell contracts and validation
- room flow rules
- guard pipeline and guard families
- governance decision logging
- human approval stubs
- audit logs
- runtime inspection CLI
- health checks and backups
- Worker Runtime preparation through model-only and storage-free components

## Core Taxonomy

```text
Worker = execution host
Cell = bounded capability
Organ = composed capability group
Agent = goal-directed coordinator
Character = social/personality surface
Room = governed boundary
ContextFrame = one condition around an action
ContextStack = operating envelope for a task
MeaningObject = governed semantic carrier
GovernanceDecision = explanation of a policy outcome
```

## Runtime Story

A task enters the system.

PiGenus wraps it in context, room, meaning, and contracts. The guard pipeline
checks whether work may proceed. Decisions and traces explain why the runtime
allowed, warned, escalated, or blocked the action.

Cells do bounded work. Meaning moves as structured objects rather than loose
prompts. Workers are prepared as execution hosts, but they do not yet execute
tasks. Future agents may dynamically coordinate cells or organs, but only as
validated shapes behind contracts, rooms, resources, guards, and traces.

## Current Worker Arc

Implemented:

- `WorkerType`
- `WorkerStatus`
- `WorkerProfile`
- `WorkerHeartbeat`
- storage-free `WorkerRegistry`
- read-only `WorkerInspectionService`

Not implemented:

- worker persistence
- `worker-list` / `worker-show` CLI
- scheduling
- execution routing
- remote workers
- provider gateways
- federation

Next worker decision:

Worker source of truth is planned as SQLite for durable profiles and current
heartbeats. Local files may bootstrap/import worker data later, but should not
be runtime truth. Discovery waits for federation and trust work.

## Data Architecture Rule

SQLite remains the local source of truth for the governed runtime.

Other storage roles may appear later, but they must be named:

- source of truth
- append-only log
- index
- cache
- derived view
- blob payload
- external capability

Embeddings are indexes, not truth. Large blobs are payloads, not memory by
themselves. Caches are rebuildable or temporary.

## Dynamic Runtime Direction

GENUS may eventually support Liquid Runtime:

```text
state + goal + room + context + meaning + resources + constraints
-> proposed form
-> validation
-> guard decision
-> action or preview
-> trace
```

Dynamic form does not mean uncontrolled emergence. A proposed agent shape is
not permission. Simulation is not execution.

## Multimodal Direction

GENUS should not become text-only.

Long term, it may use:

- language
- meaning graphs
- state fields
- visual or spatial representations
- action traces
- embeddings

But every representation must preserve provenance, room, sensitivity, truth or
confidence, guardability, decisions, and inspection.

## Hard Non-Goals Right Now

- no LLM-first runtime
- no remote execution
- no worker discovery
- no vector search
- no autonomous agents
- no dashboard-driven architecture
- no self-modification
- no hidden prompt bus
- no schema changes without migration plan

## Detailed Documents

Read these for deeper context:

- `docs/GENUS_PHILOSOPHY.md`
- `docs/GENUS_VOCABULARY.md`
- `docs/ARCHITECTURE_CONTRACT.md`
- `docs/DATA_LIFECYCLE.md`
- `docs/DATA_ARCHITECTURE.md`
- `docs/INTERNAL_COMMUNICATION.md`
- `docs/WORKER_RUNTIME_READINESS.md`
- `docs/MULTIMODAL_SYSTEMFORM.md`
- `BUILD_PLAN.md`
- `STATUS.md`

## Current Conclusion

GENUS grows safely when it can answer:

```text
What is this?
Where did it come from?
Which room governs it?
Which capability acts?
Which worker can host it?
Which guard allowed it?
Which decision explains it?
Which storage role preserves it?
How can an operator inspect it?
```
