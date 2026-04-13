"""Research-local validation helpers for bounded transition slices."""

from __future__ import annotations

from typing import Any

from ..types import require_text
from .bounded_syntax import (
    validate_step1_bullet_items,
    validate_step1_citation_keys,
    validate_step1_recommendation_text,
    validate_step1_summary_text,
)
from .errors import ResearchSynthesisValidationError

RESEARCH_CANDIDATE_REQUIRED_FIELDS = (
    "summary",
    "findings",
    "inferences",
    "uncertainties",
    "recommendation",
)
RESEARCH_CANDIDATE_FINDING_REQUIRED_FIELDS = ("text", "source_refs")
RESEARCH_CANDIDATE_FINDING_FORBIDDEN_FIELDS = ("source_id", "source_ref", "citation_keys")


def build_candidate_research_json_schema(allowed_citation_keys: tuple[str, ...]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "source_refs": {
                            "type": "array",
                            "items": {"type": "string", "enum": list(allowed_citation_keys)},
                            "minItems": 1,
                        },
                    },
                    "required": ["text", "source_refs"],
                    "additionalProperties": False,
                },
                "minItems": 1,
            },
            "inferences": {"type": "array", "items": {"type": "string"}},
            "uncertainties": {"type": "array", "items": {"type": "string"}},
            "recommendation": {"type": ["string", "null"]},
        },
        "required": list(RESEARCH_CANDIDATE_REQUIRED_FIELDS),
        "additionalProperties": False,
    }


def validate_candidate_research_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ResearchSynthesisValidationError("candidate research payload must be a JSON object")

    _require_exact_keys(
        payload,
        required_fields=RESEARCH_CANDIDATE_REQUIRED_FIELDS,
        owner_label="candidate research payload",
    )

    summary = validate_step1_summary_text(payload["summary"])
    findings = _validate_candidate_findings(payload["findings"])
    inferences = list(_validate_string_list(payload["inferences"], field_name="inferences"))
    uncertainties = list(_validate_string_list(payload["uncertainties"], field_name="uncertainties"))
    recommendation = validate_step1_recommendation_text(payload["recommendation"])

    return {
        "summary": summary,
        "findings": findings,
        "inferences": inferences,
        "uncertainties": uncertainties,
        "recommendation": recommendation,
    }


def _validate_candidate_findings(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ResearchSynthesisValidationError("findings must be a list")
    if not value:
        raise ResearchSynthesisValidationError("findings must contain at least one item")

    normalized_findings: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ResearchSynthesisValidationError("research finding entries must be objects")
        forbidden_fields = [field_name for field_name in RESEARCH_CANDIDATE_FINDING_FORBIDDEN_FIELDS if field_name in item]
        if forbidden_fields:
            raise ResearchSynthesisValidationError(
                f"research finding entries must not include internal or Step1-only fields: {forbidden_fields}",
            )
        _require_exact_keys(
            item,
            required_fields=RESEARCH_CANDIDATE_FINDING_REQUIRED_FIELDS,
            owner_label="research finding entry",
        )
        try:
            text = require_text(item["text"], field_name="text")
        except (TypeError, ValueError) as exc:
            raise ResearchSynthesisValidationError(str(exc)) from exc
        source_refs = item["source_refs"]
        if not isinstance(source_refs, list):
            raise ResearchSynthesisValidationError("source_refs must be a list")
        normalized_source_refs = validate_step1_citation_keys(tuple(source_refs), field_name="source_refs")
        normalized_findings.append(
            {
                "text": text,
                "source_refs": list(normalized_source_refs),
            }
        )

    return normalized_findings


def _validate_string_list(value: Any, *, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ResearchSynthesisValidationError(f"{field_name} must be a list")
    return validate_step1_bullet_items(tuple(value), section_name=field_name)


def _require_exact_keys(payload: dict[str, Any], *, required_fields: tuple[str, ...], owner_label: str) -> None:
    missing_fields = [field_name for field_name in required_fields if field_name not in payload]
    if missing_fields:
        raise ResearchSynthesisValidationError(f"{owner_label} is missing required fields: {missing_fields}")

    extra_fields = [field_name for field_name in payload if field_name not in required_fields]
    if extra_fields:
        raise ResearchSynthesisValidationError(f"{owner_label} contains unsupported fields: {extra_fields}")
