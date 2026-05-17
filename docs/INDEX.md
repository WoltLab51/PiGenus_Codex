# PiGenus Documentation Index

This index is the recommended entry point for PiGenus and GENUS architecture
documentation.

## Read First

Start here when orienting yourself:

1. `docs/GENUS_CANONICAL_SYSTEMFORM.md` - current canonical GENUS orientation
2. `docs/CANONICAL_IMPLEMENTATION_PLAN.md` - bridge from canonical systemform to next build cycles
3. `docs/CELLULAR_INVENTORY_REVIEW.md` - code-checked inventory for first Cell-DNA candidates
4. `docs/CELL_DNA_PROTOCOL.md` - lightweight frame for responsible capabilities
5. `docs/CELL_DNA_WORKER_ASSIGNMENT_VALIDATOR.md` - first applied Cell-DNA frame
6. `docs/CELL_DNA_WORKER_ASSIGNMENT_SCHEDULING_ELIGIBILITY_VALIDATOR.md` - second applied Cell-DNA frame
7. `docs/CELL_DNA_WORKER_ASSIGNMENT_CREATOR.md` - first write-capable Cell-DNA frame
8. `docs/CELL_DNA_WORKER_ASSIGNMENT_STATUS_TRANSITION_SERVICE.md` - lifecycle Cell-DNA frame
9. `docs/WORKER_ASSIGNMENT_SCHEDULING_ELIGIBILITY_LOGGING.md` - opt-in eligibility logging semantics
10. `docs/WORKER_ASSIGNMENT_TISSUE_CONSOLIDATION_REVIEW.md` - WorkerAssignment tissue consolidation
11. `docs/WORKER_SCHEDULING_ENFORCEMENT_READINESS_GAP_REVIEW.md` - readiness gaps before scheduling enforcement
12. `docs/WORKER_FRESHNESS_POLICY.md` - heartbeat and evidence freshness semantics
13. `docs/CELL_DNA_WORKER_FRESHNESS_POLICY_VALIDATOR.md` - freshness validator Cell-DNA frame
14. `docs/WORKER_FRESHNESS_ELIGIBILITY_CONSOLIDATION_REVIEW.md` - freshness-integrated eligibility consolidation
15. `docs/WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK.md` - room/context recheck semantics before scheduling enforcement
16. `docs/CELL_DNA_WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK_VALIDATOR.md` - room/context recheck validator Cell-DNA frame
17. `docs/WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK_CONSOLIDATION_REVIEW.md` - room/context recheck implementation consolidation before wiring
18. `docs/CELL_DNA_CONSOLIDATION_REVIEW.md` - review of the first three Cell-DNA frames
19. `docs/GENUS_PHILOSOPHY.md` - why GENUS is built this way
20. `docs/GENUS_VOCABULARY.md` - shared terms and implementation status
21. `BUILD_PLAN.md` - roadmap, release arcs, and current architecture tracks
22. `STATUS.md` - current repository truth and stable invariants
23. `docs/ARCHITECTURE_CONTRACT.md` - what future work must not break
24. `docs/GENUS_ARCHITECTURE_SUMMARY.md` - compact map of how the pieces fit
25. `docs/ARCHITECTURE_CONVERGENCE_REVIEW.md` - anatomy, maturity levels, and static/dynamic boundary rules
26. `docs/GENUS_METABOLIC_STATE_GRAPH.md` - future diagnostic graph view for metabolism, dependencies, state, and flows
27. `docs/ARCHITECTURE_FITNESS_REVIEW.md` - current structural hotspot review
28. `docs/CANONICAL_ALIGNMENT_PLAN.md` - maps existing docs and runtime surfaces to the canonical systemform
29. `docs/PHILOSOPHY_ALIGNMENT_REVIEW_PROTOCOL.md` - fit check for philosophy, governance, cellular maturity, and runtime shape risk
30. `docs/DOCUMENTATION_MAINTENANCE.md` - how docs stay current

## Core Architecture

