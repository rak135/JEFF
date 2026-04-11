from jeff.cognitive import (
    ResearchRequest,
    build_document_evidence_pack,
    build_research_model_request,
    collect_document_sources,
    run_document_research,
    synthesize_research,
)
from jeff.cognitive.research import ResearchResult


def test_research_public_surface_exports_expected_entry_points() -> None:
    assert ResearchRequest.__module__ == "jeff.cognitive.research.contracts"
    assert build_research_model_request.__module__ == "jeff.cognitive.research.synthesis"
    assert synthesize_research.__module__ == "jeff.cognitive.research.synthesis"
    assert collect_document_sources.__module__ == "jeff.cognitive.research.documents"
    assert build_document_evidence_pack.__module__ == "jeff.cognitive.research.documents"
    assert run_document_research.__module__ == "jeff.cognitive.research.documents"


def test_legacy_research_result_is_isolated_but_still_public() -> None:
    assert ResearchResult.__module__ == "jeff.cognitive.research.legacy"
