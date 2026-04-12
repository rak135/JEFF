## 2026-04-11 23:04 - Added explicit runtime config and startup wiring for research CLI

- Scope: infrastructure runtime config and startup composition
- Done:
  - added typed `jeff.runtime.toml` config loading with explicit runtime, adapter, purpose override, and research sections
  - extended infrastructure runtime assembly with purpose-based adapter lookup and config-to-adapter construction
  - wired startup to load local runtime config when present and attach research runtime dependencies into the CLI context
  - added deterministic tests for config parsing, bootstrap behavior, CLI research runtime flow, and Ollama context-length mapping
- Validation: `python -m pytest -q tests\unit\infrastructure\test_runtime_config.py tests\integration\test_bootstrap_runtime_config.py tests\integration\test_cli_research_runtime_config.py` passed; full `python -m pytest -q` passed with 256 tests
- Current state: Jeff startup can now remain demo-safe without config and becomes research-runnable through explicit local runtime config when `jeff.runtime.toml` is present
- Next step: keep future runtime work bounded to explicit config evolution and downstream stage integration without adding CLI-owned model switching
- Files:
  - jeff/infrastructure/config.py
  - jeff/infrastructure/runtime.py
  - jeff/infrastructure/model_adapters/factory.py
  - jeff/infrastructure/model_adapters/providers/ollama.py
  - jeff/bootstrap.py
  - tests/unit/infrastructure/test_runtime_config.py
  - tests/integration/test_bootstrap_runtime_config.py
  - tests/integration/test_cli_research_runtime_config.py
