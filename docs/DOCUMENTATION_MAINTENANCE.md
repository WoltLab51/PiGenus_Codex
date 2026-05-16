# Documentation Maintenance

This document defines how PiGenus keeps documentation current while the runtime
grows.

## Core Rule

No meaningful runtime or architecture change is complete until the relevant
documentation has been checked.

Documentation is part of the system boundary. Outdated docs can create unsafe
architecture assumptions just as surely as outdated code.

## Minimum Sufficient Documentation

Documentation should be current, not maximal.

Update only the documents whose truth changed:

- `STATUS.md` for current repository truth
- `CHANGELOG.md` for what changed
- `BUILD_PLAN.md` for roadmap or work-order changes
- `docs/DECISIONS.md` for durable rules
- `docs/GENUS_VOCABULARY.md` for term boundaries
- a focused concept document when its topic changed

Do not duplicate the same explanation across every document. Prefer one
authoritative place and short references elsewhere.

## Required Documentation Check

For every non-trivial change, check this list before commit:

- `CHANGELOG.md`: user-visible change, concept addition, behavior change, or
  checkpoint note
- `STATUS.md`: current runtime shape, stable invariants, current checkpoint, or
  next recommended work changed
- `BUILD_PLAN.md`: roadmap, architecture track, release semantics, or next
  step changed
- `docs/GENUS_VOCABULARY.md`: new term, changed term boundary, changed status,
  or new implementation for a documented/planned term
- `docs/DECISIONS.md`: durable architecture rule, safety rule, ontology rule,
  migration rule, or non-goal changed
- `docs/ARCHITECTURE_HISTORY.md`: architecture shape changed in a way future
  readers need to understand
- `docs/PHILOSOPHY_ALIGNMENT_REVIEW_PROTOCOL.md`: non-trivial changes need a
  philosophy, governance, cellular, and RuntimeShape fit check
- Specific concept docs: update the relevant document when a change touches its
  topic

If a file is checked and no update is needed, leave it unchanged.

## Update Triggers

### Code Changes

Update documentation when code changes:

- public CLI behavior
- schema or model fields
- storage migrations or repositories
- guard, room, context, approval, or decision behavior
- event, meaning, memory, audit, or lifecycle behavior
- worker, resource, federation, LLM, evolution, or product-surface behavior
- tests that encode a new invariant

### Concept Changes

Update documentation when a concept changes:

- term meaning or boundary changes
- implementation status changes
- a planned concept becomes implemented
- a non-goal becomes allowed work
- a safety rule becomes stricter or weaker
- architecture order changes

### Release Changes

Update documentation when release status changes:

- checkpoint tag created
- semantic release cut created
- current branch or checkpoint changes
- verified test count changes
- release scope or exclusion list changes

## Vocabulary Rules

`docs/GENUS_VOCABULARY.md` is the central term map.

Update it when:

- adding a new GENUS term
- promoting a term from conceptual to documented, planned, or implemented
- adding a Python model for a documented term
- changing what a term is not
- finding two terms that overlap too much

Do not update it for every wording preference. Vocabulary changes should affect
how future builders reason about the system.

## Decision Rules

`docs/DECISIONS.md` is for durable decisions, not every implementation detail.

Add a decision when:

- a rule constrains future work
- a boundary prevents a plausible wrong design
- a feature is intentionally delayed
- a safety or governance posture changes
- a compatibility policy is established

Do not add a decision for ordinary refactors, test-only changes, or local
wording cleanup.

## Status Rules

`STATUS.md` should describe the current truth of the repository.

Update it when:

- runtime capabilities change
- stable invariants change
- current checkpoint or branch status changes
- next recommended work changes
- last verified test result changes

Avoid turning `STATUS.md` into a changelog.

## Changelog Rules

`CHANGELOG.md` records what changed.

Update it when:

- a feature, behavior, concept document, command, model, migration, test group,
  or release section is added
- an important architecture boundary changes
- a new durable decision is recorded

Use release sections when cutting a checkpoint. Keep `Unreleased` short enough
to scan.

When `Unreleased` grows beyond a handful of bullets, group it by:

```text
### Added
### Changed
### Documented
### Verified
### Not Yet Implemented
```

Rules:

- Keep only the latest verified test result in `Unreleased`.
- Group related micro-commits into capability-level bullets.
- Do not copy every decision entry into `Unreleased`; summarize the decision
  range or the durable rule and leave the detailed record in
  `docs/DECISIONS.md`.
- Do not use `Unreleased` as architecture history; put narrative context in
  `docs/ARCHITECTURE_HISTORY.md`.
- If `Unreleased` becomes hard to scan, either consolidate it or cut a
  checkpoint section before adding more items.

## Architecture History Rules

`docs/ARCHITECTURE_HISTORY.md` explains why the system shape changed over time.

Update it when:

- a new architecture layer is introduced
- a concept becomes a named track
- a decision changes how future work should be understood
- a release cut marks a new system shape

Do not use it for small implementation notes that are already clear in the
changelog.

## Build Plan Rules

`BUILD_PLAN.md` is the living architecture map.

Update it when:

- the next checkpoint changes
- a new architecture track appears
- release semantics change
- the order of work changes
- a non-goal becomes a future track or a future track becomes current work

Do not add every small task to the build plan.

## Minimal Commit Checklist

Before committing:

```text
1. Does code behavior change?
2. Does a term meaning or status change?
3. Does a durable architecture rule change?
4. Does the current status or next step change?
5. Does the changelog mention the user-visible/documented change?
6. Do tests or docs match the claimed state?
```

If all answers are no except wording cleanup, keep the commit small and do not
touch control documents unnecessarily.

## Current Conclusion

PiGenus treats documentation as operational memory.

The goal is not more paperwork. The goal is fewer hidden assumptions.
