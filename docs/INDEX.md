# PiGenus Documentation Index

This index is the recommended entry point for PiGenus and GENUS architecture
documentation.

## Read First

Start here when orienting yourself:

1. `docs/GENUS_PHILOSOPHY.md` - why GENUS is built this way
2. `docs/GENUS_VOCABULARY.md` - shared terms and implementation status
3. `BUILD_PLAN.md` - roadmap, release arcs, and current architecture tracks
4. `STATUS.md` - current repository truth and stable invariants
5. `docs/ARCHITECTURE_CONTRACT.md` - what future work must not break
6. `docs/DOCUMENTATION_MAINTENANCE.md` - how docs stay current

## Core Architecture

- `docs/GENUS_SYSTEMFORM_v0.1.md` - original Systemform framing
- `docs/PIGENUS_PHASE_0_CORE_KERNEL_SPEC_v0.1.md` - Phase 0 kernel spec
- `docs/SYSTEMFORM_GAP_ANALYSIS.md` - prototype-to-Systemform gap analysis
- `docs/CONTEXT_MODEL.md` - Room, ContextFrame, and ContextStack boundaries
- `docs/INTERNAL_COMMUNICATION.md` - governed meaning-based communication
- `docs/V0_3_GOVERNED_RUNTIME_READINESS.md` - v0.3 release readiness scope

## Governance And Safety

- `docs/DECISIONS.md` - durable architecture decisions
- `docs/ARCHITECTURE_HISTORY.md` - narrative history of architecture changes
- `docs/ARCHITECTURE_CONTRACT.md` - non-breaking rules for future work
- `docs/THREAT_MODEL.md` - current and future security/governance threats
- `docs/HUMAN_GOVERNANCE.md` - review, escalation, approval, and authority
- `docs/EVOLUTION_SANDBOX.md` - mutation as proposal, not activation

## Runtime Operations

- `docs/CLI_CONVENTIONS.md` - CLI behavior and exit code conventions
- `docs/MIGRATIONS.md` - SQLite migration policy
- `docs/PHASE_2_MEMORY_LIFECYCLE.md` - memory lifecycle implementation contract
- `docs/DOCUMENTATION_MAINTENANCE.md` - documentation upkeep rules

## Future Concept Tracks

These documents are future-facing. They define boundaries before
implementation:

- `docs/WORKER_RUNTIME.md` - workers as execution hosts
- `docs/RESOURCE_ECONOMY.md` - accounting before resource markets
- `docs/LIQUID_RUNTIME.md` - dynamic form proposals under governance
- `docs/GITHUB_IDEA_HARVEST.md` - idea harvesting without architecture merge

## Project Control Files

- `README.md` - repository overview
- `STATUS.md` - current truth and invariants
- `BUILD_PLAN.md` - roadmap and architecture tracks
- `CHANGELOG.md` - versioned changes
- `docs/GENUS_VOCABULARY.md` - central glossary
- `docs/DECISIONS.md` - durable decisions
- `docs/ARCHITECTURE_HISTORY.md` - architecture narrative

## Before Building

For non-trivial work, read or check:

```text
1. STATUS.md
2. BUILD_PLAN.md
3. docs/GENUS_VOCABULARY.md
4. docs/ARCHITECTURE_CONTRACT.md
5. docs/DOCUMENTATION_MAINTENANCE.md
6. the topic-specific document for the area being changed
```

Then update the relevant documentation before commit.

## Current Rule Of Thumb

If a change adds capability, it must preserve:

```text
contract + context + room + meaning + guard + decision + trace + test
```

If a change adds vocabulary, update `docs/GENUS_VOCABULARY.md`.

If a change constrains future architecture, update `docs/DECISIONS.md`.

If a change alters the current truth of the repository, update `STATUS.md`.
