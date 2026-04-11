# MEMORY_ARCHITECTURE.md

Status: implementation architecture proposal for Jeff Memory  
Authority: subordinate to `MEMORY_SPEC.md`, `CONTEXT_SPEC.md`, `PLANNING_AND_RESEARCH_SPEC.md`, `CORE_SCHEMAS_SPEC.md`, `ARCHITECTURE.md`, `STATE_MODEL_SPEC.md`, `TRANSITION_MODEL_SPEC.md`, and `TESTS_PLAN.md`  
Purpose: define a concrete, buildable architecture for Jeff's Memory layer and its handoff boundaries with research artifacts, source-backed history, and future autonomous brief workflows without changing canonical memory law

---

## 1. Why this document exists

Jeff already has canonical memory law. That law is the hard boundary:
- memory is durable non-truth continuity
- memory is selective, structured, and support-oriented
- only Memory creates memory candidates
- only committed `memory_id` values may be referenced canonically
- current truth lives in canonical state, not in memory
- context reads truth first and memory second
- project remains the hard isolation boundary

This document does not redefine those rules. It turns them into a buildable architecture.

It also settles one important practical design point:
- Jeff must distinguish **memory** from **research history / artifact archive**
- not everything Jeff finds should become memory
- source-backed research outputs must remain inspectable and traceable even when only a distilled subset is worth remembering

That distinction matters for future Jeff capabilities such as:
- internet research with source-backed outputs
- local-document research with provenance
- recurring market/news/project briefs
- future autonomous scheduled research runs
- selective write-through from research into memory

---

## 2. Core principles

### 2.1 Memory is not an archive
Memory must not become:
- a raw article store
- a PDF dump
- a scrape dump
- a daily news log
- a universal event archive
- a replacement for research artifacts

Memory stores what is likely to matter again.
If Jeff stores everything, retrieval quality collapses and continuity degrades into sludge.

### 2.2 Research history is not memory
Jeff needs a separate durable place for:
- research briefs
- source refs
- evidence bundles
- dated summaries
- comparison artifacts
- recurring brief outputs
- event/history records derived from research runs

Those objects remain **support artifacts**, not current truth and not memory by default.

### 2.3 Selective handoff beats automatic dumping
Research outputs may inform memory, but they do not become memory automatically.
The correct path is:

`research -> artifact/history -> Memory candidate consideration -> write/reject/defer`

### 2.4 Source traceability must survive distillation
If Jeff produces a summary, conclusion, or remembered lesson from web or local-document research, it must preserve enough linkage that the operator can still inspect:
- where it came from
- when it was observed
- what evidence supported it
- what remained uncertain

### 2.5 Future autonomy does not change memory law
A future daily or scheduled brief does not justify writing everything into memory.
Autonomous collection may widen artifact history.
Memory must remain selective.

---

## 3. Design goals

### 3.1 Hard goals
1. Preserve continuity without creating a rival truth layer.
2. Keep memory selective enough to avoid sludge.
3. Keep retrieval scoped, bounded, and useful for concrete Jeff actions.
4. Keep provenance inspectable.
5. Preserve a clear boundary between memory and research/event history.
6. Make future recurring brief workflows possible without redesigning memory semantics.
7. Make memory failure degrade usefulness, not integrity.
8. Keep the system compatible with future richer retrieval backends.

### 3.2 Non-goals
1. Remembering everything.
2. Using memory as hidden state repair.
3. Letting a framework or vector store own Jeff semantics.
4. Building a giant graph-first system in v1.
5. Making memory the default answer to current-truth questions.
6. Treating research history as memory by convenience.
7. Building autonomous background behavior in this document.

---

## 4. High-level architecture

