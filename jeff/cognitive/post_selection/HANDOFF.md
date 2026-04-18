# Module Name

- `jeff.cognitive.post_selection`

# Module Purpose

- Own the downstream bridge after Selection without taking over Selection semantics, Governance semantics, execution, or outcome ownership.

# Current Role in Jeff

- Groups the bounded post-Selection bridge into one dedicated package.
- Carries the deterministic bridge objects and transformations from `SelectionResult` plus optional override through resolved basis, materialized effective proposal, formed `Action`, and governance handoff.

# Boundaries / Non-Ownership

- Does not own Selection semantics, Selection-local decision behavior, or proposal generation.
- Does not own Governance semantics, approval policy, or governance decision rules.
- Does not own execution, outcome normalization, truth mutation, or interface rendering semantics.
- Does not imply permission, readiness, approval, or execution authority.

# Owned Files / Areas

- `jeff/cognitive/post_selection/__init__.py`
- `jeff/cognitive/post_selection/override.py`
- `jeff/cognitive/post_selection/action_resolution.py`
- `jeff/cognitive/post_selection/effective_proposal.py`
- `jeff/cognitive/post_selection/action_formation.py`
- `jeff/cognitive/post_selection/governance_handoff.py`
- `jeff/cognitive/post_selection/HANDOFF.md`

# Current Implementation Reality

- This package was extracted from the flat `jeff/cognitive/` layout for package hygiene and clearer ownership.
- The bridge remains deterministic and structural: Selection output stays separate from override choice, resolved basis, effective proposal materialization, Action formation, and governance handoff.
- The package preserves the existing downstream layering exactly; it does not redesign orchestrator, governance, or execution behavior.

# Important Invariants

- The package starts from `SelectionResult` and optional operator override; it does not redefine Selection truth.
- Resolved basis stays separate from effective proposal materialization.
- Effective proposal materialization stays separate from Action formation.
- Governance handoff stays separate from governance policy semantics and from execution.
- No bridge step implies approval or execution start.

# Next Continuation Steps

- Keep future downstream-bridge slices inside this package instead of recreating flat `jeff/cognitive/` modules.
- Preserve the separation between Selection semantics, bridge transformations, governance semantics, and execution semantics.

# Related Handoffs

- `jeff/cognitive/HANDOFF.md`
- `jeff/cognitive/selection/HANDOFF.md`
- `jeff/governance/HANDOFF.md`
- `jeff/action/HANDOFF.md`
- `jeff/interface/HANDOFF.md`
- `handoffs/system/REPO_HANDOFF.md`
