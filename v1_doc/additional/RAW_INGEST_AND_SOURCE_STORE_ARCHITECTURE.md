# RAW_INGEST_AND_SOURCE_STORE_ARCHITECTURE.md

Status: implementation architecture proposal for Jeff Source Intake and Raw Source Custody  
Authority: subordinate to `ARCHITECTURE.md`, `VISION.md`, `CORE_SCHEMAS_SPEC.md`, `STATE_MODEL_SPEC.md`, `PROJECT_AND_WORK_UNIT_MODEL_SPEC.md`, `CONTEXT_SPEC.md`, `PLANNING_AND_RESEARCH_SPEC.md`, `MEMORY_SPEC.md`, and `TESTS_PLAN.md`  
Purpose: define a concrete, buildable raw-ingest and source-custody architecture for Jeff without changing canonical truth, memory, research, or interface law

---

## 1. Why this document exists

Jeff needs a disciplined way to accept operator-provided documents and Jeff-discovered sources without collapsing them into memory, artifacts, or canonical truth.

This document exists to define that intake and custody layer.

It turns the higher-level Jeff law into a concrete source-ingest architecture:
- where new source files arrive
- how Jeff scans and classifies them
- how Jeff assigns source identity
- how Jeff handles duplicate and revision cases
- how Jeff stores source originals and sidecars
- how provenance survives
- how raw sources hand off into extraction and compiled knowledge flows

This document does **not** redefine:
- memory semantics
- research synthesis semantics
- artifact semantics
- canonical truth placement
- transition law
- operator-facing project tree meaning

---

## 2. Core design decision

Jeff uses a **Jeff-managed source custody store outside the operator-facing project tree**.

That means:

- the operator-facing project tree described in `VISION.md` remains:
  - `artifacts/`
  - `research/`
  - `outputs/`
  - `memory/`
  - `working_data/`

- raw source custody is stored separately in Jeff-managed storage, for example:

```text
jeff_data/
  source_store/
    <project_id>/
      <source_id>/
        original.ext
        metadata.json
        extraction.txt
        preview.json
```

This separation is intentional.

The operator-facing project tree is a workspace/view layer.  
The source custody store is an internal Jeff-managed storage layer.

Jeff must not blur those two layers.

---

## 3. What this layer is

This layer is Jeff's **source intake and raw source custody** layer.

It owns:
- source discovery from intake locations
- source registration
- source identity issuance
- source fingerprinting
- duplicate and revision classification
- custody-safe storage of original materials
- source metadata sidecars
- extraction sidecars
- provenance preservation
- source lifecycle state
- handoff into downstream extraction / knowledge compilation

It is a **support layer**, not a truth layer.

It is not:
- canonical truth
- memory
- compiled knowledge
- final research output
- a review/apply object family
- a shortcut around transitions

---

## 4. Non-goals

This layer does **not** own:

- topic notes
- concept notes
- comparison notes
- contradiction notes
- compiled research briefs
- memory candidate creation
- memory commits
- truth mutation
- policy/governance
- operator-facing semantic status

It may provide source materials and source metadata to those later layers.
It does not absorb their jobs.

---

## 5. Design principles

### 5.1 Raw source custody is not memory
Raw sources are not durable continuity records.
They are original source materials under custody.

Memory remains selective, structured, committed, and non-truth continuity.
No raw source automatically becomes memory.

### 5.2 Raw source custody is not truth
A stored source does not become current truth by existing.
Source presence is support availability, not authority.

### 5.3 Source custody is separate from compiled knowledge
Raw source custody preserves originals and sidecars.
Compiled knowledge transforms those sources into structured support artifacts.
Those are different layers and must remain distinct.

### 5.4 Provenance must survive
Every downstream layer must be able to trace back to the stored source and its origin metadata.
If provenance is lost, Jeff weakens its research quality and later reviewability.

### 5.5 Project scope is a hard boundary
Every stored source belongs to one primary `project_id`.
Cross-project sharing is deferred.
Jeff v1 does not use one free-floating global source pool.

### 5.6 Storage placement must be stable and Jeff-owned
Source custody cannot depend on operator naming habits or ad hoc inbox structure.
Jeff controls the managed custody layout.

### 5.7 Custody must survive downstream failure
If extraction fails, synthesis fails, or knowledge compilation fails, the raw source must still remain safely stored and traceable.

---

## 6. High-level architecture

```text
raw_inbox/
    |
    v
+---------------------------+
| Intake Scanner            |
+---------------------------+
    |
    v
+---------------------------+
| Fingerprint + Classifier  |
| - exact duplicate         |
| - same source newer rev   |
| - near duplicate          |
| - distinct source         |
+---------------------------+
    |
    v
+---------------------------+
| Source Registry           |
| - source_id issuance      |
| - metadata capture        |
| - provenance capture      |
| - lifecycle state         |
+---------------------------+
    |
    v
+---------------------------+
| Managed Source Store      |
| - original file           |
| - metadata.json           |
| - extraction.txt          |
| - preview.json            |
+---------------------------+
    |
    v
+---------------------------+
| Extraction / Downstream   |
| Knowledge Handoff         |
+---------------------------+
```