```text
Lawful upstream support inputs
(research artifacts, evidence refs, evaluation signals, operator cues, run context)
        |
        v
+----------------------------------+
| Research / Artifact History Layer|
| - research briefs                |
| - source refs                    |
| - evidence bundles               |
| - dated event/history records    |
+----------------------------------+
        |
        | selective handoff only
        v
+----------------------------------+
| Memory Candidate Builder         |
+----------------------------------+
        |
        v
+----------------------------------+
| Validation + Dedupe + Scope      |
| Type Assignment + Compression    |
+----------------------------------+
        |
        +------------------> reject / defer
        |
        v
+----------------------------------+
| Committed Memory Store           |
| - memory records                 |
| - claims / points                |
| - links / lineage                |
| - audits                         |
+----------------------------------+
        |
        +------------------> Indexer
        |                    - FTS
        |                    - pgvector
        |                    - future optional adapters
        |
        v
+----------------------------------+
| Retrieval Engine                 |
| - exact refs                     |
| - lexical                        |
| - semantic                       |
| - rerank                         |
| - conflict labeling              |
+----------------------------------+
        |
        v
+----------------------------------+
| Context Assembly                 |
| truth first, memory second       |
+----------------------------------+
```

---

## 5. Memory vs research history vs canonical truth

### 5.1 Canonical truth
Lives in canonical state only.
Memory never overrides it.
Research artifacts never override it.

### 5.2 Memory
Stores durable non-truth continuity such as:
- reusable findings
- durable lessons
- repeated operational patterns
- strategic anchors
- bounded precedents worth reusing later

### 5.3 Research history / artifact archive
Stores source-backed support objects such as:
- research briefs
- source lists
- evidence bundles
- comparison notes
- dated market/project/topic summaries
- event/history records produced by recurring research runs

### 5.4 Why the distinction matters
Example:
- a daily market brief is worth keeping as a dated artifact/history record
- only the few durable conclusions or important market events from that brief may deserve memory
- the rest remains queryable history, not memory

This prevents memory from becoming a trash heap while still preserving historical traceability.

---

## 6. Recommended stack

### 6.1 v1 stack
- PostgreSQL as the authoritative persistence layer for memory metadata, scope, lineage, support links, audits, and retrieval bookkeeping
- `pgvector` as the primary vector search extension inside PostgreSQL
- PostgreSQL full-text search for exact term and phrase retrieval
- Jeff-owned retrieval orchestration and context assembly
- Jeff-owned write pipeline
- Jeff-owned maintenance jobs

Why:
- one authoritative transactional store
- strong auditability
- strong scope filtering
- low operational complexity
- easy hybrid retrieval: SQL filter + full-text + vector similarity

### 6.2 v1.5 or v2 optional additions
- Qdrant as an optional external vector retrieval backend behind a Jeff adapter
- Graphiti or another temporal graph system as an optional specialized relationship and time-aware retrieval layer
- LlamaIndex as an optional retrieval/query/workflow helper in Infrastructure, never as owner of Jeff Memory semantics
- Zep only as an external benchmark or experiment source, never as Jeff's semantic owner

### 6.3 What remains Jeff-owned no matter what backend is used
- memory type law
- candidate creation law
- acceptance/reject/defer law
- scope rules
- truth conflict handling
- context assembly rules
- linking semantics
- supersession semantics
- maintenance policy
- research-to-memory handoff discipline

---

## 7. Memory layer responsibilities

The Memory layer owns:
- candidate creation
- candidate validation
- deduplication and incremental-value checks
- type assignment
- scope assignment
- compression into committed memory form
- commit and issuance of `memory_id`
- indexing
- retrieval
- linking
- supersession and merge discipline
- maintenance jobs
- memory observability

The Memory layer does not own:
- canonical state truth
- transitions
- governance
- proposal/selection
- execution or evaluation semantics
- research semantics
- research artifact storage semantics
- orchestration routing semantics
- interface semantics

---

## 8. Research-to-Memory handoff

### 8.1 Lawful upstream research inputs
Research may provide Memory with support such as:
- source-aware findings
- bounded inferences
- uncertainty markers
- recommendation context
- artifact refs
- source refs
- evidence refs
- recurring brief summaries
- dated event/history records

These are **inputs for consideration**, not memory candidates by themselves.

### 8.2 What usually should become memory
Examples:
- a repeated market pattern that kept recurring across multiple briefs
- a durable lesson about a supplier, tool, vendor, or research topic
- a project constraint repeatedly confirmed by multiple sources
- a decision rationale likely to matter later
- a major event with precedent value
- an operational lesson from repeated research work

### 8.3 What usually should stay only in research history
Examples:
- the full text of an article
- a raw paper download
- an entire daily market brief
- every minor market movement
- every supporting quote or web snippet
- one-off noise with no reuse value

