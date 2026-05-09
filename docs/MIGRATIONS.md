# PiGenus Migration Policy

PiGenus currently uses local SQLite and creates tables with `CREATE TABLE IF
NOT EXISTS`. This is enough for the early runtime, but schema changes must stay
intentional.

## Rules

- No silent destructive schema changes.
- No automatic row deletion during migrations.
- Migrations should be forward-only.
- Schema changes must be documented in `CHANGELOG.md`.
- Schema changes should include tests or a smoke test.
- Existing local databases should remain readable whenever practical.

## Current State

There is no migration runner yet.

For now:

- New tables may be added through `Database.initialize()`.
- New nullable columns may be added only with an explicit migration step.
- Renaming or dropping columns is out of scope.

## When To Add A Migration Runner

Add a small migration runner before any change that requires:

- `ALTER TABLE`
- backfilling existing rows
- changing stored JSON shape in a non-compatible way
- multiple schema versions in the wild

The first runner should be simple:

```text
schema_migrations(version TEXT PRIMARY KEY, applied_at TEXT NOT NULL)
```

Each migration should be idempotent or guarded by the recorded version.
