# PiGenus Migration Policy

PiGenus currently uses local SQLite and creates tables with `CREATE TABLE IF
NOT EXISTS`. This is enough for the early runtime, but schema changes must stay
intentional.

## Rules

- No silent destructive schema changes.
- No automatic row deletion during migrations.
- Migrations should be forward-only.
- Applying pending migrations should happen under an exclusive apply step.
- Schema changes must be documented in `CHANGELOG.md`.
- Schema changes should include tests or a smoke test.
- Existing local databases should remain readable whenever practical.

## Current State

PiGenus has a minimal migration runner in `pigenus.storage.migrations`.

Current migration table:

```text
schema_migrations(version TEXT PRIMARY KEY, applied_at TEXT NOT NULL)
```

Current recorded migrations:

```text
0001_initial_schema
0002_decision_logs
0003_cell_lifecycle
0004_meaning_objects
0005_worker_store
```

`Database.initialize()` applies pending migrations. Running it more than once
must be safe. Pending migration application is protected by an immediate SQLite
transaction so concurrent runtime commands do not both record the same
migration version.

For now:

- New tables should be added as explicit migrations.
- New nullable columns should be added as explicit migrations.
- Renaming or dropping columns is out of scope.

## When To Add A New Migration

Add a new migration before any change that requires:

- `ALTER TABLE`
- backfilling existing rows
- changing stored JSON shape in a non-compatible way
- multiple schema versions in the wild

Each migration should be idempotent or guarded by the recorded version.
