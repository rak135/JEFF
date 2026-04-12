## 2026-04-12 18:25 — Wired Ollama structured JSON requests

- Scope: infrastructure Ollama adapter JSON-mode request path
- Done:
  - switched Ollama JSON-mode requests from `/api/generate` prompt text to `/api/chat` messages
  - wired `ModelRequest.json_schema` through to Ollama `format` for structured outputs
  - kept non-JSON requests on the existing generate path
  - added unit and integration assertions for outgoing JSON payload shape, endpoint, and absence of an explicit `think` flag
- Validation: `pytest -q` passed (`366 passed`)
- Current state: Ollama JSON-mode requests now send real structured-output fields on the wire and the repo tests prove the payload shape
- Next step: address the next synthesis-boundary fix without changing research semantics yet
- Files:
  - jeff/infrastructure/model_adapters/providers/ollama.py
  - tests/unit/infrastructure/test_ollama_model_adapter.py
  - tests/integration/test_cli_research_runtime_config.py
  - tests/integration/test_cli_research_synthesis_runtime_errors.py
