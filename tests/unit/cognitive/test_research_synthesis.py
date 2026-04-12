from dataclasses import dataclass

import pytest

from jeff.cognitive import (
    EvidenceItem,
    EvidencePack,
    ResearchArtifact,
    ResearchRequest,
    ResearchSynthesisRuntimeError,
    ResearchSynthesisValidationError,
    SourceItem,
    build_research_model_request,
    synthesize_research,
)
from jeff.infrastructure import FakeModelAdapter


def test_build_research_model_request_includes_bounded_evidence_and_instructions() -> None:
    request = _research_request()
    evidence_pack = _evidence_pack()

    model_request = build_research_model_request(request, evidence_pack, adapter_id="fake-json")

    assert model_request.response_mode.value == "JSON"
    assert model_request.purpose == "research_synthesis"
    assert "TASK: bounded research synthesis" in model_request.prompt
    assert "Output exactly one JSON object matching json_schema." in model_request.prompt
    assert "Do not output markdown, code fences, or extra prose." in model_request.prompt
    assert "QUESTION: What does the prepared evidence support?" in model_request.prompt
    assert "ALLOWED_CITATION_KEYS: S1, S2" in model_request.prompt
    assert "Required JSON shape" not in model_request.prompt
    assert "source-a" not in model_request.prompt
    assert "source-b" not in model_request.prompt
    assert "E1|refs=S1|text=The current state is stable." in model_request.prompt
    assert "C1|Constraint A" in model_request.prompt
    assert "S1|document|Bounded Note A|doc://a|n/a|Source A says the current state is stable." in model_request.prompt
    assert model_request.json_schema["properties"]["findings"]["items"]["properties"]["source_refs"]["items"]["enum"] == [
        "S1",
        "S2",
    ]
    assert "Return exactly one JSON object that matches json_schema." in model_request.system_instructions
    assert "No markdown, no code fences, no commentary." in model_request.system_instructions
    assert model_request.metadata["citation_keys"] == ["S1", "S2"]
    assert model_request.metadata["adapter_id"] == "fake-json"


def test_successful_synthesis_using_fake_model_adapter_json_mode() -> None:
    artifact = synthesize_research(
        research_request=_research_request(),
        evidence_pack=_evidence_pack(),
        adapter=FakeModelAdapter(
            adapter_id="fake-json",
            default_json_response={
                "summary": "The prepared evidence supports a bounded conclusion.",
                "findings": [
                    {"text": "Source A describes the current state.", "source_refs": ["S1"]},
                    {"text": "Source B confirms the same constraint.", "source_refs": ["S2"]},
                ],
                "inferences": ["A minimal next step is better supported than expansion."],
                "uncertainties": ["External conditions were not observed directly."],
                "recommendation": "Proceed with the bounded option first.",
            },
        ),
    )

    assert isinstance(artifact, ResearchArtifact)
    assert artifact.summary == "The prepared evidence supports a bounded conclusion."
    assert artifact.findings[0].text == "Source A describes the current state."
    assert artifact.findings[0].source_refs == ("source-a",)
    assert artifact.inferences == ("A minimal next step is better supported than expansion.",)
    assert artifact.uncertainties == ("External conditions were not observed directly.",)


def test_malformed_json_output_fails_closed() -> None:
    with pytest.raises(ResearchSynthesisRuntimeError, match="malformed_output"):
        synthesize_research(
            research_request=_research_request(),
            evidence_pack=_evidence_pack(),
            adapter=FakeModelAdapter(adapter_id="fake-json", default_json_response=None),
        )


def test_missing_required_fields_fail_closed() -> None:
    with pytest.raises(ResearchSynthesisValidationError, match="findings must be a list"):
        synthesize_research(
            research_request=_research_request(),
            evidence_pack=_evidence_pack(),
            adapter=FakeModelAdapter(
                adapter_id="fake-json",
                default_json_response={
                    "summary": "Missing findings should fail.",
                    "inferences": [],
                    "uncertainties": [],
                    "recommendation": None,
                },
            ),
        )


