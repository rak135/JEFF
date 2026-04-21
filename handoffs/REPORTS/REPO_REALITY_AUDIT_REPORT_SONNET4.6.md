# JEFF Repo Reality Audit Report

**Audit date:** 2026-04-21  
**Audit method:** Direct repo inspection (structure, code, tests, docs) + synthesis of prior black-box validation evidence from `BLACK_BOX_OPERATOR_VALIDATION_REPORT.md`, `WORK_STATUS_REALITY_DIFF.md`, `INTERNAL_LAYER_STRENGTH_REPORT.md`, `v1_report.md`, `OPERATOR_TRUST_HARDENING_REPORT.md`, and `SCOPE_KEYED_PERSISTENCE_MIGRATION_REPORT.md`  
**Auditor stance:** Code and runtime evidence supersede docs. Partial = partial. Missing = missing.

---

## 1. Executive Verdict

### What is JEFF today, in reality?

JEFF is a **real, working, CLI-first persisted-runtime backbone** with genuine architectural discipline. It is not a spec exercise or a prototype shell. The core layers — state/transition, governance, orchestrator, CLI, research pipeline, and persisted runtime — are real in code, tested, and partially live-verified.

JEFF is **not** a finished operator product. The headline capability (`/run <objective>` → proposal → selection → execution → evaluation → truth transition) is architecturally complete but practically brittle at the LLM-dependent stages. Planning is implemented but practically unreachable. Approval continuations exist in code but have not been live-verified. Memory is real but ephemeral by default, and memory-backed proposal support is not yet operator-visible.

**Classification: Advanced prototype / partial backbone. Real where it matters most. Incomplete where it matters operationally.**

---

### What is solid?

- Core state/transition model: real, fail-closed, persisted
- Governance evaluation: real fail-closed layer, genuinely separate from execution
- Orchestrator sequencing: real, deterministic, auditable
- CLI inspection surface: genuinely usable (`/project`, `/work`, `/run list/use`, `/inspect`, `/show`, `/trace`, `/lifecycle`, `/scope`, `/selection show`, `/proposal show/raw/validate`, `/plan show/steps`)
- Research pipeline (docs + web): most operationally proven layer
- Persisted runtime under `.jeff_runtime`: real JSON persistence, scope-keyed (just hardened)
- Test suite: extensive, 950+ passing, structurally meaningful
- Repo discipline: unusually honest about its own gaps; no discovered fabricated capability claims

---

### What is fake, overstated, weak, or incomplete?

- **`/run <objective>` end-to-end**: works on the happy path, but proposal validation with real Ollama LLMs fails frequently. The bounded path is architecturally correct but operationally unreliable.
- **Planning reachability**: planning module is real in code; operators cannot reliably reach it from a standard `/run` flow. Multiple live attempts produced no `PlanArtifact`.
- **Approval-gated continuation**: code + unit/acceptance tests exist. Not live-verified. Operator cannot demonstrate this path.
- **Memory support in proposals**: memory write pipeline is real; memory reads back into proposal `input_bundle` are not surfacing in live runs.
- **Research-followup orchestration chain**: extensive code in `orchestrator/continuations/post_research.py` (~200 lines). Never exercised in live runtime via normal paths.
- **Transition vocabulary**: only `create_project`, `create_work_unit`, `create_run` — no update, archive, status-change, or richer operational lifecycle mutations.
- **Postgres memory backend**: complete in code, real schema + pgvector + FTS. No live DSN in standard setup; 28 tests permanently skipped.
- **Session scope vs runtime scope**: `--bootstrap-check` reports a "runtime project scope" while `/scope show` shows unset session scope — confusing to operators, never resolved.
- **Windows one-shot quoting**: still brittle enough to fail before Jeff sees the command.

---

### Top 5 truths the repo owner must accept right now

1. **The LLM stage is the weakest link.** The backbone is architecturally sound. The practical `operator → /run → result` flow is regularly broken by proposal validation failures with real models. This is the biggest gap between what the architecture promises and what operators experience.

2. **Planning is implemented but not operator-reachable.** A full planning module exists. In practice, selection escalates or defers before routing to planning, and operators cannot force a planning-held run through normal CLI paths. The feature appears functional but is blocked upstream.

3. **Memory writes are real; memory reads in proposals are not surfacing.** Memory handoff writes are persisted and visible in `/show`. But direct `/proposal` on those same runs still reports `memory_items=0`. Memory support is present as a pipeline construct but absent as a live operator experience.

4. **The scope-keyed persistence fix (April 21) resolved a real correctness bug.** Before that, `run-1` collisions across projects would silently cross-pollute proposal readback and flow-run support. This was a trust-destroying bug that is now fixed. But legacy flat files still exist on disk in live runtimes and can load if scoped files are absent.

5. **The repo is more honest than most, but the summary narrative still slightly underclaims the LLM reliability problem.** `WORK_STATUS_REALITY_DIFF.md` acknowledges it. But README and module handoffs describe the bounded `/run` path as working without flagging that proposal validation failure with real providers is the normal operator experience, not an edge case.

---

## 2. Repo Reality Summary

### What exists and is working

