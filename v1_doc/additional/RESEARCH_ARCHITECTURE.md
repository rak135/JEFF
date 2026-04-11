# RESEARCH_ARCHITECTURE.md

Status: implementation architecture proposal for Jeff Research  
Authority: subordinate to `PLANNING_AND_RESEARCH_SPEC.md`, `CONTEXT_SPEC.md`, `MEMORY_SPEC.md`, `ARCHITECTURE.md`, `STATE_MODEL_SPEC.md`, and `TESTS_PLAN.md`  
Purpose: define a practical, minimal, source-aware research architecture for Jeff that stays truthful, bounded, and extensible without turning research into a black-box blob

---

## 1. Why this document exists

Jeff already has canonical law for:
- bounded research
- truth-first context
- source-aware evidence handling
- memory as durable non-truth continuity
- explicit separation between findings, inference, recommendation, and truth

This document does not change those laws.
It turns them into a practical implementation shape that is simple enough for v1 and strong enough to grow later.

The key design goal is to avoid two bad extremes:

1. **research as one giant magic LLM call**
   - model finds sources
   - model decides what matters
   - model summarizes
   - model stores memory
   - no clean provenance or boundaries

2. **research as overengineered bureaucracy**
   - too many flows
   - too many object types
   - too many review layers
   - too much architecture for too little value

Jeff should instead use one simple research pipeline with pluggable source providers.

---

## 2. Core design decision

Jeff Research should be implemented as:

`ResearchRequest -> SourceCollection -> EvidencePack -> Synthesis -> ResearchArtifact -> optional Memory handoff`

This is the central simplification.

Jeff should **not** implement:
- one completely separate system for memory research
- one separate system for local document research
- one separate system for web research

Instead, Jeff should have:
- **one common research pipeline**
- **multiple source providers**

The source providers differ.
The pipeline stays the same.

---

## 3. Research principles

### 3.1 Truth-first, not memory-first
Research starts from current truth and current project scope.
Memory, local documents, and web sources are support layers.
They do not replace current truth.

### 3.2 Source-aware, not source-dump
Research must preserve where information came from.
Jeff must be able to show sources for findings.
A polished answer without provenance is not good enough.

### 3.3 Evidence before synthesis
The model should synthesize from an explicit evidence package.
It should not be the entire research engine in one opaque call.

### 3.4 Findings are not inference
Research outputs must keep these distinct:
- findings
- inference
- uncertainties
- recommendation

### 3.5 Research artifacts are not memory
Research outputs should be archived as research artifacts.
Only selected, durable, high-value lessons or events should be proposed for memory.
Research history and memory are not the same thing.

### 3.6 Keep v1 thin
The v1 implementation should be minimal and practical.
Do not build a giant workflow system before Jeff can do useful research at all.

---

## 4. High-level architecture

```text
ResearchRequest
    |
    v
Context assembly (truth-first, scope-bounded)
    |
    v
Source providers
- Memory provider
- Documents provider
- Web provider
- Hybrid combination
    |
    v
SourceCollection
    |
    v
Evidence extraction
    |
    v
EvidencePack
    |
    v
Model-backed synthesis
    |
    v
ResearchArtifact
    |
    +--> operator-facing output
    |
    +--> optional downstream proposal/planning support
    |
    +--> optional selective Memory handoff
```

---

## 5. The minimal research pipeline

## 5.1 ResearchRequest

This is the bounded operator or system request that starts research.

Suggested fields:
- `request_id`
- `project_id`
- `work_unit_id | null`
- `run_id | null`
- `question` or `objective`
- `scope_notes`
- `source_modes`
- `constraints`
- `depth`
- `freshness_requirements`
- `output_shape`

Purpose:
- define what is being researched
- define where Jeff is allowed to look
- define what kind of output is expected

This keeps research bounded from the start.

## 5.2 Context assembly

Before source acquisition, Jeff should assemble the bounded current context:
- current project truth
- current work-unit truth where relevant
- project direction and constraints
- any relevant existing memory or prior artifacts only as support

This context step should be thin.
It is not research itself.
It only ensures the research request is grounded in the right scope and current truth.

## 5.3 SourceCollection

The research pipeline should then collect candidate source material through one or more source providers.

