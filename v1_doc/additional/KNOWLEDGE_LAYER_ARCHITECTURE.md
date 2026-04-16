# KNOWLEDGE_LAYER_ARCHITECTURE.md

Status: implementation architecture proposal for Jeff Compiled Knowledge Layer  
Authority: subordinate to `ARCHITECTURE.md`, `VISION.md`, `CONTEXT_SPEC.md`, `PLANNING_AND_RESEARCH_SPEC.md`, `MEMORY_SPEC.md`, `INTERFACE_OPERATOR_SPEC.md`, `CORE_SCHEMAS_SPEC.md`, and `TESTS_PLAN.md`  
Purpose: define a concrete, buildable compiled-knowledge layer for Jeff that sits between raw source custody and selective memory, without changing canonical truth, memory, research, or interface law

---

## 1. Why this document exists

Jeff already has:
- canonical truth in state
- source-aware research law
- selective non-truth memory law
- a growing need to ingest and preserve raw sources

What Jeff does **not** yet have as a first-class implementation architecture is the layer in between:
- not raw source custody
- not memory
- not current truth
- not merely one-off research output

That missing layer is the **compiled knowledge layer**.

This document exists to define that layer concretely.

It turns higher-level Jeff law into a buildable support architecture for:
- source digests
- topic notes
- concept notes
- comparison notes
- contradiction notes
- open-questions notes
- related-topic linking
- stale detection and rebuild
- bounded handoff to memory

This layer makes Jeff more useful without weakening truth discipline.

---

## 2. Core architectural position

The compiled knowledge layer sits **between** source custody and memory.

Conceptually:

```text
raw source custody
  -> extraction / evidence preparation
  -> compiled knowledge artifacts
  -> optional memory handoff
```

It is:
- richer than raw sources
- broader than memory
- more navigable than one-off research outputs
- still only a support layer

It is not:
- canonical truth
- memory
- a transition system
- a governance system
- a hidden planner
- a generic dump of summaries

---

## 3. Core design decision

Jeff will treat compiled knowledge as its own distinct support layer.

That means:

- raw source custody remains Jeff-managed storage outside the operator-facing project tree
- compiled knowledge lives as durable project-scoped support artifacts
- memory remains selective and narrower than compiled knowledge
- current truth remains only in canonical state

This separation is intentional.

If Jeff skips this layer, it gets trapped in a bad tradeoff:
- either re-read raw sources too often
- or shove too much into memory

Both are bad.

---

## 4. What this layer is

The compiled knowledge layer is Jeff's durable, browsable, source-linked support layer.

It owns:
- source digests
- topic notes
- concept notes
- comparison notes
- contradiction notes
- open-questions notes
- topic relationship links
- note staleness tracking
- note rebuild and refresh logic
- note lineage
- note-to-source provenance preservation
- memory handoff signals

It is meant to make Jeff better at:
- answering questions against prior work
- reusing prior research
- seeing contradictions and gaps
- navigating large project knowledge
- reducing repeated raw-source reading

---

## 5. What this layer is not

This layer is not:

- current truth
- memory
- raw source custody
- execution outcome truth
- approval or readiness
- operator-facing truth status
- a replacement for bounded research
- a replacement for context assembly
- a replacement for canonical state
- an excuse to let the model quietly rewrite history

Compiled knowledge is a durable **support** layer only.

---

## 6. Design principles

### 6.1 Compiled knowledge is not memory
Compiled knowledge may be large, thematic, and navigable.
Memory is selective, continuity-oriented, and narrower.

### 6.2 Compiled knowledge is not truth
A topic note can be useful and still not be current truth.
Truth remains in state.

### 6.3 Provenance must survive
Every meaningful compiled artifact must point back to the source materials and/or upstream artifacts that support it.

### 6.4 Findings, inference, and recommendation must stay distinct
Compiled notes must not blur:
- what a source directly supports
- what Jeff infers
- what Jeff recommends doing next

### 6.5 Contradiction must stay visible
This layer must not smooth real disagreement into fake clarity.

### 6.6 Staleness must be explicit
A useful note can become stale.
Jeff must detect and label that rather than pretend freshness.

### 6.7 Project scope remains hard
Knowledge artifacts are project-scoped in v1.
Jeff does not get a free global knowledge soup.

### 6.8 Rebuildability matters
Compiled knowledge should be regenerable from preserved sources and lineage.
It must not become opaque magic.

---

## 7. Why this layer is needed

Without compiled knowledge, Jeff has three bad choices:

### 7.1 Read raw sources every time
This is slow, repetitive, and costly.

### 7.2 Overwrite knowledge into memory
This bloats memory and breaks its intended role.

