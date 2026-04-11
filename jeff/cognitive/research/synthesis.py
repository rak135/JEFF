"""Research synthesis behavior over explicit evidence."""

from __future__ import annotations

from typing import Any

from jeff.infrastructure import (
    InfrastructureServices,
    ModelAdapter,
    ModelInvocationError,
    ModelRequest,
    ModelResponseMode,
)

from ..types import require_text
from .contracts import EvidencePack, ResearchArtifact, ResearchFinding, ResearchRequest
from .errors import ResearchSynthesisError, ResearchSynthesisValidationError

_RESEARCH_SYNTHESIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "source_refs": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["text", "source_refs"],
                "additionalProperties": False,
            },
        },
        "inferences": {"type": "array", "items": {"type": "string"}},
        "uncertainties": {"type": "array", "items": {"type": "string"}},
        "recommendation": {"type": ["string", "null"]},
    },
    "required": ["summary", "findings", "inferences", "uncertainties", "recommendation"],
    "additionalProperties": False,
}


def build_research_model_request(
    request: ResearchRequest,
    evidence_pack: EvidencePack,
    adapter_id: str | None = None,
) -> ModelRequest:
    if request.question != evidence_pack.question:
        raise ValueError("research request question must match evidence pack question")

    source_lines = [
        (
            f"- {source.source_id} | type={source.source_type}"
            f" | title={source.title or 'n/a'}"
            f" | locator={source.locator or 'n/a'}"
            f" | snippet={source.snippet or 'n/a'}"
        )
        for source in evidence_pack.sources
    ]
    evidence_lines = [
        f"- refs={', '.join(item.source_refs)} | text={item.text}"
        for item in evidence_pack.evidence_items
    ]
    contradiction_lines = [f"- {item}" for item in evidence_pack.contradictions] or ["- none"]
    uncertainty_lines = [f"- {item}" for item in evidence_pack.uncertainties] or ["- none"]
    constraint_lines = [f"- {item}" for item in (request.constraints or evidence_pack.constraints)] or ["- none"]

    prompt = "\n".join(
        [
            "You are performing bounded research synthesis from prepared evidence only.",
            "Stay within the provided evidence.",
            "Do not invent sources, provenance, facts, or unstated certainty.",
            "Keep findings separate from inferences.",
            "Keep uncertainty explicit.",
            "Return JSON only and follow the required schema exactly.",
            "",
            f"Question: {request.question}",
            "Constraints:",
            *constraint_lines,
            "Sources:",
            *source_lines,
            "Evidence Items:",
            *evidence_lines,
            "Contradictions:",
            *contradiction_lines,
            "Uncertainties:",
            *uncertainty_lines,
            "",
            "Required JSON shape:",
            '{"summary":"string","findings":[{"text":"string","source_refs":["source_id"]}],"inferences":["string"],"uncertainties":["string"],"recommendation":"string or null"}',
        ]
    )

    return ModelRequest(
        request_id=f"research-synthesis:{request.project_id or 'none'}:{request.work_unit_id or 'none'}:{request.run_id or 'none'}:{request.question.lower().replace(' ', '-')}",
        project_id=request.project_id,
        work_unit_id=request.work_unit_id,
        run_id=request.run_id,
        purpose="research_synthesis",
        prompt=prompt,
        system_instructions=(
            "Synthesize only from provided evidence. "
            "Never claim unseen sources. "
            "Keep findings, inferences, and uncertainties distinct."
        ),
        response_mode=ModelResponseMode.JSON,
        json_schema=_RESEARCH_SYNTHESIS_SCHEMA,
        timeout_seconds=30,
        max_output_tokens=1200,
        reasoning_effort="medium",
        metadata={
            "research_question": request.question,
            "source_mode": request.source_mode,
            "expected_output_shape": "research_artifact_v1",
            "adapter_id": adapter_id,
            "source_ids": [source.source_id for source in evidence_pack.sources],
        },
    )


def synthesize_research(
    research_request: ResearchRequest,
    evidence_pack: EvidencePack,
    adapter: ModelAdapter,
) -> ResearchArtifact:
    if not evidence_pack.evidence_items:
        raise ResearchSynthesisValidationError("research synthesis requires at least one evidence item")

    model_request = build_research_model_request(research_request, evidence_pack, adapter_id=adapter.adapter_id)

    try:
        response = adapter.invoke(model_request)
    except ModelInvocationError as exc:
        raise ResearchSynthesisError("research synthesis invocation failed") from exc

    if response.output_json is None:
        raise ResearchSynthesisValidationError("research synthesis requires JSON output")

    return _research_artifact_from_output(
        research_request=research_request,
        evidence_pack=evidence_pack,
        payload=response.output_json,
    )


def synthesize_research_with_runtime(
    research_request: ResearchRequest,
    evidence_pack: EvidencePack,
    infrastructure_services: InfrastructureServices,
    adapter_id: str | None = None,
) -> ResearchArtifact:
    adapter = (
        infrastructure_services.get_model_adapter(adapter_id)
        if adapter_id is not None
        else infrastructure_services.get_default_model_adapter()
    )
    return synthesize_research(research_request=research_request, evidence_pack=evidence_pack, adapter=adapter)


def _research_artifact_from_output(
    *,
    research_request: ResearchRequest,
    evidence_pack: EvidencePack,
    payload: dict[str, Any],
) -> ResearchArtifact:
    summary = _required_string(payload, "summary")
    findings_payload = _required_list(payload, "findings")
    inferences = _required_string_list(payload, "inferences")
    uncertainties = _required_string_list(payload, "uncertainties")
    recommendation = _optional_string(payload.get("recommendation"), field_name="recommendation")

    known_source_ids = {source.source_id for source in evidence_pack.sources}
    findings: list[ResearchFinding] = []
    used_source_ids: list[str] = []
    for item in findings_payload:
        if not isinstance(item, dict):
            raise ResearchSynthesisValidationError("research finding entries must be objects")
        text = _required_string(item, "text")
        source_refs = _required_string_list(item, "source_refs")
        missing = [source_id for source_id in source_refs if source_id not in known_source_ids]
        if missing:
            raise ResearchSynthesisValidationError(
                f"research synthesis returned unknown source refs: {missing}",
            )
        findings.append(ResearchFinding(text=text, source_refs=tuple(source_refs)))
        for source_id in source_refs:
            if source_id not in used_source_ids:
                used_source_ids.append(source_id)

    return ResearchArtifact(
        question=research_request.question,
        summary=summary,
        findings=tuple(findings),
        inferences=tuple(inferences),
        uncertainties=tuple(uncertainties),
        recommendation=recommendation,
        source_ids=tuple(used_source_ids),
    )


def _required_string(payload: dict[str, Any], field_name: str) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str):
        raise ResearchSynthesisValidationError(f"{field_name} must be a non-empty string")
    return require_text(value, field_name=field_name)


def _optional_string(value: Any, *, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ResearchSynthesisValidationError(f"{field_name} must be a string or null")
    return require_text(value, field_name=field_name)


def _required_list(payload: dict[str, Any], field_name: str) -> list[Any]:
    value = payload.get(field_name)
    if not isinstance(value, list):
        raise ResearchSynthesisValidationError(f"{field_name} must be a list")
    return value


def _required_string_list(payload: dict[str, Any], field_name: str) -> list[str]:
    items = _required_list(payload, field_name)
    normalized: list[str] = []
    for item in items:
        if not isinstance(item, str):
            raise ResearchSynthesisValidationError(f"{field_name} entries must be strings")
        normalized.append(require_text(item, field_name=field_name))
    return normalized