| Component | Status |
|---|---|
| `jeff/core/state` — immutable canonical `GlobalState` | Real |
| `jeff/core/transition/apply.py` — fail-closed transition apply | Real |
| `jeff/runtime_persistence.py` — JSON filesystem runtime persistence | Real |
| `jeff/governance/action_entry.py` — fail-closed governance evaluation | Real |
| `jeff/cognitive/research/` — 3-step synthesis pipeline, docs + web | Real (most operationally proven) |
| `jeff/cognitive/research/persistence.py` — artifact persistence + archive | Real |
| `jeff/cognitive/proposal/generation.py` — proposal generation plumbing | Real (LLM reliability issue) |
| `jeff/cognitive/selection/decision.py` — deterministic rule-based selection | Real |
| `jeff/cognitive/evaluation.py` — deterministic verdict + override caps | Real |
| `jeff/action/execution.py` — governed subprocess execution | Real |
| `jeff/memory/write_pipeline.py` — 10-stage memory write pipeline | Real |
| `jeff/memory/store.py` — in-memory store with lexical + semantic retrieval | Real |
| `jeff/memory/postgres_store.py` — PostgreSQL + pgvector store | Real in code |
| `jeff/orchestrator/runner.py` — flow sequencing with stage validation | Real |
| `jeff/orchestrator/flows.py` — 9 explicit flow families | Real |
| `jeff/orchestrator/routing.py` — deterministic route decisions (stop/hold/followup) | Real |
| `jeff/orchestrator/lifecycle.py` — explicit lifecycle state machine | Real |
| `jeff/orchestrator/trace.py` — event-level orchestration trace | Real |
| `jeff/interface/cli.py` + `commands/` — full CLI command surface | Real |
| `jeff/infrastructure/runtime.py` — model adapter registry + purpose routing | Real |
| Ollama HTTP adapter + Fake adapter | Real |
| `jeff/knowledge/` — compiled knowledge artifact store | Real |
| `.jeff_runtime/` persisted workspace (state, flows, reviews, artifacts) | Real |
| Scope-keyed persistence for flow_runs and selection_reviews | Real (hardened April 21) |

### What exists but is partial

| Component | Partial Status |
|---|---|
| `/run <objective>` end-to-end | Architecturally wired; LLM proposal validation fails regularly with real providers |
| Planning stage (`jeff/cognitive/planning/`) | Full code, accessible via CLI (`/plan show/steps/execute/checkpoint`); not reachable via standard `/run` flow |
| Approval/reject/revalidate CLI commands | Code + acceptance tests exist; not live-demonstrated |
| Research-followup continuation chain | Full code in `orchestrator/continuations/post_research.py`; not live-exercised |
| Memory retrieval in proposal context | Write pipeline is real; proposal `input_bundle.memory_support` consistently empty in live runs |
| Post-selection orchestration continuations | Code present; bounded, explicit, not proven in live-operator use |

### What exists only as docs or scaffolding

| Component | Status |
|---|---|
| GUI (`jeff/gui/`) | Prototype scaffolding; not wired to runtime |
| Autonomous continuation | Explicitly deferred; no code |
| Broader `/run` action families beyond `RepoLocalValidationPlan` | Explicitly deferred |
| Richer transition vocabulary (update_run_status, archive, etc.) | Only 3 transition types exist |
| Web search provider beyond DuckDuckGo HTML scraping | Not present |

### What appears stale, duplicated, or drifted

| Item | Drift Assessment |
|---|---|
| `handoffs/system/WORK_STATUS_UPDATE_2026-04-18_*` | Some notes describe states superseded by April 19–21 work |
| Legacy flat bare-`run_id` files in `.jeff_runtime/` | Still present on disk if runtime predates April 21; load but are overridden by scoped files |
| `WORK_STATUS_REALITY_DIFF.md` | Reasonably current; acknowledges LLM gap with correct framing |
| `v1_report.md` + `INTERNAL_LAYER_STRENGTH_REPORT.md` | Accurate to April 19 state; scope-keyed migration not reflected |
| `jeff doc old/` folder | Superseded design docs; clearly named as old |

### Practical center of gravity

The practical center of gravity is **truthful inspection, persisted runtime continuity, and research pipeline**. The system's most reliable operator value today is: start Jeff, inspect existing run history, issue bounded research queries, and read back artifacts across process restarts. The `/run` path is real but the LLM stage makes it unreliable as a daily operator workflow.

---

## 3. Black-Box Operator Assessment

*Synthesized from `BLACK_BOX_OPERATOR_VALIDATION_REPORT.md` (April 20) plus code inspection of what changed since (April 21 scope-keyed migration, operator trust hardening).*

### Startup experience

- Clean. `python -m jeff --bootstrap-check` passes, reports 12 diagnostic checks, loads persisted runtime.
- `python -m jeff --help` is informative and accurate.
- `--reset-runtime --bootstrap-check` works as documented.

### Command discoverability

- `/help` surfaces the full operator surface accurately.
- Commands are documented honestly including conditionally-available commands (`/approve`, `/reject`, `/revalidate`).
- `/help` does not mislead about what is deferred.

### Scope handling

- **Confusing.** `--bootstrap-check` reports "runtime project scope ready: general_research" while `/scope show` shows `project_id=- work_unit_id=- run_id=-`. The distinction between runtime scope and session scope is real but operator-invisible without explanation.
- Scope-keyed persistence fix (April 21) resolves the cross-scope run-1 collision bug. This was a real operator trust failure; it is now fixed.
- `run_id` values are still not globally unique within a project by convention, so multi-run environments require explicit scoping.

### Run behavior

- `/run list` and `/run use <run_id>` work cleanly.
- `/run <objective>` creates a new run, drives the proposal/selection/execution flow, and reports a coherent result on the happy path (direct-action objective with functional proposal).
- **Practical brittle point:** proposal validation with real Ollama LLMs fails consistently in many cases. The operator sees a routing result of `reject_all` or `escalated` rather than a successful execution.
- When a run does complete successfully (e.g., `run-12`, direct-action path), it executes the fixed smoke pytest plan and reports an `acceptable` evaluation verdict.
- Planning-oriented `/run` objectives (`/run "Plan the next ..."`): proposal surfaces `planning_needed=true`, but selection escalates instead of routing to planning. No `PlanArtifact` is produced.

