# 2step_reseach_transition.md

## Purpose

This document defines a practical transition plan from the current Jeff research synthesis flow to a clearer two-step model:

1. **Step 1 — reasoning/content synthesis**
2. **Step 2 — strict JSON formatting / normalization**

The goal is not to throw away the work already done.
The goal is to build on the current repaired pipeline and convert the existing “primary synthesis + bounded repair” pattern into an explicit, cleaner, more reliable architecture.

---

## Why transition to a two-step model

The current system already proved several things:

- provenance, source identity, persistence, and render flow can work end-to-end
- citation-key remap (`S1..Sn`) was the correct move
- fail-closed boundaries were necessary and correct
- live debug checkpoints were necessary and correct
- a separate repair/formatter adapter was a useful improvement
- many models do **not** reliably return a fully valid/schema-complete research payload in one shot

Real failure patterns seen in live runs included:

- malformed JSON
- fenced JSON
- missing `summary`
- wrong field names like `finding`, `description`, or `source_ref`
- wrong nested field types
- parseable but schema-incomplete JSON

That means the current one-shot contract is still too brittle across models.

A two-step model should reduce that brittleness by separating:
- **thinking/content work**
from
- **strict schema work**

---

## Current state before transition

The current research system already has a strong base:

- bounded source acquisition
- evidence pack construction
- citation-key remap (`S1..Sn`)
- fail-closed provenance validation
- bounded malformed-output repair
- bounded schema-incomplete repair
- optional separate `research_repair` model
- live `/mode debug`
- truthful primary and repair boundaries
- downstream persistence/projection linkage fixes
- pre-Phase-02 refactors:
  - debug helper consolidation
  - `SourceItem` extension
  - discovery vs extraction separation
- real structured JSON requests wired through Ollama provider path

This matters because the transition should **reuse** these parts, not replace them.

---

## Transition principle

Do not treat the current repair path as a mistake.

Treat it as a prototype of the future second step.

Today the system effectively behaves like this:

- try one-shot synthesis
- if malformed or schema-incomplete, run formatter-like repair
- then continue

The transition plan turns that into an explicit architecture:

- **Step 1 always produces a bounded content artifact**
- **Step 2 always converts that artifact into the canonical JSON shape**

That is cleaner than pretending one model call should do everything perfectly.

---

## Target two-step architecture

## Step 1 — Research reasoning/content synthesis

### Responsibility
Produce a bounded intermediate research content artifact from prepared evidence.

### It should do
- answer the question from provided evidence only
- separate findings from uncertainties/inferences/recommendation
- use citation keys only (`S1..Sn`)
- preserve evidence grounding
- stay bounded and source-aware

### It should not do
- own final canonical JSON schema
- own backend source IDs
- be responsible for exact final field naming in the persisted artifact contract
- be treated as the final operator-facing artifact

### Output shape
The intermediate output should be simpler than the current final artifact contract.

Example conceptual shape:
- summary text
- findings list
  - text
  - citation keys
- inferences list
- uncertainties list
- recommendation text or null

This can still be JSON, but it does not need to be the exact final canonical research artifact shape yet.
It is a **content artifact**, not the final support artifact.

---

## Step 2 — Research formatter / normalizer

### Responsibility
Convert the bounded Step 1 content artifact into the exact canonical research JSON contract.

### It should do
- normalize field names
- normalize arrays
- ensure required root fields exist
- enforce exact JSON structure
- preserve only existing content
- preserve citation keys only
- output exactly one JSON object matching the final schema

### It should not do
- add new claims
- invent citations
- reinterpret evidence
- become a second reasoning pass
- hide missing content by hallucinating defaults

This stage is formatter-only.
If required content is truly absent, the flow must fail closed.

---

## What stays the same

The transition should keep these parts intact:

- evidence-first research model
- fail-closed provenance validation
- citation-key remap
- remap from citation keys back to real internal `source_id`
- persistence rules
- projection/render rules
- memory handoff rules
- runtime/config ownership in Infrastructure
- Interface staying downstream
- `/mode debug`
- support-not-truth law for research artifacts

---

## What changes

The main change is the formalization of the middle of the pipeline.

### Current shape
source acquisition -> evidence pack -> primary synthesis -> maybe repair -> remap -> provenance -> persistence/render

### Target shape
source acquisition -> evidence pack -> Step 1 content synthesis -> Step 2 formatter -> remap -> provenance -> persistence/render

