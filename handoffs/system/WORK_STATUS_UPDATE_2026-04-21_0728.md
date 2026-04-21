## 2026-04-21 07:28 - Scope-keyed persistence migration completed

- Scope completed: `flow_runs` and `selection_reviews` now persist by full scope identity and load into scope-keyed runtime maps.
- Storage shape chosen: nested scoped paths under `.jeff_runtime/flows/flow_runs/{project_id}/{work_unit_id}/{run_id}.json` and `.jeff_runtime/reviews/selection_reviews/{project_id}/{work_unit_id}/{run_id}.json`.
- In-memory key chosen: `project_id::work_unit_id::run_id`.
- Compatibility kept: legacy flat bare-`run_id` files still load; scoped files take precedence when both exist.
- Trust result: disk overwrite risk fixed, in-memory collapse risk fixed, explicit-scope readback verified, fail-closed behavior preserved.
- Automated validation: `pytest -q tests/smoke/test_bootstrap_smoke.py tests/unit/interface/test_cli_run_resolution.py tests/unit/interface/test_cli_selection_review.py tests/integration/test_runtime_workspace_persistence.py tests/integration/test_cli_planning_operator_surface.py tests/acceptance/test_acceptance_scope_isolation.py tests/antidrift/test_selection_override_truth_boundaries.py tests/integration/test_cli_run_live_context_execution.py` -> `67 passed in 26.80s`.
- Live runtime checks:
  - current workspace CLI booted cleanly
  - `/show run-10`, `/selection show run-10`, and `/inspect` worked against real persisted runtime data in `project-1/wu-1`
  - `/plan show run-10` failed truthfully because no plan artifact exists for that run
  - isolated duplicate-scope CLI checks showed `proposal-1` in `project-1/wu-1`, `proposal-2` in `project-2/wu-2`, and fail-closed `no orchestrator flow result is available for run run-1` when support was absent in the requested scope
- Primary report written: `SCOPE_KEYED_PERSISTENCE_MIGRATION_REPORT.md`
- Next best slice: add a bounded legacy-runtime hygiene surface that reports remaining flat legacy support files.