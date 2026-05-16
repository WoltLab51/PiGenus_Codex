# Canonical Alignment Plan

This plan maps current project documents and runtime surfaces against
`docs/GENUS_CANONICAL_SYSTEMFORM.md`.

It does not change runtime behavior. It is a cleanup and alignment map for
future documentation and implementation planning.

## Purpose

`docs/GENUS_CANONICAL_SYSTEMFORM.md` is now the canonical GENUS orientation.
Older blueprints, local notes, sketches, concept documents, and implementation
surfaces remain useful only when they map back to that canonical systemform.

This plan answers:

- which documents are canonical, topic-authoritative, project-control,
  historical/source memory, or implementation/runtime
- where conflicts are most likely
- what to update now, mark historical, leave as topic-authoritative, or defer
  until the next arc
- how current runtime surfaces map to the canonical cell-first direction

## Classification Rules

### Canonical Orientation

The highest orientation layer. It defines what GENUS is, what it is not, and
which direction wins when documents conflict.

### Topic-Authoritative

A focused document that owns one architecture area under the canonical
systemform. It can be the source of truth for a topic, but only inside its
scope.

### Project-Control

A living project steering file. These documents should summarize current
truth, sequencing, changes, decisions, or maintenance rules. They should not
become deep topic specifications.

### Historical / Source Memory

Useful old material, design lineage, review findings, or idea capture. It can
inspire future work, but it must be mapped to the canonical systemform before
implementation.

### Implementation / Runtime

Code, tests, runtime-operation docs, CLI conventions, migrations, and concrete
implemented surfaces. These show what PiGenus actually does today.

## Document Map

### Canonical Orientation

| Document | Classification | Alignment Notes | Strategy |
| --- | --- | --- | --- |
| `docs/GENUS_CANONICAL_SYSTEMFORM.md` | canonical orientation | Current source of truth for GENUS as bio-cybernetic operating systemform. | Leave authoritative. |
| `docs/GENUS_PHILOSOPHY.md` | canonical-supporting | Explains why GENUS favors meaning, cells, contracts, governance, and controlled evolution. | Leave as philosophy; avoid duplicating the full canonical map. |
| `docs/GENUS_VOCABULARY.md` | topic-authoritative / project-control | Owns term definitions and implementation status. | Keep aligned whenever canonical terms or statuses change. |

### Topic-Authoritative Architecture

| Document | Classification | Alignment Notes | Strategy |
| --- | --- | --- | --- |
| `docs/ARCHITECTURE_CONTRACT.md` | topic-authoritative | Owns non-breaking rules for future implementation. | Leave; later check high-risk execution and physiology language. |
| `docs/CELLULAR_SYSTEMFORM.md` | topic-authoritative | Owns cell philosophy. Some cell language predates MicroCell/RuntimeCell distinction. | Update later to reference the canonical maturity ladder instead of expanding it independently. |
| `docs/ARCHITECTURE_CONVERGENCE_REVIEW.md` | topic-authoritative / source memory | Strong map for anatomy and maturity. Some component examples may need refresh after worker-assignment slicing and canonical maturity terms. | Leave for now; update during next architecture consolidation pass. |
| `docs/PHILOSOPHY_ALIGNMENT_REVIEW_PROTOCOL.md` | topic-authoritative | Owns fit-review workflow. | Later add CanonicalSystemform as the first alignment checkpoint. |
| `docs/INTERNAL_COMMUNICATION.md` | topic-authoritative | Owns governed meaning flow; maps well to canonical nervous system. | Leave topic-authoritative. |
| `docs/MULTIMODAL_SYSTEMFORM.md` | topic-authoritative | Future meaning representation boundary; maps to variable form and nervous system. | Leave topic-authoritative. |
| `docs/CONTEXT_MODEL.md` | topic-authoritative | Correctly separates context frames from actors, agents, cells, organs, and characters. | Leave topic-authoritative. |
| `docs/DATA_LIFECYCLE.md` | topic-authoritative | Maps events, meaning, memory, decisions, audit, fossils, and assignment lifecycle. | Later add quarantine/apoptosis/regeneration references if lifecycle work resumes. |
| `docs/DATA_ARCHITECTURE.md` | topic-authoritative | Owns storage role and performance boundaries. | Leave topic-authoritative; revisit before resource economy or graph/vector storage. |
| `docs/THREAT_MODEL.md` | topic-authoritative | Already captures LLM trust, agents before contracts, dashboards before CLI, rogue workers, and mutation risks. | Later align terms with immune system, quarantine, kill switch, and high-risk organ rule. |
| `docs/HUMAN_GOVERNANCE.md` | topic-authoritative | Owns approval and authority boundaries. | Leave; revisit when high-risk approval thresholds become implementation work. |
| `docs/EVOLUTION_SANDBOX.md` | topic-authoritative | Maps well to controlled evolution and mutation-is-not-activation. | Leave topic-authoritative. |
| `docs/RESOURCE_ECONOMY.md` | topic-authoritative | Maps to metabolism/resource economy. | Leave; update before budget/accounting implementation. |
| `docs/WORKER_RUNTIME.md` | topic-authoritative with conflict risk | Mostly aligned on worker-as-host, but older "Cell = capability" language is less precise than MicroCell/Cell/RuntimeCell. | Defer update until Worker Runtime planning resumes. |
| `docs/WORKER_RUNTIME_READINESS.md` | topic-authoritative | Owns worker readiness boundary and no-execution posture. | Leave; later map habitat/device/homeostasis terms. |
| `docs/WORKER_ASSIGNMENT_SEMANTICS.md` | topic-authoritative | Owns assignment evidence and lifecycle semantics. | Leave; ensure assigned status remains non-execution proof. |
| `docs/WORKER_SCHEDULING_ENFORCEMENT.md` | topic-authoritative | Owns assigned-intent eligibility before scheduling. | Leave; later add reflex/kill-switch/resource-risk prerequisites before enforcement. |
| `docs/LIQUID_RUNTIME.md` | topic-authoritative / future concept | Maps to variable form and RuntimeShape. | Leave; update later with canonical physiology terms. |
| `docs/GITHUB_IDEA_HARVEST.md` | historical/source memory | Explicitly quarantines older ideas. | Leave as source memory. |

