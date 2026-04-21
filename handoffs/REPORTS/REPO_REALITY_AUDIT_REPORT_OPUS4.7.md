# JEFF — Repo Reality Audit

Date: 2026-04-21
Auditor stance: ruthless repo-reality auditor. Every claim treated as hypothesis until code and runtime confirmed it.
Method: parallel doc / code / test subagents + direct black-box CLI testing on Windows 11 / git-bash / Python 3.12 / Ollama at `http://127.0.0.1:11434` with `gemma4:31b-cloud`.

---

## 1. Executive Verdict

**What JEFF is today:** JEFF is a **partial-to-real CLI-first persisted runtime backbone** with one honestly-implemented end-to-end slice (`/run <objective> → proposal → selection → governance → execution → outcome → evaluation`) whose "execution" is intentionally pinned to a single hard-coded action: run the repo's own smoke pytest suite as a subprocess. It is **not** a general coding agent, not an autonomous system, not a product. It is a disciplined v1 backbone with a few real teeth, a much larger body of prose, and a GUI scaffold that is not wired to the backend.

**Classification:** advanced prototype / early backbone. Real code density is real; semantic reach is narrow by design.

**Solid:** CLI surface, truthful inspection of persisted runs, transition-is-only-truth-mutation law, separation of execution/outcome/evaluation, governance fail-closed gate before execution, real Ollama HTTP adapter, real run history persistence across processes, real artifact capture of proposal prompts and raw LLM replies, honest negative-path error messages, honest `/research docs` that cites sources and surfaces its own uncertainties.

**Fake / overstated / weak / incomplete:**
- The `/run` "action" is always the same `python -m pytest tests/smoke/...` — the LLM is constrained to emit one canned-looking option. The pipeline is real; the action surface is one action.
- The **GUI** (`gui/frontend/`) is a Tauri+React scaffold that talks only to `mockAdapter.ts`. No IPC to Python. README explicitly defers GUI; the scaffold exists anyway.
- **Memory** is real as a module but the canonical v1 claim of "PostgreSQL + pgvector authoritative" is not the runtime default. `local_file` + in-memory variants are what actually run.
- **Test suite confidence is fragile** in exactly the places that matter: the LLM is replaced by `FakeModelAdapter` returning a string the tests themselves authored; web research is 100 % monkeypatched; the bounded `/run` plan is stubbed to a `print()` in most tests.
- **Docs contain dual canon:** `MEMORY_ARCHITECTURE.md` vs `MEMORY_ARCHITECTURE_NEW.md`, `MEMORY_SPEC.md` vs `MEMORY_SPEC_NEW.md`, a `v1_doc/additional/` folder of unlabeled proposals, and 52+ `WORK_STATUS_UPDATE_*.md` files. The canon is self-aware about being design law but the file system says drift is underway.
- The **interface layer is not thin**: `jeff/interface/commands/scope.py` inlines the whole 9-stage pipeline (`_run_bounded_execution_flow`). That logic belongs in orchestrator/cognitive.
- The **orchestrator is not a pure sequencer**: `runner.py` contains stage-specific routing branches for selection→{planning,research,action} and plan→action bridging.

**Top 5 truths the owner must accept right now:**
1. `/run` is **one hard-coded self-test behind a real pipeline**, not a general execution surface. The visible LLM call exists but the constraints leave it no real choice.
2. **The test suite does not prove the LLM-facing pipeline works.** Green CI = mechanics work against canned inputs. It does not prove proposal parsing survives real model drift.
3. **Docs are ahead of code, and more docs exist than should.** Dual MEMORY_ARCHITECTURE specs, 52+ work-status files, an AUTONOMY_RESEARCH folder in a repo whose roadmap explicitly defers autonomy — this is exactly the drift `DOCS_GOVERNANCE.md` warns against.
4. **Interface ≠ thin**; **orchestrator ≠ pure sequencer**. The architecture law is partly held, partly aspirational. Two concrete boundary violations are documented in §4.
5. **The GUI is a façade.** It is real UI code running only against a mock. The README is honest about GUI being deferred, but the presence of `gui/frontend/` as a working-looking Tauri app is misleading if anyone browses the tree.

---

## 2. Repo Reality Summary