def test_primary_output_missing_summary_is_not_treated_as_success() -> None:
    events: list[dict[str, object]] = []

    with pytest.raises(ResearchSynthesisValidationError, match="summary must be a non-empty string"):
        synthesize_research(
            research_request=_research_request(),
            evidence_pack=_evidence_pack(),
            adapter=FakeModelAdapter(
                adapter_id="fake-json",
                default_json_response={
                    "findings": [{"text": "Observed fact", "source_refs": ["S1"]}],
                    "inferences": [],
                    "uncertainties": [],
                    "recommendation": None,
                },
            ),
            debug_emitter=events.append,
        )

    checkpoints = [event["checkpoint"] for event in events]
    assert "primary_synthesis_failed" in checkpoints
    assert "primary_synthesis_succeeded" not in checkpoints
    assert "repair_pass_started" in checkpoints
    assert "repair_pass_failed" in checkpoints
    assert "citation_remap_started" not in checkpoints
    failure_event = next(event for event in events if event["checkpoint"] == "primary_synthesis_failed")
    assert failure_event["payload"]["failure_class"] == "schema_incomplete"
    assert "summary must be a non-empty string" in str(failure_event["payload"]["reason"])


def test_primary_synthesis_succeeded_is_emitted_only_after_root_shape_gate_passes() -> None:
    events: list[dict[str, object]] = []

    artifact = synthesize_research(
        research_request=_research_request(),
        evidence_pack=_evidence_pack(),
        adapter=FakeModelAdapter(
            adapter_id="fake-json",
            default_json_response={
                "summary": "Artifact only.",
                "findings": [{"text": "Observed fact", "source_refs": ["S1"]}],
                "inferences": [],
                "uncertainties": [],
                "recommendation": None,
            },
        ),
        debug_emitter=events.append,
    )

    assert artifact.summary == "Artifact only."
    checkpoints = [event["checkpoint"] for event in events]
    assert "primary_synthesis_succeeded" in checkpoints
    assert "citation_remap_started" in checkpoints
    assert checkpoints.index("primary_synthesis_succeeded") < checkpoints.index("citation_remap_started")


def test_primary_schema_incomplete_json_can_succeed_via_one_repair_pass() -> None:
    events: list[dict[str, object]] = []
    adapter = _ScriptedAdapter(
        script=(
            {
                "findings": [{"text": "Observed fact", "source_refs": ["S1"]}],
                "inferences": [],
                "uncertainties": [],
                "recommendation": None,
            },
            {
                "summary": "Repaired summary.",
                "findings": [{"text": "Observed fact", "source_refs": ["S1"]}],
                "inferences": [],
                "uncertainties": [],
                "recommendation": None,
            },
        )
    )

    artifact = synthesize_research(
        research_request=_research_request(),
        evidence_pack=_evidence_pack(),
        adapter=adapter,
        debug_emitter=events.append,
    )

    assert artifact.summary == "Repaired summary."
    checkpoints = [event["checkpoint"] for event in events]
    assert "primary_synthesis_failed" in checkpoints
    assert "primary_synthesis_succeeded" not in checkpoints
    assert "repair_pass_started" in checkpoints
    assert "repair_pass_succeeded" in checkpoints
    assert checkpoints.index("primary_synthesis_failed") < checkpoints.index("repair_pass_started")
    assert checkpoints.index("repair_pass_succeeded") < checkpoints.index("citation_remap_started")


def test_primary_schema_incomplete_nested_field_mismatch_can_succeed_via_repair() -> None:
    adapter = _ScriptedAdapter(
        script=(
            {
                "summary": "Observed summary.",
                "findings": [{"description": "Observed fact", "source_ref": "S1"}],
                "inferences": [],
                "uncertainties": [],
                "recommendation": None,
            },
            {
                "summary": "Observed summary.",
                "findings": [{"text": "Observed fact", "source_refs": ["S1"]}],
                "inferences": [],
                "uncertainties": [],
                "recommendation": None,
            },
        )
    )

    artifact = synthesize_research(
        research_request=_research_request(),
        evidence_pack=_evidence_pack(),
        adapter=adapter,
    )

    assert artifact.summary == "Observed summary."
    assert artifact.findings[0].text == "Observed fact"
    assert artifact.findings[0].source_refs == ("source-a",)


