from dataclasses import dataclass, field

import pytest

from jeff.cognitive import (
    EvidenceItem,
    EvidencePack,
    ResearchRequest,
    ResearchSynthesisRuntimeError,
    ResearchSynthesisValidationError,
    SourceItem,
    synthesize_research,
)
from jeff.cognitive.research.synthesis import build_research_model_request, build_research_repair_model_request
from jeff.infrastructure import (
    ModelInvocationStatus,
    ModelMalformedOutputError,
    ModelRequest,
    ModelResponse,
    ModelTimeoutError,
    ModelUsage,
)


def test_malformed_primary_output_triggers_exactly_one_repair_attempt() -> None:
    adapter = _ScriptedAdapter(
        script=(
            ModelMalformedOutputError(
                "primary malformed",
                raw_output='summary: repaired summary\nfindings: [{"text":"Observed fact","source_refs":["S1"]}]',
            ),
            {
                "summary": "Repaired summary.",
                "findings": [{"text": "Observed fact", "source_refs": ["S1"]}],
                "inferences": [],
                "uncertainties": [],
                "recommendation": None,
            },
        )
    )

    artifact = synthesize_research(_research_request(), _evidence_pack(), adapter)

    assert artifact.summary == "Repaired summary."
    assert artifact.findings[0].source_refs == ("source-a",)
    assert len(adapter.requests) == 2
    assert adapter.requests[0].purpose == "research_synthesis"
    assert adapter.requests[1].purpose == "research_synthesis_repair"


def test_repair_pass_uses_separate_repair_adapter_when_provided() -> None:
    primary_adapter = _ScriptedAdapter(
        adapter_id="primary-research",
        script=(
            ModelMalformedOutputError(
                "primary malformed",
                raw_output='summary: repaired summary\nfindings: [{"text":"Observed fact","source_refs":["S1"]}]',
            ),
        ),
    )
    repair_adapter = _ScriptedAdapter(
        adapter_id="repair-formatter",
        script=(
            {
                "summary": "Repaired summary.",
                "findings": [{"text": "Observed fact", "source_refs": ["S1"]}],
                "inferences": [],
                "uncertainties": [],
                "recommendation": None,
            },
        ),
    )

    artifact = synthesize_research(_research_request(), _evidence_pack(), primary_adapter, repair_adapter=repair_adapter)

    assert artifact.summary == "Repaired summary."
    assert len(primary_adapter.requests) == 1
    assert len(repair_adapter.requests) == 1
    assert primary_adapter.requests[0].purpose == "research_synthesis"
    assert repair_adapter.requests[0].purpose == "research_synthesis_repair"
    assert repair_adapter.requests[0].metadata["adapter_id"] == "repair-formatter"


def test_schema_incomplete_primary_output_triggers_exactly_one_repair_attempt() -> None:
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

    artifact = synthesize_research(_research_request(), _evidence_pack(), adapter)

    assert artifact.summary == "Repaired summary."
    assert len(adapter.requests) == 2
    assert adapter.requests[0].purpose == "research_synthesis"
    assert adapter.requests[1].purpose == "research_synthesis_repair"


def test_repair_request_keeps_citation_key_contract_without_raw_source_id_leak() -> None:
    adapter = _ScriptedAdapter(
        script=(
            ModelMalformedOutputError(
                "primary malformed",
                raw_output='{"summary":"Observed","findings":[{"text":"Observed fact","source_refs":["source-a"]}]}',
            ),
            {
                "summary": "Observed.",
                "findings": [{"text": "Observed fact", "source_refs": ["S1"]}],
                "inferences": [],
                "uncertainties": [],
                "recommendation": None,
            },
        )
    )

    synthesize_research(_research_request(), _evidence_pack(), adapter)

    repair_request = adapter.requests[1]

    assert "ALLOWED_CITATION_KEYS: S1, S2" in repair_request.prompt
    assert '"enum":["S1","S2"]' in repair_request.prompt
    assert "source-a" not in repair_request.prompt
    assert "source-b" not in repair_request.prompt
    assert repair_request.metadata["citation_keys"] == ["S1", "S2"]


def test_schema_incomplete_primary_output_serializes_near_miss_json_into_repair_prompt() -> None:
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

    synthesize_research(_research_request(), _evidence_pack(), adapter)

    repair_request = adapter.requests[1]

    assert '"description":"Observed fact"' in repair_request.prompt
    assert '"source_ref":"S1"' in repair_request.prompt
    assert "source-a" not in repair_request.prompt
    assert "source-b" not in repair_request.prompt


