"""Research-local policy for Step 3 formatter fallback eligibility."""

from __future__ import annotations

from dataclasses import dataclass

from .bounded_syntax import (
    STEP1_FINDING_CITES_PREFIX,
    STEP1_FINDING_TEXT_PREFIX,
    validate_step1_bounded_text,
)
from .errors import ResearchSynthesisValidationError


@dataclass(frozen=True, slots=True)
class FormatterFallbackDecision:
    allowed: bool
    reason: str
    failure_class: str


def decide_formatter_fallback(
    *,
    bounded_text: str,
    transform_error: Exception,
) -> FormatterFallbackDecision:
    try:
        validate_step1_bounded_text(bounded_text)
    except ResearchSynthesisValidationError as exc:
        return FormatterFallbackDecision(
            allowed=False,
            reason=f"step1 bounded text is not formatter-eligible: {exc}",
            failure_class="step1_invalid",
        )

    if STEP1_FINDING_TEXT_PREFIX not in bounded_text or STEP1_FINDING_CITES_PREFIX not in bounded_text:
        return FormatterFallbackDecision(
            allowed=False,
            reason="step1 bounded text is missing formatter-required finding markers",
            failure_class="materially_incomplete",
        )

    return FormatterFallbackDecision(
        allowed=True,
        reason=f"deterministic transform failed after syntax-valid bounded text: {transform_error}",
        failure_class="structural_transform_failure",
    )
