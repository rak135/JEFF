## 2026-04-12 18:48 — Extended bounded repair to schema-incomplete primary JSON

- Scope: research synthesis repair trigger and shared schema-completeness boundary
- Done:
  - extended the single repair pass to run for primary `schema_incomplete` JSON as well as `malformed_output`
  - reused the existing repair request path by serializing near-miss primary JSON into the same repair prompt flow
  - tightened the shared progression validator to catch nested finding field/type mismatches before any false success checkpoint
  - updated unit and integration tests for repair triggering, debug sequencing, and unchanged malformed-output behavior
- Validation: `pytest -q` passed (`374 passed`)
- Current state: primary near-miss JSON now gets one bounded normalization repair attempt with truthful debug checkpoints and no extra retries
- Next step: move to the next smallest synthesis-boundary fix without widening research semantics
- Files:
  - jeff/cognitive/research/synthesis.py
  - tests/unit/cognitive/test_research_synthesis.py
  - tests/unit/cognitive/test_research_synthesis_repair_pass.py
  - tests/unit/cognitive/test_research_synthesis_runtime_errors.py
  - tests/integration/test_research_synthesis_repair_flow.py
  - tests/integration/test_cli_research_debug_stream.py
