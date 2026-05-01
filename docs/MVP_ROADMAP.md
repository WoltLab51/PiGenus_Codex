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

- Alembic migrations
- Backup and restore command
- Log rotation integration
- Per-token rate limiting
- Worker stale/offline detection
- Admin audit browser endpoint
- Job cancellation
- Retry policy controls

## Phase 3: Memory and Session Workflows

- Session/message APIs
- Memory search and compaction
- Nightly session summarization jobs
- Daily briefing generation
- Human approval queue for critical actions

## Phase 4: Developer Orchestration

- GitHub webhook intake
- Coding agent job types
- Pull request status tracking
- Worker sandbox policy
- Signed worker attestations