### 8.4 Handoff workflow

```text
Research run
  -> Research artifact created
  -> Candidate-worthy points extracted
  -> Memory candidate builder evaluates them
  -> reject / defer / write / merge / supersede
```

### 8.5 Future recurring brief example
Future autonomy may eventually support:
- daily market brief generation
- weekly project intelligence brief
- periodic topic surveillance

Correct architecture:
- every run produces a dated research artifact/history record
- only selected durable points are proposed to Memory
- Memory stays selective even if research history grows daily

---

## 9. Core implementation decisions

### 9.1 Scope model
Primary write scope in v1:
- `project_id` is required
- `work_unit_id` is optional but strongly recommended when the memory is materially local to one work unit
- `run_id` is optional but strongly recommended when the memory is materially tied to one run
- every committed memory has exactly one primary scope
- cross-project writes are forbidden in v1
- global/system memory is deferred

### 9.2 Type model
Each committed memory record has exactly one primary type:
- `episodic`
- `semantic`
- `directional`
- `operational`

Optional secondary tags may exist for retrieval tuning, but they do not replace primary type.

### 9.3 Memory identity
- `memory_id` is a Jeff-issued opaque string
- no external backend ID becomes semantic authority
- external backend identifiers may be stored as implementation linkage only

### 9.4 Truth conflict posture
When state and memory disagree:
- state wins
- memory may still be retrieved, but only as contradiction/stale/mismatch support
- retrieval output must keep conflict labeling explicit
- no automatic truth repair is performed by memory

### 9.5 Storage strategy
Use one normalized authoritative schema in PostgreSQL.
Do not store memory as one giant JSON blob table only.
Use JSON only for bounded flexible fields, not for the entire model.

---

## 10. Memory layer module layout

Recommended Python package layout:

```text
jeff/memory/
  __init__.py
  types.py
  ids.py
  schemas.py
  candidate_builder.py
  validator.py
  dedupe.py
  type_assigner.py
  scope_assigner.py
  compressor.py
  store.py
  linker.py
  indexer.py
  retrieval.py
  reranker.py
  conflict_labeler.py
  maintenance.py
  telemetry.py
  api.py
```

Module purposes:
- `candidate_builder.py`: build candidate objects from lawful support inputs
- `validator.py`: enforce hard write rules
- `dedupe.py`: detect duplicates and low incremental value
- `type_assigner.py`: select one primary memory type
- `scope_assigner.py`: enforce project/work_unit/run scope rules
- `compressor.py`: produce concise, retrievable committed form
- `store.py`: persistence, commit, read, audit
- `linker.py`: support links, related-memory links, supersession links
- `indexer.py`: maintain FTS/vector/optional external indexes
- `retrieval.py`: retrieve bounded support sets
- `reranker.py`: merge lexical, semantic, and explicit-ref candidates
- `conflict_labeler.py`: label stale/conflicting memory against current truth
- `maintenance.py`: scheduled repair, cleanup, reindex, audits
- `telemetry.py`: metrics and trace-safe events
- `api.py`: Memory module public contract

---

## 11. MEMORY_RECORD_SCHEMA

### 11.1 Core committed record fields

```json
{
  "memory_id": "mem_...",
  "memory_type": "episodic | semantic | directional | operational",
  "project_id": "proj_...",
  "work_unit_id": "wu_... | null",
  "run_id": "run_... | null",
  "summary": "short concise summary",
  "remembered_points": [
    "bounded remembered claim or point"
  ],
  "why_it_matters": "why future reuse is expected",
  "support_quality": "weak | moderate | strong",
  "stability": "tentative | stable | reinforced",
  "freshness_sensitivity": "low | medium | high",
  "retrieval_weight": 0.0,
  "status": "active | superseded | deprecated | quarantined",
  "conflict_posture": "none | stale_support | contradiction_support | mismatch_support",
  "created_at": "iso8601",
  "updated_at": "iso8601",
  "created_from_run_id": "run_... | null",
  "extractor_version": "string",
  "embedding_profile_id": "string | null",
  "schema_version": "1.0"
}
```