### Inspectability

- **Strong.** `/show`, `/trace`, `/lifecycle`, `/proposal show`, `/proposal raw`, `/proposal validate`, `/selection show` all work and produce truthful, structured output.
- `/inspect` assembles a live context package and surfaces it coherently.
- JSON mode (`--json`) works for project/work/run list commands.
- One trust gap (fixed April 21): before scope-keyed migration, `/proposal show` on a run could return the wrong scope's proposal.

### Failure honesty

- **Genuinely honest.** Jeff does not fabricate success. If proposals fail validation, it reports `reject_all`. If no plan artifact exists, `/plan show` fails cleanly with an explicit message. If scope is wrong, it fails closed.
- Memory empty reason is now surfaced in proposal output (`memory_empty_reason=...`).
- Research terminal receipt hardening ensures no silent state mutation with empty terminal output.

### Confusing/brittle flows

1. **Windows one-shot quoting.** Inner quotes in `--command` values require cmd.exe escaping or PowerShell backtick escaping. Multiple valid-looking commands fail before Jeff sees them. This is not a Jeff logic bug but it destroys operator trust in practice.
2. **Session vs runtime scope mismatch.** Documented in operator reports; still present.
3. **Planning not reachable.** Multiple attempts to reach planning via `/run` fail at selection. No CLI path reliably produces a `PlanArtifact` that could then be exercised via `/plan execute`.
4. **Memory support invisible.** Memory writes are confirmed in run history; proposal memory support reads back as empty. An operator who writes a research memory and expects it to influence the next proposal will be silently disappointed.

### What actually feels usable

- `/help`, `/project list`, `/work list`, `/run list`, `/run use`, `/show`, `/trace`, `/lifecycle`
- `/proposal show`, `/proposal raw`, `/proposal validate`
- `/selection show`, `/selection override`
- `/research docs` (functional with Ollama, needs concise question < 200 chars)
- `/inspect`
- `--bootstrap-check`, `--reset-runtime`

### What absolutely does not work (or is unreachable)

- `/run <planning-oriented-objective>` reliably routing to a `PlanArtifact`
- Memory-backed proposal support being operator-visible
- Approval/reject/revalidate flow being live-demonstrable (requires reaching `approval_required` routing state, which requires a successful proposal → selection → action → governance path where `Policy(approval_required=True)` is configured)

---

## 4. Layer-by-Layer Audit

### 4.1 Core / State / Transition

**Intended role:** One lawful truth mutation path; immutable canonical state; fail-closed validation.

**Actual implementation reality:**
- `jeff/core/state/models.py`: real `GlobalState` with nested `Project → WorkUnit → Run`.
- `jeff/core/transition/apply.py`: real fail-closed `apply_transition` with candidate construction, validation, and commit. Handles `create_project`, `create_work_unit`, `create_run`, `update_run`.
- `jeff/core/transition/validator.py`: real stale-basis rejection, unknown-scope rejection.
- Persisted to `.jeff_runtime/state/canonical_state.json` with transition audit records.

**Black-box evidence:** Persistence and reload verified live. Transitions tested in unit suite (`test_transition_rules.py`).

**Biggest strength:** Genuinely enforces one lawful mutation path. Not just a concept — code is tight and tests prove the invariants.

**Biggest weakness:** Transition vocabulary is minimal. Three-plus types (`create_project`, `create_work_unit`, `create_run`, `update_run`) cover initialization but not operational lifecycle. No archive, deprecate, status-change, or richer mutation families.

**Risk to system:** Moderate. The current vocabulary is sufficient for v1. Growth of the system will quickly demand richer transitions that don't yet exist.

**Grade: 4/5**

---

### 4.2 Governance

**Intended role:** Fail-closed evaluation of action entry; explicit policy/approval/readiness/truth-integrity checks; no leakage from selection to authorization.

**Actual implementation reality:**
- `jeff/governance/action_entry.py`: real evaluation pipeline producing `ActionEntryDecision` with `policy_verdict`, `approval_verdict`, `readiness`, `governance_outcome`, `allowed_now`.
- `jeff/governance/approval.py`, `policy.py`, `readiness.py`: real contract types with structured verdicts.
- Integration test (`test_governance_negative_boundaries.py`) proves selection-like objects cannot enter governance, stale approval is rejected, and workflow existence does not imply permission.

**Black-box evidence:** Live approval-gated acceptance test verifies `lifecycle_state=waiting` and `allowed_now=False`. Not live-verified with real runtime, but the unit+acceptance test coverage is convincing.

**Biggest strength:** Genuine separation. Governance is not a prompt. It is deterministic code with explicit outcome categories.

**Biggest weakness:** Operator-facing approval workflow stops at request-entry receipts. The live path from "approval required" → "operator issues `/approve`" → "continuation resumes" is not demonstrated in live operation. Tests cover it; live runtime has not been walked through it.

**Risk to system:** Medium. The design is correct. The live approval path is the gap.

**Grade: 4/5**

---

### 4.3 Context / Research

**Intended role:** Truth-first context assembly; bounded research pipeline (docs, web); evidence packs with provenance; bounded synthesis with debug checkpoints.

