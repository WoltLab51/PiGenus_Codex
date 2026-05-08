# PiGenus Build Plan

This file is the living technical plan for PiGenus. Update it whenever a phase
is completed, renamed, split, or moved.

## Build Rule

Every checkpoint should leave the repository with:

- Passing tests
- Updated `CHANGELOG.md`
- Updated `STATUS.md`
- This build plan adjusted when the next step changes
- A Git commit
- A version tag for stable phase checkpoints

## Completed

### pigenus-v0.1-core

Phase 1 Core Runtime established the executable nucleus:

- Structured schemas
- SQLite storage
- Event bus
- Cell registry
- Permission engine
- Audit logger
- MVP cells
- CLI demo
- Core tests

### pigenus-v0.1.5-contracts

Phase 1.5 Core Contracts made core behavior more explicit:

- Known event types and required payload keys
- `MemoryProposal` before durable memory writes
- Guard decisions tied to the source proposal
- Separate `CellState` for operational cell-local state
- Invariant tests for direct-write rejection and cell-state separation

## Current

### pigenus-v0.1.6-contexts

Phase 1.6 Context Boundaries establishes minimal room separation:

- Structured context schema
- Known context names
- Event and memory context validation
- Cell `allowed_contexts` enforcement in the orchestrator
- Invariant tests for context rejection and preservation

## Next

### Phase 2 Memory Lifecycle

Goal: make memory age, review, and protect itself without adding external AI.

Planned scope:

- `review_due_at` and `expires_at` behavior
- Status transition rules
- `canonical` protection
- Memory review CLI
- Audit logs for memory status changes
- Tests for lifecycle invariants

Out of scope:

- LLM reasoning
- Dashboards
- Distributed workers
- Autonomous evolution
- Vector search

## Later

- Context boundary expansion
- Schema registry
- Decision log
- Cell lifecycle and fitness
- Guard families
- Worker interface
- Controlled cell evolution