### 11.2 Required record rules
- `summary` must be concise and one memory-sized unit, not a report
- `remembered_points` must be bounded and individually inspectable
- `why_it_matters` is required
- `support_quality` is not probability of truth; it is support strength for reuse
- `stability` expresses how likely the memory is to remain useful without revision
- `status` defaults to `active`
- `conflict_posture` defaults to `none`
- raw logs, prompts, trace dumps, article bodies, and full briefs are forbidden

### 11.3 Claim model
Some memory records need claim-level inspection.
Support this with a separate claim table rather than hiding everything in prose.

Each claim row should include:
- `memory_claim_id`
- `memory_id`
- `claim_text`
- `claim_kind`: `fact | lesson | rationale | caution | pattern`
- `claim_support_quality`
- `claim_conflict_posture`
- `claim_order`

### 11.4 Link model
Every committed memory should have typed links.

Required:
- one primary scope link through `project_id`
- zero or one local `work_unit_id`
- zero or one local `run_id`

Optional:
- artifact links
- source refs
- evidence refs
- related committed memory links
- supersedes/superseded-by links
- research artifact refs
- event/history refs

### 11.5 Lineage model
Support explicit lineage:
- `supersedes_memory_id`
- `superseded_by_memory_id`
- `merged_into_memory_id`
- `derived_from_candidate_id`
- `derived_from_run_id`
- `derived_from_artifact_id`

---

## 12. Physical storage schema

### 12.1 `memory_records`
Authoritative committed memory rows.

Suggested columns:
- `memory_id text primary key`
- `memory_type text not null`
- `project_id text not null`
- `work_unit_id text null`
- `run_id text null`
- `summary text not null`
- `why_it_matters text not null`
- `support_quality text not null`
- `stability text not null`
- `freshness_sensitivity text not null`
- `retrieval_weight double precision not null default 0`
- `status text not null`
- `conflict_posture text not null default 'none'`
- `created_from_run_id text null`
- `extractor_version text not null`
- `embedding_profile_id text null`
- `schema_version text not null`
- `created_at timestamptz not null`
- `updated_at timestamptz not null`
- `supersedes_memory_id text null`
- `superseded_by_memory_id text null`
- `merged_into_memory_id text null`

### 12.2 `memory_points`
Bounded remembered points or compressed claim-like payload.

### 12.3 `memory_claims`
Optional stricter claim-level rows when needed.

### 12.4 `memory_links`
Typed links from memory to support objects.
Expected `link_type` values:
- `artifact_support`
- `source_support`
- `evidence_support`
- `research_artifact_support`
- `history_record_support`
- `related_memory`
- `supersedes`
- `superseded_by`
- `derived_from`

### 12.5 `memory_embeddings`
Embedding storage and versioning.

### 12.6 `memory_candidates`
Pre-commit candidate staging.

### 12.7 `memory_write_events`
Audit trail for write decisions.

### 12.8 `memory_retrieval_events`
Retrieval audit and evaluation surface.

### 12.9 `memory_maintenance_jobs`
Scheduled or manual maintenance job registry.

---

## 13. Write-time source inputs

Allowed support inputs:
- research findings and recommendation context
- execution residue
- outcome object and evidence refs
- evaluation verdict and rationale
- operator-marked continuity cues
- bounded current-truth refs when needed for linkage
- research artifact refs
- evidence bundle refs
- recurring brief artifact refs
- event/history artifact refs

Not allowed as direct memory authority:
- raw article or PDF bodies
- full chat dumps
- raw prompts
- raw traces
- unfiltered daily news dumps
- model output without provenance linkage

---

## 14. MEMORY_WRITE_PIPELINE

Canonical pipeline:
1. candidate creation by Memory
2. candidate validation
3. deduplication and incremental-value check
4. type assignment
5. scope assignment
6. compression into concise retrievable form
7. accept / reject / defer decision
8. commit and storage
9. indexing
10. linking

Rules:
- no step may be skipped silently
- no committed memory ID exists before successful commit
- a deferred or rejected candidate does not become canonically referenceable
- indexing and required linking are part of a successful write
- if the pipeline cannot complete honestly, the candidate must be rejected or deferred rather than partially committed

