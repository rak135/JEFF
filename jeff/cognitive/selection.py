"""Selection results with explicit non-selection outcomes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from jeff.core.schemas import ProposalId, SelectionId, coerce_proposal_id, coerce_selection_id

from .proposal import ProposalSet
from .types import require_text

NonSelectionOutcome = Literal["reject_all", "defer", "escalate"]


@dataclass(frozen=True, slots=True)
class SelectionResult:
    selection_id: SelectionId
    considered_proposal_ids: tuple[ProposalId, ...]
    selected_proposal_id: ProposalId | None = None
    non_selection_outcome: NonSelectionOutcome | None = None
    rationale: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "selection_id",
            coerce_selection_id(str(self.selection_id)),
        )
        object.__setattr__(
            self,
            "considered_proposal_ids",
            tuple(coerce_proposal_id(str(proposal_id)) for proposal_id in self.considered_proposal_ids),
        )
        if self.selected_proposal_id is not None:
            object.__setattr__(
                self,
                "selected_proposal_id",
                coerce_proposal_id(str(self.selected_proposal_id)),
            )
        object.__setattr__(self, "rationale", require_text(self.rationale, field_name="rationale"))

        chose_one = self.selected_proposal_id is not None
        chose_none = self.non_selection_outcome is not None
        if chose_one == chose_none:
            raise ValueError("selection must choose exactly one proposal or one explicit non-selection outcome")
        if chose_one and self.selected_proposal_id not in self.considered_proposal_ids:
            raise ValueError("selected proposal must come from the considered proposal set")


def select_from_proposals(
    *,
    proposal_set: ProposalSet,
    selection_id: str,
    selected_proposal_id: str | None = None,
    non_selection_outcome: NonSelectionOutcome | None = None,
    rationale: str,
) -> SelectionResult:
    considered_ids = tuple(option.proposal_id for option in proposal_set.options)
    return SelectionResult(
        selection_id=selection_id,
        considered_proposal_ids=considered_ids,
        selected_proposal_id=selected_proposal_id,
        non_selection_outcome=non_selection_outcome,
        rationale=rationale,
    )
