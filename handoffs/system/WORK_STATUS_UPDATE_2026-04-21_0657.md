## 2026-04-21 06:57 — Closed operator trust hardening slice

- Scope: proposal scope hardening, persisted support review, and missing operator-trust artifacts
- Done:
  - added `tests/acceptance/test_acceptance_proposal_scope_hardening.py` to reproduce the historical cross-scope proposal drift shape using the persisted runtime store
  - verified explicit-scope proposal readback resolves correctly and does not cross from one colliding `run-1` scope into another
  - completed a bounded review of bare-`run_id` storage for `flow_runs` and `selection_reviews`
  - wrote `OPERATOR_TRUST_HARDENING_REPORT.md` with the acceptance-test result, filename review conclusion, tests, and live runtime evidence
- Validation: `python -m pytest ... -q` over the bounded hardening suite passed with `69 passed in 2.23s`; live runtime checks confirmed fail-closed wrong-scope proposal readback and visible research receipts
- Current state: the original proposal readback drift bug is fixed; `flow_runs` and `selection_reviews` still need a future scope-keyed storage migration because bare `run_id` filenames remain a collision risk
- Next step: migrate `flow_runs` and `selection_reviews` to scoped persistence keys with a backward-compatible loader
- Files:
  - `tests/acceptance/test_acceptance_proposal_scope_hardening.py`
  - `OPERATOR_TRUST_HARDENING_REPORT.md`
  - `jeff/interface/commands/proposal.py`
  - `jeff/interface/commands/support/flow_runs.py`
  - `jeff/interface/commands/support/selection_review_runtime.py`