### 7.3 Keep only one-off research artifacts
This leaves Jeff with fragmented knowledge and weak navigability.

Compiled knowledge is the missing middle:
- richer than memory
- cleaner than raw sources
- more reusable than one-off output

---

## 8. High-level architecture

```text
raw source store
    |
    v
+-----------------------------+
| Extraction / Evidence Prep  |
+-----------------------------+
    |
    v
+-----------------------------+
| Knowledge Compiler          |
| - source digest             |
| - topic note                |
| - concept note              |
| - comparison note           |
| - contradiction note        |
| - open questions note       |
+-----------------------------+
    |
    v
+-----------------------------+
| Knowledge Registry          |
| - artifact identity         |
| - lineage                   |
| - staleness                 |
| - related topics            |
+-----------------------------+
    |
    +------------------> retrieval / context support
    |
    +------------------> optional memory handoff signals
    |
    +------------------> maintenance / rebuild jobs
```

---

## 9. Knowledge artifact families

Jeff should support a bounded set of compiled knowledge artifact families.

### 9.1 `source_digest`
Purpose:
- compress one source into a useful support artifact

Should include:
- source summary
- important claims
- key evidence-bearing points
- uncertainty or extraction caveats
- provenance back to the source

### 9.2 `topic_note`
Purpose:
- summarize one topic across multiple sources

Should include:
- what the topic is
- the major supported points
- what is contested
- what remains unresolved
- which sources matter most

### 9.3 `concept_note`
Purpose:
- define and explain one concept in a reusable way inside project context

Should include:
- concept definition
- why it matters
- related concepts
- project-specific usage notes
- source support

### 9.4 `comparison_note`
Purpose:
- compare alternatives, approaches, tools, architectures, or positions

Should include:
- compared options
- comparison criteria
- strengths and weaknesses
- contradictions or caveats
- recommendation only if supported

### 9.5 `contradiction_note`
Purpose:
- preserve and focus real disagreement rather than hide it

Should include:
- conflicting claims
- which sources support each side
- conflict type
- whether conflict is unresolved or partially explained

### 9.6 `open_questions_note`
Purpose:
- record what still needs research or clarification

Should include:
- unresolved questions
- why they matter
- what is missing
- suggested follow-up paths

### 9.7 `topic_map`
Purpose:
- provide a bounded map of related topics, notes, and source clusters

This can be added later if the first implementation slice wants to stay smaller.

---

## 10. Artifact identity and scope

Each knowledge artifact should have a Jeff-issued opaque `artifact_id`.

Required scope fields:
- `project_id`
- optional `work_unit_id`
- optional `run_id`

Rules:
- project scope is mandatory in v1
- cross-project compiled artifacts are deferred
- a knowledge artifact may derive from multiple sources, but it still belongs to one project scope

---

## 11. Recommended artifact schema shape

Suggested shape:

```json
{
  "artifact_id": "art_...",
  "artifact_type": "topic_note",
  "project_id": "proj_...",
  "work_unit_id": null,
  "run_id": null,
  "title": "Memory vs Compiled Knowledge",
  "summary": "Short bounded summary.",
  "sections": [
    {
      "heading": "Key Points",
      "body": "..."
    }
  ],
  "source_refs": [
    {
      "source_id": "src_..."
    }
  ],
  "derived_from_artifact_ids": [],
  "related_artifact_ids": [],
  "staleness_status": "fresh",
  "generator_version": "1.0",
  "generated_at": "2026-04-16T08:00:00Z",
  "updated_at": "2026-04-16T08:00:00Z",
  "schema_version": "1.0"
}
```

This is a recommended implementation shape, not a final shared-schema law document.

---

## 12. Required content rules by artifact family

### 12.1 Every compiled artifact must be bounded
It should represent one coherent unit, not a sprawling book.

### 12.2 Every compiled artifact must preserve provenance
Useful content must point back to sources and/or upstream artifacts.

### 12.3 Every compiled artifact must preserve support distinctions
It must remain possible to tell:
- supported claim
- inference
- unresolved uncertainty
- recommendation

### 12.4 Every compiled artifact must remain inspectable
A future reader must be able to understand what the note is and where it came from without reopening everything blindly.

### 12.5 Every compiled artifact must remain regenerable
Jeff should be able to rebuild or refresh the artifact later.

---

## 13. Compilation pipeline

The compiled knowledge layer should use a bounded multi-step pipeline.

### 13.1 Source selection
Choose relevant stored sources and/or upstream research artifacts.

### 13.2 Evidence preparation
Extract or select the evidence-bearing parts that matter.

### 13.3 Claim grouping
Group related points and isolate contradictions.

### 13.4 Artifact generation
Produce the compiled knowledge artifact with explicit structure.

