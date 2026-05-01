# Contributing To PiGenus

PiGenus is a private persistent orchestration and memory node for GENUS. Every change must preserve that role.

Before changing code, read:

- [PiGenus Charter](docs/PIGENUS_CHARTER.md)
- [Architecture](docs/ARCHITECTURE.md)
- [MVP Roadmap](docs/MVP_ROADMAP.md)
- [Roadmap Guardrails](docs/ROADMAP_GUARDRAILS.md)

## Required Change Discipline

Every non-trivial change must answer:

- Which charter function does this strengthen: persistence, orchestration, administration, interface readiness, or continuity?
- Which roadmap phase does this belong to?
- Does it keep PiGenus low-resource and Raspberry-Pi-suitable?
- Does it avoid turning PiGenus into a main LLM host, GPU service, or frontend-only project?
- Does it preserve security defaults and recoverability?
- Are tests or docs updated?

## Local Verification

Run:

```bash
pigenus-guardrails
pytest
```

For operational changes, also run a local smoke test or update [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Dependency Policy

Runtime dependencies must stay small and justified. Heavy ML, GPU, model-serving, or vector-database dependencies do not belong in PiGenus core unless there is an explicit architecture decision and roadmap update.

Workers may integrate heavier tools later, but PiGenus core remains the reliable private coordination layer.