All providers should emit a common shape.

Suggested shared source shape:
- `source_type`
- `source_ref`
- `title`
- `snippet`
- `provenance`
- `freshness`
- `scope_fit`
- `authority_hint`

Jeff does not need one source model per mode if one common shape works.

## 5.4 Evidence extraction

Jeff should extract evidence from the gathered sources before synthesis.

Suggested evidence shape:
- `evidence_id`
- `source_ref`
- `text`
- `claim_type`
- `confidence_hint`
- `relevance`
- `conflict_flags`

This is where Jeff reduces source dumps into bounded research material.

## 5.5 EvidencePack

This is the explicit input to model-backed synthesis.

Suggested contents:
- `question` / `objective`
- `scope`
- `source_refs`
- `evidence_items`
- `contradictions`
- `uncertainty_markers`
- `constraints`

The key rule is:
**the model synthesizes from this pack; it does not invent the research process around it.**

## 5.6 Synthesis

The synthesis step uses the model adapter infrastructure.
It should produce a structured research result with explicit separation of meaning.

Suggested output shape:
- `summary`
- `findings[]`
- `inferences[]`
- `uncertainties[]`
- `recommendation | null`
- `source_refs[]`

This can be model-backed, but it must be validated and fail closed on malformed output.

## 5.7 ResearchArtifact

Every completed research run should produce an artifact that is:
- inspectable
- source-aware
- timestamped
- reusable later
- suitable for operator review

Suggested artifact contents:
- request metadata
- scope
- source refs
- findings
- inferences
- uncertainties
- recommendation
- generation timestamp
- provider / synthesis metadata if useful

Research artifacts are the main history layer for research work.

---

## 6. Source modes

## 6.1 Memory mode

Purpose:
Use committed Jeff memory as support input for current research.

Behavior:
- retrieve committed memory scoped to the current project first
- prefer local scope (`run -> work_unit -> project`) where useful
- label stale or conflicting memory explicitly
- never let memory override current truth

Use cases:
- resume long-running project work
- recall prior conclusions
- reuse lessons and rationale

Important rule:
Memory mode is support retrieval, not authoritative world-state lookup.

## 6.2 Documents mode

Purpose:
Research over local documents, notes, project files, artifacts, PDFs, markdown, code, and similar bounded local sources.

Behavior:
- search only inside allowed project/document scope
- return snippets and source refs, not giant bodies by default
- preserve local provenance
- feed extracted evidence into the shared pipeline

Use cases:
- documentation audits
- local project research
- repo/document synthesis
- extracting decision-relevant material from existing files

## 6.3 Web mode

Purpose:
Research the internet in a bounded, source-aware way.

Behavior:
- perform bounded search/fetch within the current question and scope
- preserve source identity and freshness
- compare sources where needed
- extract evidence instead of dumping raw pages into the model

Use cases:
- market/company briefings
- tool/vendor research
- topic research
- comparison of public claims and current developments

Important rule:
Web mode must preserve verifiability and freshness.

## 6.4 Hybrid mode

Purpose:
Combine memory, local documents, and web research in one bounded run.

Behavior:
- gather source items from multiple providers
- preserve source classes and provenance
- keep truth-first ordering
- avoid letting one support layer silently dominate another

Use cases:
- project research that needs both internal context and external evidence
- decision support that needs prior lessons plus current public information

Hybrid mode is not a new research system.
It is just multiple source providers feeding the same pipeline.

---

## 7. Research artifacts, history, and verifiability

This area is critical.

Jeff should not treat memory as the archive of everything it ever researched.
That would poison memory.

Instead, Jeff should separate:

### 7.1 Research artifact history
This is where the full research output history lives.

It should contain:
- dated briefings
- research reports
- source refs
- evidence-backed findings
- uncertainty notes
- comparison outputs
- historical research snapshots

This is where Jeff should keep things like:
- daily market briefs
- project research outputs
- topic briefings
- study summaries

### 7.2 Memory
Memory should hold only selected durable continuity:
- important patterns
- important event summaries with future value
- operational lessons
- durable strategic constraints
- reusable conclusions
- significant recurring market or company developments if they are likely to matter later

Research history and memory are complementary, not interchangeable.

---

## 8. Research-to-Memory handoff