### Project-Control Documents

| Document | Classification | Alignment Notes | Strategy |
| --- | --- | --- | --- |
| `docs/INDEX.md` | project-control | Entry point; should point to canonical orientation and this plan. | Update now. |
| `BUILD_PLAN.md` | project-control | Roadmap; should reference canonical alignment before future implementation planning. | Update now, lightly. |
| `STATUS.md` | project-control | Current repository truth. | Update now, briefly. |
| `CHANGELOG.md` | project-control | Records grouped changes. | Update now. |
| `docs/DECISIONS.md` | project-control | Durable decision log; D-104 already records the canonical source-of-truth rule. | No new decision needed for this plan. |
| `docs/ARCHITECTURE_HISTORY.md` | project-control / historical | Narrative of architecture evolution. | No update needed for this docs-only mapping plan. |
| `docs/DOCUMENTATION_MAINTENANCE.md` | project-control | Owns documentation upkeep and project-control roles. | Later add canonical alignment plan to Project Control Map if drift appears. |
| `docs/FULL_CHECK.md` | project-control | Full verification workflow. | Later add canonical alignment check to concept/release levels. |
| `docs/GENUS_ARCHITECTURE_SUMMARY.md` | project-control / summary | Compact architecture summary. | Defer until the next architecture summary refresh. |

### Historical / Source Memory

| Document | Classification | Alignment Notes | Strategy |
| --- | --- | --- | --- |
| `docs/GENUS_SYSTEMFORM_v0.1.md` | historical/source memory | Original Systemform framing. It predates canonical physiology and cell maturity language. | Mark or treat as historical in a later pass; do not implement directly from it. |
| `docs/PIGENUS_PHASE_0_CORE_KERNEL_SPEC_v0.1.md` | historical/source memory | Phase 0 kernel spec. Useful lineage, but older than current v0.4 worker and canonical terms. | Mark or treat as historical in a later pass. |
| `docs/SYSTEMFORM_GAP_ANALYSIS.md` | historical/source memory / analysis | Useful gap analysis from prototype to Systemform. Some gaps are now closed or reframed. | Update only if reused for a new gap review. |
| `docs/V0_3_GOVERNED_RUNTIME_READINESS.md` | historical/source memory / release record | Accurate for v0.3 release readiness, not current v0.4 planning. | Leave as release history. |
| `docs/RUNTIME_VERIFICATION.md` | historical/source memory / verification record | Records a specific runtime verification pass. | Leave as verification history. |

### Runtime Operations

| Document | Classification | Alignment Notes | Strategy |
| --- | --- | --- | --- |
| `docs/CLI_CONVENTIONS.md` | implementation/runtime | Owns CLI behavior and exit-code conventions. | Leave; revisit if command cells become real runtime surfaces. |
| `docs/MIGRATIONS.md` | implementation/runtime | Owns migration discipline. | Leave. |
| `docs/PHASE_2_MEMORY_LIFECYCLE.md` | implementation/runtime / historical spec | Memory lifecycle implementation contract. | Leave unless memory lifecycle work resumes. |

