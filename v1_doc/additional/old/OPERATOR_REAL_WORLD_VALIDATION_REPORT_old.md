# OPERATOR_REAL_WORLD_VALIDATION_REPORT

## 1. Purpose

- This run tested Jeff as an operator-facing CLI tool through the real documented entrypoint `python -m jeff` and one-shot CLI commands via `python -m jeff --command ...`.
- This run covered startup/orientation, scoped inspection surfaces, docs research, web research, selection review visibility, override attempts, downstream review-chain visibility, and evaluation visibility.
- Operator-style in this run meant: use the real CLI surface first, do not import backend internals to fake successful flows, and treat anything not honestly reachable from the CLI as not operator-available.
- I did not unit-test backend modules, manually stitch proposal/selection/evaluation objects together, or patch Jeff to make the demo path look better.
- I did not fully drive the live interactive shell through a persistent TTY because the current automation harness provides EOF immediately after startup; I still started the real interactive entrypoint and used the real one-shot CLI extensively.

## 2. Environment and startup path

- Repo: `C:\DATA\PROJECTS\JEFF`
- Date of validation: `2026-04-17`
- Python entrypoint used: `python -m jeff`
- Runtime config present: `jeff.runtime.toml`
- Research artifact root configured: `.jeff_runtime/research_artifacts`
- Runtime adapter config loaded by Jeff: `ollama_default`, `ollama_research`, `ollama_formatter`
- Local runtime availability:
  - `python -m jeff --bootstrap-check` reported runtime config loaded and research artifact store ready.
  - `Invoke-RestMethod http://127.0.0.1:11434/api/tags` showed Ollama responding and listing models including `gemma4:31b-cloud` and `qwen3:8b`.
- Startup path behavior:
  - `python -m jeff` displayed the interactive shell banner and prompt cleanly:
    - `Jeff v1 interactive shell`
    - startup explanation
    - command-driven hint
    - prompt `jeff:/>`
  - In this harness the process then received EOF immediately, so I could not keep a real sticky interactive session open.
- Practical startup judgment:
  - Startup messaging is clear.
  - The actual operator flow becomes awkward as soon as scope must persist across commands, because one-shot mode resets state every invocation.

### Minimal fixes made during operator validation

- None.

## 3. Exact command log

### Startup and orientation

- `python -m jeff --help`
- `python -m jeff --bootstrap-check`
- `python -m jeff`
- `python -m jeff --command "/help"`
- `python -m jeff --command "/project list"`
- `python -m jeff --command "/scope show"`
- `python -m jeff --command "/project use project-1"`
- `python -m jeff --command "/work list"`
- `python -m jeff --command "/work use wu-1"`
- `python -m jeff --command "/run list"`
- `python -m jeff --command "/show"`
- `python -m jeff --command "/show run-1"`
- `python -m jeff --command "/show run-1" --json`
- `python -m jeff --command "/trace run-1"`
- `python -m jeff --command "/lifecycle run-1"`

### Research

- `python -m jeff --% --command "/research docs \"What does Jeff currently document as the startup path and CLI-first posture?\" README.md v1_doc/CLI_V1_OPERATOR_SURFACE.md --handoff-memory"`
- `python -m jeff --json --% --command "/research docs \"Startup path?\" README.md"`
- `python -m jeff --json --% --command "/research docs \"CLI help surface?\" v1_doc/CLI_V1_OPERATOR_SURFACE.md"`
- `python -m jeff --json --% --command "/research docs \"Jeff CLI startup and scope?\" README.md v1_doc/CLI_V1_OPERATOR_SURFACE.md"`
- `python -m jeff --json --% --command "/research docs \"What is this prompt for?\" PROMPTS/evaluation/JUDGMENT.md"`
- `python -m jeff --json --% --command "/research docs \"What is shared rules?\" PROMPTS/research/SHARED_RULES.md"`
- `python -m jeff --% --command "/research docs \"What is shared rules?\" PROMPTS/research/SHARED_RULES.md --handoff-memory"`
- `python -m jeff --% --command "/research docs \"Missing path test\" missing-file-does-not-exist.md"`
- `python -m jeff --% --command "/research docs \"No input path test\""`
- `python -m jeff --json --% --command "/research web \"Jeff CLI startup path\" \"Jeff README python -m jeff\""`
- `python -m jeff --% --command "/research web \"No query test\""`