Research may feed Memory.
It must not directly write Memory.

Correct handoff shape:

`ResearchArtifact -> selective candidate suggestion -> Memory pipeline -> write / reject / defer`

What Research may hand off:
- bounded findings
- bounded recommendations
- event summaries
- important patterns
- important rationale
- source refs and provenance
- support-quality hints

What Research may not do:
- create committed memory directly
- bypass deduplication
- bypass value checks
- bypass scope checks
- store raw source dumps as memory

### 8.1 What should typically go to memory
- durable lessons
- repeated patterns
- significant precedent events
- important company/project milestones
- stable source-backed conclusions likely to matter again

### 8.2 What should usually stay only in research history
- full daily brief bodies
- raw article summaries
- whole paper summaries unless truly reusable later
- one-off low-value updates
- routine noise
- raw source extracts

This division is especially important for long-running recurring research.

---

## 9. Future recurring research example: morning market brief

This is a future use case, not a v1 requirement.

Desired behavior:
- the operator defines a recurring market-research objective
- Jeff runs a bounded web research pass focused on selected companies or sectors
- Jeff produces a morning market brief with sources
- Jeff stores the brief as a research artifact
- Jeff selectively proposes important items for memory

### Example flow

```text
Scheduled trigger
    -> ResearchRequest
    -> web source provider
    -> SourceCollection
    -> Evidence extraction
    -> EvidencePack
    -> synthesis
    -> MorningMarketBrief artifact
    -> optional Memory candidate suggestions
    -> Memory pipeline decides write / reject / defer
```

Important rule:
The daily brief history should live primarily in research artifacts or a future event/archive layer.
Memory should only keep the subset that has durable future value.

---

## 10. Future recurring research example: project internet research

Desired behavior:
- the operator asks Jeff to research a topic or project online
- Jeff gathers and compares relevant public sources
- Jeff produces a source-backed memo or comparison output
- Jeff archives that output as a research artifact
- Jeff proposes only the durable parts for memory

Examples:
- researching a technology stack
- researching a market opportunity
- researching competitors
- researching studies on a scientific topic

The core rules stay the same:
- bounded scope
- source refs
- evidence before synthesis
- memory remains selective

---

## 11. Recommended v1 implementation shape

Jeff should implement Research in phases.

## 11.1 Phase C2a - synthesis only
- model-backed synthesis over an explicit EvidencePack
- no source acquisition yet
- no provider-specific logic in cognitive

## 11.2 Phase C2b - memory source provider
- retrieve committed memory as support input
- preserve scope and conflict labels

## 11.3 Phase C2c - documents source provider
- retrieve local documents and artifacts
- emit SourceItems and EvidenceItems

## 11.4 Phase C2d - web source provider
- bounded internet source acquisition
- source refs, freshness, evidence extraction

## 11.5 Phase C2e - research-to-memory handoff
- selective candidate suggestion
- no direct memory write

This phased approach is simpler and safer than trying to build the whole research stack at once.

---

## 12. Minimal module layout proposal

A practical minimal layout could look like this:

```text
jeff/
  cognitive/
    research.py
  infrastructure/
    model_adapters/
    research_sources/
      __init__.py
      base.py
      memory.py
      documents.py
      web.py
  artifacts/
    research_store.py        # future or equivalent location
```

This does **not** require a huge new subsystem on day one.
It just shows where the responsibilities should live as Research grows.

---

## 13. What not to do

Do not:
- turn research into one giant black-box LLM call
- use memory as the full research archive
- dump whole source bodies into memory
- let the model invent provenance
- merge findings and inference into one blob
- let web/document research bypass bounded scope
- build four separate large research frameworks when one pipeline with multiple providers is enough

These are exactly the failure modes Jeff should avoid.

---

## 14. Practical summary

The right simple architecture for Jeff Research is:

- **one common research pipeline**
- **multiple source providers**
- **explicit evidence extraction**
- **model-backed synthesis over bounded inputs**
- **research artifacts for history and verifiability**
- **selective Memory handoff for durable continuity**

That gives Jeff:
- verifiable research
- reusable research history
- future recurring briefings
- source-backed outputs
- clean memory discipline

without turning research into either chaos or bureaucracy.