**Working and real (verified at runtime):**
- `python -m jeff --help`, `--bootstrap-check`, `--reset-runtime`, `--command`, `--json`, `--project/--work/--run` flags.
- `/help`, `/project list`, `/work list`, `/run list`, `/scope show`, `/inspect <run>`, `/show <run>`, `/trace <run>`, `/lifecycle <run>`, `/selection show`, `/proposal show`, `/proposal raw`, `/research docs`, `/research web` (faked in tests but real wiring in `/research docs` against local file; see §3).
- `/run <objective>`: confirmed end-to-end against live Ollama. Run `run-15` completed in 89 s with a real `initial-raw.txt` LLM artifact at `.jeff_runtime/artifacts/proposals/.../initial-raw.txt` and a real pytest subprocess stdout "22 passed in 6.05s".
- Run history persists across processes in `.jeff_runtime/` (14 prior runs visible before my tests).
- Governance fail-closed gate: `/approve` on a run not in `approval_required` returns a clear refusal. `/inspect` on nonexistent project returns a clear refusal with remedy hint. Error honesty is real.
- Research produced an honest summary citing source paths AND flagged a contradiction in the doc itself ("lists eight specific layers but states nine").

**Partial (exists but narrow or unproven under stress):**
- Proposal / selection / evaluation pipeline: real modules, real adapter call, but the constraint string (`scope.py:442-446`) channels the LLM to a single direct_action. The "0..3 serious options" guarantee is architectural; under the `/run` path in practice it's always 1.
- Conditional planning: code exists (`cognitive/planning/`, 1349 LOC), but the `/run` smoke path does not reach it (`active_stage=evaluation` after completion, no planning summary for any observed run).
- Research (web): real HTTP code exists in `cognitive/research/*` but every test fakes it; no live black-box proof in this audit.
- Memory: real write pipeline, two backends, dedupe/linker/indexer — but the runtime default is `local_file` / in-memory; the PostgreSQL path is opt-in and Windows-native-only.
- Approval/revalidate/reject: code paths exist and unit tests cover them with monkeypatched triggers. I was unable to reach `routed_outcome=approval_required` without seeding state, so this was not black-box verified by me.

**Exists only as scaffolding / docs:**
- `gui/frontend/` Tauri+React app: complete UI scaffolding, uses `mockAdapter.ts`, no Python IPC, not wired to backend.
- `gui/Jeff/*.jsx,*.html`: static design mocks.
- `v1_doc/additional/` proposals (ARCHON_INTEGRATION, RESEARCH_V2_ROADMAP, KNOWLEDGE_LAYER_ARCHITECTURE, etc.): unlabeled, unclear authority.
- `handoffs/AUTONOMY_RESEARCH/`: deep research into self-improving agent systems — the roadmap explicitly defers autonomy.
- `MEMORY_ARCHITECTURE_NEW.md` / `MEMORY_SPEC_NEW.md`: parallel canon.

**Stale / churn signals:**
- 52+ `handoffs/system/WORK_STATUS_UPDATE_*.md` files across 5 days.
- 11 top-level `.md` reports at repo root (CLI_report, functionality_report, refactor_report, v1_report, INTERFACE_REFACTOR_PROPOSAL, INTERNAL_LAYER_STRENGTH_REPORT, BLACK_BOX_OPERATOR_VALIDATION_REPORT, OPERATOR_TRUST_HARDENING_REPORT, SCOPE_KEYED_PERSISTENCE_MIGRATION_REPORT, WORK_STATUS_REALITY_DIFF, this one).
- `v1_doc/additional/old/REAL_REPO_STATE_AUDIT.md` is the newest untracked file (2026-04-21).
- `cognitive/planning/checkpoint.py` = 4 LOC (empty stub).
- `_build_repo_local_validation_plan` duplicated 3× (scope.py:215, plan.py:338, requests.py:435).

**Practical center of gravity:** `jeff/cognitive/` (16 k LOC) + `jeff/interface/commands/` (3.8 k LOC, including the inlined `/run` pipeline in `scope.py`). That is where the work really lives. Core/transition (1 k LOC) is clean but small. Governance (448 LOC) is surprisingly thin for a headline feature.

---

## 3. Black-Box Operator Assessment

### Concrete commands run and their observed behavior