**Actual implementation reality:**
- `jeff/cognitive/context.py`: truth-first assembly ordering explicitly documented and implemented.
- `jeff/cognitive/research/synthesis.py`: 3-step synthesis pipeline (Step 1: bounded text, Step 2: deterministic transform, Step 3: optional formatter fallback). Real LLM calls, debug checkpoints, provenance validation.
- `jeff/cognitive/research/documents.py`: document evidence pack builder. Real file reading.
- `jeff/cognitive/research/web.py`: DuckDuckGo HTML scraping, content extraction, evidence pack construction.
- `jeff/cognitive/research/persistence.py`: artifact persistence + archive store.
- `jeff/cognitive/research/bounded_syntax.py`: syntax spec for Step 1 output — this is the validation layer that rejects malformed LLM output.

**Black-box evidence:** `/research docs` produced structured findings from real Ollama. Research artifact persistence verified in `.jeff_runtime/artifacts/research/`. Research bounded-syntax errors observed live (`summary must stay concise and below 200 characters`) — honest failure, not silent corruption.

**Biggest strength:** Most operationally proven subsystem. The bounded syntax + deterministic transform approach is architecturally strong and honest about what it can't do.

**Biggest weakness:** The 200-character summary constraint on `/research docs` is undiscoverable from help text. Operators learn about it via error. Web research is DuckDuckGo HTML scraping — fragile and not documented as such.

**Risk to system:** Low-medium. Research is real. The limits are real and mostly acceptable for v1.

**Grade: 4/5**

---

### 4.4 Proposal / Selection / Planning

**Intended role:** Proposal generation (bounded 0..3 options); deterministic selection; conditional planning insertion; explicit non-selection outcomes.

**Actual implementation reality:**
- `jeff/cognitive/proposal/generation.py`: real prompt build + LLM call + bridge result.
- `jeff/cognitive/proposal/parsing.py`: real proposal response parsing with fail-closed validation.
- `jeff/cognitive/selection/decision.py`: deterministic rule-based selection with explicit `_HARD_REJECT_PHRASES`, `_DEFER_TYPES`, `_ESCALATE_TYPES`.
- `jeff/cognitive/selection/api.py`: `run_selection_hybrid` — hybrid LLM + deterministic selection path.
- `jeff/cognitive/planning/`: formation, validation, persistence, checkpoint, action bridge — all present and real.

**Black-box evidence:**
- Direct `/proposal` works and is inspectable.
- Proposal with archive evidence surfaced real `evidence_items=2`.
- Proposal with thin scope honest at `proposal_count=0`.
- Selection escalation observed live when proposal framed judgment boundary.
- Planning `PlanArtifact`: not produced in any live `/run` attempt. `/plan show` fails closed correctly.

**Biggest strength:** Selection determinism. The rule-based selection layer prevents arbitrary autonomous choices. Non-selection outcomes are explicit and surfaced.

**Biggest weakness:** Planning is unreachable from normal `/run` flow. LLM proposal validation failure rate is the dominant operator experience. Memory support does not surface in proposals despite memory writes existing.

**Risk to system:** High. This is the core value-delivery layer and it is the most operationally broken. Architecture is sound; LLM stage reliability is not.

**Grade: 3/5**

---

### 4.5 Execution / Outcome / Evaluation

**Intended role:** Governed subprocess execution; normalized outcome; deterministic evaluation with override caps.

**Actual implementation reality:**
- `jeff/action/execution.py`: real `RepoLocalValidationPlan` + `GovernedExecutionRequest` + `ExecutionResult` with `subprocess.run`, timeout, stdout/stderr capture.
- `jeff/action/outcome.py`: normalized outcome contract.
- `jeff/cognitive/evaluation.py`: real `EvaluationResult` with `EvaluationVerdict` (7 values) + `RecommendedNextStep` (8 values) + `deterministic_override_reasons`.

**Black-box evidence:** Live run `run-12` executed the smoke pytest validation plan and completed with `acceptable` evaluation and `evidence=strong`. Governed execution is real.

**Biggest strength:** One fixed execution plan type (`RepoLocalValidationPlan`) keeps the execution scope honest and bounded. Evaluation override reasons prevent model-only verdicts from overriding deterministic failures.

**Biggest weakness:** Only one action plan type exists. No broad execution action vocabulary. The "execution" in JEFF today means "run pytest" — that's it.

**Risk to system:** Medium. For v1 bounded scope, it's honest and real. Growth requires richer plan types.

**Grade: 3/5** (honest and real but intentionally narrow)

---

### 4.6 Memory

**Intended role:** Non-truth memory layer; 10-stage write pipeline; in-memory + PostgreSQL stores; retrieval with semantic + lexical search; memory never directly mutates canonical truth.

**Actual implementation reality:**
- `jeff/memory/write_pipeline.py`: real 10-stage pipeline (candidate creation, validation, dedupe, type assignment, scope validation, compression, accept/reject/defer, commit, indexing, linking). Atomic write block on Postgres path.
- `jeff/memory/store.py` (`InMemoryMemoryStore`): real in-memory store with retrieval.
- `jeff/memory/postgres_store.py`: real PostgreSQL store (~580 lines) with pgvector HNSW, FTS, atomic transactions.
- `jeff/memory/retrieval.py`: real 10-stage retrieval pipeline.

**Black-box evidence:** Memory handoff writes confirmed in `/show` (run-8, run-10, run-12 show `memory_handoff outcome=write`). Memory reads in proposal context: `memory_items=0` in every live test case. Postgres: not live-tested (no DSN available).

**Biggest strength:** Memory pipeline discipline is genuinely strong. The "memory is not truth" law is enforced in code. Write pipeline is non-trivial and real.

**Biggest weakness:** Default startup uses `InMemoryMemoryStore` — memory is ephemeral by default. Memory writes don't surface back into proposal support in live runs. The write → read → proposal-influence loop is unproven at operator level.

**Risk to system:** Medium. The law is sound. The practical loop from write to retrieval to proposal influence is broken or unverified.