---

## 7. Intake model

Jeff should treat new incoming source materials as **staged intake**, not immediately trusted internal storage.

Recommended intake path:

```text
raw_inbox/
  <project_id>/
    <incoming files>
```

Alternative future intake modes may include:
- explicit operator import command
- connector imports
- Jeff-discovered web materials staged into intake
- batch import jobs

The default v1 model should stay simple:
- operator or Jeff places source material into a project-scoped intake location
- Jeff scans intake on command or bounded polling
- Jeff classifies and stores each intake item

---

## 8. Intake trigger model

V1 should support at least one of these entry paths:

### 8.1 Explicit operator command
Example shape:
- `/sources ingest`
- `/sources ingest <project_id>`

This is simplest and most controlled for v1.

### 8.2 Bounded polling
Jeff periodically scans intake locations with modest cadence.

Useful later, but not required for the first implementation slice.

### 8.3 Future connector-triggered intake
Deferred beyond the initial architecture slice.

V1 recommendation:
- implement explicit ingest first
- add passive polling only after correctness and custody discipline are stable

---

## 9. Source identity model

Each stored source receives a Jeff-issued opaque `source_id`.

Rules:
- `source_id` is the canonical identity of the stored source record
- filename is not identity
- path is not identity
- URL is not identity
- locator metadata may help classify and dedupe, but does not replace `source_id`

A source may have:
- multiple locators
- multiple ingestion events
- revision links
- duplicate relationships

But one stored source record still has one canonical `source_id`.

---

## 10. Recommended storage placement

Because raw source custody is Jeff-managed internal storage, the recommended placement is outside the operator-facing project workspace tree.

Recommended root:

```text
jeff_data/
  source_store/
    <project_id>/
      <source_id>/
        original.ext
        metadata.json
        extraction.txt
        preview.json
```

### 10.1 Why this placement is preferred
- keeps operator-facing project tree semantically clean
- avoids confusing source custody with artifacts or memory
- keeps managed storage stable even if workspace layout evolves
- makes clear that custody storage is Jeff-owned, not ad hoc operator workspace content

### 10.2 Why it should not live under `memory/`
Because raw source custody is not memory.

### 10.3 Why it should not default to `working_data/`
Because that would turn `working_data/` into a junk bucket and blur operator workspace with internal managed storage.

---

## 11. Managed source directory contents

Each stored source directory should contain:

### 11.1 `original.ext`
The original file bytes under Jeff custody.

Rules:
- preserve original content
- preserve original extension when practical
- do not overwrite silently

### 11.2 `metadata.json`
Structured source metadata and lineage.

### 11.3 `extraction.txt`
Best-effort extracted text, when extraction succeeds.

Rules:
- absence is allowed
- failure to produce this file must not invalidate source custody

### 11.4 `preview.json`
Small bounded preview content and extraction summary, useful for quick inspection and downstream routing.

Typical contents may include:
- title guess
- short preview text
- extraction quality flags
- detected language
- page count or section hints when available

---

## 12. Source metadata model

Each source should carry metadata roughly of this shape:

```json
{
  "source_id": "src_...",
  "project_id": "proj_...",
  "work_unit_id": null,
  "run_id": null,
  "origin_type": "operator_upload",
  "original_filename": "paper.pdf",
  "stored_filename": "original.pdf",
  "stored_path": "jeff_data/source_store/proj_123/src_456/original.pdf",
  "mime_type": "application/pdf",
  "size_bytes": 123456,
  "content_hash": "sha256:...",
  "text_hash": null,
  "duplicate_status": "distinct",
  "duplicate_of_source_id": null,
  "revision_status": "current",
  "supersedes_source_id": null,
  "superseded_by_source_id": null,
  "locator": {
    "kind": "local_path",
    "value": "raw_inbox/proj_123/paper.pdf"
  },
  "provenance": {
    "origin_label": "operator upload",
    "origin_captured_at": "2026-04-16T08:00:00Z"
  },
  "discovered_at": "2026-04-16T08:00:00Z",
  "ingested_at": "2026-04-16T08:00:02Z",
  "extraction_status": "succeeded",
  "language": "en",
  "schema_version": "1.0"
}
```

This is not a final schema law document.
It is the recommended implementation shape.

---

## 13. Provenance rules

Provenance is mandatory.

Every source record should preserve:
- where the source came from
- how Jeff first saw it
- when it was ingested
- what project it belongs to
- any important locator or origin information