The new model makes Step 2 normal instead of exceptional.

---

## Why this is better than the current repair-centric model

### Current model weakness
The current model still assumes:
- primary should ideally return exact final JSON
- formatter/repair is backup behavior

But live behavior showed:
- many models return near-miss output often enough that formatter behavior is effectively normal, not exceptional

### Two-step model benefit
A two-step model:
- matches actual model behavior more honestly
- lowers pressure on the reasoning model
- gives the formatter a narrower, more mechanical job
- should improve cross-model reliability
- makes debugging cleaner because failures split into:
  - content-generation failure
  - formatter/schema failure

---

## Migration goals

The transition should achieve these goals:

1. improve reliability across models
2. reduce dependence on one-shot strict JSON behavior
3. preserve the current validated downstream architecture
4. keep transition bounded and incremental
5. avoid broad rewrites
6. stay compatible with Phase 02 work

---

## Recommended migration strategy

Do not flip everything at once.

Use staged migration.

---

## Phase T0 — Freeze current repaired baseline

Before transition:
- keep the current repaired system stable
- verify working baseline with the most reliable local model setup
- avoid mixing unrelated Phase 02 work into the transition

### Deliverables
- one known-good runtime config
- one docs research sanity check
- one web research sanity check
- debug logs for both

### Recommended baseline
Use the most reliable local model pair available.
From current experience, local Qwen is the best baseline candidate.

---

## Phase T1 — Introduce explicit Step 1 intermediate artifact

### Goal
Create a formal intermediate content artifact shape for research reasoning output.

### Work
- define a new Step 1 output contract in `jeff/cognitive/research/`
- make it narrow and bounded
- keep citation keys only
- do not use real backend `source_id`
- do not couple it to persistence

### Important
This is not the final persisted research artifact.
It is an internal content product between synthesis and formatting.

### Acceptance
- Step 1 contract exists
- tests cover valid/invalid Step 1 content artifacts
- no downstream semantics changed yet

---

## Phase T2 — Convert current repair prompt into explicit formatter-stage prompt

### Goal
Promote the current repair prompt into the standard formatter-stage prompt.

### Work
- create a dedicated formatter request builder
- formatter always receives:
  - Step 1 artifact
  - allowed citation keys
  - exact final schema
- formatter produces final canonical JSON artifact payload

### Important
Do not let formatter invent missing content.
If Step 1 is missing required content, formatter fails closed.

### Acceptance
- formatter stage works as a normal stage, not only as exception path
- formatter prompt is strictly formatting-only
- unit tests prove no semantic widening

---

## Phase T3 — Route normal research through Step 1 -> Step 2 by default

### Goal
Make the two-step flow the standard research path.

### New normal flow
1. source acquisition
2. evidence pack
3. Step 1 content synthesis
4. Step 2 formatter
5. citation remap
6. provenance validation
7. persistence
8. projection/render

### Work
- replace “primary final artifact synthesis” as the default assumption
- use current repair model override as formatter-stage model selection
- preserve existing debug checkpoints and expand them clearly for two-step flow

### Suggested debug checkpoints
- content_synthesis_started
- content_synthesis_failed / succeeded
- formatter_started
- formatter_failed / succeeded
- citation_remap_started / succeeded / failed
- provenance_validation_started / succeeded / failed

### Acceptance
- current behavior remains fail-closed
- two-step flow works end-to-end
- old downstream logic remains intact

---

## Phase T4 — Narrow the exceptional repair path

### Goal
After the formatter becomes a normal stage, shrink the meaning of “repair”.

### Result
Instead of:
- “repair malformed or schema-incomplete primary output”

the system becomes:
- Step 1 content generation
- Step 2 formatter
- optional bounded formatter retry only if truly justified

This makes the architecture cleaner and more honest.

---

## Migration sequence by code area

## 1. Contracts
Add an explicit intermediate Step 1 artifact contract.

Likely location:
- `jeff/cognitive/research/contracts.py`
or a small nearby module if keeping separation cleaner

### Add
- intermediate content artifact dataclass or schema helper
- validators for Step 1 artifact completeness
- no persistence coupling

---

## 2. Synthesis
Split current synthesis responsibility into:
- Step 1 content generation
- Step 2 final formatting

Likely location:
- `jeff/cognitive/research/synthesis.py`