**Grade: 3/5**

---

### 4.7 Orchestrator

**Intended role:** Deterministic stage sequencer; flow family enforcement; routing decisions; lifecycle/trace emission; bounded continuation logic.

**Actual implementation reality:**
- `jeff/orchestrator/flows.py`: 9 explicit flow families with typed stage orders.
- `jeff/orchestrator/runner.py`: ~500 lines, real stage sequencing with handoff validation.
- `jeff/orchestrator/validation.py`: fail-closed stage sequence and type validation.
- `jeff/orchestrator/routing.py`: deterministic routing decisions; `auto_execute=True` explicitly raises `ValueError` — hardcoded anti-auto-execution.
- `jeff/orchestrator/lifecycle.py`: real lifecycle state machine.
- `jeff/orchestrator/trace.py`: per-event trace emission.
- `jeff/orchestrator/continuations/`: post_research, post_selection, planning, boundary_routes — all present.

**Black-box evidence:** Live run demonstrated orchestrator routing to `blocked_or_escalation` with `lifecycle_state=waiting`. Acceptance test (`test_acceptance_backbone_flow.py`) walks the full `bounded_proposal_selection_action` flow end-to-end.

**Biggest strength:** `auto_execute=True` in `RoutingDecision.__post_init__` raises immediately. The orchestrator enforces non-authorization semantically, not by convention. Handoff validation is type-enforced.

**Biggest weakness:** Continuation chains (post_research, planning) are present but not live-exercised. The orchestrator is a bounded in-process coordinator; there is no queue, no job system, no multi-process continuation.

**Risk to system:** Low for current scope. Medium when continuation depth grows.

**Grade: 4/5**

---

### 4.8 Interface / CLI

**Intended role:** CLI-first operator surface; one-shot and interactive modes; session-local scope (non-canonical); JSON output mode.

**Actual implementation reality:**
- `jeff/interface/cli.py`: real `JeffCLI` with `run_one_shot` and `run_interactive`.
- `jeff/interface/commands/registry.py`: real dispatcher over all command handlers.
- Commands: `project`, `work`, `run`, `scope`, `mode`, `json`, `inspect`, `show`, `trace`, `lifecycle`, `plan`, `proposal`, `request` (approve/reject/revalidate/retry/recover), `research`, `selection` — all wired to real handlers.
- `jeff/interface/render.py`: human-readable rendering.
- `jeff/interface/json_views.py`: structured JSON views.
- Session scope is process-local only; explicitly non-canonical.

**Black-box evidence:** All read-oriented commands verified live. One-shot `--command` works. JSON mode works for list commands. `/help` is accurate.

**Biggest strength:** CLI is real. It is not aspirational. Every command in `/help` is wired to real handler code.

**Biggest weakness:** Request commands (`/approve`, `/reject`, `/revalidate`) are lawful only when the flow is in the right routing state, which is hard to reach in practice. Windows quoting makes one-shot commands awkward. Session scope vs runtime scope is confusing without explanation.

**Risk to system:** Low-medium. CLI is functional. UX friction (quoting, scope semantics) is real but not blocking for a determined operator.

**Grade: 4/5**

---

### 4.9 Infrastructure / Providers

**Intended role:** Model adapter registry; purpose-based routing; contract runtime; Ollama + Fake adapters.

**Actual implementation reality:**
- `jeff/infrastructure/runtime.py`: real `InfrastructureServices` with adapter registry and purpose override routing.
- `jeff/infrastructure/contract_runtime.py`: real `ContractRuntime` with strategy-aware calls.
- `jeff/infrastructure/model_adapters/`: Ollama adapter (real HTTP calls to `http://127.0.0.1:11434`) + Fake adapter.
- `jeff/infrastructure/config.py`: `jeff.runtime.toml` reader.
- Purpose overrides: `research`, `formatter_bridge`, `proposal`, `selection`, `planning`, `evaluation` — each can route to a different adapter.

**Black-box evidence:** Live `/research docs` used Ollama (real HTTP calls verified). `jeff.runtime.toml` configures `gemma4:31b-cloud` for default/proposal/planning and `qwen3:8b` for formatter. Bootstrap check verifies config loaded.

**Biggest strength:** Purpose-based routing is real and configurable. Fake adapter enables full test suite without live LLM.

**Biggest weakness:** Only two provider kinds (Ollama, Fake). No OpenAI, Anthropic, or other API. No retry, streaming, or async support. Runtime reliability depends entirely on Ollama availability and model quality.

**Risk to system:** High operationally. Single-provider dependency on local Ollama with specific models is fragile. Provider breadth is absent.

**Grade: 3/5**

---

### 4.10 Docs / Handoffs / Tests

**Intended role:** Continuous operator handoff discipline; canonical spec in `v1_doc/`; module handoffs for each layer; work status chain; anti-drift tests.

**Actual implementation reality:**
- `handoffs/system/` contains 45+ dated work status updates with precise, concrete descriptions.
- Module `HANDOFF.md` files exist in every major package.
- `v1_doc/` contains spec documents (`ARCHITECTURE.md`, `STATE_MODEL_SPEC.md`, `ORCHESTRATOR_SPEC.md`, etc.) used as semantic law.
- Anti-drift tests in `tests/antidrift/`: `test_antidrift_semantic_boundaries.py`, `test_selection_hybrid_failure_truthfulness.py`, `test_selection_override_truth_boundaries.py`.
- Test families: smoke (3), unit (deep per-layer), integration (30+), acceptance (7), antidrift (3).
- Last known test result: 952 passed, 28 skipped, 5 failed (April 19). 5 failures tied to persisted runtime state drift in quickstart tests.
- April 21 work added scope-keyed migration tests and proposal scope hardening tests.