Possible locator kinds:
- local path
- URL
- DOI
- repo path
- connector import reference
- batch import id

Locator rules:
- locator helps explain origin
- locator does not replace source identity
- multiple locators may point to the same source over time

---

## 14. Fingerprinting strategy

Jeff should use layered fingerprinting, not naive filename checks.

### 14.1 Required fingerprint
- byte-level content hash of the stored original

### 14.2 Optional but strongly recommended fingerprints
- normalized extracted-text hash
- title / author / date hints
- origin locator hints
- document metadata hints

### 14.3 Why multiple fingerprints matter
A single hash is enough for exact duplicate detection.
It is not enough for revision or near-duplicate reasoning.

---

## 15. Duplicate and revision handling

Jeff should distinguish at least these cases.

### 15.1 Exact duplicate
Definition:
- same effective content
- same byte hash, or another clearly equivalent hard signal

Behavior:
- do not create a new primary stored source record
- preserve an ingest event or seen record
- preserve any new locator metadata if useful
- mark new intake item as exact duplicate of the existing `source_id`

### 15.2 Same source, newer revision
Definition:
- same underlying source lineage
- new revision is materially newer or updated
- not merely another copy of the same bytes

Behavior:
- create a new stored source record with a new `source_id`
- link it with `supersedes_source_id`
- old source remains preserved and auditable
- newer revision becomes the current revision within that source lineage

This case is first-class.
Jeff must not overwrite earlier revisions silently.

### 15.3 Near duplicate
Definition:
- strongly similar content or topic identity
- not safe enough to declare exact duplicate
- not safe enough to declare revision lineage automatically

Behavior:
- preserve as separate stored source unless a stronger rule settles identity
- mark relationship as near-duplicate support only
- do not auto-collapse

### 15.4 Distinct source
Definition:
- none of the above cases apply

Behavior:
- store normally as a new primary source record

---

## 16. Revision lineage rules

When Jeff identifies `same source, newer revision`, it must preserve lineage.

Recommended lineage fields:
- `supersedes_source_id`
- `superseded_by_source_id`
- `revision_status`
- optional `revision_reason`

Important rules:
- old revisions are retained
- new revision gets a new `source_id`
- downstream knowledge jobs may prefer the current revision
- custody layer must not delete historical revisions by convenience

---

## 17. Source lifecycle model

Recommended source lifecycle states:

- `discovered`
- `staged`
- `ingested`
- `duplicate_exact`
- `duplicate_near`
- `revision_current`
- `revision_superseded`
- `extraction_pending`
- `extraction_succeeded`
- `extraction_failed`
- `quarantined`
- `archived`

Not every stage must be surfaced to operators in v1.
But the underlying state model should be explicit enough for audit and debugging.

---

## 18. Ingest flow in detail

### 18.1 Discover
Jeff finds staged input in the intake location.

### 18.2 Read and classify basics
Jeff captures basic file metadata:
- path
- size
- extension
- candidate MIME type
- discovered timestamp

### 18.3 Fingerprint
Jeff computes content hash and any other available signals.

### 18.4 Duplicate / revision decision
Jeff compares against existing stored sources within the same project scope.

### 18.5 Register source outcome
Depending on classification:
- exact duplicate => seen record / locator update
- newer revision => new source record with lineage
- near duplicate => separate source with relationship flag
- distinct => new source record

### 18.6 Store under custody
Jeff moves or copies source material into managed source storage.

### 18.7 Create sidecars
Jeff writes metadata and any available extraction/preview sidecars.

### 18.8 Emit handoff
Jeff emits a downstream event or queued record for extraction / knowledge processing.

---

## 19. Copy vs move policy

This must be explicit.

Recommended v1 default:
- **copy into managed source store**
- mark intake item as processed
- optional cleanup step may remove staged intake only after successful custody write

Why copy-first is safer:
- avoids losing operator material during partial failure
- easier recovery if custody write fails midway
- fail-closed posture is stronger

Future configurable modes may include:
- move after verified custody success
- keep original always
- delete intake after success

But v1 should prefer safer custody over aggressive cleanup.

---

## 20. Extraction handoff

This architecture stops at custody plus minimal sidecar creation.

It may trigger downstream processing such as:
- text extraction
- title detection
- metadata enrichment
- preview generation
- source digest generation
- topic classification

Important rule:
- extraction failure does not invalidate custody success
- custody succeeds or fails on its own terms

That keeps source intake stable even when extraction quality is weak.

---

## 21. Relationship to compiled knowledge

The source custody layer hands off to downstream compiled knowledge work.

Expected downstream flow:

```text
source_store
  -> extraction
  -> source digest
  -> topic / concept / comparison notes
  -> optional memory handoff
```

