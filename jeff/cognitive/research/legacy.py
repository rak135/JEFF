"""Legacy research contracts still needed by current callers/tests."""

from __future__ import annotations

from dataclasses import dataclass

from ..types import (
    Recommendation,
    ResearchFinding as LegacyResearchFinding,
    ResearchInference,
    SourceSummary,
    normalize_text_list,
)
from .contracts import ResearchRequest


@dataclass(frozen=True, slots=True)
class ResearchResult:
    request: ResearchRequest
    sources: tuple[SourceSummary, ...]
    findings: tuple[LegacyResearchFinding, ...]
    inferences: tuple[ResearchInference, ...] = ()
    contradictions: tuple[str, ...] = ()
    uncertainty_notes: tuple[str, ...] = ()
    recommendation: Recommendation | None = None

    def __post_init__(self) -> None:
        source_ids = {source.source_id for source in self.sources}
        if not source_ids:
            raise ValueError("research results must keep at least one source summary")

        for finding in self.findings:
            missing = [source_id for source_id in finding.source_ids if source_id not in source_ids]
            if missing:
                raise ValueError(f"research finding references unknown source ids: {missing}")

        if self.inferences and not self.findings:
            raise ValueError("research inferences require findings")

        for inference in self.inferences:
            if min(inference.based_on_finding_indexes) < 0:
                raise ValueError("inference finding indexes must be zero or greater")
            if max(inference.based_on_finding_indexes) >= len(self.findings):
                raise ValueError("research inference points to a missing finding")

        object.__setattr__(
            self,
            "contradictions",
            normalize_text_list(self.contradictions, field_name="contradictions"),
        )
        object.__setattr__(
            self,
            "uncertainty_notes",
            normalize_text_list(self.uncertainty_notes, field_name="uncertainty_notes"),
        )
