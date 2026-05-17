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
python -m pigenus.cli.main meaning-ingest-memory mem_example --db pigenus.sqlite3
python -m pigenus.cli.main decision-list --db pigenus.sqlite3
python -m pigenus.cli.main guard-decision-list --db pigenus.sqlite3 --family room_flow
python -m pigenus.cli.main guard-decision-summary --db pigenus.sqlite3
python -m pigenus.cli.main audit-list --db pigenus.sqlite3
python -m pigenus.cli.main cell-list --db pigenus.sqlite3
python -m pigenus.cli.main worker-list --db pigenus.sqlite3
python -m pigenus.cli.main worker-show worker_local --db pigenus.sqlite3
python -m pigenus.cli.main worker-scheduling-preview meaning_ingester --db pigenus.sqlite3 --runtime python
python -m pigenus.cli.main worker-scheduling-preview meaning_ingester --db pigenus.sqlite3 --runtime python --log --actor agent_preview --room room_developer
python -m pigenus.cli.main worker-execution-preflight worker_local meaning_ingester --db pigenus.sqlite3 --runtime python
python -m pigenus.cli.main worker-execution-preflight worker_local meaning_ingester --db pigenus.sqlite3 --runtime python --log --actor agent_preflight --room room_developer
python -m pigenus.cli.main worker-assignment-list --db pigenus.sqlite3
python -m pigenus.cli.main worker-assignment-create worker_local meaning_ingester dec_preflight --db pigenus.sqlite3 --room room_developer --actor agent_scheduler_preview --runtime python --sensitivity private
python -m pigenus.cli.main worker-assignment-transition wasg_candidate assigned --db pigenus.sqlite3 --actor agent_operator --reason operator_ready
python -m pigenus.cli.main worker-assignment-scheduling-eligibility wasg_candidate --db pigenus.sqlite3
python -m pigenus.cli.main worker-assignment-scheduling-eligibility wasg_candidate --db pigenus.sqlite3 --log --actor operator_cli
python -m pigenus.cli.main context-list
python -m pigenus.cli.main context-boundary-check input_cell@0.1.0 --context developer/default --db pigenus.sqlite3
python -m pigenus.cli.main context-boundary-list --db pigenus.sqlite3 --allowed no
python -m pigenus.cli.main permission-list
```

`memory-review` may update memory lifecycle status and write audit logs.
`backup-create` creates a new SQLite snapshot file but does not initialize,
migrate, repair, or overwrite runtime storage.
`meaning-ingest-memory` creates a meaning object from an existing memory object
but does not alter memory lifecycle, guard enforcement, audit logs, or decision logs.
`context-boundary-check` is read-only by default. With `--log`, it writes one
preview decision record to the decision log.
`worker-scheduling-preview` is read-only by default. With `--log`, it writes
one governance decision record to the decision log.
`worker-execution-preflight` is read-only by default. With `--log`, it writes
one governance decision record to the decision log.
`worker-assignment-list` is read-only and does not create assignments,
schedule, reserve, route, call providers, or execute.
`worker-assignment-create` creates pending assignment intent and writes one
audit row after validation. It does not create governance decisions, schedule,
reserve, route, call providers, or execute.
`worker-assignment-transition` applies validated assignment lifecycle status
changes and writes one audit row. It does not create governance decisions,
schedule, reserve, route, call providers, or execute.
`worker-assignment-scheduling-eligibility` is read-only by default. With
`--log`, it writes one governance decision record for allow, deny, or review
results and skips not-considered results. It does not mutate assignments, write
audit rows, schedule, reserve, route, call providers, or execute.

`runtime-overview`, `health-check`, `event-list`, `event-show`, `memory-list`,
`meaning-list`, `meaning-show`, `decision-list`, `guard-decision-list`,
`guard-decision-summary`, `audit-list`, `cell-list`, `worker-list`,
`worker-show`, `worker-scheduling-preview` without `--log`, `context-list`,
`worker-execution-preflight` without `--log`, `worker-assignment-list`,
`worker-assignment-scheduling-eligibility` without `--log`,
`context-boundary-check` without `--log`, `context-boundary-list`, and
`permission-list` are read-only.