### 13.5 Provenance binding
Attach the relevant source refs and upstream artifact refs.

### 13.6 Note classification
Decide which artifact family the note belongs to.

### 13.7 Registry write
Persist the note, lineage, relationships, and staleness metadata.

### 13.8 Optional memory handoff signal
Emit support signals for memory review, without creating memory directly.

---

## 14. Artifact lineage model

Compiled knowledge must preserve lineage explicitly.

Useful lineage fields include:
- `derived_from_source_ids`
- `derived_from_artifact_ids`
- `supersedes_artifact_id`
- `superseded_by_artifact_id`
- `rebuilt_from_artifact_id`

Rules:
- rebuild must not silently erase lineage
- replacement should preserve traceability
- old artifacts may remain inspectable even when superseded

---

## 15. Relationship graph and linking

This layer should preserve useful relationships such as:

- source digest -> source
- topic note -> source digests
- topic note -> related topic notes
- concept note -> topic notes
- comparison note -> compared concepts or topics
- contradiction note -> affected notes
- open-questions note -> topic or concept notes

This relationship graph is for support navigation, not for canonical truth.

---

## 16. Staleness model

Compiled knowledge can become stale for many reasons.

### 16.1 Causes of staleness
- newer revision of a source exists
- new relevant source was ingested
- upstream digest changed materially
- a contradiction appeared
- prior support became weak or outdated
- topic note is too old for a freshness-sensitive domain

### 16.2 Staleness statuses
Recommended statuses:
- `fresh`
- `stale_review_needed`
- `stale_rebuild_needed`
- `superseded`
- `quarantined`

### 16.3 Rules
- stale notes must not silently pretend freshness
- stale notes may still be retrievable as support, but labeled
- stale notes may trigger rebuild jobs

---

## 17. Refresh and rebuild rules

Jeff should support bounded maintenance behavior.

### 17.1 Refresh
A lighter update where support expanded but the note identity still stands.

### 17.2 Rebuild
A stronger regeneration because the previous artifact is no longer good enough.

### 17.3 Supersession
Used when a new artifact materially replaces an old one.

Rules:
- do not overwrite silently
- preserve lineage
- preserve operator inspectability

---

## 18. Relationship to bounded research

Compiled knowledge is downstream of research and source preparation.

Research still owns:
- bounded inquiry
- evidence extraction for a question
- direct research outputs
- support for proposal or planning

Compiled knowledge owns:
- durable thematic support organization across time
- browsable project knowledge
- cross-source note maintenance

Research and compiled knowledge must not collapse into one blob.

---

## 19. Relationship to context assembly

Compiled knowledge is eligible support for context assembly.

But context remains truth-first.

That means context priority still works like this:
1. canonical truth
2. governance-relevant truth where needed
3. committed memory
4. compiled knowledge artifacts
5. raw sources when necessary

Compiled knowledge must not outrank truth.
It must not silently replace memory.
It must not let raw-source or old-note residue masquerade as current truth.

---

## 20. Relationship to memory

Compiled knowledge is broader than memory and upstream of memory handoff.

Rules:
- compiled knowledge may suggest what seems reusable
- compiled knowledge may provide support for memory work
- compiled knowledge does **not** create memory candidates
- compiled knowledge does **not** commit memory
- Memory remains the only owner of memory candidate creation, validation, commit, and `memory_id` issuance

This boundary is hard.

---

## 21. Relationship to operator surfaces

Compiled knowledge can later support operator surfaces such as:
- topic view
- source digest view
- contradiction view
- knowledge gaps view
- rebuild status view
- related topics navigation

Possible future commands:
- `/topic show <topic>`
- `/topic related <topic>`
- `/knowledge gaps`
- `/knowledge lint`
- `/artifact rebuild <artifact_id>`

These remain support surfaces, not truth surfaces.

---

## 22. Recommended persistence placement

Compiled knowledge should live in a durable project-scoped storage location distinct from raw source custody and distinct from memory.

One reasonable direction:

```text
projects/
  <project_id>/
    research/
      knowledge/
        <artifact_id>.json
```

or

```text
projects/
  <project_id>/
    artifacts/
      knowledge/
        <artifact_id>.json
```

The exact placement can be decided later based on how the project tree evolves.

The important rule is:
- compiled knowledge belongs in operator/project-visible support storage
- raw source custody stays in Jeff-managed internal source storage outside the project tree

---

## 23. Recommended module layout

Suggested package structure:

```text
jeff/knowledge/
  __init__.py
  ids.py
  models.py
  compiler.py
  digests.py
  topics.py
  concepts.py
  comparisons.py
  contradictions.py
  open_questions.py
  lineage.py
  linking.py
  staleness.py
  registry.py
  retrieval.py
  maintenance.py
  telemetry.py
  api.py
```