## Current Runtime Surface Map

| Runtime Surface | Classification | Canonical Mapping | Alignment Notes |
| --- | --- | --- | --- |
| `pigenus/schemas/*` | implementation/runtime | Stable core contracts and ontology. | Systemform schemas are part of the stable core; no schema change in this plan. |
| `pigenus/cells/*` | implementation/runtime | Current primitive runtime cells. | These are legacy/early cells, not full canonical RuntimeCells yet. |
| `pigenus/core/guard_pipeline.py` | implementation/runtime | Immune tissue / guard decision path. | Aligned; no runtime change. |
| `pigenus/core/room_flow.py` | implementation/runtime | Room policy / immune tissue. | Aligned. |
| `pigenus/core/governance_decision_log.py` | implementation/runtime | DecisionTrace / GovernanceDecision persistence. | Aligned. |
| `pigenus/core/human_approval.py` | implementation/runtime | Human approval threshold foundation. | Aligned but still stub-like. |
| `pigenus/core/meaning_ingestion.py` | implementation/runtime | Nervous system / meaning flow bridge. | Service / GovernedCell candidate, not RuntimeCell. |
| `pigenus/core/worker_registry.py` | implementation/runtime | Worker inventory hot state. | Worker remains execution host, not intelligence. |
| `pigenus/core/worker_inspection.py` | implementation/runtime | Worker/habitat inspection candidate. | Aligned with no-execution posture. |
| `pigenus/core/worker_scheduling_preview.py` | implementation/runtime | Shape/worker suitability preview. | Preview only; no scheduling or reservation. |
| `pigenus/core/worker_execution_preflight.py` | implementation/runtime | High-risk execution pre-check precursor. | Needs future resource/risk/reflex/kill-switch boundaries before execution. |
| `pigenus/core/worker_assignment_*` | implementation/runtime | Assignment intent lifecycle, not execution. | Must keep assigned status distinct from execution proof. |
| `pigenus/storage/*` | implementation/runtime | Source-of-truth persistence surfaces. | SQLite remains local governed truth. |
| `pigenus/cli/main.py` | implementation/runtime | Operator surface entry point. | Deterministic dispatcher, not dynamic command-cell routing. |
| `pigenus/cli/worker_commands.py` | implementation/runtime | StaticCellBoundary for worker inspection/previews. | Aligned; not a RuntimeCell. |
| `pigenus/cli/worker_assignment_commands.py` | implementation/runtime | Stable assignment command router. | Aligned after split. |
| `pigenus/cli/worker_assignment_inspection_commands.py` | implementation/runtime | Read-only assignment inspection boundary. | Aligned. |
| `pigenus/cli/worker_assignment_lifecycle_commands.py` | implementation/runtime | Assignment lifecycle command boundary. | Writes assignment/audit only through services; no execution. |
| `pigenus/cli/meaning_commands.py` | implementation/runtime | StaticCellBoundary for meaning operator surface. | Aligned; not dynamic routing. |
| `tests/*` | implementation/runtime | Evidence for behavior and boundaries. | Tests remain the proof surface for no-write, no-execution, and read-only invariants. |

## Likely Conflict Zones

### Older Blueprint Language

Risk:

Older Systemform and Phase 0 documents may describe goals before the canonical
bio-cybernetic operating systemform existed.

Current strategy:

- mark historical later
- keep useful concepts as source memory
- do not implement directly from older wording unless mapped to the canonical
  systemform

### Agent-First Phrasing

Risk:

Some future concept documents discuss agents as natural next objects. GENUS is
not agent-first; agents come after cells and organs.

Current strategy:

- leave topic-authoritative docs that already say agents remain governed
- update any future agent text to: cells -> organs -> agents -> characters
- block any implementation plan that starts with autonomous agents

### LLM-First Phrasing

Risk:

LLM references may be read as orchestration direction.

Current strategy:

- leave current stop lines in place
- keep LLMGateway planned only
- require meaning wrapping, provenance, room policy, guards, resource policy,
  audit, and trace before LLM behavior can act

### Dashboard-First Phrasing

Risk:

Visual or dashboard language may bypass CLI semantics and operator safety.

Current strategy:

- leave dashboard as later product surface
- require CLI semantics before dashboard behavior
- do not let dashboard drive architecture

