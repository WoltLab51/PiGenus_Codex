# GitHub Idea Harvest

This document captures ideas from older or parallel WoltLab51 GENUS/PiGenus
repositories without merging their architecture into the current governed
runtime.

## Core Rule

Harvest ideas, do not merge architectures.

An idea from another repository may become useful, but it does not enter the
current PiGenus runtime until it has:

- A source repository and evidence
- A target architecture track
- A compatibility check against the governed runtime
- A risk note
- A durable decision when it changes architecture
- Tests when it becomes implementation

This keeps old work valuable without letting it bypass the current Systemform,
meaning, room, guard, approval, and inspection layers.

## Initial Sources

### WoltLab51/Genus

Observed direction:

- Personal GENUS vision with assistant, family memory, DnD master, and project
  assistant surfaces
- Multi-agent product thinking
- DevLoop concepts such as planner, builder, tester, and reviewer
- Growth-system concepts such as need observation, orchestration, and bootstrap
- LLM routing and provider selection
- Memory, run journal, need store, and tool memory concepts
- API, frontend, security, and sandbox boundaries

Useful ideas:

- Character and identity surfaces belong in a later agent/character model
- Product surfaces should remain downstream of CLI and runtime semantics
- DevLoop is a candidate future operator workflow
- Need observation may inform Liquid Runtime proposals later
- LLM routing belongs behind a provider-neutral gateway, not inside the kernel

Risks:

- The repository is broad and product-shaped, so importing it directly would
  overload the governed runtime with agents, LLMs, UI, and proactivity too soon
- Family, DnD, and assistant use cases are valuable examples, not kernel
  requirements

Disposition:

- Harvest as vision and future surface inventory
- Do not merge implementation into v0.3

### WoltLab51/UrPi

Observed direction:

- Raspberry Pi 5 focused runtime stability
- Task and memory persistence
- Docker/module deployment thinking
- SQLite-first storage with optional Redis or Qdrant
- Health checks and deployment verification
- Module contract and roadmap documentation

Useful ideas:

- Local-first deployment discipline belongs in Operations and Continuity
- Pi-oriented health and startup checks are relevant before worker runtime
- Module contracts may inform future cell or worker packaging
- Optional external services should remain optional until the local core is
  boringly reliable

Risks:

- Deployment and module patterns may not match current Systemform governance
- Optional vector or service dependencies could arrive too early if copied
  wholesale

Disposition:

- Harvest stability, deploy verification, and operations discipline
- Do not import module architecture without a compatibility decision

### WoltLab51/PiGenus_mistral

Observed direction:

- Private infrastructure core
- Stability and maintainability over maximum performance
- Persistence, orchestration, administration, interfaces, and continuity as
  the five core functions
- Worker and job concepts
- JWT/admin surfaces
- REST worker client direction
- Systemd/APScheduler continuity
- Audit, backup, health, and metrics services

Useful ideas:

- Worker/job language is highly relevant to the future Worker Runtime arc
- Administration and health surfaces belong after operator inspection remains
  stable
- Continuity concepts may become an Operations and Continuity document
- Audit, backup, and health reinforce the current boring-reliability posture

Risks:

- Worker/job implementation must not bypass rooms, guards, approval, resource
  accounting, or decision logging
- Admin and REST surfaces should follow CLI/runtime semantics, not define them

Disposition:

- Harvest as the strongest input for v0.4 Worker Runtime and Operations
- Rebuild concepts against the current governed runtime instead of copying code

### WoltLab51/PiGenus_Core, WoltLab51/PiGenus_01, WoltLab51/PiGenus_kimi

Observed direction:

- Low currently visible documentation signal
- Possible placeholders, experiments, or early shells

Disposition:

- Keep on the source list
- Inspect only when a specific question points there

### WoltLab51/Monry

Observed direction:

- Archived repository

Disposition:

- Do not mine by default
- Inspect only if the user asks or a specific missing idea points there

## Harvest Categories

### Adopt As Principles Now

- Stability before performance
- Local continuity before federation
- Operator visibility before autonomy
- Long-term carrying capacity before short-term impressiveness
- Idea harvest before architecture merge

### Candidate Documentation Next

- `docs/OPERATIONS_CONTINUITY.md`
- `docs/AGENT_CHARACTER_MODEL.md`
- `docs/DEV_LOOP_MODEL.md`
- `docs/LLM_GATEWAY.md`

### Candidate Implementation Later

- Worker profile and heartbeat
- Job lease, acknowledgement, timeout, and retry semantics
- Systemd or service deployment checks
- Health and metrics inspection
- Admin surfaces after CLI semantics are stable

### Do Not Import Yet

- LLM router
- Autonomous growth system
- Assistant-specific behavior
- Family-specific behavior
- DnD-specific behavior
- Vector search
- Dashboard or frontend surface
- Remote worker execution

## Process

When harvesting from another repository:

1. Record the source repository.
2. Summarize the idea in current PiGenus vocabulary.
3. Assign it to an architecture track.
4. Mark it as adopt, later, reject, or needs decision.
5. State what must not be copied.
6. Add a durable decision if it changes the architecture.
7. Implement only after tests and compatibility boundaries are clear.

## Current Conclusion

The older repositories contain valuable memory of where GENUS wanted to go.
The current PiGenus repository remains the governed runtime line. Ideas may be
harvested into documents, decisions, and later work packages, but the runtime
keeps its current rule:

```text
No capability enters the system by nostalgia.
It enters by contract, guard, trace, and test.
```
