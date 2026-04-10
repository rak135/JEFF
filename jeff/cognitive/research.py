"""Bounded, source-aware research contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from jeff.core.schemas import Scope

from .types import (
    Recommendation,
    ResearchFinding,
    ResearchInference,
    SourceSummary,
    normalize_text_list,
    require_text,
)

ResearchMode = Literal["direct_output", "decision_support"]


@dataclass(frozen=True, slots=True)
class ResearchRequest:
    objective: str
    scope: Scope
    research_mode: ResearchMode

    def __post_init__(self) -> None:
        object.__setattr__(self, "objective", require_text(self.objective, field_name="objective"))


@dataclass(frozen=True, slots=True)
class ResearchResult:
    request: ResearchRequest
    sources: tuple[SourceSummary, ...]
    findings: tuple[ResearchFinding, ...]
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