### Worker-As-Intelligence Phrasing

Risk:

Worker examples may be misread as intelligent agents.

Current strategy:

- keep worker as execution host
- update older worker docs later where "worker runs agent" language might be
  confused with worker intelligence
- require cells/organs/agents to carry capability and goal semantics, not
  workers

### Assigned-As-Execution Phrasing

Risk:

WorkerAssignment `assigned` status might be mistaken for running work.

Current strategy:

- leave `WORKER_ASSIGNMENT_SEMANTICS.md` and
  `WORKER_SCHEDULING_ENFORCEMENT.md` topic-authoritative
- keep current stop line: assigned is necessary for future scheduling
  consideration, never execution proof
- require future high-risk execution rule before live behavior

### Cell Terminology Before MicroCell / RuntimeCell Distinction

Risk:

Older cellular documents sometimes say "cell" broadly, before the canonical
MicroCell, Cell, CapabilityCell, GovernedCell, and RuntimeCell ladder existed.

Current strategy:

- leave existing cell docs as topic-authoritative for now
- update them later to reference the canonical maturity ladder
- do not rename every service as a RuntimeCell
- use Cell-DNA frames for new responsible capabilities

## Update Strategy

### Update Now

This commit updates only the navigation and project-control surfaces needed to
make the alignment plan discoverable:

- `docs/CANONICAL_ALIGNMENT_PLAN.md`
- `docs/INDEX.md`
- `BUILD_PLAN.md`
- `STATUS.md`
- `CHANGELOG.md`

No runtime code, schemas, migrations, tests, or old documents are changed.

### Mark Historical

Later small docs-only pass:

- `docs/GENUS_SYSTEMFORM_v0.1.md`
- `docs/PIGENUS_PHASE_0_CORE_KERNEL_SPEC_v0.1.md`
- `docs/SYSTEMFORM_GAP_ANALYSIS.md` if it is reused as current guidance

Goal: add a short historical/source-memory note, not rewrite the files.

### Leave As Topic-Authoritative

Leave these as current topic authority unless their topic is active:

- `docs/ARCHITECTURE_CONTRACT.md`
- `docs/CELLULAR_SYSTEMFORM.md`
- `docs/ARCHITECTURE_CONVERGENCE_REVIEW.md`
- `docs/INTERNAL_COMMUNICATION.md`
- `docs/DATA_LIFECYCLE.md`
- `docs/DATA_ARCHITECTURE.md`
- `docs/THREAT_MODEL.md`
- `docs/HUMAN_GOVERNANCE.md`
- `docs/RESOURCE_ECONOMY.md`
- `docs/EVOLUTION_SANDBOX.md`
- worker topic documents

When a topic becomes active, update only the relevant document and keep the
canonical systemform as the alignment check.

### Defer Until Next Arc

Defer deeper alignment until the next implementation arc:

- Cell-DNA frame template in a workflow document
- high-risk execution checklist in worker/resource docs
- habitat/device/homeostasis terms in Worker Runtime docs
- quarantine/apoptosis/regeneration terms in Threat Model and Data Lifecycle
- RuntimeShape physiology alignment in Liquid Runtime

## Alignment Checklist For Future Work

Before a future implementation plan, answer:

```text
1. Does the work map to the canonical systemform?
2. Is it stable core, variable form, tissue, organ, organism, or habitat work?
3. Is it a Function, MicroCell, Cell, CapabilityCell, GovernedCell, RuntimeCell,
   Organ, Agent, Character, or plain implementation helper?
4. Does cell ceremony scale with responsibility?
5. Does it preserve worker-as-host, not worker-as-intelligence?
6. Does it preserve assigned-as-intent, not assigned-as-execution?
7. Does it avoid LLM-first, dashboard-first, agent-first, and hidden prompt-bus
   behavior?
8. If high-risk execution is involved, are room policy, resource/risk budget,
   worker/habitat health, contract, guards, reflexes, kill switch, audit,
   approval thresholds, recovery path, and shadow/dry-run evidence present?
9. Are docs and tests proportional to risk?
```

## Current Conclusion

The repository is broadly aligned with the canonical GENUS direction.

The main alignment work is not runtime repair. It is controlled terminology and
document stewardship:

- mark older blueprints as source memory when needed
- keep topic documents authoritative inside their scope
- update cell language to the maturity ladder when those docs become active
- keep Worker Runtime behind physiology, risk, resource, reflex, and kill-switch
  boundaries before live execution
- preserve PiGenus as the local reference runtime distribution, not the whole
  GENUS system
