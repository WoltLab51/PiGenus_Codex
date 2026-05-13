# Architecture Contract

This document defines the boundaries future PiGenus work must preserve.

It is not a feature plan. It is a contract for building without weakening the
governed runtime.

## Core Rule

Do not add capability by bypassing governance.

Every meaningful extension must preserve:

```text
contract + context + room + meaning + guard + decision + trace + test
```

## Current Baseline

The current baseline is `pigenus-v0.3.0-governed-runtime`.

It includes:

- structured events
- local event persistence
- memory lifecycle
- Meaning Store
- Systemform models and adapters
- rooms and context boundaries
- contract validation
- room flow rules
- guard pipeline and guard families
- governance decision logging
- human approval stub records
- audit logs
- health checks
- snapshot backups
- read-only operator inspection

Future work must treat this baseline as valid unless a deliberate migration or
replacement decision is recorded.

## Non-Breaking Rules

### Storage

- No schema change without a migration plan.
- No migration that silently deletes or rewrites existing data.
- No read-only CLI command should initialize, migrate, repair, or mutate
  storage.
- Full JSON payloads should remain available when indexed columns are added.

### Events And Communication

- No free-form prompt bus between runtime components.
- No hidden direct cell-to-cell communication for meaningful actions.
- Relevant communication must carry source, room or context, truth status,
  sensitivity, time, and enough provenance to inspect.
- Events, MeaningObjects, GovernanceDecisions, and AuditLogs must remain
  distinct surfaces.

### Meaning

- Raw text may appear as payload, but it must not replace structured meaning.
- Meaning movement across rooms must remain guardable.
- Meaning persistence must remain inspectable through deterministic queries
  before semantic ranking or vector search is added.
- Future intent, target scope, causal links, and suggested actions require a
  schema and migration decision before becoming runtime fields.

### Rooms And Context

- Room remains the governed information and action boundary.
- ContextFrame remains a condition around an action.
- ContextStack remains an operating envelope assembled from frames.
- Do not replace Room with ContextFrame or ContextStack.
- Do not treat context as an actor, agent, cell, organ, or character.

### Contracts And Capabilities

- No new capability without a declared contract or compatibility path.
- Capability declaration is not authorization.
- Contract validation must remain deterministic and inspectable.
- Cells carry capabilities, organs carry compositions, agents carry goals, and
  workers carry execution.

### Guards And Decisions

- Guard outcomes must remain explainable through ordered traces.
- Hard block enforcement must not be weakened without an explicit decision.
- Review and escalation must remain distinguishable from approval.
- GovernanceDecision must remain distinct from EventLog and AuditLog.
- New guard families or decision states require tests and documentation.

### Human Approval

- Human approval is a governance decision, not a UI button.
- No actor, agent, worker, or LLM may approve its own escalation.
- Approval records must include enough evidence to explain approve/reject
  actions when approval becomes active behavior.

### Workers

- Worker means execution host, not intelligence.
- Workers must not bypass rooms, guards, contracts, approval, resource policy,
  or auditability.
- Worker heartbeat, capability profile, cost profile, privacy profile, and
  failure semantics must be inspectable before remote execution is trusted.

### LLMs

- No LLM-first runtime behavior.
- No LLM output becomes trusted meaning without structured wrapping,
  provenance, truth status, sensitivity, and guardability.
- LLMGateway belongs behind governance, not inside the kernel.

### Evolution

- Mutation is never activation.
- MutationProposal must remain separate from active behavior.
- Shadow mode, fitness comparison, rollback, fossil records, guard checks, and
  human approval are required before any controlled evolution activates.

### Documentation

- Documentation maintenance is part of the checkpoint process.
- Vocabulary must be updated when term meaning or implementation status
  changes.
- Decisions must be recorded when future work becomes constrained.
- Changelog, Status, Build Plan, Architecture History, and topic docs must be
  checked before non-trivial commits.

## Contribution Checklist

Before merging or committing a non-trivial change:

```text
1. Does this preserve the v0.3 governed runtime baseline?
2. Does it add or change storage? If yes, where is the migration plan?
3. Does it add a capability? If yes, where is the contract?
4. Does it move meaning? If yes, where are room, sensitivity, truth, and guard checks?
5. Does it alter guard, approval, or enforcement behavior? If yes, where are tests and decisions?
6. Does it introduce a new term? If yes, is GENUS_VOCABULARY.md updated?
7. Does it change architecture? If yes, are Decisions and Architecture History updated?
8. Does it change current status or next work? If yes, is STATUS.md updated?
9. Does the changelog describe the change?
10. Are tests or docs aligned with the claimed state?
```

## Current Conclusion

PiGenus can grow only by preserving accountability.

New intelligence belongs on top of contracts, rooms, meaning, guards,
decisions, traces, and tests.
