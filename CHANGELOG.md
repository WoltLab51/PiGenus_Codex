# Changelog

## Unreleased

## pigenus-v0.2.3-schema-registry

- Added minimal schema registry for event contracts
- Added `schema-list` CLI command
- Added tests tying registry output to runtime event validation
- Cleaned current status and build-plan phase layout
- Verified: 41 tests passed

## pigenus-v0.2.2-migrations

- Added minimal SQLite migration runner
- Added `schema_migrations` table
- Moved initial table creation into `0001_initial_schema`
- Made `Database.initialize()` apply migrations idempotently
- Added migration smoke tests for fresh, repeated, and existing databases
- Verified: 36 tests passed

## pigenus-v0.2.1-lifecycle-polish

- Added read-only `memory-list` CLI command
- Added status and context filters for memory listing
- Added CLI conventions and exit-code documentation
- Added SQLite migration policy documentation
- Added tests proving `memory-list` does not mutate storage
- Verified: 33 tests passed

## pigenus-v0.2-memory-lifecycle

- Bumped package version to `0.2.0`
- Added Phase 2 Memory Lifecycle implementation specification
- Added deterministic `MemoryLifecycleEngine`
- Added memory lifecycle service with status persistence and audit logging
- Added repository support for memory listing, due lifecycle lookup, and status updates
- Added `memory-review` CLI with deterministic `--now`
- Implemented review due and expiry rules without automatic deletion
- Protected `canonical` memory from automatic lifecycle changes
- Added lifecycle invariant tests
- Added architecture history and decision log documents
- Updated project-control rules for future checkpoints
- Verified: 29 tests passed

## pigenus-v0.1.6-contexts

- Added Phase 1.6 minimal context boundaries
- Added structured context schema with known context names
- Added context boundary checks before orchestrated cell execution
- Added invariant tests for context rejection and proposal context preservation
- Added `BUILD_PLAN.md` and `STATUS.md` as living project control documents
- Verified: 20 tests passed

## pigenus-v0.1.5-contracts

- Added Phase 1.5 Core Contracts
- Formalized known event types and required payload keys
- Added `MemoryProposal` as the required path before durable memory writes
- Added separate `CellState` storage for operational cell-local state
- Hardened guard decision payloads with blocking-cell metadata
- Verified: 14 tests passed

## pigenus-v0.1-core

- Implemented Phase 1 Core Runtime
- Added structured schemas, SQLite storage, event bus, registry, permissions, audit logger
- Added MVP cells and simple orchestrator
- Added CLI demo
- Added Phase-1 hardening tests
- Verified: 9 tests passed