| Command | Result | Notes |
|---|---|---|
| `python -m jeff --help` | Works. Argparse help clean. | Documents PowerShell quoting pitfalls. |
| `python -m jeff --bootstrap-check` | `bootstrap checks passed`, all 12 checks green. | Reports Ollama adapter config, research memory backend, artifact root. |
| `python -m jeff --command "/help"` on git-bash | **FAILS**: `unsupported command: C:/Program Files/Git/help`. | Git-bash path conversion mangles the leading `/`. `MSYS_NO_PATHCONV=1` fixes it. README documents PowerShell quoting but not git-bash pathconv. **Operator friction on the default Windows dev shell.** |
| `... --command "/help"` with MSYS_NO_PATHCONV=1 | Real multi-section help. | Documents broader surface than README lists (`/proposal validate`, `/proposal repair`, `/plan execute`, `/plan checkpoint`). |
| `/project list` | Lists `general_research`, `project-1`. | Real canonical truth. |
| `/work list --project project-1` | Lists `wu-1`. | Real. |
| `/run list` with 14 prior runs | Lists run-1..14 with correct lifecycles. | Real persistence across processes. |
| `/scope show` and `/scope show --json` | Scope honestly described as session-local/process-local only, explicit `[hint] one-shot scope can be set with outer flags`. | Honest. JSON view is a clean object. |
| `/inspect` on `wu-1` with multiple runs and no `--run` | Returns `[error] inspect found multiple runs ... Use /run list, then /run use <run_id> to choose`. | Refusal instead of guessing. Honest. |
| `/inspect` on `run-5` (completed) | Full truth+derived+support blob. `execution.stdout` visibly `22 passed in 5.23s`. | Fields match the claimed architecture vocabulary. |
| `/lifecycle`, `/trace` on `run-13` (escalated) | Real event list (`routing_decision`, `flow_escalated`) with human reason. | Trace is real. |
| `/selection show --json` on `run-5` | Structured: selection + override + resolved_choice + action_formation + governance_handoff. | Matches `v1_doc/PROPOSAL_AND_SELECTION_SPEC.md` shape. |
| `/proposal raw` on `run-15` | Returns real LLM output. Points to artifact file at `.jeff_runtime/artifacts/proposals/.../initial-raw.txt`. | Real. The raw looks canned because the LLM was constrained to one option. |
| `/run smoke_validation_for_audit` on `project-1/wu-1` | Created `run-15`, 89 s, real Ollama call, real pytest subprocess, 22 pytests passed, evaluation=acceptable. | **End-to-end real.** |
| `/research docs "list the layers" v1_doc/ARCHITECTURE.md` | ~60 s. Real summary with source citations and an honest `[support] uncertainties` line flagging that the doc itself is inconsistent (8 layers named, 9 stated). | Best operator experience in the audit. |
| `/approve` on `run-5` (routed_outcome=none) | `[error] approve is not currently available for run run-5; it requires a run routed to approval_required`. | Fail-closed. Honest. |
| `garbage not a slash command` | `[error] unsupported command: ...`. | Honest. |
| `--project nonexistent` | `[error] unknown project_id: nonexistent. Use /project list to discover valid project_id values.` | Honest with remedy. |

### Discoverability
Good for a CLI-first tool. `/help` is comprehensive. The `--bootstrap-check` output is a rare example of honest startup reporting: it reports which features are enabled and why. Hint lines appear in many outputs (`[hint] next=/project list then /project use <project_id>`).

### Failure honesty
Strong. Every negative path I tried returned a specific, remediable message. Nothing silently succeeded. This is the single biggest differentiator versus typical agentic demos.

### Brittle / confusing
- Git-bash `--command "/help"` failure is an operator-hostile trap on the most common Windows dev shell.
- `/inspect` with no `--run` in a work-unit with N>1 runs refuses — correct, but a 14-run list is awkward to navigate without `/run use` binding. The README says `/run use` is session-local only, so one-shot users must keep passing `--run`.
- Run selection inside a multi-run work-unit relies on explicit `--run` flags; there is no implicit "latest run".
- PowerShell quoting is documented but fiddly.

### Usable vs not
Usable: `/inspect`, `/show`, `/selection show`, `/trace`, `/lifecycle`, `/run <objective>`, `/research docs ...`, `/help`, `/project list`, `/work list`, `/run list`, `/scope show`, negative-path errors.
Not really usable as a product today: `/plan execute` (planning not reached via `/run`), `/research web` (not black-box verified), `/approve`/`/reject`/`/revalidate` (could not trigger without state manipulation), broad memory surface (none exposed by design).

---

## 4. Layer-by-Layer Audit

Grades: **1** = spec-only, **5** = solid, thick, and proven.

### Core / state / transition — Grade 5
- **Intended role:** Only lawful mutation path for canonical state.
- **Reality:** `jeff/core/transition/apply.py:215-224` is the sole `state_version`-bumping site. All callers route through `apply_transition`; memory, governance, cognitive never mutate `GlobalState`. Compact (~1 k LOC).
- **Black-box evidence:** Multi-run persistence across processes reflects transition integrity.
- **Strength:** Boundary held. Validator has three phases (request/candidate/commit).
- **Weakness:** Small — most of the actual state-manipulation happens upstream in cognitive/interface where builders pile up before commit.
- **Risk:** Low.