Write outcomes:
- `write`
- `reject`
- `defer`
- `supersede_existing`
- `merge_into_existing`

---

## 15. Retrieval pipeline

### 15.1 Retrieval principles
- truth first, memory second
- scope filter before ranking
- exact linkage before semantic search
- stronger provenance over weaker summary when support matters
- stale/conflicting memory stays labeled as support

### 15.2 Retrieval stages
1. determine retrieval purpose
2. determine scope window
3. gather exact linked memory
4. gather lexical candidates
5. gather semantic candidates
6. dedupe and merge candidates
7. rerank by scope fit, purpose fit, support quality, and recency
8. label stale/conflict posture
9. return bounded memory package

### 15.3 Retrieval outputs
Return:
- memory summaries
- relevant remembered points / claims
- why the memory matters
- provenance links
- stale/conflict labels when relevant

Do not return:
- giant raw bodies by default
- hidden stitched truth
- unbounded memory dumps

---

## 16. Research history / event archive interplay

This document does not define the full research archive schema, but Memory must be designed to interoperate with it.

Expected future support-object classes:
- `research_brief`
- `research_comparison`
- `evidence_bundle`
- `source_set`
- `brief_history_record`
- `event_history_record`

Memory should link to these by thin refs rather than absorbing them into memory bodies.

For future recurring workflows such as daily market briefs:
- every run should produce a dated artifact/history record with source refs
- Memory should consider only the distilled durable subset
- retrieval may later combine memory plus selected dated artifacts when the operator asks for history

---

## 17. Maintenance jobs

Recommended maintenance jobs:
- embedding backfill / re-embed
- stale-link checker
- orphan candidate cleanup
- duplicate cluster review
- supersession cleanup
- retrieval quality audit
- conflict-label refresh against current truth
- archive-link integrity audit

Maintenance rules:
- maintenance may improve indexes and labels
- maintenance must not silently rewrite memory meaning
- maintenance must not repair truth
- maintenance must remain scoped and auditable

---

## 18. Observability

Memory observability should record:
- candidate created / rejected / deferred / committed counts
- duplicate rejection rates
- retrieval latency
- retrieval source mix
- top rejection reasons
- stale/conflict retrieval rates
- supersession events
- archive-to-memory handoff volumes

Observability is support only.
It must not become hidden semantics.

---

## 19. Tests

### 19.1 Required invariants
Tests must prove:
- memory never overrides canonical truth
- only Memory creates memory candidates
- only committed `memory_id` values can be linked canonically
- wrong-project retrieval is rejected
- duplicate/low-value candidate rejection works
- archive/history refs may support memory but do not become memory automatically
- research outputs cannot bypass the memory write pipeline

### 19.2 Additional recommended tests
- recurring brief artifacts produce candidate-worthy distilled outputs only when value thresholds are met
- one-off news/event noise is rejected from memory when it lacks reuse value
- source/provenance linkage survives compression into memory
- conflict labels remain explicit when memory contradicts current truth

---

## 20. Phased implementation

### Phase M1 - Minimal bounded memory core
- committed memory record model
- write pipeline
- simple store
- scope-safe retrieval
- truth-separation tests

### Phase M2 - Better indexing and provenance linkage
- FTS
- pgvector
- memory claims / points
- richer support linking

### Phase M3 - Research-aware handoff
- lawful input from research artifacts and evidence bundles
- research-artifact refs in memory links
- rejection rules for archive-dump attempts

### Phase M4 - Recurring brief compatibility
- archive/history integration
- selective daily/weekly brief memory handoff
- better episodic/event precedent capture without archive collapse into memory

### Phase M5 - Maintenance and quality improvement
- re-embedding
- conflict refresh
- duplicate cluster cleanup
- retrieval quality audits

---

## 21. Bottom line

Jeff should preserve two different kinds of continuity:

1. **Research/history continuity**
   Source-backed artifacts, dated summaries, evidence bundles, and recurring brief history.

2. **Memory continuity**
   Distilled, selective, reusable lessons and findings that are likely to matter again.

If those two are collapsed together, memory becomes sludge.
If they are separated cleanly, Jeff can support rich future workflows such as source-backed market/project/topic briefs while keeping memory useful, bounded, and trustworthy.
