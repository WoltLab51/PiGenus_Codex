# PiGenus Threat Model

This document captures the main security and governance threats for the current
PiGenus governed runtime and the later GENUS architecture tracks.

It is a planning and review document, not a new implementation layer.

## Core Rule

Threats are handled first by preserving observability, boundaries, and
accountability.

For PiGenus, the first safety question is not "can it do this?" but:

```text
Can we see who caused it, in which room, under which contract, with what
meaning, guard decision, trace, and audit evidence?
```

## Current Trust Boundary

Current trusted baseline:

- local runtime process
- local SQLite storage
- structured events
- Meaning Store
- memory lifecycle
- Systemform models and adapters
- room flow rules
- guard pipeline
- decision logging
- audit logging
- read-only inspection commands
- snapshot backups

Current untrusted or partially trusted inputs:

- user input
- meaning payloads
- event payloads
- imported repository ideas
- future LLM output
- future worker output
- future remote/federated records
- future mutation proposals

## Threats

### T-001: Prompt Or Meaning Injection

Risk:

Untrusted text or meaning payloads may attempt to override instructions,
mislabel provenance, hide sensitive content, or request actions outside the
current room or contract.

Current mitigations:

- structured events
- MeaningObject wrapping
- truth status
- sensitivity
- room IDs
- provenance fields
- guard pipeline
- room flow rules
- decision traces

Future hardening:

- explicit intent fields
- target scope fields
- source trust scoring
- LLM output quarantine
- injection-focused guard family

### T-002: Room Boundary Bypass

Risk:

Meaning may move from private, family, financial, child-related, secret, or
other protected rooms into less protected rooms without a visible decision.

Current mitigations:

- Room model
- context-to-room adapter
- room flow rules
- sensitivity overrides
- truth status overrides
- guard decision logging
- context boundary inspection

Future hardening:

- room policy registry
- signed room export records
- room-scoped approval requirements
- room transition tests for every new sensitive room type

### T-003: Capability Escalation

Risk:

A cell, organ, agent, worker, or LLM-backed component may perform or request a
capability beyond its declared scope.

Current mitigations:

- CellSpec
- CellContract
- contract validator
- permissions
- room scope
- human approval required fields
- architecture contract

Future hardening:

- CellType and CellInstance registry
- OrganContract
- Worker capability profile
- capability leases
- denied-by-default capability routing

### T-004: Stale Or False Memory

Risk:

Old, contested, deprecated, simulated, unsafe, or low-confidence meaning may be
treated as current truth.

Current mitigations:

- Memory lifecycle states
- review and expiry behavior
- fossil status
- TruthStatus
- confidence
- Meaning Store filters
- canonical memory protection

Future hardening:

- review due policies for MeaningObject
- stale meaning summaries
- source validation
- freshness checks in retrieval
- truth-status-aware agent routing

### T-005: Approval Spoofing Or Self-Approval

Risk:

An automated component may approve its own escalation or create approval-like
records without sufficient human evidence.

Current mitigations:

- Human approval stub records
- human governance documentation
- architecture contract rule against self-approval
- decision log persistence

Future hardening:

- approval authority registry
- approval evidence schema
- signed approval records
- approval inspection CLI
- approval state transition tests

### T-006: Audit Or Decision Log Gaps

Risk:

Important events, decisions, guard outcomes, or lifecycle changes may occur
without a durable trace.

Current mitigations:

- event persistence
- decision logs
- audit logs
- guard-decision-list
- guard-decision-summary
- context-boundary-list
- read-only inspection commands

Future hardening:

- coverage tests for required log surfaces
- missing-trace health checks
- log integrity checks
- exportable signed decision records

### T-007: Rogue Worker

Risk:

A future worker may execute tasks, access data, or report capabilities outside
its declared profile.

Current mitigations:

- worker runtime concept only
- architecture contract says workers carry execution, not intelligence
- workers may not bypass rooms, guards, contracts, approval, or resource policy

Future hardening:

- worker registry
- heartbeat and status
- capability profile
- cost and privacy profile
- worker leases
- timeout and retry semantics
- per-worker audit records

### T-008: LLM Output Treated As Trusted

Risk:

LLM output may be treated as fact, instruction, approval, or executable action
without structured wrapping and governance.

Current mitigations:

- no LLM integration in the current runtime
- architecture contract blocks LLM-first behavior
- MeaningObject requires truth status, sensitivity, room, and provenance

Future hardening:

- LLMGateway quarantine
- simulated or believed default truth status for model outputs
- source labels for provider/model/run
- LLM-specific guard family
- no direct action from raw LLM text

### T-009: Silent Mutation

Risk:

The system may alter its own behavior, contracts, policies, prompts, routing,
or code without explicit proposal, comparison, approval, and rollback.

Current mitigations:

- no automatic mutation
- Evolution Sandbox concept
- architecture contract: mutation is never activation
- fossil and rollback requirements documented

Future hardening:

- MutationProposal model
- shadow mode comparison
- fitness test reports
- rollback plan records
- human approval before activation

### T-010: Resource Abuse

Risk:

Compute, storage, privacy, money, human attention, or external service access
may be consumed without accountable grants or limits.

Current mitigations:

- ResourceGrant model
- Resource Economy concept
- architecture contract
- no worker runtime yet

Future hardening:

- ResourcePolicy registry
- usage records
- room-scoped budgets
- worker cost profiles
- approval requirements for high-risk resources

### T-011: Documentation Drift

Risk:

Future work may follow stale vocabulary, obsolete status, or outdated
architecture assumptions.

Current mitigations:

- documentation index
- documentation maintenance rules
- vocabulary glossary
- architecture contract
- decisions
- architecture history

Future hardening:

- release checklist
- PR checklist
- docs freshness checks
- status verification task before semantic releases

## Review Checklist

Before adding a non-trivial capability, ask:

```text
1. What untrusted input can enter this path?
2. What room does the meaning belong to?
3. What contract allows the actor to touch it?
4. What guard checks the movement or action?
5. What decision explains the result?
6. What trace proves the decision order?
7. What audit or event record remains afterward?
8. What human approval is required, if any?
9. What stale or unsafe memory could affect it?
10. What documentation must be updated?
```

## Current Conclusion

The current v0.3 runtime is intentionally local, deterministic, and inspectable.

The largest future risks come from adding power before accountability:

- workers before worker governance
- LLMs before meaning wrapping
- agents before contracts
- federation before trust
- evolution before rollback
- dashboards before CLI semantics

PiGenus should keep the current order:

```text
observe -> bound -> guard -> decide -> audit -> then expand
```