### Governance — Grade 3
- **Intended role:** First-class approval + readiness gates before execution.
- **Reality:** Real fail-closed evaluator in `action_entry.py:52-87`. But `policy.py` = 17 LOC, `approval.py` = 80 LOC, `readiness.py` = 48 LOC — mostly data shapes. The "first-class distinct approval and readiness" claim is **structurally true but thinly implemented**.
- **Black-box evidence:** Refusal to `/approve` when not routed to `approval_required` is honest.
- **Strength:** The gate actually gates. `GovernedExecutionRequest.__post_init__` refuses anything without `allowed_now=True`.
- **Weakness:** No diverse policy sources; approval evaluation was reachable in tests only via monkeypatch.
- **Risk:** Medium — will break under real multi-source policy.

### Context / research — Grade 3
- **Intended role:** Bounded research with source-aware evidence, no truth mutation.
- **Reality:** `cognitive/research/` is 3789 LOC and real. `/research docs` end-to-end works and cites sources. Web path exists but is untested against real HTTP in the suite.
- **Black-box evidence:** The docs research run honestly surfaced a contradiction in `ARCHITECTURE.md` itself. That is the output of a system that is trying.
- **Strength:** Uncertainty field in output is the right idea.
- **Weakness:** No second-opinion evaluator; no retrieval quality scoring; source curation = filesystem path only. The research deep-research literature in `handoffs/AUTONOMY_RESEARCH/*` says this is not enough — but the spec also doesn't claim more.
- **Risk:** Low for v1 scope; high if research is ever asked to do more than summarize.

### Proposal / selection / planning — Grade 3
- **Intended role:** Generate 0..3 serious options, select one, plan only if needed.
- **Reality:** Full real pipeline — prompt rendering, LLM call, parse, validate, repair, selection (deterministic + hybrid), action materialization. ~6 k LOC combined.
- **Black-box evidence:** Run 15 produced real `initial-raw.txt`; the proposal output was 14 lines of key-value text with one option and 0 risks/assumptions. The "0..3 options" machinery is present but the `/run` constraint channel collapses it to 1.
- **Strength:** Artifact persistence (`.jeff_runtime/artifacts/proposals/.../initial-raw.txt`) is disciplined and auditable.
- **Weakness:** Planning is reachable only via non-`/run` flow families. "Serious options" under real models is not proved by tests.
- **Risk:** Medium — first real stress test (longer objectives, real feature work) will expose the constraint vs the claim.

### Execution / outcome / evaluation — Grade 3
- **Intended role:** Three distinct things that must not collapse.
- **Reality:** They are three files. `action/execution.py` (real subprocess runner, 305 LOC), `action/outcome.py` (pure normalizer, 94 LOC), `cognitive/evaluation.py` (verdict mapping, 213 LOC). `tests/antidrift/test_antidrift_semantic_boundaries.py:205-247` asserts no cross-attribute leaks.
- **Black-box evidence:** `run-5`, `run-15` show all three fields populated distinctly.
- **Strength:** Separation is both coded and unit-tested as a boundary.
- **Weakness:** Only **one execution family** exists (`RepoLocalValidationPlan`). Outcome normalization has only one shape to normalize. Evaluation has no real contract beyond deterministic mapping + LLM override hook. The "evaluator stack" advocated by the research docs (patch applies → reproducer → tests → lint → static analysis → smoke → canary → reviewer → human) is not present.
- **Risk:** High if JEFF scales beyond self-test; layered evaluator stack is a whole product.

### Memory — Grade 3
- **Intended role:** Durable non-truth continuity with Memory-only candidate authorship.
- **Reality:** 4.4 k LOC across 26 files. Real write pipeline, local+postgres stores, dedupe, linker, indexer, maintenance, scope assigner. Antidrift test asserts `MemoryCandidate` cannot be direct-constructed.
- **Black-box evidence:** `/inspect run-5` shows `memory_handoff outcome=write memory_id=memory-1`. Memory is really being written at run boundaries.
- **Strength:** Non-truth boundary held; Memory never imports `GlobalState`.
- **Weakness:** v1 canon claims PostgreSQL+pgvector authoritative; runtime default is `local_file` or in-memory. The authoritative-Postgres spec does not match runtime reality. Dual `MEMORY_ARCHITECTURE.md` / `_NEW.md` files.
- **Risk:** Medium — docs overclaim; code works for the small claim.