def test_repair_prompt_requires_exact_json_typing_and_forbids_markdown() -> None:
    request = _research_request()
    evidence_pack = _evidence_pack()
    primary_request = build_research_model_request(request, evidence_pack, adapter_id="research-primary")

    repair_request = build_research_repair_model_request(
        request,
        evidence_pack,
        '```json {"summary":"Observed","findings":[{"text":"Observed fact","source_refs":"S1"}]} ```',
        primary_request=primary_request,
        adapter_id="repair-formatter",
    )

    assert "Output exactly one JSON object matching json_schema." in repair_request.prompt
    assert "Do not output markdown, code fences, or extra prose." in repair_request.prompt
    assert "findings must be a JSON array." in repair_request.prompt
    assert "Each findings item must be a JSON object with text and source_refs." in repair_request.prompt
    assert "finding.source_refs must be a JSON array of strings using only allowed citation keys." in repair_request.prompt
    assert 'Even one citation must be ["S1"], never "S1".' in repair_request.prompt
    assert "source-a" not in repair_request.prompt
    assert "source-b" not in repair_request.prompt
    assert "No markdown, no code fences, no commentary." in repair_request.system_instructions
    assert "Do not add claims, sources, evidence, or certainty." in repair_request.system_instructions


def test_invented_citation_keys_in_repaired_output_fail_closed() -> None:
    adapter = _ScriptedAdapter(
        script=(
            ModelMalformedOutputError("primary malformed", raw_output="summary: bad"),
            {
                "summary": "Repaired summary.",
                "findings": [{"text": "Observed fact", "source_refs": ["S9"]}],
                "inferences": [],
                "uncertainties": [],
                "recommendation": None,
            },
        )
    )

    with pytest.raises(ResearchSynthesisValidationError, match="unknown citation refs"):
        synthesize_research(_research_request(), _evidence_pack(), adapter)

    assert len(adapter.requests) == 2


def test_non_malformed_failures_do_not_trigger_repair() -> None:
    adapter = _ScriptedAdapter(script=(ModelTimeoutError("timed out while waiting for provider"),))

    with pytest.raises(ResearchSynthesisRuntimeError, match="timeout"):
        synthesize_research(_research_request(), _evidence_pack(), adapter)

    assert len(adapter.requests) == 1


def test_repair_pass_falls_back_to_primary_adapter_when_not_provided() -> None:
    adapter = _ScriptedAdapter(
        adapter_id="primary-research",
        script=(
            ModelMalformedOutputError(
                "primary malformed",
                raw_output='summary: repaired summary\nfindings: [{"text":"Observed fact","source_refs":["S1"]}]',
            ),
            {
                "summary": "Repaired summary.",
                "findings": [{"text": "Observed fact", "source_refs": ["S1"]}],
                "inferences": [],
                "uncertainties": [],
                "recommendation": None,
            },
        ),
    )

    artifact = synthesize_research(_research_request(), _evidence_pack(), adapter)

    assert artifact.summary == "Repaired summary."
    assert len(adapter.requests) == 2
    assert [request.purpose for request in adapter.requests] == ["research_synthesis", "research_synthesis_repair"]
    assert adapter.requests[1].metadata["adapter_id"] == "primary-research"


def test_repair_is_attempted_only_once() -> None:
    adapter = _ScriptedAdapter(
        script=(
            ModelMalformedOutputError("primary malformed", raw_output="summary: bad"),
            ModelMalformedOutputError("repair malformed", raw_output="still bad"),
        )
    )

    with pytest.raises(ResearchSynthesisRuntimeError, match="malformed_output"):
        synthesize_research(_research_request(), _evidence_pack(), adapter)

    assert len(adapter.requests) == 2


def test_repaired_json_missing_summary_is_not_treated_as_success() -> None:
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
                "findings": [{"text": "Observed fact", "source_refs": ["S1"]}],
                "inferences": [],
                "uncertainties": [],
                "recommendation": None,
            },
        )
    )

    with pytest.raises(ResearchSynthesisValidationError, match="summary must be a non-empty string"):
        synthesize_research(_research_request(), _evidence_pack(), adapter, debug_emitter=events.append)

    checkpoints = [event["checkpoint"] for event in events]
    assert "repair_pass_started" in checkpoints
    assert "repair_pass_failed" in checkpoints
    assert "repair_pass_succeeded" not in checkpoints
    failure_event = next(event for event in events if event["checkpoint"] == "repair_pass_failed")
    assert failure_event["payload"]["failure_class"] == "schema_incomplete"
    assert "summary must be a non-empty string" in str(failure_event["payload"]["reason"])


