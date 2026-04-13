## 2026-04-13 19:56 — Wired Step 1 and Step 2 into live research synthesis

- Scope: `jeff.cognitive.research` Slice 3 primary-path transition
- Done:
  - switched `research_synthesis` requests from JSON mode to bounded Step 1 text mode
  - wired live synthesis through syntax precheck and deterministic Step 2 transform before existing citation remap/provenance validation
  - updated research debug checkpoints to truthful content-generation and deterministic-transform labels
  - updated focused unit and runtime-integration tests for bounded-text-first synthesis and no live repair fallback
- Validation: passed `pytest tests/unit/cognitive/test_research_bounded_syntax.py tests/unit/cognitive/test_research_deterministic_transformer.py tests/unit/cognitive/test_research_synthesis.py tests/unit/cognitive/test_research_synthesis_citation_keys.py tests/unit/cognitive/test_research_synthesis_runtime_errors.py tests/unit/cognitive/test_research_synthesis_repair_pass.py tests/unit/cognitive/test_research_public_surface.py tests/unit/interface/test_research_debug_mode.py tests/integration/test_research_synthesis_with_runtime.py`
- Current state: live research synthesis now uses Step 1 bounded text and Step 2 deterministic transform while downstream remap/provenance behavior stays unchanged
- Next step: add Slice 4 formatter fallback without changing downstream remap/provenance semantics
- Files:
  - jeff/cognitive/research/synthesis.py
  - jeff/cognitive/research/debug.py
  - tests/unit/cognitive/test_research_synthesis.py
  - tests/unit/interface/test_research_debug_mode.py