The custody layer does not create:
- topic notes
- concept notes
- memory candidates
- memory records

It only makes those later steps possible and traceable.

---

## 22. Relationship to memory

Raw sources never become memory automatically.

At most, raw sources may later support:
- a memory candidate
- a knowledge artifact that supports memory work
- a memory contradiction or freshness check

Memory remains the only layer that:
- creates memory candidates
- validates them
- commits them
- issues `memory_id`

This architecture must not weaken that rule.

---

## 23. Recommended module layout

Recommended package structure:

```text
jeff/sources/
  __init__.py
  ids.py
  models.py
  intake.py
  scanner.py
  fingerprint.py
  dedupe.py
  revision.py
  registry.py
  store.py
  extraction_sidecar.py
  provenance.py
  lifecycle.py
  telemetry.py
  api.py
```

Suggested roles:
- `scanner.py`: intake discovery
- `fingerprint.py`: hashing and signal building
- `dedupe.py`: exact / near duplicate checks
- `revision.py`: same-source newer-revision classification
- `registry.py`: source record registration
- `store.py`: filesystem custody operations
- `extraction_sidecar.py`: extracted text and preview sidecars
- `provenance.py`: locator and origin handling
- `lifecycle.py`: explicit source lifecycle transitions
- `telemetry.py`: ingest metrics and audit events
- `api.py`: public source-layer contract

---

## 24. Observability and audit

Jeff should record bounded ingest events such as:
- intake discovery
- fingerprint success/failure
- duplicate classification
- revision classification
- custody write success/failure
- sidecar generation success/failure
- extraction handoff emitted
- quarantine placement

These events are critical for:
- diagnosing ingest bugs
- proving no silent overwrites occurred
- understanding duplicate/revision decisions

---

## 25. Failure modes

The source layer must explicitly handle these cases:

### 25.1 Broken or unreadable file
Behavior:
- quarantine or fail ingest cleanly
- do not silently pretend success

### 25.2 Partial custody write failure
Behavior:
- no successful ingest state unless custody write completes
- preserve recovery visibility

### 25.3 Hashing failure
Behavior:
- fail or quarantine
- do not continue as if identity is reliable

### 25.4 False duplicate classification
Behavior:
- classification must be auditable
- near duplicate must stay non-destructive

### 25.5 Wrong project binding
Behavior:
- reject or quarantine
- project boundary remains hard

### 25.6 Extraction failure after custody success
Behavior:
- source remains ingested
- extraction status becomes failed
- later retry remains possible

### 25.7 Silent overwrite temptation
Forbidden.
Jeff must not overwrite historical source records or revisions by convenience.

---

## 26. Security and safety posture

Even though this is not a full security spec, the source layer should assume:
- intake content may be malformed
- filenames may be hostile or messy
- metadata may be misleading
- extracted text may fail or contain junk

Therefore:
- stored filenames should be Jeff-controlled
- paths must be sanitized
- source identity must not depend on arbitrary operator path shape
- sidecar generation must fail closed

---

## 27. Test strategy

Minimum acceptance coverage should include:

- exact duplicate classification
- same source newer revision classification
- near duplicate non-collapse behavior
- distinct source normal ingest
- custody write produces expected directory structure
- metadata sidecar correctness
- lineage correctness for superseded revisions
- wrong-project rejection
- extraction failure does not destroy custody success
- idempotent re-ingest of exact duplicate
- no silent overwrite of stored originals
- quarantine path for unreadable sources

This layer needs anti-drift tests because sloppy source custody will poison every downstream layer.

---

## 28. Open edges and deferred work

Deferred beyond the initial slice:
- richer semantic near-duplicate detection
- multimodal source preview generation
- connector-native imports
- richer revision inference using DOI / citation graphs
- shared/global source pool outside one project
- source retention policies beyond basic archive behavior
- richer operator inspection commands for source lineage

---

## 29. Recommended first implementation slice

The first useful slice should be intentionally narrow:

1. project-scoped `raw_inbox`
2. explicit ingest command
3. content hash fingerprint
4. exact duplicate handling
5. same source newer revision handling
6. managed source store write
7. `metadata.json`
8. best-effort `extraction.txt`
9. extraction failure visibility
10. bounded test coverage

Do not try to solve every document-intelligence problem in the first pass.
Get custody right first.
If custody is weak, everything downstream inherits garbage.

---

## 30. Final architecture summary

Jeff should treat raw source intake as its own disciplined custody layer:

- intake is staged
- custody is Jeff-managed
- project scope is hard
- source identity is explicit
- duplicates and revisions are distinct cases
- originals are preserved
- provenance survives
- extraction is downstream
- compiled knowledge is downstream
- memory is downstream
- truth remains elsewhere

The raw source layer is the floor beneath knowledge work, not the knowledge work itself.
