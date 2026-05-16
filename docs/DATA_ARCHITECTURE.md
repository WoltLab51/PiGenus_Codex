# Data Architecture

This document defines PiGenus storage roles and performance boundaries. It does
not replace `docs/DATA_LIFECYCLE.md` or `docs/MIGRATIONS.md`.

Relationship to existing documents:

- `docs/DATA_LIFECYCLE.md` explains how data objects live, move, age, and become inspectable.
- `docs/MIGRATIONS.md` explains how SQLite schema changes are applied.
- This document explains which storage role should hold which kind of data and
  how performance should be protected as GENUS grows.

## Core Rule

SQLite remains the local source of truth for the governed runtime.

Other stores may appear later, but they must be classified as:

```text
source of truth
append-only record
index
cache
derived view
blob payload
external capability
```

GENUS should always know which category a storage surface belongs to.

## Storage Roles

### SQLite Core Store

Purpose:

Durable local truth for the governed runtime.

Current examples:

- events
- memory objects
- meaning objects
- cells
- audit logs
- decision logs
- schema migrations

Future candidates:

- worker profiles
- worker heartbeats or heartbeat summaries
- worker inspection records, if needed
- resource usage records
- agent shape proposals
- graph edges, if kept simple enough

Rule:

SQLite is the first persistence choice when data must be local, inspectable,
transactional, and part of the governed runtime.

### Append-Only Logs

Purpose:

Preserve what happened and why.

Current examples:

- EventLog through `events`
- AuditLog through audit storage
- GovernanceDecision records through decision logs

Rule:

Append-only records should not be silently rewritten. Corrections should be new
records or explicit lifecycle transitions.

### Meaning Store

Purpose:

Persist structured meaning while keeping common filters fast.

Current shape:

- full `MeaningObject` JSON payload
- indexed room, type, truth status, and sensitivity columns

Rule:

The full semantic object remains available even when additional indexed columns
are added for performance.

### Graph Layer

Purpose:

Represent relationships between meaning, actors, cells, rooms, workers,
decisions, and future agent shapes.

First safe shape:

```text
edges(source_id, edge_type, target_id, room_id, created_at, evidence_ref)
```

Rule:

Start with explicit edge records before adding a graph database. A graph
database may become useful later, but it should not become the source of truth
for governed decisions.

### Vector Or Embedding Store

Purpose:

Similarity search and semantic retrieval.

Rule:

Embeddings are indexes, not truth. A vector match may suggest relevant meaning,
but it does not prove truth, permission, provenance, or room compatibility.

Vector storage should wait until deterministic Meaning Store retrieval remains
boring and inspectable.

### Blob Or Object Store

Purpose:

Store large payloads outside core tables.

Future examples:

- images
- audio
- PDFs
- long logs
- model outputs
- sensor captures

First safe shape:

```text
blob_id
sha256
media_type
path
size_bytes
sensitivity
created_at
```

Rule:

Large payloads should be referenced by hash and metadata. The meaning object
should carry the governed interpretation or reference, not blindly become a
large binary container.

### Hot State And Cache

Purpose:

Speed up repeated runtime reads.

Examples:

- worker registry in memory
- context and permission registries
- loaded contracts
- recent heartbeats
- candidate form proposals

Rule:

Cache may improve read speed, but it must be rebuildable from truth sources or
clearly marked as temporary runtime state.

## Performance Boundaries

### Hot Path

The hot path is work needed frequently during task evaluation:

- actor identity
- room and context stack
- cell contracts
- worker profile and heartbeat
- resource grants
- guard policy inputs
- meaning metadata

Hot-path data should be:

- small
- indexed when persisted
- cacheable when safe
- deterministic to load
- separate from large payloads

### Cold Path

Cold-path data is slower or larger:

- full audit history
- older events
- fossils
- large blobs
- historical graph traversals
- backup snapshots

Cold-path data should remain inspectable, but it should not slow routine task
checks.

### Write Path

The write path must be strict:

- validate before persistence
- preserve source, room, sensitivity, truth or confidence, creator, and time
- record decisions and traces for meaningful actions
- avoid hidden side effects in read-only commands
- use migrations for schema changes

### Read Path

The read path may be optimized:

- indexed columns
- derived summaries
- cache
- rebuilt indexes
- read-only inspection views

But optimized reads must not become a second truth source.

## Worker Runtime Storage Direction

Worker work now has both storage-free runtime helpers and a minimal SQLite
truth surface:

- `WorkerProfile`
- `WorkerHeartbeat`
- `WorkerRegistry`
- `WorkerInspectionService`
- `worker_profiles`
- `worker_heartbeats`

`worker-list` and `worker-show` are read-only CLI commands over the SQLite
worker store. `worker-scheduling-preview` is also read-only: it reads stored
worker profiles and current heartbeats, builds temporary in-memory preview
state, and does not persist decisions unless `--log` is provided. With
`--log`, it writes one governance decision record through the existing decision
log and does not create scheduling tables or execution records.

Worker source-of-truth decision:

```text
Durable worker identity -> SQLite
Current worker heartbeat -> SQLite-backed current state
Heartbeat history -> optional append-only/audit-style later surface
Local file -> bootstrap/import only
Discovery -> later federation/trust feature, not local runtime truth
```

Recommended direction:

```text
SQLite worker store -> read-only worker-list/show -> scheduling preview CLI -> guarded scheduling
```

Not yet:

- network discovery
- remote execution
- provider routing
- LLM worker orchestration
- federation

The first worker store was intentionally small:

- `worker_profiles` for full `WorkerProfile` JSON plus indexed identity,
  worker type, status, owner, and home room columns
- `worker_heartbeats` for latest `WorkerHeartbeat` JSON plus indexed worker ID,
  status, and seen-at columns

It did not create scheduling tables, assignment tables, execution records, or
remote discovery state.

Scheduling preview is storage-free unless an explicit preview logger is called.
It may rank or explain candidate workers, and it may produce a log-compatible
`GovernanceDecision`. `WorkerSchedulingPreviewLogger` may store that decision
through the existing decision log as append-only governance evidence, but it
must not create durable assignments, execution records, reservations, routes,
or provider calls.

WorkerAssignment now has a minimal local truth table:

- `worker_assignments` for full `WorkerAssignment` JSON plus indexed worker,
  status, room, capability, and governance-decision columns

This store remains assignment intent only. It requires a known worker and an
existing governance decision record before persistence. It still avoids
execution records, provider routes, reservations, and tool-call state.
`worker-assignment-list` exposes those records as a read-only inspection
surface without creating assignments, decisions, audit logs, routing, or
execution.
WorkerAssignmentValidator checks semantic evidence before future assignment
creation, but it does not persist records itself.
WorkerAssignmentCreator writes one assignment truth record and one audit row.
The audit row explains that durable assignment intent was created; it is not a
second truth record and not a governance decision.
`worker-assignment-create` exposes this as a CLI write path, but it remains
assignment intent only and does not activate, schedule, route, or execute.

Worker storage adapters now live in a dedicated module:

- `pigenus/storage/worker_repositories.py`

The legacy `pigenus.storage.repositories` import surface remains compatible.
This is a structural domain split only; it does not change SQL, migrations,
assignment behavior, routing, or execution.

## Database Design Principles

1. Keep truth small and inspectable.
2. Keep large payloads out of hot tables.
3. Keep indexed metadata next to full JSON payloads when that preserves flexibility.
4. Keep append-only records append-only.
5. Keep derived indexes rebuildable.
6. Keep vector search outside the truth boundary.
7. Keep worker execution behind governance.
8. Keep read-only commands read-only.
9. Keep migrations forward-only.
10. Keep performance decisions visible in documentation.

## Current Conclusion

The next storage decision should not be "which database is exciting?"

It should be:

```text
Which data is truth?
Which data is index?
Which data is cache?
Which data is payload?
Which data is audit evidence?
```

GENUS can become dynamic only if its storage roles stay boring.
