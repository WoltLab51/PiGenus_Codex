# GENUS Vocabulary

This glossary keeps GENUS terms stable across code, documentation, and future
planning. Some terms are implemented today. Others are documented, planned, or
conceptual.

Status meanings:

- `implemented`: present in current runtime code
- `documented`: defined in architecture documents, not fully implemented
- `planned`: intended future implementation track
- `conceptual`: useful idea, not yet an implementation commitment

## Core Terms

| Term | Status | Short Definition | Relationship | Current Repo Correspondence | Boundary |
| --- | --- | --- | --- | --- | --- |
| MeaningObject | implemented | Structured semantic object carrying meaning, room, truth status, sensitivity, provenance, confidence, and time metadata. | Communicated through Internal Communication Layer, stored by Meaning Store, checked by guards and room flow rules. | `pigenus.schemas.systemform.MeaningObject`; `MeaningRepository`; `meaning-list`; `meaning-show`. | Not just raw text and not automatically durable memory. |
| Event | implemented | Typed runtime trace of something requested, produced, or observed. | Events carry context and payload, and are persisted by the local event bus. | `pigenus.schemas.events.Event`; `pigenus.core.event_bus.EventBus`; `EventRepository`. | Not a generic message table and not a governance decision. |
| Actor | implemented | Entity that can be responsible for action, communication, or governance state. | May be a human, cell, organ, agent, character, system, or future worker-linked executor. | `pigenus.schemas.systemform.ActorIdentity`. | Not every message, context, or worker process is automatically an actor. |
| ActorType | implemented | Controlled category for actor identity. | Distinguishes humans, cells, organs, agents, characters, and systems. | `pigenus.schemas.systemform.ActorType`. | Does not define permissions by itself. |
| MeaningFlow | documented | Logical communication flow that moves meaning through traceable runtime surfaces. | `MeaningObject -> Event -> GuardPipeline -> DecisionTrace -> GovernanceDecision -> optional MeaningStore / EventLog / AuditLog`. | Defined here and in Internal Communication documentation; no single runtime class. | Not a queue, broker, or schema migration. |
| Provenance | implemented | Evidence trail for where meaning came from and how it was derived. | Supports trust, auditability, source review, and future graph links. | `MeaningObject.provenance`; `MeaningObject.source`; memory source context. | Not proof that content is true. |
| DecisionTrace | documented | Ordered explanation of why a guard or governance result happened. | Attached to guard results and serialized into governance decision details. | Guard pipeline trace steps in `pigenus.core.guard_pipeline`; decision log details. | Not a free-form explanation without stable order. |
| GovernanceDecision | implemented | Structured decision produced by governance or guard evaluation. | Records allow, warn, block, escalate, quarantine, revoke, or archive decisions. | `pigenus.schemas.systemform.GovernanceDecision`; durable `DecisionRecord` surfaces. | Not the same as an event or audit log. |
| EventLog | implemented | Persisted chronological record of typed runtime events. | Shows what happened or was requested in the runtime flow. | `events` table via `EventRepository`; `event-list`; `event-show`. | Does not explain policy reasoning and is not an audit log. |
| AuditLog | implemented | Append-only operational record of safety-relevant actions and lifecycle changes. | Complements events and decisions with operational accountability. | Audit repository and `audit-list`. | Not the main runtime event stream and not a governance decision. |
| Cell | implemented | Smallest reusable capability unit in the current runtime. | Declared through cell specs and adapted toward CellContract. | `pigenus.schemas.cells.CellSpec`; `CellRepository`; `cell-list`. | Not an agent, character, worker, or whole organ. |
| CellType | planned | Reusable category of cell capability. | Future registry concept for grouping compatible cell instances. | Mentioned in build plan and worker/runtime vocabulary, not implemented as a model. | Not a running cell instance. |
| CellInstance | planned | One concrete registered or running instance of a cell capability. | Future bridge between worker execution and cell capability declarations. | Current `CellSpec` covers some instance-like runtime registration behavior. | Not the reusable cell type itself. |
| Organ | documented | Composition of cells that provides a larger capability. | Sits above cells and below agents. | Defined in `docs/WORKER_RUNTIME.md` and internal communication taxonomy. | Not a worker and not automatically goal-directed. |
| OrganType | planned | Reusable kind of organ composition. | Future registry concept for organ contracts and standard compositions. | Not implemented. | Not one concrete organ instance. |
| OrganInstance | planned | Concrete active or configured organ composition. | May use cells across one or more workers in later runtime arcs. | Not implemented. | Not an agent unless it carries goal-directed coordination. |
| Agent | documented | Goal-directed coordinator that uses cells or organs to pursue a task. | Sits above organs and below characters in social/personality terms. | ActorType includes `AGENT`; future model not implemented. | Not a worker, cell, organ, or character. |
| Character | documented | Social/personality surface with identity, relationship memory, and durable interaction style. | May use agents but is not the same as an agent. | ActorType includes `CHARACTER`; concept appears in philosophy and future docs. | Not a context, room, or worker. |
| Room | implemented | Governed information and action boundary. | Used by meaning objects, room flow rules, guards, and context boundary metadata. | `pigenus.schemas.systemform.Room`; context-to-room adapter. | Not replaced by ContextFrame or ContextStack. |
| ContextFrame | implemented | One formal condition around an action. | Frames may reference rooms, policies, capabilities, sources, truth, sensitivity, risk, or audit level. | `pigenus.schemas.systemform.ContextFrame`. | Not an actor, agent, character, cell, or organ. |
| ContextStack | implemented | Concrete operating envelope assembled from ContextFrames. | Intended future per-task envelope. | `pigenus.schemas.systemform.ContextStack`. | Ontology-only until a separate migration and inspection plan exists. |
| Contract | implemented | Governed promise about what an actor or cell may do and under which constraints. | CellContract currently formalizes cell permissions, capabilities, room scope, obligations, resources, and approval needs. | `pigenus.schemas.systemform.CellContract`; contract validator. | Not a suggestion and not runtime permission by itself without validation. |
| Capability | implemented | Declared ability that a cell or future worker/organ can provide. | Used by CellContract and future worker/cell routing. | `CellContract.capabilities`; `CellSpec` input/output event types and permissions. | Not proof of authorization. |
| Guard | implemented | Rule or evaluation that checks whether an action or meaning movement should proceed. | Produces guard results and trace steps. | Contract validator, room flow rules, guard pipeline. | Not an LLM judge and not hidden policy. |
| GuardPipeline | implemented | Ordered guard evaluation pipeline. | Combines contract validation and room flow rules into final decisions and traces. | `pigenus.core.guard_pipeline.GuardPipeline`. | Does not invent capabilities or bypass storage-free constraints. |
| RoomFlowRule | implemented | Deterministic rule for semantic movement between rooms. | Used by the GuardPipeline to allow, review, escalate, or block room-to-room meaning flow. | `pigenus.core.room_flow.RoomFlowRules`. | Not general routing and not a replacement for rooms. |
| TruthStatus | implemented | Semantic status describing how a meaning object should be treated as knowledge. | Used by MeaningObject, ContextFrame, room flow rules, and meaning queries. | `pigenus.schemas.systemform.TruthStatus`. | Not absolute truth or model confidence. |
| Sensitivity | implemented | Information sensitivity class. | Used by MeaningObject, ContextFrame, room flow rules, and meaning queries. | `pigenus.schemas.systemform.Sensitivity`. | Not a room by itself and not an access grant. |
| Intent | documented | Purpose or action direction behind communication. | Needed for future richer internal communication and task envelopes. | Documented in `docs/INTERNAL_COMMUNICATION.md`; current events carry action-like payload keys. | Not a current required MeaningObject field. |
| Source | implemented | Origin of a meaning, event, memory, or decision. | Needed for provenance, auditability, and guardability. | `MeaningObject.source`; event `created_by_cell`; memory source context. | Not always a trusted source. |
| TargetScope | documented | Intended recipient, room, actor group, or delivery scope for communication. | Candidate future communication field. | Documented in `docs/INTERNAL_COMMUNICATION.md`; not implemented. | Not the same as Room, though it may reference rooms. |
| MemoryObject | implemented | Durable local memory record in the current runtime. | Can be adapted into MeaningObject and governed by lifecycle rules. | `pigenus.schemas.memory.MemoryObject`; `MemoryRepository`. | Not the full semantic communication object. |
| Fossil | implemented | Lifecycle status for expired dormant memory or preserved historical records. | Current memory lifecycle concept and future evolution rollback concept. | `MemoryStatus.FOSSIL`; evolution sandbox docs. | Not deletion and not active truth. |
| HumanApproval | implemented | Governance-controlled human review record for pending, approved, or rejected actions. | Supports future approval workflows without turning approval into a UI-only button. | Human approval stub records through decision logging; `docs/HUMAN_GOVERNANCE.md`. | Not agent self-approval and not enforcement by itself unless wired by policy. |
| ApprovalState | implemented | State of a human approval record. | Tracks pending, approved, and rejected approval outcomes. | Human approval stub model/tests and decision records. | Not the same as GuardDecisionType. |
| ResourcePolicy | documented | Rules for granting, limiting, accounting, and reviewing resource use. | Connects ResourceGrant, Resource Economy, Worker Runtime, rooms, and approvals. | `docs/RESOURCE_ECONOMY.md`; `ResourceGrant` model. | Not an internal market or dynamic pricing system. |
| MutationProposal | documented | Proposed runtime or architecture change that is not active behavior. | Core concept in Evolution Sandbox. | `docs/EVOLUTION_SANDBOX.md`. | Mutation is never activation. |
| EvolutionSandbox | documented | Future governed environment for proposing, testing, comparing, approving, and rolling back mutations. | Depends on guards, approval, traces, fossils, rollback, and tests. | `docs/EVOLUTION_SANDBOX.md`; build plan track. | Not current self-modification. |
| Worker | documented | Execution host with hardware/runtime/cost/privacy/status characteristics. | Workers carry execution, cells carry capability, agents carry goals. | `docs/WORKER_RUNTIME.md`; build plan worker track. | Not intelligence itself. |
| WorkerProfile | implemented | Structured record describing worker identity, runtime inventory, cost, privacy, and status surfaces. | Prepared by Worker Runtime readiness before WorkerRegistry implementation. | `pigenus.schemas.systemform.WorkerProfile`; `docs/WORKER_RUNTIME_READINESS.md`. | Not a scheduler and not proof of authorization. |
| WorkerHeartbeat | implemented | Liveness and freshness signal for a worker. | Helps decide whether a known worker can be considered for governed execution later. | `pigenus.schemas.systemform.WorkerHeartbeat`; `docs/WORKER_RUNTIME_READINESS.md`. | Not health proof by itself and not permission to execute. |
| WorkerRegistry | implemented | Storage-free registry for known worker profiles and latest heartbeats. | Prepares later worker inspection without adding persistence, scheduling, or execution. | `pigenus.core.worker_registry.WorkerRegistry`. | Not a repository, scheduler, router, or execution engine. |
| WorkerInspection | implemented | Read-only operator-facing view of worker profile, heartbeat, inventory, and considerable status. | Built from WorkerRegistry before any CLI or persistence exists. | `pigenus.core.worker_inspection.WorkerInspectionService`. | Not storage, scheduling, routing, health repair, or execution. |
| WorkerSourceOfTruth | documented | Policy that durable worker identity and current heartbeat state should be backed by SQLite. | Guides future worker store, worker-list, and worker-show work. | `docs/WORKER_RUNTIME_READINESS.md`; `docs/DATA_ARCHITECTURE.md`; `D-069`. | Not discovery, remote execution, or local config as runtime truth. |
| CapabilityProfile | documented | Future inventory of what a worker can technically run. | Must be compared with cells, organs, contracts, rooms, context stacks, and guards. | `docs/WORKER_RUNTIME_READINESS.md`. | Not an authorization grant. |
| CostProfile | documented | Future description of expected worker resource cost, latency, energy, or monetary constraints. | Connects Worker Runtime to Resource Economy and ResourcePolicy. | `docs/WORKER_RUNTIME_READINESS.md`; `docs/RESOURCE_ECONOMY.md`. | Not dynamic pricing or an internal market. |
| PrivacyProfile | documented | Future description of worker data exposure and sensitivity limits. | Constrains which rooms, meanings, and sensitivities may reach a worker. | `docs/WORKER_RUNTIME_READINESS.md`. | Not a room and not a substitute for guards. |
| FailureSemantics | documented | Future description of timeout, retry, partial-result, heartbeat-loss, audit, and cleanup behavior. | Keeps worker failures inspectable before scheduling or execution exists. | `docs/WORKER_RUNTIME_READINESS.md`. | Not recovery implementation by itself. |
| LLMGateway | planned | Provider-neutral gateway for model calls. | Future layer behind governance, meaning, rooms, and resource controls. | Mentioned in harvest and candidate future docs. | Not a kernel primitive and not current orchestration. |
| Multimodal Systemform | documented | Future principle that language, graph, state-field, visual, spatial, and action representations should enter GENUS as governed meaning. | Connects Internal Communication, Liquid Runtime, Worker Runtime, MeaningObject, guards, and future LLM or vision capabilities. | `docs/MULTIMODAL_SYSTEMFORM.md`. | Not current LLM, vision, embedding, vector, sensor, or robotics implementation. |
| StateField | conceptual | Future dense or dynamic representation of runtime or world state. | May support Liquid Runtime or multimodal world modeling later. | `docs/MULTIMODAL_SYSTEMFORM.md`. | Not a hidden mutable truth store. |
| MeaningGraph | conceptual | Future graph representation linking meaning objects, provenance, relations, and causal or semantic edges. | Could extend Meaning Runtime after deterministic storage and retrieval remain stable. | `docs/MULTIMODAL_SYSTEMFORM.md`; related to `MeaningObject.parent_ids`. | Not vector search and not proof of truth. |
| DataArchitecture | documented | Storage-role and performance boundary map for GENUS data. | Complements DataLifecycle and MigrationPolicy by defining truth, index, cache, payload, and append-only roles. | `docs/DATA_ARCHITECTURE.md`. | Not a schema migration by itself. |
| StorageRole | documented | Classification for a storage surface such as truth, append-only log, index, cache, derived view, payload, or external capability. | Required before new persistence, graph, vector, blob, or cache layers are added. | `docs/DATA_ARCHITECTURE.md`. | Not a database technology choice. |
| SourceOfTruth | documented | Authoritative local runtime record for governed state. | Currently centered on SQLite for PiGenus. | `docs/DATA_ARCHITECTURE.md`; SQLite repositories. | Not the same as index, cache, embedding, or blob payload. |
| Index | documented | Query acceleration or retrieval surface derived from truth records. | May include indexed columns, future graph edges, or vector search. | `docs/DATA_ARCHITECTURE.md`; current SQLite indexes. | Not proof of truth or permission. |
| Cache | documented | Temporary or rebuildable hot state used for performance. | Includes in-memory registries and loaded runtime metadata. | `docs/DATA_ARCHITECTURE.md`; `WorkerRegistry` is currently storage-free hot state. | Not durable truth unless explicitly persisted elsewhere. |
| BlobPayload | documented | Large external payload referenced by metadata and hash. | Future home for images, logs, PDFs, audio, sensor captures, or large model outputs. | `docs/DATA_ARCHITECTURE.md`. | Not a MeaningObject by itself. |
| Systemform Kernel | documented | Additive ontology and governance layer around the original runtime prototype. | Includes actors, rooms, meaning, contracts, resources, decisions, adapters, guards, and context concepts. | Systemform models, adapters, docs, gap analysis, decisions. | Not a replacement of the existing prototype. |
| Internal Communication Layer | documented | Principle that GENUS communicates through governed meaning flow, not loose prompts. | Connects events, meaning objects, decisions, traces, rooms, contracts, cells, organs, agents, characters, and workers. | `docs/INTERNAL_COMMUNICATION.md`. | Not an implemented message broker yet. |

## Current Vocabulary Boundary

The glossary is authoritative for meaning, not for implementation status.

A `documented`, `planned`, or `conceptual` term may be valid GENUS vocabulary
even when no Python class exists yet. A future implementation must still earn
its place through contracts, guards, traces, tests, and migration discipline.

## Implementation Rule

When adding code for a glossary term:

1. Keep the existing meaning of the term.
2. Update this glossary if the implementation changes the boundary.
3. Add or update a durable decision when the architecture changes.
4. Add tests for implemented behavior.
5. Avoid renaming existing runtime concepts only to match future vocabulary.

## Current Conclusion

Vocabulary comes before architecture expansion.

GENUS should be able to say what something is before it lets that thing act.
