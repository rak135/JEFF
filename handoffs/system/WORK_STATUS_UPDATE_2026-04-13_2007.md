## 2026-04-13 20:07 — Added Step 3 formatter fallback bridge

- Scope: `jeff.cognitive.research` Slice 4 formatter fallback wiring
- Done:
  - added `formatter.py` for Step 3 formatter request building and hard output validation
  - added `fallback_policy.py` for explicit formatter eligibility after deterministic-transform failure
  - wired formatter fallback into live synthesis after Step 2 failure while keeping downstream remap/provenance unchanged
  - updated debug checkpoints and focused unit/integration tests for truthful formatter fallback behavior
- Validation: passed `pytest tests/unit/cognitive/test_research_bounded_syntax.py tests/unit/cognitive/test_research_deterministic_transformer.py tests/unit/cognitive/test_research_synthesis.py tests/unit/cognitive/test_research_synthesis_citation_keys.py tests/unit/cognitive/test_research_synthesis_runtime_errors.py tests/unit/cognitive/test_research_synthesis_repair_pass.py tests/unit/cognitive/test_research_public_surface.py tests/unit/interface/test_research_debug_mode.py tests/integration/test_research_synthesis_with_runtime.py tests/integration/test_research_synthesis_repair_flow.py tests/integration/test_cli_research_debug_stream.py`
- Current state: research now runs Step 1, Step 2, and Step 3 fallback with the existing `research_repair` runtime purpose used explicitly as a temporary formatter bridge
- Next step: clean up temporary repair naming and compatibility surfaces after the formatter bridge is stable
- Files:
  - jeff/cognitive/research/formatter.py
  - jeff/cognitive/research/fallback_policy.py
  - jeff/cognitive/research/synthesis.py
  - tests/integration/test_research_synthesis_repair_flow.py
