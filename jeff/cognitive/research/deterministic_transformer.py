"""Deterministic parser from Step 1 bounded text to candidate research payload."""

from __future__ import annotations

from typing import Any

from .bounded_syntax import (
    STEP1_BULLET_PREFIX,
    STEP1_FINDINGS_SECTION,
    STEP1_FINDING_CITES_PREFIX,
    STEP1_FINDING_TEXT_PREFIX,
    STEP1_INFERENCES_SECTION,
    STEP1_NONE_LITERAL,
    STEP1_RECOMMENDATION_SECTION,
    STEP1_REQUIRED_HEADERS,
    STEP1_REQUIRED_SECTION_NAMES,
    STEP1_SUMMARY_SECTION,
    STEP1_UNCERTAINTIES_SECTION,
    validate_step1_bounded_text,
)
from .contracts import Step1BoundedArtifact, Step1BoundedFinding
from .errors import ResearchSynthesisValidationError
from .validators import validate_candidate_research_payload


def parse_step1_bounded_text(artifact_text: str) -> Step1BoundedArtifact:
    validate_step1_bounded_text(artifact_text)
    sections = _split_step1_sections(artifact_text)

    return Step1BoundedArtifact(
        summary=sections[STEP1_SUMMARY_SECTION],
        findings=_parse_findings_section(sections[STEP1_FINDINGS_SECTION]),
        inferences=_parse_bullet_section(sections[STEP1_INFERENCES_SECTION], section_name="inferences"),
        uncertainties=_parse_bullet_section(sections[STEP1_UNCERTAINTIES_SECTION], section_name="uncertainties"),
        recommendation=_parse_recommendation_section(sections[STEP1_RECOMMENDATION_SECTION]),
    )


def transform_step1_bounded_text_to_candidate_payload(artifact_text: str) -> dict[str, Any]:
    artifact = parse_step1_bounded_text(artifact_text)
    candidate_payload = build_candidate_research_payload(artifact)
    return validate_candidate_research_payload(candidate_payload)


def build_candidate_research_payload(artifact: Step1BoundedArtifact) -> dict[str, Any]:
    return {
        "summary": artifact.summary,
        "findings": [
            {
                "text": finding.text,
                "source_refs": list(finding.citation_keys),
            }
            for finding in artifact.findings
        ],
        "inferences": list(artifact.inferences),
        "uncertainties": list(artifact.uncertainties),
        "recommendation": artifact.recommendation,
    }


def _split_step1_sections(artifact_text: str) -> dict[str, str]:
    parsed_sections: dict[str, str] = {}
    current_section: str | None = None
    current_lines: list[str] = []
    expected_headers = list(STEP1_REQUIRED_HEADERS)

    for raw_line in artifact_text.splitlines():
        line = raw_line.rstrip()
        stripped_line = line.strip()
        if stripped_line in STEP1_REQUIRED_HEADERS:
            if not expected_headers:
                raise ResearchSynthesisValidationError(f"unexpected extra section header: {stripped_line}")
            expected_header = expected_headers.pop(0)
            if stripped_line != expected_header:
                expected_name = expected_header.removesuffix(":")
                raise ResearchSynthesisValidationError(
                    f"step1 bounded text requires {expected_name} section in canonical order",
                )
            if current_section is not None:
                parsed_sections[current_section] = "\n".join(current_lines).strip()
            current_section = stripped_line.removesuffix(":")
            current_lines = []
            continue

        if current_section is None:
            if stripped_line:
                raise ResearchSynthesisValidationError("step1 bounded text must start with SUMMARY:")
            continue
        current_lines.append(line)

    if current_section is not None:
        parsed_sections[current_section] = "\n".join(current_lines).strip()

    missing_sections = [section_name for section_name in STEP1_REQUIRED_SECTION_NAMES if section_name not in parsed_sections]
    if missing_sections:
        raise ResearchSynthesisValidationError(f"step1 bounded text is missing required sections: {missing_sections}")
    return parsed_sections


def _parse_findings_section(section_text: str) -> tuple[Step1BoundedFinding, ...]:
    lines = [line.rstrip() for line in section_text.splitlines() if line.strip()]
    if len(lines) % 2 != 0:
        raise ResearchSynthesisValidationError("findings entries must use paired text and cites lines")

    findings: list[Step1BoundedFinding] = []
    for index in range(0, len(lines), 2):
        text_line = lines[index]
        cites_line = lines[index + 1]
        if not text_line.startswith(STEP1_FINDING_TEXT_PREFIX):
            raise ResearchSynthesisValidationError("findings entries must start with '- text: '")
        if not cites_line.startswith(STEP1_FINDING_CITES_PREFIX):
            raise ResearchSynthesisValidationError("findings entries must keep a following '  cites: ' line")
        findings.append(
            Step1BoundedFinding(
                text=text_line[len(STEP1_FINDING_TEXT_PREFIX) :],
                citation_keys=tuple(
                    item.strip()
                    for item in cites_line[len(STEP1_FINDING_CITES_PREFIX) :].split(",")
                ),
            )
        )

    return tuple(findings)


def _parse_bullet_section(section_text: str, *, section_name: str) -> tuple[str, ...]:
    lines = [line.rstrip() for line in section_text.splitlines() if line.strip()]
    items: list[str] = []
    for line in lines:
        if not line.startswith(STEP1_BULLET_PREFIX):
            raise ResearchSynthesisValidationError(f"{section_name} entries must start with '{STEP1_BULLET_PREFIX}'")
        items.append(line[len(STEP1_BULLET_PREFIX) :])
    return tuple(items)


def _parse_recommendation_section(section_text: str) -> str | None:
    normalized_recommendation = section_text.strip()
    if normalized_recommendation == STEP1_NONE_LITERAL:
        return None
    return normalized_recommendation