### Selection / review chain / request surfaces

- `python -m jeff --command "/selection show run-1"`
- `python -m jeff --command "/selection show run-1" --json`
- `python -m jeff --% --command "/selection override proposal-1 --why \"Operator wants the original choice recorded explicitly.\" run-1"`
- `python -m jeff --% --command "/selection override proposal-999 --why \"Invalid proposal id test.\" run-1"`
- `python -m jeff --command "/approve run-1"`
- `python -m jeff --command "/reject run-1"`
- `python -m jeff --command "/retry run-1"`
- `python -m jeff --command "/approve run-999"`

### Proposal / evaluation reachability checks

- `python -m jeff --command "/proposal show run-1"`
- `python -m jeff --command "/evaluation show run-1"`

### Artifact inspection

- `Get-ChildItem -Recurse .jeff_runtime\research_artifacts`
- `Get-Content .jeff_runtime\research_artifacts\research-6408b036a1b682a4.json`

## 4. Results by layer

### Research

- Reachable through CLI? `partial`

#### What worked

- The docs research command is genuinely operator-reachable.
- Ad-hoc research without preselected scope works. Jeff truthfully anchored the run into `project_id=general_research` with an auto-created work unit and run.
- Small bounded local document inputs succeeded.
- Successful runs rendered readable operator output with:
  - artifact id
  - question
  - summary
  - findings
  - uncertainties
  - memory handoff disposition
- Artifact persistence is real. Successful docs research created files such as:
  - `.jeff_runtime/research_artifacts/research-6408b036a1b682a4.json`
- The persisted artifact is inspectable and contains summary, findings, uncertainties, source items, and scope ids.
- Memory handoff visibility is truthful. On the successful handoff test Jeff explicitly said `memory_handoff=defer` and gave the reason.

#### What failed

- Docs research on larger repo-facing questions was unstable:
  - one attempt failed with `summary must stay concise and below 200 characters`
  - multiple bounded repo-doc attempts timed out against `ollama_research`
- Web research reached the real runtime but timed out on the bounded test query.
- Failed docs/web runs did not persist artifacts, which is correct, but the operator has no high-level command to list successful artifacts by run.

#### What was confusing

- PowerShell quoting is fragile for research commands because the whole slash command must survive as one `--command` argument and then Jeff parses it again internally.
- The missing-path docs failure was not operator-friendly. Jeff reported `document evidence pack requires at least one document source` instead of naming the bad path.
- One-shot mode has no stable way to enable debug mode for the next command, so the advertised `/mode debug` surface is not very useful outside a true interactive shell.
- Artifact discovery is filesystem-first. The CLI shows the artifact id but not the exact artifact file path.

#### What is implemented in backend but not honestly operator-available yet

- Nothing extra needed to be inferred here. The main issue is reliability and inspectability of the existing CLI path, not complete absence of a research command.

### Proposal

- Reachable through CLI? `no`

#### What worked

- The bootstrapped demo run exposes some proposal-adjacent downstream facts in `/show run-1`, such as `selected_proposal_id=proposal-1`.

#### What failed

- There is no proposal command in `/help`.
- `/proposal show run-1` returns `unsupported command`.
- I found no lawful CLI path that generates or inspects a ProposalResult directly.
- The help text's "normal flow" ends at `/inspect`, `/trace`, and `/lifecycle`; it does not expose proposal output.

#### What was confusing

- `/show run-1` implies proposal happened inside the demo flow, but the operator cannot inspect the proposal object itself.
- The spec docs talk about richer flow semantics than the shipped CLI actually exposes.

#### What is implemented in backend but not honestly operator-available yet