def test_unknown_citation_refs_in_returned_findings_fail_closed() -> None:
    with pytest.raises(ResearchSynthesisValidationError, match="unknown citation refs"):
        synthesize_research(
            research_request=_research_request(),
            evidence_pack=_evidence_pack(),
            adapter=FakeModelAdapter(
                adapter_id="fake-json",
                default_json_response={
                    "summary": "This should fail source validation.",
                    "findings": [{"text": "Unsupported claim", "source_refs": ["S9"]}],
                    "inferences": [],
                    "uncertainties": [],
                    "recommendation": None,
                },
            ),
        )


def test_findings_inferences_and_uncertainties_remain_distinct() -> None:
    artifact = synthesize_research(
        research_request=_research_request(),
        evidence_pack=_evidence_pack(),
            adapter=FakeModelAdapter(
                adapter_id="fake-json",
                default_json_response={
                    "summary": "Distinct fields stay distinct.",
                    "findings": [{"text": "Observed fact", "source_refs": ["S1"]}],
                    "inferences": ["Interpretation"],
                    "uncertainties": ["Open question"],
                    "recommendation": None,
                },
            ),
    )

    assert artifact.findings[0].text == "Observed fact"
    assert artifact.inferences == ("Interpretation",)
    assert artifact.uncertainties == ("Open question",)


def test_synthesize_research_returns_research_artifact_not_model_response() -> None:
    result = synthesize_research(
        research_request=_research_request(),
        evidence_pack=_evidence_pack(),
            adapter=FakeModelAdapter(
                adapter_id="fake-json",
                default_json_response={
                    "summary": "Artifact only.",
                    "findings": [{"text": "Observed fact", "source_refs": ["S1"]}],
                    "inferences": [],
                    "uncertainties": [],
                    "recommendation": None,
                },
            ),
    )

    assert isinstance(result, ResearchArtifact)
    assert not hasattr(result, "output_json")


def _research_request() -> ResearchRequest:
    return ResearchRequest(
        question="What does the prepared evidence support?",
        project_id="project-1",
        work_unit_id="wu-1",
        run_id="run-1",
        constraints=("Constraint A",),
    )


def _evidence_pack() -> EvidencePack:
    return EvidencePack(
        question="What does the prepared evidence support?",
        sources=(
            SourceItem(
                source_id="source-a",
                source_type="document",
                title="Bounded Note A",
                locator="doc://a",
                snippet="Source A says the current state is stable.",
            ),
            SourceItem(
                source_id="source-b",
                source_type="document",
                title="Bounded Note B",
                locator="doc://b",
                snippet="Source B says the same constraint still holds.",
            ),
        ),
        evidence_items=(
            EvidenceItem(
                text="The current state is stable.",
                source_refs=("source-a",),
            ),
            EvidenceItem(
                text="The key constraint still holds.",
                source_refs=("source-b",),
            ),
        ),
        contradictions=("No direct contradiction found.",),
        uncertainties=("External verification was not performed.",),
        constraints=("Constraint A",),
    )


@dataclass(slots=True)
class _ScriptedAdapter:
    script: tuple[object, ...]
    adapter_id: str = "research-scripted"
    provider_name: str = "fake"
    model_name: str = "research-model"
    calls: int = 0

    def invoke(self, request_model):  # type: ignore[no-untyped-def]
        step = self.script[self.calls]
        self.calls += 1
        if isinstance(step, Exception):
            raise step
        assert isinstance(step, dict)
        from jeff.infrastructure import ModelInvocationStatus, ModelResponse, ModelUsage

        return ModelResponse(
            request_id=request_model.request_id,
            adapter_id=self.adapter_id,
            provider_name=self.provider_name,
            model_name=self.model_name,
            status=ModelInvocationStatus.COMPLETED,
            output_text=None,
            output_json=step,
            usage=ModelUsage(input_tokens=1, output_tokens=1, total_tokens=2, estimated_cost=0.0, latency_ms=1),
            warnings=(),
            raw_response_ref=f"fake://{self.adapter_id}/{request_model.request_id}",
        )
