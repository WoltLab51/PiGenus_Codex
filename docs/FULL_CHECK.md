# PiGenus Full Check

This document defines the complete quality check for PiGenus changes,
checkpoints, release cuts, and larger architecture discussions.

It is a process document, not a runtime feature.

## Core Rule

Every meaningful change should be checked at the right depth.

Small documentation changes need a small check. Runtime, architecture, release,
or governance changes need the full check.

## Check Levels

### Level 1: Small Documentation Change

Use for wording, links, glossary additions, or small concept clarifications.

Required:

```text
git status --short
git diff --check
relevant doc review
CHANGELOG.md update if user-visible or architecture-relevant
commit
push when appropriate
```

Tests are optional unless code or generated examples changed.

### Level 2: Concept Or Architecture Change

Use for new concept documents, vocabulary boundaries, architecture decisions,
future tracks, non-goals, threat model changes, or lifecycle rules.

Required:

```text
git status --short
git diff --check
docs/INDEX.md checked
docs/GENUS_VOCABULARY.md checked
docs/ARCHITECTURE_CONTRACT.md checked
docs/PHILOSOPHY_ALIGNMENT_REVIEW_PROTOCOL.md checked for architecture fit
docs/DOCUMENTATION_MAINTENANCE.md checked
docs/DECISIONS.md updated if durable
docs/ARCHITECTURE_HISTORY.md updated if architecture shape changed
BUILD_PLAN.md updated if roadmap/track/order changed
STATUS.md updated if current truth or next work changed
CHANGELOG.md updated
commit
push when appropriate
```

Tests are optional if no runtime behavior changed.

### Level 3: Runtime Change

Use for code, models, CLI, storage, guards, room/context behavior, meaning,
memory, decisions, audit, backup, health, lifecycle, or tests.

Required:

```text
git status --short
git diff --check
.venv\Scripts\python.exe -m pytest
CI expected to pass after push
docs/ARCHITECTURE_CONTRACT.md checked
docs/THREAT_MODEL.md checked
docs/PHILOSOPHY_ALIGNMENT_REVIEW_PROTOCOL.md checked for governed path and maturity fit
docs/DATA_LIFECYCLE.md checked if data/storage changes
docs/GENUS_VOCABULARY.md updated if terms/status changed
docs/DECISIONS.md updated if durable rule changed
docs/ARCHITECTURE_HISTORY.md updated if architecture shape changed
BUILD_PLAN.md updated if roadmap/next step changed
STATUS.md updated with latest verified test result when relevant
CHANGELOG.md updated
commit
push when appropriate
```

### Level 4: Release Or Checkpoint Cut

Use before semantic releases, stable tags, larger merges, or PRs intended to
become a baseline.

Required:

```text
git status --short
git diff --check
.venv\Scripts\python.exe -m pytest
docs/INDEX.md checked
docs/GENUS_PHILOSOPHY.md checked
docs/GENUS_VOCABULARY.md checked
docs/ARCHITECTURE_CONTRACT.md checked
docs/THREAT_MODEL.md checked
docs/PHILOSOPHY_ALIGNMENT_REVIEW_PROTOCOL.md checked
docs/DATA_LIFECYCLE.md checked
docs/DOCUMENTATION_MAINTENANCE.md checked
docs/DECISIONS.md checked
docs/ARCHITECTURE_HISTORY.md updated
BUILD_PLAN.md current checkpoint and next step checked
STATUS.md current checkpoint and test result updated
CHANGELOG.md release/checkpoint section prepared
git log --oneline -5 reviewed
tag created for stable checkpoint if appropriate
push branch and tag when appropriate
GitHub Actions CI checked after push
```

## Architecture Review Questions

For concept, runtime, or release work:

```text
1. Does this preserve the v0.3 governed runtime baseline?
2. Does it add capability without contract, room, meaning, guard, decision, trace, or test?
3. Does it introduce a new term or change an existing boundary?
4. Does it create data that lacks source, room/context, truth/confidence, sensitivity, storage, inspection, or aging rules?
5. Does it add a threat not covered in THREAT_MODEL.md?
6. Does it weaken hard block, approval, audit, or decision behavior?
7. Does it introduce LLM, worker, federation, dashboard, vector search, or evolution behavior too early?
8. Does the documentation still tell the truth after the change?
9. Does it pass the Philosophy Alignment Review at the right depth?
```

## ChatGPT Review Role

ChatGPT can be useful as an external discussion partner for:

- philosophy and ontology questions
- architecture language
- concept completeness
- roadmap ordering
- naming clarity
- threat brainstorming
- product or user-facing framing

ChatGPT should not be treated as repository truth.

Codex remains responsible for:

- reading the actual repository
- checking current code and docs
- running local commands
- applying edits
- running tests
- committing and pushing
- preserving the architecture contract

Use ChatGPT input as proposal material. Translate it into repo terms before
committing.

## ChatGPT Handoff Prompt

When asking ChatGPT for review, use a bounded prompt like:

```text
Please review this PiGenus/GENUS architecture proposal conceptually.

Assume the repository already has:
- v0.3 governed runtime baseline
- GENUS philosophy
- GENUS vocabulary
- architecture contract
- documentation maintenance
- internal communication layer
- threat model
- data lifecycle map

Please check:
1. conceptual consistency
2. missing risks
3. terminology conflicts
4. whether this should be implemented now, documented only, or deferred

Do not propose a rewrite.
Do not introduce LLMs, workers, federation, dashboards, vector search, or evolution unless explicitly relevant.
Return concise recommendations and note what should remain out of scope.
```

## PR Or Merge Check

Before a PR or merge:

```text
1. Is the branch scope small enough to review?
2. Are all tests green if code changed?
3. Is the changelog updated?
4. Are status and next work accurate?
5. Are decisions and vocabulary updated if needed?
6. Does the architecture contract still hold?
7. Does the threat model need a new or changed risk?
8. Does data lifecycle need an update?
9. Is the working tree clean after commit?
10. Is the pushed branch current?
11. Has GitHub Actions CI passed or been noted as pending?
```

## Current Conclusion

The full check exists to keep PiGenus boring in the best way:

```text
observable
bounded
testable
documented
governed
```

When in doubt, do the smaller next step and make the system easier to inspect.