### Orchestrator — Grade 3
- **Intended role:** Deterministic, non-thinking sequencer only.
- **Reality:** `runner.py` is 874 LOC with stage-specific routing branches for selection→{planning, research, action} and plan→action bridging. `continuations/` (1487 LOC) holds post_selection/post_research/approval/boundary routing. Not pure sequencing.
- **Strength:** Stage order is enforced; trace events are real.
- **Weakness:** `ORCHESTRATOR_SPEC.md:63-73` explicitly warns against owning business logic; the current runner owns routing semantics. `runner.py` has ~20 pass-through shim functions wrapping `continuations.*` — indirection without value.
- **Risk:** Medium — boundary drift is already happening.

### Interface / CLI — Grade 3
- **Intended role:** Thin truthful operator surface.
- **Reality:** 6.5 k LOC. `commands/scope.py` (477 LOC) contains the entire 9-stage `/run` pipeline inlined. `render.py` (980) + `json_views.py` (1563) are thick view layers. `interface/commands/plan.py` and `requests.py` reach into `jeff.orchestrator.continuations` directly — cross-layer import.
- **Black-box evidence:** Surface is real and truthful (see §3). Views match the claimed architectural vocabulary.
- **Strength:** Honest outputs, honest errors, JSON view is well-shaped.
- **Weakness:** Far from thin; misallocated pipeline logic; `_build_repo_local_validation_plan` duplicated 3×; git-bash friction.
- **Risk:** High if the CLI continues to accumulate — it is already the second-largest module.

### Infrastructure / providers — Grade 4
- **Intended role:** Replaceable adapters to LLMs, config, storage.
- **Reality:** Real. `model_adapters/providers/ollama.py:47-129` is a working urllib HTTP client speaking `/api/generate` + `/api/chat` with JSON mode. `fake.py` is a disciplined test adapter. `contract_runtime.py:193,211,247` invokes `adapter.invoke` at three documented call sites.
- **Black-box evidence:** Live Ollama call in run-15 proven by artifact and timing.
- **Strength:** Honest kind dispatch; `ModelTransportError` raised cleanly when Ollama is down.
- **Weakness:** Only Ollama is implemented. No Anthropic, OpenAI, or local GGUF loader — though the abstraction supports adding them.
- **Risk:** Low for v1 scope.

### Knowledge — Grade 2
- **Intended role:** Compiled/linked knowledge support for proposal/selection.
- **Reality:** 1.4 k LOC. `registry.py`, `compiler.py`, `retrieval.py`, `models.py` exist; wiring into `/run` is a single `knowledge_topic_query` string. `[support] live_context support_counts=memory:0 compiled_knowledge:0 archive:0 direct:0` in all observed runs — i.e. knowledge is not actually feeding `/run`.
- **Risk:** Medium — implemented-but-disconnected is a classic drift pattern.

### Docs / handoffs / tests (as a deliverable layer) — Grade 2
- **Reality:** `v1_doc/` is disciplined canon. Alongside it: dual `_NEW.md` specs, an unlabeled `additional/` proposals folder, 52+ work-status updates, 11 top-level reports, an `AUTONOMY_RESEARCH/` that contradicts the deferred-autonomy roadmap.
- **Risk:** High — this is the most visible sign that the backbone is under drift pressure.

### GUI — Grade 1
- **Intended role:** Deferred per README.
- **Reality:** `gui/frontend/` is a live Vite + React + Tauri scaffold with pages (Overview, RunDetail, Memory, ChangesReview) using `mockAdapter.ts`. No Python IPC. `gui/Jeff/*.jsx,*.html` are static design mocks.
- **Risk:** Low for the core system; high for "JEFF is a real product" narrative cleanliness. It is a façade that exists while the README says GUI is deferred.

---

## 5. Design vs Reality Matrix

