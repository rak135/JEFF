# Module Name

- `jeff.action`

# Module Purpose

- Own execution and outcome reporting for governed actions.

# Current Role in Jeff

- Accepts governed execution requests, records execution results, and normalizes observed outcomes for downstream evaluation.
- Intentionally stays narrow after the evaluation move to Cognitive.

# Boundaries / Non-Ownership

- Does not own action formation from proposal/selection/planning.
- Does not own policy, approval, readiness, evaluation, memory authorship, or canonical truth mutation.
- Does not let execution side effects become truth automatically.

# Owned Files / Areas

- `jeff/action/execution.py`
- `jeff/action/outcome.py`
- `jeff/action/types.py`

# Dependencies In / Out

- In: consumes governed action-entry results and bounded `Action` contracts.
- Out: passes execution results and normalized outcomes to Cognitive evaluation, Memory, and Orchestrator handoffs.

# Canonical Docs to Read First

- `v1_doc/ARCHITECTURE.md`
- `v1_doc/EXECUTION_OUTCOME_EVALUATION_SPEC.md`

# Current Implementation Reality

- The module now exposes execution and outcome only.
- Evaluation is no longer implemented here.
- The current repo does not implement a broad apply/rollback/change-control subsystem; Action remains a bounded v1 layer.

# Important Invariants

- Governance must allow start before execution begins.
- Execution, outcome, and evaluation remain distinct.
- Execution completion does not imply objective completion.
- Outcome is not canonical truth.

# Active Risks / Unresolved Issues

- This layer is intentionally thin; future work must not turn it into a catch-all for governance, workflow, or hidden transition logic.
- Real-world mutation support flows remain deferred beyond the current baseline.

# Next Continuation Steps

- Keep any Action follow-up bounded to execution/outcome contracts and guard against evaluation or governance drift back into this package.

# Submodule Map

- `execution.py`: governed execution request and result contracts; no separate handoff.
- `outcome.py`: normalized observed result contract; no separate handoff.
- `types.py`: Action-layer literal families and support types; no separate handoff.

# Related Handoffs

- `handoffs/system/REPO_HANDOFF.md`
- `jeff/governance/HANDOFF.md`
- `jeff/cognitive/HANDOFF.md`
- `jeff/orchestrator/HANDOFF.md`
