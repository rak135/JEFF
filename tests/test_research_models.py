import pytest

from jeff.cognitive.research import ResearchRequest, ResearchResult
from jeff.cognitive.types import Recommendation, ResearchFinding, ResearchInference, SourceSummary
from jeff.core.schemas import Scope


def test_research_result_preserves_findings_inference_and_recommendation() -> None:
    request = ResearchRequest(
        objective="Compare two bounded approaches",
        scope=Scope(project_id="project-1", work_unit_id="wu-1"),
        research_mode="decision_support",
    )
    result = ResearchResult(
        request=request,
        sources=(
            SourceSummary(
                source_id="source-1",
                source_family="document",
                scope=Scope(project_id="project-1", work_unit_id="wu-1"),
                summary="Project note",
            ),
        ),
        findings=(ResearchFinding(statement="Current scope is narrow", source_ids=("source-1",)),),
        inferences=(ResearchInference(statement="A minimal option is safer", based_on_finding_indexes=(0,)),),
        uncertainty_notes=("External constraints remain unknown",),
        recommendation=Recommendation(summary="Prefer a bounded first pass"),
    )

    assert result.findings[0].statement == "Current scope is narrow"
    assert result.inferences[0].statement == "A minimal option is safer"
    assert result.recommendation is not None


def test_research_result_requires_source_aware_findings() -> None:
    request = ResearchRequest(
        objective="Answer a bounded question",
        scope=Scope(project_id="project-1"),
        research_mode="direct_output",
    )

    with pytest.raises(ValueError, match="unknown source ids"):
        ResearchResult(
            request=request,
            sources=(
                SourceSummary(
                    source_id="source-1",
                    source_family="document",
                    scope=Scope(project_id="project-1"),
                    summary="Project note",
                ),
            ),
            findings=(ResearchFinding(statement="Claim", source_ids=("missing-source",)),),
        )
