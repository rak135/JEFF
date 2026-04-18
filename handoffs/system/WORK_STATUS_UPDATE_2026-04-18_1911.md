## 2026-04-18 19:11 - Removed root-level ad hoc test runners

- Scope: repo-root test helper cleanup
- Done:
  - removed unreferenced root-level pytest wrapper scripts
  - removed the root-level one-off research example runner
  - removed the root-level direct debug script for Step 1 research checks
- Validation: `python -m pytest -q tests/unit/cognitive/test_research_synthesis.py tests/unit/cognitive/test_research_bounded_syntax.py tests/unit/cognitive/test_research_deterministic_transformer.py` passed (`30 passed`)
- Current state: documented pytest workflow still uses `tests/` directly and repo root no longer contains misleading test-like scripts
- Next step: keep future test automation inside `tests/` and keep ad hoc probes out of repo root
- Files:
  - run_baseline_tests.py
  - run_full_tests.py
  - run_research_example.py
  - run_tests.py
  - test_runner.py
  - test_step1_improvements.py
