# Architecture Fitness Review

This review records where PiGenus has grown complex and where the next
structural cuts should happen. It is an analysis document, not a refactor.

The goal is to make future cell-oriented structure safer without changing
runtime behavior, storage, CLI semantics, guard decisions, or tests.

## Scope

Reviewed areas:

- `pigenus/cli/main.py`
- `pigenus/storage/repositories.py`
- CLI and repository coupling in `tests/`
- candidate structural boundaries for later cell-like modules

Out of scope:

- no file moves
- no command rewrites
- no schema changes
- no runtime cell orchestration
- no worker execution
- no LLM, agent, dashboard, federation, or evolution behavior

## Method

The review used a small Architecture Fitness pass:

1. Hotspot analysis by file size and command count.
2. Responsibility mapping for CLI and repository code.
3. Test-coupling review for subprocess, database, audit, decision, and worker
   store interactions.
4. Cell-boundary mapping for future module slices.
5. Refactor risk classification before any behavior-preserving extraction.

Initial measured hotspots before the worker CLI extraction:

| Area | Size / Count | Fitness Signal |
| --- | ---: | --- |
| `pigenus/cli/main.py` | 937 lines | High concentration of parser, dispatch, DB wiring, service wiring, filtering, and formatting |
| CLI command branches | 25 branches | Commands are still centrally dispatched in one file |
| CLI parser commands | 25 commands | Parser construction is also centralized |
| `pigenus/storage/repositories.py` | 526 lines | Eight repository classes share one file |
| `tests/test_governance_decision_log.py` | 314 lines | Broad governance/CLI persistence coverage |
| `tests/test_worker_scheduling_preview.py` | 212 lines | Rich worker placement rules with durable-decision compatibility |
| `pigenus/schemas/systemform.py` | 256 lines | Many ontology models, but still a coherent schema surface |
| `pigenus/core/worker_execution_preflight.py` | 230 lines | Single-purpose service with explicit checks |

First extraction result:

| Area | Size / Count | Fitness Signal |
| --- | ---: | --- |
| `pigenus/cli/main.py` | 658 lines | Main CLI remains deterministic entry point and dispatcher |
| `pigenus/cli/worker_commands.py` | 307 lines | Worker parser and command handling now have a dedicated static module boundary |

## Findings

### Necessary Kernel Complexity

Most current complexity is legitimate kernel complexity:

- Systemform models define the shared ontology.
- Guards, room flows, approvals, and decision traces make policy explainable.
- Meaning Store, EventLog, AuditLog, and DecisionLog provide traceable state.
- Worker Runtime preparation is intentionally staged as readiness, inspection,
  preview, and preflight before execution.
- Tests encode important safety invariants, especially read-only inspection and
  no unintended audit or decision writes.

This complexity should not be removed just to make the code look smaller. It is
the cost of keeping capability observable and governable.

### Avoidable Organizational Complexity

The avoidable complexity is mostly structural:

- `pigenus/cli/main.py` has become the main growth point.
- CLI parsing, command dispatch, repository setup, service construction, output
  formatting, filtering helpers, and error handling live together.
- Worker commands are especially dense because they combine worker store reads,
  registry construction, scheduling preview, preflight checks, optional logging,
  and output formatting.
- `pigenus/storage/repositories.py` is still acceptable for a small runtime, but
  it now mixes event, memory, meaning, worker, cell, audit, and decision
  persistence in one file.
- CLI tests often seed SQLite state, call subprocess commands, and then inspect
  repositories for side effects. That is valuable coverage, but it also shows
  that command boundaries should be extracted carefully.

The system is not overbuilt at the kernel level. It is beginning to need better
module boundaries around operator surfaces and storage adapters.

## Responsibility Map

### Current CLI Responsibilities

`pigenus/cli/main.py` currently owns:

- argument parser construction
- command dispatch
- database lifecycle decisions
- repository wiring
- service wiring
- worker registry construction from SQLite rows
- guard and boundary decision filtering
- output formatting
- CLI error messages and exit codes

This makes the CLI predictable, but it also turns one file into a coordination
surface for many domains.

### Current Repository Responsibilities

`pigenus/storage/repositories.py` currently contains:

- `EventRepository`
- `MemoryRepository`
- `MeaningRepository`
- `WorkerRepository`
- `CellRepository`
- `CellStateRepository`
- `AuditRepository`
- `DecisionRepository`

The single file still helps discover persistence behavior quickly. The cost is
that future storage changes will become harder to review unless repository
classes are split by domain before more worker, resource, or execution stores
arrive.

### Current Test Coupling

Tests do useful work by crossing boundaries:

- CLI tests call commands through subprocess.
- Several tests seed SQLite repositories before invoking CLI commands.
- Read-only commands are checked by asserting unchanged audit and decision
  counts.
- Worker CLI tests inspect `WorkerRepository`, `DecisionRepository`, and
  `AuditRepository` after commands run.

This is good safety coverage. It also means the first refactor should preserve
command behavior exactly and keep tests as the main proof that the extraction
did not create hidden side effects.

## Cell Boundary Candidates

The next cuts should use cell thinking as module boundaries, not as dynamic
runtime behavior yet.

Implemented first boundary:

```text
pigenus/cli/main.py
  remains parser/dispatch entry point

pigenus/cli/worker_commands.py
  owns worker-list
  owns worker-show
  owns worker-scheduling-preview
  owns worker-execution-preflight
  owns worker CLI formatting helpers
  owns worker registry construction from WorkerRepository
```

Why worker CLI first:

- It is the active v0.4 arc.
- It has strong tests already.
- It is dense enough to reduce `main.py` meaningfully.
- It is still read-only or explicit-opt-in logging, so behavior boundaries are
  clear.
- It prepares future Worker Runtime work without introducing execution.

Recommended later boundaries:

```text
pigenus/cli/meaning_commands.py
  meaning-list
  meaning-show
  meaning-ingest-memory

pigenus/cli/decision_commands.py
  decision-list
  guard-decision-list
  guard-decision-summary
  context-boundary-list

pigenus/cli/inspection_commands.py
  runtime-overview
  health-check
  event-list
  event-show
  audit-list
  cell-list
  context-list
  permission-list
```

Repository splitting should come after the first CLI extraction, not before it.
The CLI hotspot is larger and safer to slice because behavior is well covered
by subprocess tests.

## Refactor Risk Matrix

| Candidate | Benefit | Risk | Timing |
| --- | --- | --- | --- |
| Extract worker CLI handlers into `pigenus/cli/worker_commands.py` | High | Medium | Done |
| Move worker parser registration into the worker CLI module | Medium | Medium | Done |
| Extract meaning CLI handlers | Medium | Low-medium | Done |
| Extract decision/guard CLI handlers | Medium | Medium | After worker and meaning extraction |
| Split `repositories.py` by domain | Medium | Medium-high | Later, before new execution/resource stores |
| Introduce dynamic cell routing for CLI commands | Conceptually high | High | Not now |
| Add runtime command cells or self-routing CLI organs | Future high | High | Only after static module boundaries are stable |

## Meaning CLI Boundary Result

Completed structural checkpoint:

```text
Add meaning CLI command module boundary
```

Result:

- `pigenus/cli/meaning_commands.py` now owns meaning parser registration and
  meaning command handling.
- `pigenus/cli/main.py` remains the deterministic parser and dispatcher.
- Current command names, arguments, output shape, exit codes, and
  side-effect behavior.
- No new commands, storage, migrations, assignments, provider routing, or
  execution were added.

Next structural candidates:

- decision/guard CLI module boundary
- repository domain split before new execution/resource stores
- no dynamic command-cell routing yet

## Non-Goals For The Next Refactor

- no dynamic cell runtime
- no autonomous command routing
- no LLM interpretation of CLI input
- no worker assignment
- no worker execution
- no repository split in the same commit
- no command behavior changes

## Conclusion

PiGenus is not bloated because it has contracts, guards, decisions, meaning,
workers, and documentation. Those are the governed runtime.

The current bloat risk is narrower:

```text
too much operator-surface coordination in one CLI file
too many persistence domains in one repository file
```

The right move is a sequence of small structural extractions. The worker and
meaning CLI boundaries are complete; future slices should keep using the
Philosophy Alignment Review before code movement.