**Biggest strength:** Handoff discipline is genuinely unusual. Dated, concrete, specific. When the previous audit found a trust bug (cross-scope run-1 collision), the handoff system captured it, tracked the fix, and verified it. This is how software should be maintained.

**Biggest weakness:** Some early handoffs (April 17–18) describe states now partially superseded. Not a lie, just historical. The aggregated `WORK_STATUS_UPDATE.md` is less current than the individual dated files.

**Risk to system:** Low. Handoffs and docs are a genuine strength, not a liability.

**Grade: 4/5**

---

## 5. Design vs Reality Matrix

| Claimed Capability | Evidence in Code | Evidence in Runtime | Status | Comments |
|---|---|---|---|---|
| Truthful inspection (`/show`, `/trace`, `/lifecycle`, `/proposal show`) | Strong — real handlers and views | Verified live | **Real** | Best operator surface in the system |
| Bounded `/run` behavior (one fixed pytest plan) | Strong — `RepoLocalValidationPlan` is the only plan type | Verified live (run-12) | **Real** | Works on happy path; LLM proposal stage is the bottleneck |
| Approval-gated continuation | Code + acceptance tests present | Not live-demonstrated | **Partial** | Requires reaching `approval_required` routing state, which requires a successful LLM proposal chain |
| Separation of truth / state / proposal / selection / governance / execution / evaluation / memory / transition | Verified in code structure — each is a distinct module with own contracts | Verified by acceptance + antidrift tests | **Real** | Genuine architectural discipline, not marketing |
| CLI-first operator surface | Real command registry, real handlers | All read commands verified live | **Real** | |
| Anti-drift coverage | 3 antidrift test files; semantic boundary tests | Test suite passes | **Real** | |
| Research pipeline (docs + web) | Full synthesis pipeline in code | Verified live with Ollama | **Real** | Bounded syntax errors are honest failures |
| Persisted runtime across restarts | Full persistence in `runtime_persistence.py` | Verified: restart-safe readback of runs/proposals | **Real** | Scope-keyed migration completed April 21 |
| Memory write pipeline (10 stages) | Full pipeline in `write_pipeline.py` | Writes confirmed in `/show` output | **Real** | Write confirmed; read-back into proposals is the gap |
| Memory retrieval in proposal context | Pipeline code exists in retrieval + context assembly | `memory_items=0` in every tested live proposal | **Weak** | Write-read loop not operator-visible |
| Planning stage (`/plan show/execute/checkpoint`) | Full planning module with checkpoint logic | `/plan show` fails closed correctly; no live PlanArtifact produced | **Partial** | Implemented but practically unreachable via normal flow |
| PostgreSQL memory backend | Full `postgres_store.py` (~580 lines) with pgvector + FTS | Not tested live (no DSN) | **Partial** | Real in code; needs external Postgres + pgvector |
| Research-followup orchestration chain | Full code in `continuations/post_research.py` | Never triggered in live operation | **Partial** | Code real; path not exercised |
| Scope isolation (no cross-scope run-1 collision) | Scope-keyed persistence + fail-closed lookup | Verified post April 21 migration | **Real** (recently fixed) | Was a real trust bug before April 21 |
| GUI | Prototype scaffolding in `gui/` | Not wired to runtime | **Absent** (explicitly deferred) | Honestly deferred |
| Autonomous continuation | No code | Not present | **Absent** (explicitly deferred) | Honestly deferred |
| Broad `/run` action families | One action type only | Confirmed | **Absent** (explicitly deferred) | Honestly deferred |
| Multiple LLM providers | Only Ollama + Fake | Confirmed | **Absent** | Not deferred — just not built |

---

## 6. What Is Actually Strong

**1. Core/transition/state discipline.** One lawful mutation path, enforced in code, tested for stale-basis rejection and scope violations, persisted atomically. This is not handwaving — it is working code.

**2. Research pipeline architecture.** The bounded-syntax + deterministic-transform + optional-formatter-fallback pattern is genuinely thoughtful. Failures are explicit, not silent. Evidence packs are structured and provenance-tracked. This is the most operationally proven layer.

**3. Orchestrator non-authorization.** `auto_execute=True` in `RoutingDecision` raises immediately. The orchestrator is not allowed to authorize actions by construction. This is a real invariant, not a convention.

**4. Governance fail-closed.** `evaluate_action_entry` requires typed `Action`, `Policy`, and `CurrentTruthSnapshot`. Wrong types raise before evaluation. Governance outcome is deterministic given inputs.

**5. Persisted runtime continuity.** Fresh-process restart reloads canonical state, flow runs, selection reviews, and research artifacts. The scope-keyed migration ensures this is now correct across colliding `run_id` values.

**6. Handoff and work-status discipline.** The dated work status chain is an unusually honest and detailed self-audit trail. The system was caught with a real trust bug (cross-scope collision) and fixed it the same day it was found. That is healthy.

**7. Test coverage depth.** Smoke + unit + integration + acceptance + antidrift is a real multi-layer strategy, not a pile of `assert True`. The antidrift tests specifically protect semantic boundaries, which is the kind of testing that prevents architectural drift.

**8. Proposal inspectability surface.** `/proposal show`, `/proposal raw`, `/proposal validate` give the operator three views of the same artifact. The raw view is particularly honest about what the LLM actually returned.

---

## 7. What Is Weak, Fake, or Missing