Suggested roles:
- `compiler.py`: orchestration of note generation
- `digests.py`: source digest generation
- `topics.py`: topic note generation
- `concepts.py`: concept note generation
- `comparisons.py`: comparison note generation
- `contradictions.py`: contradiction note generation
- `open_questions.py`: unresolved-questions artifacts
- `lineage.py`: supersession and derivation tracking
- `linking.py`: related-topic and artifact relationships
- `staleness.py`: freshness and rebuild decisions
- `registry.py`: persistence and index registry
- `retrieval.py`: compiled-knowledge retrieval for context
- `maintenance.py`: rebuild and linting jobs
- `telemetry.py`: observability and audit
- `api.py`: public compiled-knowledge contract

---

## 24. Knowledge retrieval role

This layer should help Jeff answer questions more efficiently.

Retrieval should support:
- exact artifact fetch by id
- topic-oriented lookup
- relationship expansion
- freshness-aware filtering
- contradiction-aware fetch
- bounded packaging for context assembly

Retrieval should prefer:
- fresh relevant notes
- notes with strong provenance
- notes with tighter scope match

Retrieval should avoid:
- dumping too many overlapping notes
- stale notes without labeling
- using compiled knowledge when raw-source verification is clearly required

---

## 25. Maintenance and linting jobs

This layer should support bounded maintenance jobs such as:

- stale topic note detection
- stale digest detection after source revision
- provenance gap scan
- overlapping note detection
- contradiction sweep
- orphan note detection
- related-topic rebuild
- rebuild candidate suggestion
- note quality lint

These jobs improve the layer over time without turning it into an uncontrolled autonomous system.

---

## 26. Failure modes

This layer must explicitly guard against:

### 26.1 Hallucinated synthesis
A note says more than the sources support.

### 26.2 Provenance loss
The note becomes useful-looking but untraceable.

### 26.3 Contradiction suppression
The layer smooths disagreement into fake confidence.

### 26.4 Memory blur
The layer starts storing continuity-like statements as if they were memory.

### 26.5 Truth blur
The layer starts sounding like current truth.

### 26.6 Stale-note optimism
Old notes stay unlabeled and mislead later context.

### 26.7 Note duplication
Multiple notes cover the same thing with no relationship discipline.

### 26.8 Weak-source dominance
A poor source drives the note because it was easier to summarize.

---

## 27. Security and safety posture

This is not a security spec, but the layer should assume:
- extracted content may be noisy
- source metadata may be misleading
- generated summaries may overstate support
- stale knowledge may look cleaner than fresh uncertainty

Therefore:
- provenance must be mandatory
- rebuild must be explicit
- stale labeling must be explicit
- contradiction visibility must be preserved
- support language must remain disciplined

---

## 28. Test strategy

Minimum acceptance coverage should include:

- source digest preserves source refs
- topic note preserves contradictions rather than hiding them
- concept note remains bounded and linked
- comparison note preserves compared alternatives clearly
- stale detection triggers when newer source revision arrives
- rebuild preserves lineage
- retrieval does not outrank truth-first context rules
- memory handoff does not create memory directly
- duplicate topic note detection works
- related-topic linking remains project-scoped
- stale artifacts remain labeled on retrieval

This layer needs anti-drift tests because it is one of the easiest places for semantic sludge to form.

---

## 29. Recommended first implementation slice

The first useful slice should stay narrow and disciplined:

1. `source_digest`
2. `topic_note`
3. artifact identity and registry
4. source refs and provenance binding
5. basic related-artifact links
6. basic staleness flagging
7. basic retrieval for context support
8. optional memory handoff signal
9. anti-drift tests

Do not try to build the full knowledge garden on day one.
Get the first two artifact families right first.

---

## 30. Open edges and deferred work

Deferred beyond the initial slice:
- richer topic maps
- visual knowledge graphs
- multimodal knowledge notes from images and figures
- slide/report generation directly from topic notes
- more advanced contradiction clustering
- operator editing workflows over compiled notes
- cross-project knowledge federation
- richer timeline-aware note refresh policies

---

## 31. Final architecture summary

Jeff should treat compiled knowledge as a first-class support layer between raw source custody and selective memory.

That means:

- raw sources stay preserved under custody
- compiled knowledge turns them into durable navigable support
- memory remains narrower and selective
- truth remains elsewhere
- provenance survives
- contradictions remain visible
- stale knowledge is labeled
- rebuild is possible
- memory handoff stays bounded and non-authoritative

The compiled knowledge layer is what lets Jeff accumulate understanding without turning raw source storage into sludge or memory into a junk drawer.
