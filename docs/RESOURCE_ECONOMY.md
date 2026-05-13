# Resource Economy

Resource Economy is a future GENUS architecture track. It is not part of the
v0.3 governed runtime implementation.

The purpose of Resource Economy is not to create an internal market first. Its
first purpose is accounting: make resource use explicit before optimization,
pricing, or negotiation.

Core rule:

```text
No scaling without accountability.
```

## Why This Exists

GENUS cannot safely add workers, agents, liquid runtime shapes, federation, or
evolution without knowing what they consume.

Resources include more than CPU and memory. A governed runtime may need to
track:

- compute
- memory
- storage
- time
- attention
- money
- network
- privacy budget
- risk budget
- human review capacity

If these are implicit, future orchestration will be hard to debug and easy to
abuse.

## ResourceGrant

PiGenus already has a `ResourceGrant` model. It represents an explicit budget
assigned to an actor in a room.

That model is the correct starting point:

```text
actor_id
room_id
limits
granted_by
expires_at
```

Future Resource Economy should extend this idea carefully rather than replacing
it with broad market mechanics.

## Budgets Before Markets

GENUS should not start with auctions, prices, internal credits, or competitive
resource markets.

The safer order is:

```text
limits -> grants -> usage records -> summaries -> quotas -> cost profiles -> optimization
```

Only after accounting is reliable should any market-like behavior be
considered.

## Room-Scoped Resources

Resource policy should be room-aware.

Examples:

- `room_developer` may allow local experimentation with low risk.
- `room_private` may require strict privacy budgets.
- `room_trading` may require explicit money and risk limits.
- `room_family` may require stricter human review.

Resources should not float globally without room context.

## Worker Relationship

Workers provide execution capacity, but they should not spend resources freely.

Worker selection must respect:

- actor contract
- room policy
- context stack
- worker capability
- worker cost profile
- resource grant
- guard decision

This prevents a powerful worker from becoming an uncontrolled execution path.

## Meaning And Attention

Resource Economy should eventually treat attention as a resource.

Meaning objects, memories, decisions, and audit records may compete for review,
retrieval, summarization, or human attention. The system should be able to
explain why one item was surfaced and another was not.

This should begin as reporting, not optimization.

## First Safe Implementation Shape

When implemented, Resource Economy should start with read-only accounting:

```text
ResourceUsageRecord
resource-usage-list
resource-usage-summary
per-room usage totals
per-actor usage totals
```

It should not start with:

- dynamic pricing
- internal credits
- market allocation
- autonomous budget changes
- self-granted resources

## Guard Relationship

Resource checks belong in governance.

If a proposed action exceeds a resource grant, it should block or escalate
through the guard pipeline. Resource failures should be visible in decision
families and summaries.

## Non-Goals

Resource Economy is not:

- a cryptocurrency
- an internal stock market
- permission to maximize utilization
- a replacement for human approval
- a way to bypass room policy

## Relationship To v0.3

v0.3 has the foundation:

- `ResourceGrant`
- contract validation
- guard decisions
- decision logging
- guard summaries
- room/context governance

Resource Economy comes later, after the system can report usage without
changing behavior. The first milestone should be visibility, not optimization.