**1. LLM proposal validation failure rate is hidden in the narrative.**  
WORK_STATUS_REALITY_DIFF.md says "proposal validation failure rate with real LLMs" is the primary gap. README says `/run` "creates one bounded repo-local validation run, drives proposal and selection under the configured model/runtime." That framing is architecturally accurate but operationally misleading. The typical operator experience is: `/run <objective>` → proposal fails validation → `reject_all` or `escalated` → no execution.

**2. Planning is implemented but unreachable.**  
The planning module (`jeff/cognitive/planning/`) is real. `/plan show/steps/execute/checkpoint` are real handlers. But in live operation, selection escalates or defers before routing to planning, even when proposals explicitly contain `planning_needed=true`. This makes the planning feature invisible to operators unless they manually construct test scenarios.

**3. Memory → proposal feedback loop is broken at the operator level.**  
Memory writes are confirmed. Memory retrieval code exists. But live `/proposal` commands consistently return `memory_items=0` even after memory handoff writes on the same run. This means the "memory-informed proposal" capability — which is architecturally present — is not delivering in practice.

**4. Transition vocabulary is minimal.**  
Three transition types (`create_project`, `create_work_unit`, `create_run`) plus `update_run` cover initialization. No archive, deprecate, status-change, or richer lifecycle transitions exist. The claim "transition is the only lawful truth mutation path" is true, but the set of lawful mutations is very small.

**5. Windows quoting is an operator UX blocker.**  
One-shot `--command` with inner quotes requires non-obvious escaping on Windows. Multiple documented operator attempts failed before reaching Jeff. This is not Jeff's fault architecturally, but it is a real daily friction point that makes the system feel unreliable.

**6. Session scope / runtime scope confusion is unresolved.**  
`--bootstrap-check` reports a runtime scope ("runtime project scope ready: general_research"). `/scope show` in the same session reports `project_id=- work_unit_id=- run_id=-`. The distinction is technically correct but operator-invisible. No help text explains this.

**7. Infrastructure provider breadth is absent.**  
Only Ollama and Fake adapters exist. No OpenAI, Anthropic, Gemini API, or cloud provider. For operators without a local Ollama instance running the specific configured model, the system is non-functional beyond read-only inspection.

**8. Postgres memory is code-complete but operationally optional.**  
The PostgreSQL memory backend is a real, substantial implementation (~580 lines, pgvector HNSW, FTS, atomic writes). But it is not the default, requires an external DSN, and 28 tests are permanently skipped without a real database. Default startup is ephemeral memory.

---

## 8. Testing Reality

### What the tests prove

- **Core/transition invariants:** Unit tests prove stale-basis rejection, unknown-scope rejection, and that `apply_transition` is the only lawful mutation path. These are meaningful.
- **Governance non-leakage:** Integration tests prove selection-like objects cannot enter governance; stale approval does not authorize.
- **Orchestrator non-authorization:** Unit tests + antidrift tests prove `auto_execute=True` raises; stage validation enforces type expectations.
- **Memory write pipeline stages:** Unit tests for each of the 10 stages. Not shallow.
- **Research bounded-syntax:** Unit tests for Step 1 validation, deterministic transform, formatter fallback decisions.
- **Acceptance backbone flow:** `test_acceptance_backbone_flow.py` walks the full `bounded_proposal_selection_action` flow with staged handlers and verifies lawful completion.
- **Scope isolation:** `test_acceptance_scope_isolation.py` and `test_acceptance_proposal_scope_hardening.py` prove cross-scope collision is rejected (post-April-21 fix).

### What the tests do NOT prove

- **LLM stage reliability with real providers.** The entire test suite runs against the Fake adapter. Zero tests exercise the Ollama adapter with a live model. Test confidence for the real proposal/research/selection chain is structurally limited.
- **Approval/reject continuation live path.** Acceptance tests construct staged handlers that inject pre-built governance decisions. They don't prove the path works through real CLI → real LLM → real governance decision → real continuation.
- **Planning reachability via real flow.** Tests construct `PlanArtifact` directly and inject it. They don't prove that a standard `/run` objective reliably routes to planning.
- **Memory → proposal retrieval loop.** Memory write tests exist. Memory retrieval tests exist. No test demonstrates that a prior memory write surfaces as `memory_items > 0` in a subsequent live `/proposal`.
- **Research-followup chain in live runtime.** Post-research continuation tests exist but use staged handlers. Not proven against real LLM + persistence.

### Test confidence vs black-box reality

Tests are more confident than black-box reality justifies for the LLM-dependent paths. The Fake adapter makes everything pass cleanly. Real Ollama produces validation failures that tests never see. This is not a test design failure — it is a structural honesty gap: the test suite proves the deterministic layers are correct; it cannot prove the LLM layers are reliable.

The 5 failures in the April 19 run are smoke/quickstart tests broken by persisted runtime state drift — not backbone logic. That is the correct kind of failure: the tests are sensitive enough to catch state drift.

**Test confidence grade for deterministic layers: High**  
**Test confidence grade for LLM-dependent paths: Low (Fake-only coverage)**

---

## 9. Repo Honesty Assessment

| Area | Honesty Assessment |
|---|---|
| README | **Mostly honest.** States "strongest today at truthful inspection, bounded /run, approval-gated continuation." Does not prominently disclose that LLM proposal validation fails regularly. Explicit about what is deferred (GUI, autonomous continuation, broad /run families). |
| Handoffs (dated work status) | **Very honest.** Each update is specific, dated, and concrete. Bugs are recorded as bugs. Partial progress is recorded as partial. The system caught and fixed a real trust bug (scope collision) within hours of identifying it. |
| `WORK_STATUS_REALITY_DIFF.md` | **Honest.** Explicitly calls out the LLM proposal validation failure rate as the primary gap. Notes memory is ephemeral by default. No false claims found. |
| `INTERNAL_LAYER_STRENGTH_REPORT.md` | **Honest.** Written as a code-first audit. Grades layers with genuine weaknesses acknowledged. Describes planning as "implemented but thin." |
| `v1_report.md` | **Honest.** States "backbone is real today" and separately describes what still remains. Does not conflate backbone existence with operational completeness. |
| `BLACK_BOX_OPERATOR_VALIDATION_REPORT.md` | **Honest.** Documents exactly what worked and exactly what failed. Does not smooth over the planning reachability failure or memory support gap. |
| Architecture claims | **Honest at the layer level.** Each layer claim (truthful inspection, bounded /run, approval-gated, etc.) is real in code. The gap is between "real in code + tests" and "reliable in live operation." |

