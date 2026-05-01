# PiGenus MVP Roadmap

## Phase 1: Reliable Core

- Health endpoint
- Admin token auth
- Worker registration and heartbeat
- Job submission
- Capability-aware job leasing
- Job ack/fail lifecycle
- SQLite persistence
- Audit log
- Nightly scheduler skeleton
- systemd deployment
- Core tests

## Phase 2: Operational Hardening

- Backup and restore command: implemented
- Worker stale/offline detection: implemented in maintenance
- Admin audit endpoint: implemented
- User and trusted device administration: implemented baseline
- Manual maintenance endpoint: implemented
- Alembic migrations
- Log rotation integration
- Per-token rate limiting
- Job cancellation: implemented
- Retry policy controls

## Phase 3: Memory and Session Workflows

- Session/message APIs: implemented baseline
- Memory create/search/update APIs: implemented baseline
- Nightly session summarization jobs: queued by maintenance
- Daily briefing generation: queued by maintenance
- Actual summarizer/compressor worker implementations
- Human approval queue for critical actions

## Phase 4: Developer Orchestration

- GitHub webhook intake
- Coding agent job types
- Pull request status tracking
- Worker sandbox policy
- Signed worker attestations
