# Changelog

## Unreleased

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
