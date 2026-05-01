# PiGenus Roadmap Guardrails

This document explains how to keep repository work aligned with the PiGenus charter and roadmap.

## Binding Order

When there is uncertainty, use this order:

1. [PiGenus Charter](PIGENUS_CHARTER.md)
2. [Architecture](ARCHITECTURE.md)
3. [MVP Roadmap](MVP_ROADMAP.md)
4. Current issue or implementation request

If a requested change conflicts with the charter, update the request or reject the change. Do not bend PiGenus into a different product.

## Allowed Direction

PiGenus work should improve at least one of these:

- Persistence
- Orchestration
- Administration
- Interface readiness
- Continuity

Good examples:

- Better backups and restore flows
- Safer worker registration
- Clearer audit logs
- More reliable job lifecycle handling
- Deployment and recovery tooling
- Memory/session APIs
- Worker coordination protocols

## Scope Warnings

Pause and re-check the roadmap before adding:

- Heavy LLM/model runtime dependencies
- GPU or accelerator requirements
- A frontend that becomes the product instead of an admin surface
- Microservice splits without operational need
- Self-modifying behavior
- Public-internet exposure assumptions
- Unbounded background automation without audit or human oversight

## Roadmap Update Rule

When a change completes, starts, or materially changes a roadmap item, update [MVP_ROADMAP.md](MVP_ROADMAP.md) in the same change.

When a change creates a new architectural direction, update [ARCHITECTURE.md](ARCHITECTURE.md) or add an ADR.

When a change affects deployment, update [DEPLOYMENT.md](DEPLOYMENT.md).

## Guardrail Check

Run:

```bash
pigenus-guardrails
```

The guardrail check verifies that the core project files still reference the charter/roadmap, that required roadmap phases exist, and that runtime dependencies do not include banned heavy compute/model-serving packages.
