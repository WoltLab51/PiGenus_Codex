# Evolution Sandbox

Evolution Sandbox is a future GENUS architecture track. It is not part of the
v0.3 governed runtime implementation.

The purpose of Evolution Sandbox is to make adaptation possible without
allowing uncontrolled self-modification.

Core rule:

```text
Mutation is never activation.
```

## Why This Exists

GENUS may eventually need to improve cells, organs, policies, prompts,
retrieval strategies, resource use, or runtime shapes.

That pressure is real. It is also dangerous.

Without a sandbox, "evolution" becomes an excuse for:

- hidden behavior changes
- unreviewed policy drift
- capability escalation
- brittle optimizations
- loss of rollback
- unclear responsibility

Evolution must therefore begin as proposal, comparison, and trace. Not as
automatic replacement.

## Evolution Units

Evolution proposals may eventually target:

- cell configuration
- organ composition
- prompt or instruction templates
- retrieval strategy
- resource policy
- guard policy
- context stack defaults
- worker routing strategy
- liquid runtime shape proposal strategy

They should not target the core storage, audit, decision, or guard semantics
without a separate architecture decision.

## Proposal First

Every mutation begins as a proposal.

A mutation proposal should include:

- target object
- proposed change
- reason
- expected benefit
- expected risk
- affected rooms
- affected actors or agents
- required resources
- rollback plan
- evaluation plan
- creator
- created_at

The proposal is not active behavior.

## Shadow Mode

Mutations run in shadow mode first.

Shadow mode means:

- no production replacement
- no hidden policy change
- no automatic activation
- results are compared against the current baseline
- traces and metrics are recorded

The system may observe how a mutation would behave, but it must not silently
become the active path.

## Fitness Comparison

Fitness must be explicit and testable.

Possible fitness signals:

- test pass/fail
- guard decision quality
- output correctness
- resource cost
- latency
- audit completeness
- human approval outcome
- regression count
- safety violations

No single score should override safety constraints.

## Fossils And Rollback

Rejected, retired, or replaced variants should leave fossil records.

Fossils make it possible to answer:

- what changed?
- why was it tried?
- why was it rejected or replaced?
- what did it cost?
- how can it be restored if needed?

Rollback is not optional. Any activation plan must include a rollback path.

## Human Approval

Activation requires human governance.

The stricter rule:

```text
No mutation becomes active without explicit approval.
```

Approval should include the proposal, trace, comparison, risk, rollback plan,
and affected rooms.

## Guard Relationship

Evolution must pass through the existing governance model:

- room policy
- context stack compatibility
- contracts
- resource grants
- guard pipeline
- decision logging
- approval records

Evolution cannot bypass the kernel that makes runtime behavior accountable.

## Non-Goals

Evolution Sandbox is not:

- autonomous self-improvement
- live code rewriting
- hidden prompt mutation
- automatic policy drift
- permission escalation
- replacing tests with vibes
- optimizing away auditability

## First Safe Implementation Shape

When implemented, Evolution Sandbox should start as read-only proposal and
comparison:

```text
MutationProposal
mutation-proposal-list
mutation-proposal-show
shadow comparison records
fossil records
```

Activation should come later, after proposal inspection, comparison, approval,
and rollback semantics are boring.

## Relationship To v0.3

v0.3 provides the governed runtime baseline.

Evolution Sandbox comes later because the system must first know what it is,
what it is allowed to do, what it changed, and how to undo it.

The correct order is:

```text
governed runtime -> proposal -> shadow comparison -> approval -> activation -> fossil/rollback
```
