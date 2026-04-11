# Module Name

- `jeff.core`

# Module Purpose

- Own canonical truth, foundational containers, and the only lawful mutation path.

# Current Role in Jeff

- Provides shared IDs and scope schemas, global/project/work-unit/run state models, and transition validation/commit.
- Acts as the source of current truth for every downstream layer.

# Boundaries / Non-Ownership

- Does not own proposal, selection, planning, approval, readiness, execution, evaluation, memory authorship, or interface semantics.
- Does not accept canonical mutation outside transition logic.

# Owned Files / Areas

- `jeff/core/schemas/`
- `jeff/core/state/`
- `jeff/core/containers/`
- `jeff/core/transition/`

# Dependencies In / Out

- In: none from semantic peer layers; Core stays at the bottom of the semantic stack.
- Out: read surfaces feed Governance, Cognitive, Memory, Orchestrator, and interface projections; transition results update canonical state for the whole repo.

# Canonical Docs to Read First

- `v1_doc/ARCHITECTURE.md`
- `v1_doc/CORE_SCHEMAS_SPEC.md`
- `v1_doc/STATE_MODEL_SPEC.md`
- `v1_doc/TRANSITION_MODEL_SPEC.md`
- `v1_doc/PROJECT_AND_WORK_UNIT_MODEL_SPEC.md`

# Current Implementation Reality

- Global state is in-memory and contains nested projects, work units, and runs.
- Transition handling currently covers the implemented create flows and fail-closed validation.
- The repo relies on Core invariants heavily in anti-drift and acceptance tests.

# Important Invariants

- There is one global canonical state with nested projects.
- Project is the hard isolation boundary inside canonical truth.
- A run belongs to exactly one work unit and one project.
- Only transitions mutate canonical truth.
- Canonical state may reference only committed memory IDs.

# Active Risks / Unresolved Issues

- Runtime storage is still in-memory only.
- Any convenience path that mutates truth outside transition logic would be an architectural break, especially from interface or orchestrator code.

# Next Continuation Steps

- Keep strengthening transition and state invariants when new bounded v1 work touches truth mutation or scope handling.

# Submodule Map

- `schemas/`: shared ID, scope, and envelope primitives; no separate handoff.
- `state/`: canonical truth topology and bootstrap helpers; no separate handoff.
- `containers/`: project/work-unit/run container models; no separate handoff.
- `transition/`: validation and commit path for canonical mutation; no separate handoff.

# Related Handoffs

- `handoffs/system/REPO_HANDOFF.md`
- `jeff/governance/HANDOFF.md`
- `jeff/memory/HANDOFF.md`
- `jeff/orchestrator/HANDOFF.md`
