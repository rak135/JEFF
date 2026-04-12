## 2026-04-12 17:33 â€” Unified research schema-completeness boundary

- Scope: research synthesis and repair success-boundary truthfulness
- Done:
  - replaced the repair-only root-shape check with one shared schema-completeness gate for progression
  - made primary synthesis emit `primary_synthesis_failed` instead of false success for schema-incomplete JSON
  - kept repair pass fail-closed and made `repair_pass_succeeded` depend on the same shared gate
  - added unit and integration coverage to ensure schema-incomplete payloads stop before citation remap and debug output stays truthful
- Validation: targeted synthesis-boundary tests passed; full `pytest -q` passed
- Current state: both primary and repair branches now require schema-complete research payloads before success is reported or citation remap begins
- Next step: continue tightening only misleading success boundaries while preserving existing research semantics and downstream validation
- Files:
  - jeff/cognitive/research/synthesis.py
  - tests/unit/cognitive/test_research_synthesis.py
  - tests/unit/cognitive/test_research_synthesis_runtime_errors.py
  - tests/integration/test_research_synthesis_repair_flow.py