- The backend clearly has a proposal layer and proposal modules, but there is no real CLI/operator surface to generate, inspect, or review proposal output.

### Selection / Override / Review chain

- Reachable through CLI? `partial`

#### What worked

- `/selection show run-1` is reachable.
- It truthfully shows the original selection result:
  - disposition `selected`
  - `selected_proposal_id=proposal-1`
- It also truthfully shows that the review chain is absent:
  - override missing
  - resolved choice missing
  - action formation missing
  - governance handoff missing
- Override attempts fail closed and do not claim success.
- Re-running `/selection show run-1` after failed override attempts still shows the original selection unchanged.

#### What failed

- `/selection override ... run-1` is not usable on the shipped startup demo path because Jeff reports `no selection review data is available for run run-1`.
- Because the initial selection review chain is missing, I could not lawfully validate:
  - successful override recording
  - refreshed resolved choice
  - refreshed action formation
  - refreshed governance handoff
  - invalid proposal-id rejection against a populated considered set
- `/approve`, `/reject`, and `/retry` are present but unavailable for the demo run because `current routed_outcome is none`.

#### What was confusing

- `/help` advertises `/selection show` and `/selection override` as real operator commands, but the default demo run does not carry the review-chain data needed to make override usable.
- `/show run-1` suggests a completed proposal-selection-action-evaluation pipeline, while `/selection show run-1` immediately reveals that the operator cannot inspect the actual downstream review chain behind that summary.

#### What is implemented in backend but not honestly operator-available yet

- The backend clearly has code for:
  - operator overrides
  - resolved downstream choice
  - effective proposal materialization
  - action formation
  - governance handoff
- I found no lawful CLI path from the shipped startup/demo context that materializes the initial `selection_reviews` record required to expose that chain to a real operator.

### Evaluation

- Reachable through CLI? `partial`

#### What worked

- `/show run-1` exposes an operator-visible evaluation summary:
  - active stage `evaluation`
  - `evaluation_verdict=acceptable`
- `/trace run-1` and `/lifecycle run-1` show evaluation as the terminal stage in the demo flow.

#### What failed

- There is no evaluation command in `/help`.
- `/evaluation show run-1` returns `unsupported command`.
- There is no dedicated operator surface to inspect evaluation inputs, reasoning summary, evidence basis, or output object.

#### What was confusing

- The operator can see that evaluation happened, but not what exactly was evaluated or why the verdict was acceptable.

#### What is implemented in backend but not honestly operator-available yet

- The backend has an evaluation layer, but the CLI exposes only a thin derived verdict summary, not a real evaluation review surface.

## 5. Truthfulness assessment

- Original selection vs override:
  - Partially truthful.
  - Jeff clearly preserved the original selection truth and clearly stated that no review chain existed.
  - I could not validate the successful override distinction because no real CLI path exposed an initial review chain to override.
- Action formed vs governance evaluated:
  - Partially truthful.
  - `/show run-1` separates `execution_status`, `outcome_state`, and `evaluation_verdict`.
  - `/selection show run-1` also refuses to invent action/governance records when they are missing.
- Governance evaluated vs execution performed:
  - Truthful in the demo summary view.
  - `/show run-1` keeps `governance_outcome`, `execution_status`, `outcome_state`, and `evaluation_verdict` as distinct derived fields.
- Real failure vs missing data vs unsupported path:
  - Mostly truthful.
  - Good examples:
    - missing scope errors are explicit
    - unsupported proposal/evaluation commands are explicit
    - missing review chain is explicit
    - research timeout JSON is explicit about adapter/model/base URL
  - Weak example:
    - missing docs path error is too generic and obscures the actual operator mistake
- Overall truthfulness judgment:
  - Jeff is better at admitting missing data than at giving the operator a usable path to inspect the missing layer.

## 6. Operator-friendliness assessment

- Startup: `3/5`
  - The banner, prompt, and `/help` orientation are clear.
  - The practical flow degrades quickly because one-shot mode resets scope and the interactive shell is the only obvious way to make scope comfortable.
