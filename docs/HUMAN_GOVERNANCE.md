# Human Governance

Human Governance is a future GENUS architecture track. PiGenus v0.3 already
has human approval stub records, but it does not yet implement a full approval
workflow or UI.

The purpose of Human Governance is to preserve accountable human judgment at
the points where automation should slow down.

Core rule:

```text
Human approval is a governance decision, not a UI button.
```

## Why This Exists

As GENUS gains workers, resource accounting, liquid runtime proposals,
federation, and eventual evolution, some actions should not be decided by
automation alone.

Human Governance defines when the system must:

- ask
- wait
- explain
- record
- stop

It prevents "approval" from becoming a thin interaction layer added after
policy has already become dangerous.

## Review, Escalation, And Approval

These states should remain distinct:

- `review`: the system can continue in warning or preview mode, but the event
  deserves inspection
- `escalate`: the system should not proceed normally without explicit
  higher-level handling
- `approval`: a named human or governance authority must approve or reject
  before activation

Approval is stronger than review. Escalation is not the same as approval; it is
the signal that the decision left the normal automated path.

## Approval Subjects

Human Governance may apply to:

- guard decisions
- resource grant changes
- worker activation
- risky room transitions
- context stack activation
- liquid runtime shape execution
- federation trust changes
- evolution or mutation proposals

Approvals should reference the object being approved, not just a free-text
description.

## Who Can Approve

Approval authority should be explicit and room-aware.

Examples:

- developer room actions may be approved by a local operator
- private room actions may require the owner
- family room actions may require stricter policy
- trading room actions may require explicit financial approval
- evolution proposals may require special governance policy

No agent should self-approve its own escalation.

## Required Evidence

An approval request should include:

- actor
- room
- context stack if present
- proposed action
- reason
- guard family
- risk level
- resource impact
- trace
- expiration or review window

If the system cannot explain why it needs approval, it should not ask for blind
approval.

## Human Approval Stub

PiGenus already has a human approval stub:

- pending
- approved
- rejected

That is enough for v0.3. Future work should extend the semantics before adding
a rich UI.

The correct order is:

```text
approval records -> approval inspection -> approval policy -> approval UI
```

## Relationship To Workers

Workers increase execution power. Human Governance should be able to require
approval for:

- first activation of a worker
- external provider usage
- network-enabled execution
- high-cost execution
- privacy-sensitive execution
- failed heartbeat recovery

## Relationship To Resource Economy

Some resource changes should require approval:

- increasing money limits
- increasing privacy budget
- granting high-risk room resources
- overriding quotas
- assigning expensive workers

The system should never silently raise its own budget.

## Relationship To Liquid Runtime

Liquid Runtime should produce proposals and previews before execution.

Human Governance decides when a proposed runtime shape must wait for human
approval before becoming real.

## Relationship To Evolution

Evolution requires the strictest human governance.

Mutation proposals should remain in shadow mode until explicitly approved.
Activation requires trace, test comparison, rollback plan, and fossil record.

## Non-Goals

Human Governance is not:

- a cosmetic confirmation popup
- a way to bypass guard rules
- a replacement for audit logs
- blanket permission for future actions
- self-approval by the requesting agent

## First Safe Implementation Shape

When implemented, Human Governance should start with inspection:

```text
approval-list
approval-show
approval status filters
approval decision references
```

Only after approval inspection is boring should approve/reject commands or UI
be added.

## Relationship To v0.3

v0.3 has the minimal approval record foundation.

Human Governance comes later to define policy semantics, authority, evidence,
and inspection before any broad approval UI exists.
