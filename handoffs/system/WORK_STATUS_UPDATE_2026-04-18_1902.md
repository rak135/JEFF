## 2026-04-18 19:02 â€” Added persisted runtime workspace slice

- Scope: startup/runtime persistence and support-record reload
- Done:
  - added `.jeff_runtime/` runtime-home management and JSON persistence for canonical state, transitions, flow runs, and selection reviews
  - changed startup to load persisted runtime state by default and initialize the first runtime state lawfully when missing
  - moved research artifact writes to `.jeff_runtime/artifacts/research/` with legacy read compatibility for `.jeff_runtime/research_artifacts/`
  - kept CLI session scope local-only while wiring lawful transition persistence through existing command paths
- Validation: targeted pytest suites passed for runtime persistence, bootstrap/runtime config, CLI startup smoke, interface selection flows, and research persistence
- Current state: Jeff now reuses persisted runtime truth and persisted support records across restarts without adding a second truth layer or a database
- Next step: extend persisted runtime support as new orchestrator flows or review objects become operator-visible
- Files:
  - jeff/runtime_persistence.py
  - jeff/bootstrap.py
  - jeff/interface/commands.py
  - jeff/cognitive/research/persistence.py
  - tests/integration/test_runtime_workspace_persistence.py
