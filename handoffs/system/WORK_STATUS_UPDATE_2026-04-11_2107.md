## 2026-04-11 21:07 - Refactored cognitive research into submodule package

- Scope: cognitive research module structure and ownership cleanup
- Done:
  - replaced the flat `jeff/cognitive/research.py` and `research_documents.py` files with a dedicated `jeff/cognitive/research/` package
  - split research contracts, synthesis behavior, document acquisition, errors, and legacy compatibility into bounded files
  - preserved the existing public research surface through package exports and updated `jeff.cognitive` re-exports
  - isolated the still-needed legacy `ResearchResult` contract into `research/legacy.py`
  - added a focused public-surface guard test and kept existing research tests green
- Validation: targeted research refactor tests passed and full `python -m pytest -q` passed with 199 tests
- Current state: research now has a cleaner package structure with stable behavior and clearer ownership boundaries
- Next step: keep future research work inside the new package slices without reintroducing blob modules or leaking provider logic
- Files:
  - jeff/cognitive/research/__init__.py
  - jeff/cognitive/research/contracts.py
  - jeff/cognitive/research/synthesis.py
  - jeff/cognitive/research/documents.py
  - jeff/cognitive/research/legacy.py