| Claimed capability | Evidence in code | Evidence in runtime | Status | Comments |
|---|---|---|---|---|
| CLI-first persisted runtime | `jeff/interface/cli.py`, `runtime_persistence.py` 1900 LOC | `--bootstrap-check` green; 14 prior runs reloaded from disk | **real** | Solid. |
| Bounded `/run` validation | `scope.py:215-233` `_build_repo_local_validation_plan` | run-15 ran real `pytest tests/smoke/*`, 22 passed | **real** | Only one plan exists. |
| Truthful inspection | `render.py`, `json_views.py`, `interface/commands/inspect.py` | `/inspect`, `/show`, `/trace`, `/lifecycle`, `/selection show` all return real persisted fields | **real** | Best feature. |
| Approval-gated continuation | `governance/action_entry.py`, `interface/commands/requests.py` | `/approve` on non-routed run refused | **partial** | Not black-box reachable to full approve/revalidate chain without seeding state. Tests force it via monkeypatch. |
| Transitions = only truth mutation path | `core/transition/apply.py:215-224` single state_version bump site | Run history integrity across restarts | **real** | Held. |
| 0..3 serious proposal options | `cognitive/proposal/*` parser expects multi-option | Run-15 `initial-raw.txt` has 1 option | **partial / constrained** | Constraint channel collapses to 1 under `/run`. Under real tasks this is unproven. |
| Hybrid selection (deterministic + LLM) | `cognitive/selection/api.py` | `/selection show` populates rationale string | **partial** | Real code; black-box diversity not verified. |
| Execution ≠ outcome ≠ evaluation | 3 files + antidrift test | 3 distinct fields visible in `/show` | **real** | Held. |
| Memory as non-truth continuity | `memory/*` never imports `core.transition` or `GlobalState` | `memory_handoff outcome=write memory_id=memory-1` in `/inspect` | **real** | Boundary held; scope smaller than `MEMORY_SPEC.md` advertises. |
| PostgreSQL + pgvector authoritative (v1) | `memory/postgres_store.py` exists | `bootstrap-check` reports `backend=local_file` | **misleading** | Doc canon says Postgres authoritative; runtime default is not. |
| Anti-drift coverage | `tests/antidrift/*.py` (19 tests) | Some real boundary assertions, no import-boundary tests | **partial** | Real but narrow. |
| Deterministic non-thinking orchestrator | `orchestrator/runner.py` | Runs complete deterministically | **partial** | Runner owns routing/branching semantics — not pure sequencing. |
| Research with evidence + citations | `cognitive/research/*`, `/research docs` | Real summary with source paths, honest uncertainties | **real** | Best-shaped output in the audit. |
| Research web | `cognitive/research/web.py` | Not black-box tested live; tests 100% monkeypatch | **absent-at-runtime** | Exists in code, no live proof. |
| Conditional planning | `cognitive/planning/*` 1349 LOC | Not reached via `/run` (no planning summary visible) | **partial / dormant** | Code present; not on the live path. |
| GUI | `gui/frontend/` (Tauri + React) | Uses `mockAdapter.ts`; no Python IPC | **façade** | Scaffold present despite README deferring GUI. |
| Broad `/memory` command family | No CLI surface | `/help` explicitly says none | **absent by design** | Honest. |
| Autonomous continuation | None | Not started | **absent by design** | Honest. |
| CLI `/rationale`, `/telemetry`, `/health`, stall/loop detection (CLI_V1 spec §9-12) | `/help` does not list them | Not surfaced | **absent / spec-only** | Overclaim in CLI_V1_OPERATOR_SURFACE.md. |

---

## 6. What Is Actually Strong

1. **End-to-end `/run` closes the loop with a real LLM and a real subprocess.** The chain is not a diagram. Run-15 is proof.
2. **Truthful inspection.** `/inspect`, `/show`, `/trace`, `/lifecycle`, `/selection show` return persisted reality with clearly-labeled `[truth]`, `[derived]`, `[support]`, `[telemetry]` sections. Docs and code use the same vocabulary.
3. **Transition-is-only-truth-mutation law.** Compact, enforced, tested, and respected by every other layer.
4. **Honest errors.** Every negative path I tried returned a specific message with a remedy.
5. **Proposal artifact persistence.** Every proposal produces an `initial-raw.txt` and structured record at a stable filesystem path. This is exactly the audit trail the research docs say operator-trustworthy systems need.
6. **`/research docs`** citing sources and flagging its own uncertainty about the source material.
7. **Separation of execution / outcome / evaluation** — held in code and asserted in antidrift tests. Most agent systems collapse these.
8. **Bootstrap-check honesty.** `--bootstrap-check` explicitly reports which features are enabled and why, including `bounded /run objective path enabled: repo-local validation`, `research memory backend configured: local_file`. No bluster.

---

## 7. What Is Weak, Fake, or Missing

### Weak
- **Governance policy** is thin (17 LOC `policy.py`, 48 LOC `readiness.py`). The claim "first-class distinct approval and readiness" is structurally true but materially small.
- **Orchestrator** owns stage-specific routing branches it is not supposed to (`runner.py:157-320`). Boundary drift is already in code.
- **Interface** inlines the `/run` pipeline (`scope.py:236-426`). `_build_repo_local_validation_plan` duplicated 3×.
- **Knowledge layer** exists but is not fed into live runs.
- **Anti-drift tests** cover semantic contracts, not module-import boundaries. Nothing would catch a new import from `memory` to `core.transition`.

