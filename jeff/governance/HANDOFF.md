# Module Name

- `jeff.governance`

# Module Purpose

- Own permission and action-entry law for bounded actions.

# Current Role in Jeff

- Evaluates whether a bounded action may start now through policy, approval, readiness, and current-truth checks.
- Produces explicit allow, block, defer, escalate, or approval-required results for downstream execution entry.

# Boundaries / Non-Ownership

- Does not own canonical truth, proposal generation, selection, execution side effects, outcome normalization, evaluation, memory, or transition commit.
- Does not let selection or planning imply permission.

# Owned Files / Areas

- `jeff/governance/policy.py`
- `jeff/governance/approval.py`
- `jeff/governance/readiness.py`
- `jeff/governance/action_entry.py`

# Dependencies In / Out

- In: reads current scope/state facts from Core and consumes bounded `Action` contracts.
- Out: passes explicit action-entry decisions to Action and Orchestrator.

# Canonical Docs to Read First

- `v1_doc/ARCHITECTURE.md`
- `v1_doc/POLICY_AND_APPROVAL_SPEC.md`
- `v1_doc/EXECUTION_OUTCOME_EVALUATION_SPEC.md`

# Current Implementation Reality

- The implementation is intentionally narrow and fail-closed.
- Approval, readiness, and action-entry remain distinct in both models and operator-facing views.
- Freshness/revalidation logic is present only to the degree currently implemented in the v1 backbone; this is not a broad policy engine.

# Important Invariants

- Selection does not imply permission.
- Approval does not imply apply.
- Approval and readiness remain distinct.
- Governance decides whether action may start; execution does not bypass that boundary.

# Active Risks / Unresolved Issues

- Any future convenience shortcut from selection or CLI commands straight into execution would break this layer.
- Governance remains intentionally compact; future work must not flatten its distinct verdicts into generic status reporting.

# Next Continuation Steps

- If follow-up work touches action start conditions, extend tests here first so permission and readiness boundaries stay explicit.

# Submodule Map

- `policy.py`: policy posture and gating inputs; no separate handoff.
- `approval.py`: approval contract; no separate handoff.
- `readiness.py`: readiness contract; no separate handoff.
- `action_entry.py`: start-time evaluation and decision contract; no separate handoff.

# Related Handoffs

- `handoffs/system/REPO_HANDOFF.md`
- `jeff/cognitive/HANDOFF.md`
- `jeff/action/HANDOFF.md`
- `jeff/orchestrator/HANDOFF.md`