def test_schema_incomplete_primary_output_with_wrong_nested_fields_emits_truthful_repair_debug() -> None:
    events: list[dict[str, object]] = []
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

    artifact = synthesize_research(_research_request(), _evidence_pack(), adapter, debug_emitter=events.append)

    assert artifact.summary == "Observed summary."
    checkpoints = [event["checkpoint"] for event in events]
    assert "primary_synthesis_failed" in checkpoints
    assert "primary_synthesis_succeeded" not in checkpoints
    assert "repair_pass_started" in checkpoints
    assert "repair_pass_succeeded" in checkpoints
    failure_event = next(event for event in events if event["checkpoint"] == "primary_synthesis_failed")
    assert failure_event["payload"]["failure_class"] == "schema_incomplete"
    assert "text must be a non-empty string" in str(failure_event["payload"]["reason"])


def test_schema_incomplete_repair_output_with_blank_summary_emits_repair_pass_failed() -> None:
    events: list[dict[str, object]] = []
    adapter = _ScriptedAdapter(
        script=(
            ModelMalformedOutputError("primary malformed", raw_output="summary: bad"),
            {
                "summary": "   ",
                "findings": [{"text": "Observed fact", "source_refs": ["S1"]}],
                "inferences": [],
                "uncertainties": [],
                "recommendation": None,
            },
        )
    )

    with pytest.raises(ResearchSynthesisRuntimeError, match="malformed_output"):
        synthesize_research(_research_request(), _evidence_pack(), adapter, debug_emitter=events.append)

    checkpoints = [event["checkpoint"] for event in events]
    assert "repair_pass_failed" in checkpoints
    assert "repair_pass_succeeded" not in checkpoints
    failure_event = next(event for event in events if event["checkpoint"] == "repair_pass_failed")
    assert failure_event["payload"]["failure_class"] == "schema_incomplete"
    assert "summary must be a non-empty string" in str(failure_event["payload"]["reason"])


def test_repaired_json_with_wrong_root_types_is_not_treated_as_success() -> None:
    events: list[dict[str, object]] = []
    adapter = _ScriptedAdapter(
        script=(
            ModelMalformedOutputError("primary malformed", raw_output="summary: bad"),
            {
                "summary": "Repaired summary.",
                "findings": [{"text": "Observed fact", "source_refs": ["S1"]}],
                "inferences": [],
                "uncertainties": [],
                "recommendation": 7,
            },
        )
    )

    with pytest.raises(ResearchSynthesisRuntimeError, match="malformed_output"):
        synthesize_research(_research_request(), _evidence_pack(), adapter, debug_emitter=events.append)

    checkpoints = [event["checkpoint"] for event in events]
    assert "repair_pass_failed" in checkpoints
    assert "repair_pass_succeeded" not in checkpoints
    failure_event = next(event for event in events if event["checkpoint"] == "repair_pass_failed")
    assert "recommendation must be a string or null" in str(failure_event["payload"]["reason"])


def test_repair_pass_succeeded_is_emitted_only_after_root_shape_gate_passes() -> None:
    events: list[dict[str, object]] = []
    adapter = _ScriptedAdapter(
        script=(
            ModelMalformedOutputError("primary malformed", raw_output="summary: bad"),
            {
                "summary": "Repaired summary.",
                "findings": [{"text": "Observed fact", "source_refs": ["S1"]}],
                "inferences": [],
                "uncertainties": [],
                "recommendation": None,
            },
        )
    )

    artifact = synthesize_research(_research_request(), _evidence_pack(), adapter, debug_emitter=events.append)

    assert artifact.summary == "Repaired summary."
    checkpoints = [event["checkpoint"] for event in events]
    assert "repair_pass_succeeded" in checkpoints
    assert "citation_remap_started" in checkpoints
    assert checkpoints.index("repair_pass_succeeded") < checkpoints.index("citation_remap_started")


def _research_request() -> ResearchRequest:
    return ResearchRequest(
        question="What does the prepared evidence support?",
        project_id="project-1",
        work_unit_id="wu-1",
        run_id="run-1",
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
            EvidenceItem(text="The current state is stable.", source_refs=("source-a",)),
            EvidenceItem(text="The same constraint still holds.", source_refs=("source-b",)),
        ),
    )


@dataclass(slots=True)
class _ScriptedAdapter:
    script: tuple[object, ...]
    adapter_id: str = "research-scripted"
    provider_name: str = "fake"
    model_name: str = "research-model"
    requests: list[ModelRequest] = field(default_factory=list)

    def invoke(self, request_model: ModelRequest) -> ModelResponse:
        self.requests.append(request_model)
        step = self.script[len(self.requests) - 1]
        if isinstance(step, Exception):
            raise step
        assert isinstance(step, dict)
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