### Refactor target
Current `synthesize_research(...)` should become orchestration of two internal stages rather than “try final artifact generation, then maybe repair”.

---

## 3. Runtime model routing
Use existing runtime purpose override pattern.

Current system already supports:
- `research`
- `research_repair`

Transition target:
- keep `research` for Step 1
- treat current `research_repair` as the official formatter-stage model
- optionally rename later if architecture wants clearer names, but not required immediately

No broad runtime redesign is needed first.

---

## 4. Debug / observability
Preserve the current good work here.

Update debug so operators can tell:
- Step 1 failed
- Step 2 failed
- remap failed
- provenance failed

This should make the flow easier to reason about than the current “primary + repair” language.

---

## 5. Tests
Transition only if tests move with it.

### Add
- Step 1 artifact tests
- Step 2 formatter-stage tests
- end-to-end two-step research flow tests
- fail-closed tests for missing content in Step 1
- formatter non-invention tests

### Preserve
- citation remap tests
- provenance tests
- persistence/projection tests
- debug stream tests

---

## Suggested slice plan

## Slice 1 — Introduce Step 1 intermediate artifact
Smallest slice:
- define the contract
- add validators
- no behavior switch yet

## Slice 2 — Extract dedicated formatter request builder
Smallest slice:
- formatter prompt becomes an explicit first-class path
- still can be used from current repair flow

## Slice 3 — Make formatter stage explicit in synthesis orchestration
Smallest slice:
- current primary+repair flow becomes content+formatter flow
- keep downstream unchanged

## Slice 4 — Rename/reframe debug checkpoints
Smallest slice:
- make debug language reflect actual architecture
- keep same downstream truthfulness

## Slice 5 — Optional cleanup of old repair terminology
Smallest slice:
- reduce “repair” naming where it no longer matches reality

---

## Risks

## Risk 1 — Formatter silently becomes a second reasoner
If the formatter is allowed too much freedom, the second step stops being safe.

### Mitigation
- strict prompt
- no new claims
- no new citations
- fail closed on missing content

## Risk 2 — Intermediate artifact becomes underspecified
If Step 1 contract is vague, formatter has to guess.

### Mitigation
- define Step 1 contract clearly
- validate it before formatter runs

## Risk 3 — Too much change at once
If we mix this transition with Phase 02 provider work, debugging gets messy.

### Mitigation
- do transition slices before or separate from larger Phase 02 discovery/extraction slices

## Risk 4 — Duplicate validation logic
If the transition adds parallel validators everywhere, code becomes ugly.

### Mitigation
- use shared helpers
- keep validation ownership clean
- respect the pre-Phase-02 refactor direction

---

## Recommended model roles after transition

### Step 1 model
Best at:
- reasoning from evidence
- summarizing
- separating findings / uncertainties / inferences

### Step 2 model
Best at:
- strict JSON output
- formatting discipline
- field normalization
- schema compliance

These may be:
- the same model in smaller setups
- different models in more robust setups

The architecture should support both.

---

## Suggested runtime baseline during transition

For stability:
- use the most reliable local model as the default Step 1 model
- use the most reliable formatter-capable local model as Step 2 model

Based on current practical behavior, local Qwen is the strongest baseline candidate.
Cloud models can stay experimental until proven stable under the new flow.

---

## Acceptance criteria for the transition

The transition is successful when:

1. Step 1 and Step 2 are explicit stages
2. one-shot strict JSON is no longer the core assumption
3. formatter does not invent new content
4. citation-key discipline remains intact
5. remap/provenance/persistence/render stay unchanged
6. `/mode debug` clearly separates stage failures
7. the fail rate for schema-complete final artifacts drops materially
8. local reliable models can run the flow consistently

---

## Recommended immediate next step

Do **not** jump straight into a broad rewrite.

Start with:
1. explicit Step 1 intermediate artifact contract
2. explicit formatter request builder based on the current repair prompt
3. keep the current downstream validated pipeline unchanged

That gives the cleanest bridge from today’s repaired system to a proper two-step research architecture.

---

## Final recommendation

The transition should happen incrementally.

You already did the hard stabilization work:
- truthful boundaries
- citation safety
- persistence safety
- debug visibility
- provider structured-output fix

Now the next mature step is to stop pretending the formatter is only an exception path and make it an explicit second stage.

That should improve reliability more honestly than trying to force every primary model to produce the final perfect JSON artifact in one shot.