### Overstated / misleading
- **"PostgreSQL + pgvector authoritative v1"** — runtime default is not Postgres. `WORK_STATUS_REALITY_DIFF.md` already admits this.
- **"0..3 serious options"** under `/run` is always 1. The constraint string in `scope.py:442-446` prevents a real multi-option test from running here.
- **CLI_V1_OPERATOR_SURFACE.md** lists `/rationale`, `/telemetry`, `/health`, stall/loop detection, debug mode. `/help` does not surface these. Either the CLI is missing them or `/help` is lying — either way the documented surface ≠ the real surface.
- **README "anti-drift coverage"** — real but 19 tests that mostly assert no-cross-attribute-leak. Not the belt-and-braces the word implies.
- **GUI scaffolding** exists despite the README saying GUI is explicitly deferred.

### Fake / façade
- `gui/frontend/` using `mockAdapter.ts` with no backend IPC.
- The apparent "3 proposal options" in prompt templates when `/run` always constrains to 1.

### Missing (vs what docs or research-docs imply)
- **Layered evaluator stack** (patch applies → reproducer → tests → lint → smoke → canary → reviewer → human). The research docs argue this is what would make JEFF real; today there is one deterministic evaluator mapping.
- **Real execution families beyond `RepoLocalValidationPlan`.** One action. The `/run` surface is honest about this, but it is worth saying out loud: JEFF cannot yet do anything except run its own smoke tests.
- **Rollback as a first-class runtime operation.** Research docs call this essential. Not present.
- **Second-opinion evaluator / reviewer** for research or proposals.
- **A single authoritative status document.** 52+ WORK_STATUS_UPDATE files is the opposite.
- **Module-import boundary tests** in antidrift/.
- **Live-provider contract tests** that verify the parser survives real model drift.
- **Live web-research tests** of any kind.

---

## 8. Testing Reality

- **1081 tests collected** (unit 816, integration 192, acceptance 32, antidrift 19, smoke 22). Smoke subset passes in ~6 s.
- **`FakeModelAdapter`** returns `default_text_response` verbatim. Every integration test that exercises proposal or selection feeds it a 14-line string the tests themselves authored. The parser is tested; **the model's real output is not**.
- **Web research** is 100 % monkeypatched (every `_search_web_query` and `_fetch_web_page_excerpt` call). No test proves real HTTP works.
- **Bounded `/run` plan** is stubbed to a one-line `print()` in most integration tests. Exactly one test (`test_run_objective_launches_real_flow_and_calls_live_context_once`) actually runs the real pytest-in-pytest-in-pytest recursion.
- **Approval/revalidate flows** rely on `monkeypatch.setattr(command_scope, "build_run_governance_inputs", ...)` to force `approval_required=True`. The real policy-to-approval coupling is not exercised.
- **Antidrift** asserts useful things (MemoryCandidate authorship, execution≠outcome≠evaluation) but not module-import boundaries.
- **Truthfulness of inspection** is asserted mostly against canned `FlowRunResult` objects from `tests/fixtures/cli.py:70-254` — proves the renderer is truthful *given* a state, not that state assembly is truthful.
- **Real things tested well:** transition engine, container invariants, persistence round-trip, memory write rules (commit/defer/reject), atomic file writes, subprocess entrypoint, JSON view shape.

**Would green CI mean the system works?** Partially. Green CI proves: CLI doesn't crash, transitions are sound, persistence round-trips, approval mechanics hold *under forced inputs*, memory write rules are enforced, rendering of hand-built states is truthful. Green CI does **not** prove: real LLM produces parseable proposals, bounded pytest `/run` recursion is stable, web research returns usable sources, governance triggers without test setup, or that module boundaries hold.

**Test confidence grade: 3 / 5.**

---

## 9. Repo Honesty Assessment

- **README honesty:** High. Explicitly defers GUI, broad API, broad `/run`, broad memory CLI, autonomous continuation. Explicitly says `/run` is not a general command runner. Rare in agent repos.
- **Canon honesty (`v1_doc/`):** High. The canon reads as design law and admits it. `DOCS_GOVERNANCE.md` explicitly forbids the parallel-authority pattern the repo is currently violating via `_NEW.md` duplication.
- **Derivative report honesty:** Mixed. `WORK_STATUS_REALITY_DIFF.md` is the most honest document in the repo and explicitly rates claims against reality. The victory-lap reports (`OPERATOR_TRUST_HARDENING_REPORT.md`, `INTERNAL_LAYER_STRENGTH_REPORT.md`, `BLACK_BOX_OPERATOR_VALIDATION_REPORT.md`) lean marketing-ish beside the disciplined canon.
- **Handoff honesty:** Low in aggregate — 52+ `WORK_STATUS_UPDATE_*.md` files are the opposite of a consolidated status. Individually they may be honest; collectively they are noise.
- **Architecture honesty:** Medium. Claims are real intentions but some are structurally thin (governance, knowledge) and some aren't on the live path (planning, knowledge support).
- **Implementation-reality honesty:** Medium-high. Code matches docs more than it contradicts them, but the Postgres-authoritative claim and the CLI §9–12 surface are two real gaps.

