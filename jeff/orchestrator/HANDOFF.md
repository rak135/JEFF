# Module Name

- `jeff.orchestrator`

# Module Purpose

- Coordinate bounded stage sequencing across the existing semantic layers without owning their business logic.

# Current Role in Jeff

- Defines flow families and stage order, validates stage handoffs, routes blocked/defer/retry/escalate outcomes, and records lifecycle and trace events.

# Boundaries / Non-Ownership

- Does not own truth semantics, governance semantics, proposal logic, evaluation logic, memory rules, transition law, or interface semantics.
- Does not synthesize missing semantic outputs.

# Owned Files / Areas

- `jeff/orchestrator/flows.py`
- `jeff/orchestrator/validation.py`
- `jeff/orchestrator/routing.py`
- `jeff/orchestrator/runner.py`
- `jeff/orchestrator/lifecycle.py`
- `jeff/orchestrator/trace.py`

# Dependencies In / Out

- In: depends on public contracts from Core, Governance, Cognitive, Action, and Memory.
- Out: provides deterministic flow results and traceable lifecycle/output bundles to the interface layer.

# Canonical Docs to Read First

- `v1_doc/ARCHITECTURE.md`
- `v1_doc/ORCHESTRATOR_SPEC.md`
- `v1_doc/TESTS_PLAN.md`

# Current Implementation Reality

- The current orchestrator is deterministic and bounded.
- It validates stage order and semantic handoffs rather than generating business meaning itself.
- Acceptance and anti-drift tests already cover several cross-layer failure cases and truthfulness expectations.

# Important Invariants

- Orchestrator does not absorb business logic.
- Orchestrator does not synthesize missing outputs.
- Blocked or approval-gated flows stop honestly.
- Routing decisions stay distinct from semantic stage outputs.

# Active Risks / Unresolved Issues

- Richer workflow engines remain deferred.
- Autonomous continuation remains deferred.
- Any future convenience abstraction that hides stage boundaries or permissions inside the runner would be drift.

# Next Continuation Steps

- If future work extends flows, add handoff validation and acceptance coverage first so sequencing remains downstream of semantic owners.

# Submodule Map

- `flows.py`: flow families and stage ordering; no separate handoff.
- `validation.py`: handoff and stage-output validation; no separate handoff.
- `routing.py`: bounded follow-up routing; no separate handoff.
- `runner.py`: deterministic flow runner; no separate handoff.
- `lifecycle.py`: orchestration-local lifecycle state; no separate handoff.
- `trace.py`: compact ordered trace events; no separate handoff.

# Related Handoffs

- `handoffs/system/REPO_HANDOFF.md`
- `jeff/core/HANDOFF.md`
- `jeff/governance/HANDOFF.md`
- `jeff/cognitive/HANDOFF.md`
- `jeff/action/HANDOFF.md`
- `jeff/memory/HANDOFF.md`
- `jeff/interface/HANDOFF.md`