- `docs/GENUS_CANONICAL_SYSTEMFORM.md` - canonical bio-cybernetic systemform orientation and conflict rule
- `docs/CANONICAL_IMPLEMENTATION_PLAN.md` - practical next-cycle plan and initial cellular inventory
- `docs/CELLULAR_INVENTORY_REVIEW.md` - code-checked inventory review and first Cell-DNA candidates
- `docs/CELL_DNA_PROTOCOL.md` - lightweight Cell-DNA protocol for responsible capabilities
- `docs/CELL_DNA_WORKER_ASSIGNMENT_VALIDATOR.md` - first applied Cell-DNA frame
- `docs/CELL_DNA_WORKER_ASSIGNMENT_SCHEDULING_ELIGIBILITY_VALIDATOR.md` - second applied Cell-DNA frame
- `docs/CELL_DNA_WORKER_ASSIGNMENT_CREATOR.md` - first write-capable Cell-DNA frame
- `docs/CELL_DNA_WORKER_ASSIGNMENT_STATUS_TRANSITION_SERVICE.md` - lifecycle-changing Cell-DNA frame
- `docs/CELL_DNA_CONSOLIDATION_REVIEW.md` - consolidation review before further Cell-DNA or logging work
- `docs/CANONICAL_ALIGNMENT_PLAN.md` - alignment map for current docs and runtime surfaces
- `docs/GENUS_METABOLIC_STATE_GRAPH.md` - derived graph view for metabolism, dependencies, state, resources, and diagnosis
- `docs/GENUS_SYSTEMFORM_v0.1.md` - original Systemform framing
- `docs/PIGENUS_PHASE_0_CORE_KERNEL_SPEC_v0.1.md` - Phase 0 kernel spec
- `docs/CELLULAR_SYSTEMFORM.md` - GENUS cell philosophy and static cell boundary rules
- `docs/ARCHITECTURE_CONVERGENCE_REVIEW.md` - GENUS anatomy, maturity ladder, runtime flow, and stable-core/variable-shape boundaries
- `docs/SYSTEMFORM_GAP_ANALYSIS.md` - prototype-to-Systemform gap analysis
- `docs/CONTEXT_MODEL.md` - Room, ContextFrame, and ContextStack boundaries
- `docs/INTERNAL_COMMUNICATION.md` - governed meaning-based communication
- `docs/MULTIMODAL_SYSTEMFORM.md` - future language, graph, state, visual, and spatial meaning boundary
- `docs/WORKER_ASSIGNMENT_SEMANTICS.md` - worker assignment creation evidence and status boundary
- `docs/WORKER_SCHEDULING_ENFORCEMENT.md` - boundary between assigned intent and future scheduling behavior
- `docs/WORKER_ASSIGNMENT_SCHEDULING_ELIGIBILITY_LOGGING.md` - opt-in decision logging semantics for assigned-intent eligibility
- `docs/WORKER_ASSIGNMENT_TISSUE_CONSOLIDATION_REVIEW.md` - WorkerAssignment tissue consolidation before scheduling enforcement
- `docs/WORKER_SCHEDULING_ENFORCEMENT_READINESS_GAP_REVIEW.md` - freshness and safety gaps before scheduling enforcement
- `docs/WORKER_FRESHNESS_POLICY.md` - heartbeat and governance evidence freshness policy semantics
- `docs/CELL_DNA_WORKER_FRESHNESS_POLICY_VALIDATOR.md` - Cell-DNA frame for freshness validation
- `docs/WORKER_FRESHNESS_ELIGIBILITY_CONSOLIDATION_REVIEW.md` - consolidation after freshness is wired into scheduling eligibility
- `docs/WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK.md` - room/context recheck semantics before scheduling enforcement
- `docs/CELL_DNA_WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK_VALIDATOR.md` - Cell-DNA frame for room/context recheck validation
- `docs/WORKER_ASSIGNMENT_ROOM_CONTEXT_RECHECK_CONSOLIDATION_REVIEW.md` - consolidation of the read-only room/context recheck validator before wiring
- `docs/DATA_LIFECYCLE.md` - lifecycle of events, meaning, memory, decisions, audit, and fossils
- `docs/DATA_ARCHITECTURE.md` - storage roles, performance boundaries, and truth/index/cache distinctions
- `docs/GENUS_ARCHITECTURE_SUMMARY.md` - concise current architecture summary
- `docs/V0_3_GOVERNED_RUNTIME_READINESS.md` - v0.3 release readiness scope
- `docs/ARCHITECTURE_FITNESS_REVIEW.md` - current CLI/repository slicing review

## Governance And Safety

- `docs/DECISIONS.md` - durable architecture decisions
- `docs/ARCHITECTURE_HISTORY.md` - narrative history of architecture changes
- `docs/ARCHITECTURE_CONTRACT.md` - non-breaking rules for future work
- `docs/PHILOSOPHY_ALIGNMENT_REVIEW_PROTOCOL.md` - review protocol for keeping changes aligned with GENUS philosophy
- `docs/THREAT_MODEL.md` - current and future security/governance threats
- `docs/HUMAN_GOVERNANCE.md` - review, escalation, approval, and authority
- `docs/EVOLUTION_SANDBOX.md` - mutation as proposal, not activation

## Runtime Operations

- `docs/CLI_CONVENTIONS.md` - CLI behavior and exit code conventions
- `docs/MIGRATIONS.md` - SQLite migration policy
- `docs/RUNTIME_VERIFICATION.md` - post-release runtime verification notes
- `docs/PHASE_2_MEMORY_LIFECYCLE.md` - memory lifecycle implementation contract
- `docs/DOCUMENTATION_MAINTENANCE.md` - documentation upkeep rules
- `docs/FULL_CHECK.md` - complete quality check levels for docs, runtime, releases, PRs, and ChatGPT review

## Future Concept Tracks

These documents are future-facing. They define boundaries before
implementation:

- `docs/WORKER_RUNTIME.md` - workers as execution hosts
- `docs/WORKER_RUNTIME_READINESS.md` - v0.4 worker identity, heartbeat, profile, and failure boundary
- `docs/WORKER_SCHEDULING_ENFORCEMENT.md` - assigned intent before future scheduling
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
6. docs/FULL_CHECK.md when the change is non-trivial
7. the topic-specific document for the area being changed
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
