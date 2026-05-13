# Runtime Verification

This document records the post-release runtime verification track after
`pigenus-v0.3.1-architecture-control`.

It verifies existing runtime surfaces before new features are added.

## Scope

Current target checkpoint:

```text
pigenus-v0.3.2-post-release-runtime-verification
```

Verification covers:

- health check
- runtime overview
- migrations
- read-only inspection commands
- backup creation
- meaning queries
- guard decision summaries
- context, permission, schema, event, audit, decision, cell, and memory
  inspection
- full test suite

## Current Verification Pass

Commands run against the current local runtime:

```text
.venv\Scripts\python.exe -m pigenus.cli.main health-check --db pigenus.sqlite3
.venv\Scripts\python.exe -m pigenus.cli.main runtime-overview --db pigenus.sqlite3
.venv\Scripts\python.exe -m pigenus.cli.main event-list --db pigenus.sqlite3 --limit 5
.venv\Scripts\python.exe -m pigenus.cli.main meaning-list --db pigenus.sqlite3
.venv\Scripts\python.exe -m pigenus.cli.main audit-list --db pigenus.sqlite3
.venv\Scripts\python.exe -m pigenus.cli.main decision-list --db pigenus.sqlite3
.venv\Scripts\python.exe -m pigenus.cli.main guard-decision-summary --db pigenus.sqlite3
.venv\Scripts\python.exe -m pigenus.cli.main memory-list --db pigenus.sqlite3
.venv\Scripts\python.exe -m pigenus.cli.main cell-list --db pigenus.sqlite3
.venv\Scripts\python.exe -m pigenus.cli.main context-list --db pigenus.sqlite3 --show-cells
.venv\Scripts\python.exe -m pigenus.cli.main context-boundary-list --db pigenus.sqlite3
.venv\Scripts\python.exe -m pigenus.cli.main permission-list
.venv\Scripts\python.exe -m pigenus.cli.main schema-list
.venv\Scripts\python.exe -m pigenus.cli.main backup-create --db pigenus.sqlite3 --output-dir .testdata\runtime-verification --name v032-verification.sqlite3
```

Observed results:

- `health-check`: healthy
- `runtime-overview`: reports zero current local rows and known static
  boundaries
- inspection commands: return clean empty-state messages where expected
- `permission-list`: reports default developer memory-write permission
- `schema-list`: reports known event contracts
- `backup-create`: created a SQLite snapshot with integrity `ok`

## Finding: Concurrent Migration Apply Race

During the first verification pass, multiple CLI commands were run in
parallel against the same local database while a pending migration was being
applied.

Observed failure:

```text
sqlite3.IntegrityError: UNIQUE constraint failed: schema_migrations.version
```

Cause:

Two runtime commands could see a pending migration at nearly the same time and
then both attempt to record the same migration version.

Fix:

`MigrationRunner.apply()` now acquires an immediate SQLite write transaction
around reading applied versions, applying pending statements, recording
migration versions, and committing the result.

Boundary:

This is a runtime hardening fix, not a schema change.

## Test Results

Read-only hash verification:

```text
Before: CAC9FB4E09D4246F5365B4AD3DC68C6B01B9B0A0FFA7C41B6AE1349D2CA0D9DD
After:  CAC9FB4E09D4246F5365B4AD3DC68C6B01B9B0A0FFA7C41B6AE1349D2CA0D9DD
Read-only verification: unchanged
```

Commands included memory, meaning, event, audit, decision, guard summary, cell,
context, context-boundary, permission, schema, runtime-overview, and
health-check surfaces on a copied local database.

Targeted tests:

```text
.venv\Scripts\python.exe -m pytest tests\test_migrations.py
3 passed

.venv\Scripts\python.exe -m pytest tests\test_event_inspection_cli.py tests\test_runtime_overview_cli.py tests\test_health_check_cli.py
14 passed
```

Full suite:

```text
.venv\Scripts\python.exe -m pytest
187 passed
```

## Current Conclusion

The runtime verification pass found one real hardening issue in migration
application. The issue was fixed without adding a migration or changing the
runtime schema.

Read-only inspection surfaces were verified against a copied local database by
comparing the database hash before and after the command pass.
