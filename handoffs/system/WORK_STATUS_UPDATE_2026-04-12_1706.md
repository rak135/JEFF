## 2026-04-12 17:06 â€” Hardened research synthesis and repair prompts

- Scope: research synthesis prompt contract and malformed-output repair prompt
- Done:
  - simplified the primary synthesis prompt into a shorter structured JSON-only contract
  - removed the handwritten required-JSON-shape block and kept `json_schema` as the authoritative schema path
  - hardened system instructions and prompt wording against markdown, code fences, and extra prose
  - tightened repair prompt typing rules for `findings` and `finding.source_refs`
  - updated deterministic unit coverage for the new prompt contract
- Validation: targeted synthesis/repair prompt tests passed; full `pytest -q` passed
- Current state: research synthesis and repair prompts are shorter, stricter, citation-key safe, and still preserve the existing artifact semantics
- Next step: use live runtime results to judge whether additional bounded prompt cleanup is needed before any broader research-runtime changes
- Files:
  - jeff/cognitive/research/synthesis.py
  - tests/unit/cognitive/test_research_synthesis.py
  - tests/unit/cognitive/test_research_synthesis_repair_pass.py
  - tests/unit/cognitive/test_research_synthesis_citation_keys.py
