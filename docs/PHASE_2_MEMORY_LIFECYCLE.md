# Phase 2 Memory Lifecycle

This document defines the next implementation phase for PiGenus. It should be
updated before Phase 2 code changes if the lifecycle contract changes.

## Goal

Make memory age, require review, expire when appropriate, and protect canonical
knowledge without adding LLMs, dashboards, distributed workers, vector search,
or autonomous evolution.

Phase 2 answers:

```text
Where does this memory belong?
How fresh is it?
When should it be reviewed?
Can it expire?
What must never be automatically deleted or downgraded?
```

Phase 1.6 already answers the first question through context boundaries. Phase
2 handles the rest.

## Memory Statuses

PiGenus already defines these memory statuses:

- `fresh`: newly created, not yet proven useful
- `active`: valid and currently useful
- `watch`: valid but needs attention soon
- `stale`: likely outdated or unverified
- `dormant`: retained but not currently useful
- `dead`: no longer valid for active use
- `fossil`: preserved as historical evidence or warning
- `canonical`: protected durable knowledge

## Allowed Manual Transitions

Manual review may perform these transitions:

```text
fresh -> active
fresh -> stale
active -> watch
active -> stale
active -> dormant
watch -> active
watch -> stale
stale -> active
stale -> dormant
stale -> dead
dormant -> active
dormant -> fossil
dead -> fossil
fossil -> active
```

`canonical` is special:

```text
canonical -> canonical
```

No automatic process may downgrade, delete, expire, or fossilize canonical
memory. A future explicit human/admin override may exist, but it is out of
scope for this phase.

## Automatic Lifecycle Rules

The lifecycle engine should be deterministic and conservative.

### Review Due

If `review_due_at` is present and is now or in the past:

- `fresh` becomes `watch`
- `active` becomes `watch`
- `watch` remains `watch`
- `stale`, `dormant`, `dead`, `fossil`, and `canonical` remain unchanged

### Expiry

If `expires_at` is present and is now or in the past:

- `fresh` becomes `dead`
- `active` becomes `dead`
- `watch` becomes `dead`
- `stale` becomes `dead`
- `dormant` becomes `fossil`
- `dead` remains `dead`
- `fossil` remains `fossil`
- `canonical` remains `canonical`

Expiry should not delete rows. It only changes status.

### Last Validated

When a memory is manually moved to `active`, set `last_validated_at` to the
transition time unless the caller provides a more specific validation time.

### Last Used

Phase 2 may expose a repository method to update `last_used_at`, but the review
CLI does not need to use it.

## Lifecycle Engine

Add a small core component:

```text
MemoryLifecycleEngine
```

Responsibilities:

- Validate requested status transitions
- Apply automatic review and expiry rules
- Refuse automatic changes to `canonical`
- Return a structured decision explaining whether status changed

The engine should not write to SQLite directly. Repositories or services should
perform persistence.

## Repository Support

Add repository methods for:

- Listing memory objects
- Updating memory status and lifecycle timestamps
- Fetching memories due for review or expiry

Keep the repository simple and SQLite-backed.

## Audit Requirements

Every status change must create an audit log row with:

- actor
- action
- memory_id
- old_status
- new_status
- reason
- source

Suggested actions:

- `memory_lifecycle_review`
- `memory_lifecycle_expire`
- `memory_lifecycle_manual_transition`

## CLI

Add a small CLI command:

```powershell
python -m pigenus.cli.main memory-review --db pigenus.sqlite3
```

Expected behavior:

- Opens the SQLite database
- Applies deterministic lifecycle rules
- Prints how many memories were checked
- Prints how many statuses changed
- Does not require user interaction
- Does not delete memory

Optional arguments:

```text
--now ISO_TIMESTAMP
```

This makes tests deterministic.

## Tests

Add tests for:

- Allowed manual status transitions
- Rejected manual status transitions
- Review due changes `active` to `watch`
- Expiry changes `active` to `dead`
- Expiry changes `dormant` to `fossil`
- `canonical` is not changed by review or expiry
- Status changes create audit logs
- CLI `memory-review` runs and reports counts
- No lifecycle rule changes context

## Out Of Scope

- Automatic deletion
- Human/admin canonical override
- LLM-based memory review
- Vector memory
- Cross-context memory promotion
- Background scheduler
- Web dashboard

## Done Criteria

Phase 2 is complete when:

- Lifecycle rules are implemented and tested
- `memory-review` CLI works from a clean editable install
- `CHANGELOG.md`, `BUILD_PLAN.md`, `STATUS.md`, and architecture docs are updated
- Tests pass
- A checkpoint commit and tag are created
