# PiGenus CLI Conventions

PiGenus CLI commands should stay boring, scriptable, and testable.

## Exit Codes

- `0`: command completed successfully
- `1`: runtime or data error
- `2`: usage error from argument parsing

## Output

- Output is human-readable plain text.
- Summary lines should stay stable enough for tests.
- Commands should not print stack traces for expected user errors.
- Read-only commands should clearly avoid writes.

## Command Behavior

- Commands that mutate storage should say so in the name or help text.
- Commands that inspect storage should be read-only.
- Commands that accept time should support deterministic `--now` values.
- Commands should use `--db` for the SQLite path.

## Current Commands

```powershell
python -m pigenus.cli.main run-demo --db pigenus.sqlite3
python -m pigenus.cli.main runtime-overview --db pigenus.sqlite3
python -m pigenus.cli.main health-check --db pigenus.sqlite3
python -m pigenus.cli.main backup-create --db pigenus.sqlite3 --output-dir backups
python -m pigenus.cli.main memory-review --db pigenus.sqlite3 --now 2026-05-08T00:00:00+00:00
python -m pigenus.cli.main event-list --db pigenus.sqlite3
python -m pigenus.cli.main event-show evt_example --db pigenus.sqlite3
python -m pigenus.cli.main memory-list --db pigenus.sqlite3
python -m pigenus.cli.main meaning-list --db pigenus.sqlite3 --room room_developer
python -m pigenus.cli.main meaning-show bo_example --db pigenus.sqlite3
python -m pigenus.cli.main decision-list --db pigenus.sqlite3
python -m pigenus.cli.main audit-list --db pigenus.sqlite3
python -m pigenus.cli.main cell-list --db pigenus.sqlite3
python -m pigenus.cli.main context-list
python -m pigenus.cli.main permission-list
```

`memory-review` may update memory lifecycle status and write audit logs.
`backup-create` creates a new SQLite snapshot file but does not initialize,
migrate, repair, or overwrite runtime storage.

`runtime-overview`, `health-check`, `event-list`, `event-show`, `memory-list`,
`meaning-list`, `meaning-show`, `decision-list`, `audit-list`, `cell-list`,
`context-list`, and `permission-list` are read-only.