- Research docs: `2/5`
  - Small bounded inputs work and persist artifacts honestly.
  - Larger, more realistic repo-facing inputs were unreliable due to timeouts and one contract-validation failure.
  - Quoting and missing-path error quality are weak.
- Research web: `1/5`
  - The command is exposed and reaches the runtime.
  - The bounded real test timed out and produced no usable research artifact.
- Proposal visibility: `1/5`
  - No real operator surface exists.
  - Proposal is implied by downstream fields but not inspectable.
- Selection review: `2/5`
  - The CLI truthfully shows the original selection and truthfully shows the review chain is absent.
  - That is honest, but not enough to make the selection review flow actually usable.
- Override entry: `1/5`
  - The command exists, but the default real CLI path does not provide the required review-chain data.
  - PowerShell quoting also adds friction.
- Overall CLI ergonomics: `2/5`
  - Discoverability is decent.
  - Stateful operator work is awkward outside a persistent shell, and several advertised flows stop at shallow summaries or missing-data walls.

## 7. Hard failures and gaps

### True bugs

- Docs research can fail after synthesis with `summary must stay concise and below 200 characters` instead of repairing or truncating output.
- Bounded docs and web research against the configured `ollama_research` adapter timed out on realistic repo-sized/operator-sized prompts.
- Missing-doc-path feedback is too generic to be a good operator error.

### Missing operator surfaces

- No proposal command or proposal inspect surface.
- No evaluation command or evaluation inspect surface.
- No lawful CLI path found to materialize the initial selection review chain for the shipped demo run.
- No real operator path found to generate proposal/selection from a fresh objective in the current CLI. `/run` currently exposes list/use semantics, not a usable objective-launch flow.

### Confusing UX

- `/help` presents a multi-step scoped workflow, but one-shot mode cannot carry the scope across invocations.
- Research and override commands are awkward to quote from PowerShell.
- `/show run-1` suggests more end-to-end inspectability than the operator actually gets from `/selection show run-1`.
- Artifact persistence is real but not surfaced through a CLI artifact-list or artifact-open command.

### Backend-implemented but operator-inaccessible capabilities

- Proposal generation/review backend
- Selection override downstream recomputation chain
- Action formation and governance handoff review chain
- Evaluation layer beyond a single verdict field

## 8. Recommended next fixes

### Top 3 operator-facing fixes

1. Make scoped CLI work practical outside a live TTY.
   - Add explicit one-shot scope selectors, or a batch/multi-command mode, or both.
2. Make the selection review chain truly operator-available on the demo path.
   - Either attach it to the startup demo run or provide a lawful command that materializes it from existing run truth.
3. Add direct inspect commands for proposal and evaluation.
   - The operator should not have to infer those layers from `/show`.

### Top 3 backend/flow fixes blocking operator usefulness

1. Stabilize research runtime on realistic inputs.
   - Current timeouts make docs/web research unreliable as an operator tool.
2. Repair research output-contract handling.
   - Overlong summary output should be repaired automatically or reported with a clearer recovery path.
3. Provide a real operator flow from objective -> proposal -> selection -> review chain.
   - Right now the shipped CLI mostly inspects a canned result instead of letting the operator drive the flow.

## 9. Final verdict

- Is Jeff usable today as a real operator tool?
  - Narrowly, yes, for startup inspection, demo-flow inspection, and small bounded docs research.
  - Broadly, no, not yet.
- For which flows?
  - `/help`, `/project list`, `/scope show`, `/show run-1`, `/trace run-1`, `/lifecycle run-1`
  - small ad-hoc docs research with artifact persistence
  - truthful failure reporting for some missing-data and unsupported-path cases
- What is still too fragile or incomplete?
  - realistic docs/web research reliability
  - proposal visibility
  - real operator-driven proposal/selection flow
  - usable selection override and downstream review-chain refresh
  - real evaluation inspectability
  - non-interactive scope ergonomics

- Blunt summary:
  - Jeff currently feels like a truthful demo inspector with a partially working research side path, not yet like a full real-world operator console for the whole cognitive stack.
