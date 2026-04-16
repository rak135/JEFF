# WORK_STATUS_UPDATE_compacted

Last updated: 2026-04-16  
Primary sources:
- [WORK_STATUS_UPDATE.md](C:/DATA/PROJECTS/JEFF/handoffs/system/WORK_STATUS_UPDATE.md)
- [FULL_REPO_REVIEW.md](C:/DATA/PROJECTS/JEFF/FULL_REPO_REVIEW.md)

## Purpose

This file is the compact current-status snapshot for the Jeff project.  
Use it as the first project-status read before diving into the rolling history in `WORK_STATUS_UPDATE.md`.

## Project Snapshot

- Jeff is currently a CLI-first, in-memory v1 backbone with a clean layered structure.
- The canonical backbone exists end to end: core state -> transitions -> governance -> cognitive stages -> orchestrator -> interface.
- The research vertical is the most mature part of the system and is the only cognitive stage currently using a real model adapter/runtime path.
- Research now runs through the live 3-step bounded-text pipeline:
  - Step 1: bounded text generation
  - Step 2: deterministic transform
  - Step 3: formatter fallback after Step 2 failure only
- Infrastructure now includes:
  - model adapter abstractions and providers
  - runtime assembly and config
  - vocabulary modules (`purposes`, `output_strategies`, `capability_profiles`)
  - `ContractRuntime`
- Proposal, selection, planning, evaluation, governance, action, memory, and orchestrator are implemented and tested, but outside research they remain deterministic/rule-based rather than model-backed.

## What Is Implemented Now

### Backbone

- Immutable global state and transition-controlled truth updates are in place.
- Canonical containers (`project`, `work_unit`, `run`) exist and are validated.
- Governance boundaries are explicit: policy, approval, readiness, and action-entry are separate concepts.
- Orchestrator sequencing, routing, validation, lifecycle, and trace exist as deterministic code.
- The CLI is the only operator surface and stays thin and truthful.

### Research

- Document and web research acquisition paths exist.
- Research artifacts persist as JSON support records.
- Research-to-memory handoff exists.
- Debug checkpoints are available through `/mode debug`.
- Citation remap, provenance validation, and fail-closed boundaries are strong.
- The 3-step transition is complete and active in production code.

### Infrastructure

- Fake and Ollama adapters exist.
- Runtime config and purpose-based adapter routing exist.
- `ContractRuntime` is present and research has adopted it for Step 1 and the formatter bridge runtime path.

## Current Reality And Limits

- Truth is still in-memory only. `GlobalState` is not persisted across restarts.
- Memory storage is still in-memory only.
- The orchestrator is a tested staged runner, not a live runtime loop or background service.
- No non-research cognitive stage currently uses a model adapter.
- Transition support is still narrow: only `create_project`, `create_work_unit`, and `create_run` are implemented.
- Web acquisition is intentionally basic and not yet a robust search/retrieval layer.
- The CLI is command-driven and practical, but it is not a broad API or GUI surface.

## Known Issues And Active Debt

- Full suite status from the 2026-04-15 review: `378 passed / 10 failed`.
- The 10 failing tests are known pre-existing failures caused by outdated fake-adapter fixtures that still assume the old JSON-first synthesis contract.
- Research artifact persistence currently uses a doubled path on disk:
  - configured root: `.jeff_runtime/research_artifacts`
  - effective write path: `.jeff_runtime/research_artifacts/research_artifacts`
- `ContractCallRequest` is still too thin for the clean `invoke()` path because it does not yet carry the full fields needed for JSON mode and reasoning configuration.
- The formatter bridge still uses the temporary infrastructure-facing name `research_repair`.
- `jeff/infrastructure/HANDOFF.md` is stale and does not reflect the newer vocabulary modules or `ContractRuntime`.
- Some compatibility surfaces remain intentionally in place:
  - `jeff/cognitive/research/legacy.py`
  - `invoke_with_request()` for full `ModelRequest` control

## Recommended Next Slice

The recommended next slice is a narrow infrastructure-hardening pass before any Proposal/Evaluation model adoption.

1. Expand `ContractCallRequest` to carry `response_mode`, `json_schema`, and `reasoning_effort`.
2. Move research Step 1 to the clean `ContractRuntime.invoke()` path.
3. Retire `research_repair` naming in infrastructure and use neutral formatter-bridge vocabulary.
4. Fix the doubled artifact-store path.
5. Rewrite the 10 outdated tests to emit valid Step 1 bounded text.
6. Refresh `jeff/infrastructure/HANDOFF.md`.

After that, the next major phase should be Proposal adoption of `ContractRuntime`, then Evaluation adoption.

## Explicitly Not Recommended Next

- Do not start broad orchestrator-runtime-loop work yet.
- Do not start global-state persistence until the needed transition vocabulary is clearer.
- Do not add new model providers speculatively.
- Do not rewrite `commands.py` yet.
- Do not introduce Instructor, Guardrails, or BAML yet.

## Milestone Arc

- 2026-04-10: core backbone, governance, cognitive contracts, action/outcome/evaluation, memory, orchestrator skeleton, and CLI-first surface were established.
- 2026-04-11: startup/packaging, handoffs, test reorganization, CLI flow improvements, infrastructure adapter/runtime foundations, and initial research runtime slices landed.
- 2026-04-12: research robustness improved across provenance, transparency, error surfacing, repair handling, debug checkpoints, and Ollama structured JSON requests.
- 2026-04-13: the 3-step bounded-text research transition was completed and made the live primary path.
- 2026-04-15: infrastructure vocabulary modules and `ContractRuntime` landed, and research adopted the runtime path.

## Practical Reading Order

1. Read this file for the current status.
2. Read [REPO_HANDOFF.md](C:/DATA/PROJECTS/JEFF/handoffs/system/REPO_HANDOFF.md) for startup and repo orientation.
3. Read the nearest module handoff for the area being changed.
4. Use [WORK_STATUS_UPDATE.md](C:/DATA/PROJECTS/JEFF/handoffs/system/WORK_STATUS_UPDATE.md) only when you need detailed implementation history.
