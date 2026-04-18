## 2026-04-18 09:05 - Tightened CLI inspect and scope ergonomics

- Scope: interface operator surface
- Done:
  - added top-level one-shot scope flags and repeatable `--command` support in `python -m jeff`
  - made `/inspect`, `/show`, `/selection show`, and `/selection override` attach lawful selection-review data when available
  - expanded `/show` with bounded proposal and evaluation summaries and expanded `/selection show` with bounded proposal detail
  - attached a truthful demo selection-review chain so the normal startup path can use `/selection show` and `/selection override`
  - tightened help text and updated the interface handoff to match the current operator surface
- Validation: `python -m pytest -q tests/smoke/test_bootstrap_smoke.py tests/smoke/test_cli_entry_smoke.py tests/smoke/test_quickstart_paths.py tests/unit/interface/test_cli_scope_and_modes.py tests/unit/interface/test_cli_usability.py tests/unit/interface/test_cli_run_resolution.py tests/unit/interface/test_cli_json_views.py tests/unit/interface/test_cli_truthfulness.py tests/unit/interface/test_cli_selection_review.py tests/unit/interface/test_cli_selection_override.py tests/antidrift/test_selection_override_truth_boundaries.py tests/acceptance/test_acceptance_selection_override_chain.py` passed (`62 passed`)
- Current state: the CLI keeps the same bounded command vocabulary but is now more usable and informative on the normal demo path
- Next step: none for this bounded interface slice
- Files:
  - `jeff/main.py`
  - `jeff/interface/commands.py`
  - `jeff/interface/json_views.py`
  - `jeff/interface/render.py`
  - `jeff/bootstrap.py`
