# Module Name

- `jeff.cognitive`

# Module Purpose

- Own bounded reasoning inputs and outputs: context, research, proposal, selection, conditional planning, and evaluation.

# Current Role in Jeff

- Assembles truth-first context, produces bounded proposal sets, records honest selection results, plans only when needed, and evaluates outcomes after execution.
- Evaluation now physically and semantically lives in this layer.

# Boundaries / Non-Ownership

- Does not own canonical truth, policy semantics, approval, readiness, execution, outcome normalization, memory candidate creation, or transition commit.
- Does not let proposal, selection, or planning imply permission.

# Owned Files / Areas

- `jeff/cognitive/context.py`
- `jeff/cognitive/research.py`
- `jeff/cognitive/proposal.py`
- `jeff/cognitive/selection.py`
- `jeff/cognitive/planning.py`
- `jeff/cognitive/evaluation.py`
- `jeff/cognitive/types.py`

# Dependencies In / Out

- In: reads truth from Core first and may consume governance constraints or memory retrieval inputs where supported.
- Out: passes selected or plan-refined intent downstream as `Action` input and consumes Action outcomes for evaluation.

# Canonical Docs to Read First

- `v1_doc/ARCHITECTURE.md`
- `v1_doc/CONTEXT_SPEC.md`
- `v1_doc/PLANNING_AND_RESEARCH_SPEC.md`
- `v1_doc/PROPOSAL_AND_SELECTION_SPEC.md`
- `v1_doc/EXECUTION_OUTCOME_EVALUATION_SPEC.md`

# Current Implementation Reality

- Proposal remains bounded to 0..3 serious options.
- Planning is present but conditional rather than universal.
- Evaluation behavior stayed the same through the recent layer-alignment cleanup; only placement and imports changed.

# Important Invariants

- Context starts from current canonical truth before memory or artifacts.
- Proposal padding is forbidden.
- Selection does not imply permission.
- Evaluation remains distinct from outcome and transition.

# Active Risks / Unresolved Issues

- Research and planning are contract-level and bounded; they are not broad workflow or autonomy systems.
- Future work must keep evaluation in Cognitive and avoid drifting it back into Action or interface-specific labeling.

# Next Continuation Steps

- If this layer changes, preserve the truth-first read path and keep evaluation, selection, and planning boundaries locked with targeted tests.

# Submodule Map

- `context.py`: truth-first context assembly; no separate handoff.
- `research.py`: bounded research request/result contracts; no separate handoff.
- `proposal.py`: option generation contracts; no separate handoff.
- `selection.py`: bounded choice and non-selection results; no separate handoff.
- `planning.py`: conditional planning only; no separate handoff.
- `evaluation.py`: outcome judgment contracts; no separate handoff.

# Related Handoffs

- `handoffs/system/REPO_HANDOFF.md`
- `jeff/governance/HANDOFF.md`
- `jeff/action/HANDOFF.md`
- `jeff/memory/HANDOFF.md`
- `jeff/orchestrator/HANDOFF.md`
