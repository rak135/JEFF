## 2026-04-12 17:47 â€” Fixed repair-branch schema-incomplete debug surfacing

- Scope: research repair-branch debug truthfulness at the shared schema-completeness boundary
- Done:
  - normalized blank/invalid root-field gate failures into `ResearchSynthesisValidationError` inside the shared progression helper
  - ensured schema-incomplete repair payloads emit `repair_pass_failed` with `failure_class=schema_incomplete`
  - added deterministic coverage for blank-summary repair output and live CLI debug surfacing
- Validation: targeted repair/debug tests passed; full `pytest -q` passed
- Current state: schema-incomplete repair output now shows a truthful repair failure checkpoint with bounded reason before the final fail-closed error
- Next step: continue only small truthfulness fixes where live debug and final failure still diverge
- Files:
  - jeff/cognitive/research/synthesis.py
  - tests/unit/cognitive/test_research_synthesis_repair_pass.py
  - tests/integration/test_cli_research_debug_stream.py
