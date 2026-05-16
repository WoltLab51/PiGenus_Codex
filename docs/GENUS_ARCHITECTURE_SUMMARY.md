# GENUS Architecture Summary

This is the compact map of the current GENUS/PiGenus architecture. It points to
the detailed documents instead of replacing them.

## What GENUS Is

GENUS is not a single AI agent.

It is a governed environment for digital capabilities, meaning, memory,
workers, agents, characters, and decisions.

Its first duty is to make intelligence-shaped work observable, bounded,
testable, and accountable.

PiGenus is the local reference runtime for GENUS. It is the current Python
implementation and edge-friendly runtime distribution, not the entire GENUS
system and not a Raspberry-Pi-only product.

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
- minimal SQLite worker store
- read-only `worker-list` and `worker-show`
- storage-free Worker Scheduling Preview
- Scheduling Preview to GovernanceDecision conversion
- opt-in Scheduling Preview decision logging
- read-only `worker-scheduling-preview`
- explicit `worker-scheduling-preview --log`
- storage-free Worker Execution Preflight
- `worker-execution-preflight` with explicit `--log`
- minimal WorkerAssignment Store for governed assignment intent
- read-only `worker-assignment-list`
- WorkerAssignmentValidator for matching preflight allow evidence
- WorkerAssignmentCreator for service-only assignment creation with audit
- `worker-assignment-create` for pending assignment intent creation
- WorkerAssignment status transition semantics
- WorkerAssignmentStatusTransitionValidator for read-only status graph checks
- WorkerAssignmentStatusTransitionService for service-only status updates with
  audit
- `worker-assignment-transition` for service-backed assignment status updates

Documented:

- Worker Scheduling Enforcement boundary between assigned intent and any
  future scheduling, reservation, routing, provider call, or execution

Not implemented:

- durable scheduling
- execution routing
- remote workers
- provider gateways
- federation

Next worker decision:

Worker source of truth is SQLite for durable profiles, current heartbeats, and
minimal assignment intent. Local files may bootstrap/import worker data later,
but should not be runtime truth. Discovery waits for federation and trust work.

Scheduling preview can explain candidate workers, but it does not assign or
execute work. Its governance conversion is log-compatible and can be persisted
through explicit preview logging, but it is not persisted by default. The
`worker-scheduling-preview` CLI exposes the explanation without logging unless
`--log` is provided.

Worker Execution Preflight checks one specific worker before any assignment or
execution path exists. It produces ordered eligibility checks and a
governance-shaped result, but it does not execute. The
`worker-execution-preflight` CLI exposes that check and may log one decision
only with explicit `--log`.

WorkerAssignment now has a minimal SQLite store for governed assignment intent.
It requires a known worker and governance decision evidence, and
`worker-assignment-list` makes those records inspectable without creating
assignments, scheduling, routing, or executing. WorkerAssignmentValidator checks
matching preflight allow evidence before creation. Successful assignment
creation must write one `worker_assignment_created` audit row.
WorkerAssignmentCreator implements that service boundary without scheduling,
routing, or execution. `worker-assignment-create` exposes the service as a thin
CLI wrapper for pending intent creation only.

WorkerAssignment status transition semantics are documented before transition
behavior exists. They define intent-lifecycle changes only and keep `assigned`
separate from execution proof.
WorkerAssignmentStatusTransitionValidator makes that graph executable without
mutating stored assignment state.
WorkerAssignmentStatusTransitionService applies validated status changes and
writes audit, but it remains service-only and does not schedule or execute.
`worker-assignment-transition` exposes that service as a thin CLI wrapper for
assignment lifecycle status only.

Worker Scheduling Enforcement is now documented as the next boundary. It
states that `assigned` is necessary for future scheduling consideration but not
sufficient for execution. A future read-only enforcement check must revalidate
current worker state, heartbeat freshness, capability and runtime compatibility,
room/context constraints, guards, resources, and approval evidence before any
real scheduling can exist.

Worker storage repositories now live in
`pigenus/storage/worker_repositories.py`, with the existing
`pigenus.storage.repositories` import surface preserved for compatibility.

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