**Net:** canon is disciplined and honest; the perimeter around the canon (derivative reports, `_NEW.md` duplicates, `additional/`, `AUTONOMY_RESEARCH/`, status-update sprawl) is where drift is visibly happening.

---

## 10. Final Architectural Risk Assessment

Ranked by severity:

1. **Docs-outrunning-code drift.** Dual MEMORY canon, unlabeled `additional/` proposals, 52+ work-status files, AUTONOMY_RESEARCH directly contradicting ROADMAP_V1's deferral. This is the #1 risk because the canon itself warns against exactly this.
2. **Interface and orchestrator boundary erosion.** `scope.py` inlines the full `/run` pipeline; `runner.py` owns routing semantics. Both violations of stated law, both already in code.
3. **LLM-contract brittleness masked by test stubs.** The only real-model proof is one 89-second black-box run with a heavily constrained prompt. A real change in the operator objective or model could produce unparseable proposals and the tests would not catch it.
4. **Narrow action surface sold as a pipeline.** `/run` = one pytest plan. Any growth requires real action family registration, which is not yet designed visibly.
5. **Missing layered evaluator stack.** The research docs' strongest recommendation (Agentless/AutoCodeRover-style deterministic check ladder) is not present. A single verdict mapping is not a moat.
6. **GUI façade.** Not urgent, but confusing on first sight.
7. **Knowledge layer disconnected.** Built but unused on the live path — classic dead-code-in-waiting.
8. **Approval/readiness thin.** Small surface today; will crack under any real policy source beyond the test monkeypatches.

---

## 11. Recommended Next Moves

Not a wishlist. Five moves, in priority order, that would materially increase truthfulness and usability.

1. **Consolidate docs. Make the canon authoritative and singular.**
   Delete or merge `MEMORY_ARCHITECTURE_NEW.md` / `MEMORY_SPEC_NEW.md`. Label `v1_doc/additional/*` as proposed/deferred/archived. Squash `handoffs/system/WORK_STATUS_UPDATE_*.md` into one current status + an archive. Explicitly retract or inline any claim that doesn't match runtime (Postgres-authoritative, CLI `/rationale`/`/telemetry`/stall detection, etc.). This is the single biggest reputational cleanup available for free.

2. **Move the `/run` pipeline out of `interface/commands/scope.py`.**
   `_run_bounded_execution_flow` belongs in a cognitive or orchestrator-side flow factory. Delete the two duplicate `_build_repo_local_validation_plan` functions. This makes the boundary law true instead of aspirational.

3. **Add one real second action family.**
   Even a `file_patch_validation` or `run_targeted_tests` action — anything that is not the smoke suite — would prove `/run` is a pipeline and not a one-trick pony. Pair it with a layered evaluator (patch-applies → tests-pass) to start building the ladder the research docs recommend.

4. **Add a contract-record test for the real provider.**
   Record one real Ollama proposal response and build a test that replays it into the parser. Today's tests let a real-model output drift break production without CI noticing.

5. **Either wire the GUI to the backend or archive it.**
   `gui/frontend/` + `mockAdapter.ts` is the single most misleading part of the repo tree. Either run it through a thin JSON bridge to `jeff` one-shot commands, or move it to `experiments/` / delete it.

Explicitly **not recommended yet**: autonomous continuation, broader `/run` action families beyond one more, broad `/memory` CLI, self-improvement loops. All of these are in the research docs as aspirations, and the research docs themselves are honest that JEFF is not ready.

---

## 12. Required Grades

| Dimension | Grade |
|---|---|
| Overall repo reality | **3 / 5** |
| Operator usability | **3 / 5** |
| Architectural integrity | **3 / 5** |
| Implementation maturity | **3 / 5** |
| Docs-vs-reality honesty | **3 / 5** |
| Test confidence | **3 / 5** |

**Rationale:** Every dimension lands at 3 for the same underlying reason. JEFF has a real skeleton and a few real muscles in a posture that is unusually honest for the genre, but the skeleton is larger than the muscle, the claims perimeter is wider than the verified surface, and the test suite does not prove the LLM-side of the pipeline works outside test fixtures. None of the dimensions scores lower than 3 because the core is genuine and not pretending. None scores higher than 3 because across the board the claims, the docs, and the scaffolding outrun what is verified to work today.

**What would move every grade to 4:** execute the five moves in §11.