**Overall repo honesty: High.** This is unusual. The repo owner appears to be applying the same "truthful inspection" discipline to the repo itself that the system is supposed to enforce over its runtime state.

---

## 10. Final Architectural Risk Assessment

### Risk 1: LLM stage reliability is the load-bearing gap (HIGH)
The entire value of the bounded `/run` path depends on the LLM (Ollama) producing proposal output that passes JEFF's validation. Current reality: failures are frequent, not edge cases. Architecture is sound; the layer above the architecture is the bottleneck. This is not a bug — it is a fundamental challenge for any LLM-driven proposal system. But it is also the risk that most threatens JEFF's claim to be a reliable operator tool.

### Risk 2: Planning feature is invisible to operators (MEDIUM-HIGH)
Planning code is real and substantial. But operators cannot reach it via normal flow. If the planning capability is intended to be a differentiating feature, it is currently dormant. Selection behavior gates it off before operators can experience it.

### Risk 3: Memory → proposal feedback loop not closing (MEDIUM)
Memory writes happen. Memory retrieval code exists. The pipeline code connects them. But the operator-facing loop (write memory → retrieve in next proposal → influence selection) is not closing in live runs. This gap makes the memory subsystem feel ornamental rather than functional.

### Risk 4: Single-provider infrastructure (MEDIUM)
Ollama-only means JEFF's practical reach is limited to operators running a local Ollama with specific models. Any provider outage, model mismatch, or performance issue blocks the entire LLM-dependent path. No fallback. No cloud provider alternative.

### Risk 5: Ephemeral memory default (LOW-MEDIUM)
Default startup uses in-memory store. Memory vanishes on process exit. The Postgres path is real but requires setup. For operators expecting memory to accumulate across sessions, the default behavior is surprising and not prominently documented.

### Risk 6: Transition vocabulary narrowness (LOW-MEDIUM)
Three mutation types are sufficient for v1. Growth of the system to cover operational lifecycle (run completion, archiving, status changes, recovery) will require richer transitions that do not yet exist.

### Risk 7: Legacy flat persistence files on disk (LOW)
Pre-April-21 runtimes have flat `run_id`-only persistence files. These still load (backward compat preserved) but could cause confusion in inherited runtimes. A hygiene surface to report and migrate legacy files would reduce future operator confusion.

---

## 11. Recommended Next Moves

Listed by impact on practical operator trustworthiness.

**Move 1: Make LLM proposal failures visible and diagnosable.**  
When proposal generation fails validation, the operator should see: (a) what the raw LLM output was, (b) which validation rule it failed, (c) a specific recommendation. Currently failures often surface as terse routing outcomes. This single change would make the system feel less broken and more honest.

**Move 2: Expose the planning routing path explicitly.**  
Add a `/run --hold-for-planning <objective>` variant or a post-selection `planning` routing override that an operator can request. Alternatively, document the exact LLM prompt conditions that reliably produce a `planning_insertion` outcome. Planning should not be accidental.

**Move 3: Fix the memory → proposal feedback loop.**  
Diagnose why `memory_items=0` in live proposals after confirmed memory writes. Either the retrieval query isn't matching, the in-memory store isn't persisting across process restarts (ephemeral by default), or the context assembly isn't requesting memory retrieval. This is a high-value fix: if memory-backed proposals work, a major claimed capability becomes real.

**Move 4: Document the session scope vs runtime scope distinction prominently.**  
Add one line to `--bootstrap-check` output explaining that "runtime project scope" is the persisted default scope and session scope starts blank. This removes the most common operator confusion with zero code change.

**Move 5: Add a `/run` dry-run or validation mode.**  
Before launching a full LLM-backed run, let the operator see: which flow family will be used, what context will be assembled, whether infrastructure services are ready. This turns invisible pre-execution failures into visible pre-execution diagnostics.

---

## Required Grades

| Dimension | Grade | Reasoning |
|---|---|---|
| **Overall repo reality** | **3/5** | Real backbone, not a prototype shell. But the primary claimed capability (bounded `/run`) is operationally unreliable. |
| **Operator usability** | **3/5** | Read commands are genuinely usable. Write/run path is frustrating in practice. Windows quoting and scope confusion add friction. |
| **Architectural integrity** | **5/5** | Layer separation is genuine and enforced. Auto-execution prohibition is hardcoded. Governance is a real separate gate. This is architecturally excellent. |
| **Implementation maturity** | **3/5** | Core and research layers are mature. Proposal/planning/memory-feedback loop are real but thin. Execution vocabulary is minimal. |
| **Docs-vs-reality honesty** | **4/5** | Unusually honest. LLM reliability gap is acknowledged but not prominently foregrounded in README. Handoff discipline is exemplary. |
| **Test confidence** | **3/5** | Deterministic layers are well-tested. LLM-dependent paths are Fake-adapter-only. Test suite does not validate real operator experience. |

---

*End of REPO_REALITY_AUDIT_REPORT.md*
