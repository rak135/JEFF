import pytest

from jeff.cognitive.proposal import ProposalOption, ProposalSet
from jeff.cognitive.selection import SelectionResult, select_from_proposals
from jeff.core.schemas import Scope
from jeff.governance import may_start_now


def _proposal_set() -> ProposalSet:
    scope = Scope(project_id="project-1", work_unit_id="wu-1")
    return ProposalSet(
        scope=scope,
        options=(
            ProposalOption(
                proposal_id="proposal-1",
                proposal_type="direct_action",
                option_summary="Implement the bounded change",
                scope=scope,
            ),
            ProposalOption(
                proposal_id="proposal-2",
                proposal_type="investigate",
                option_summary="Investigate the missing edge case first",
                scope=scope,
            ),
        ),
    )


def test_selection_can_choose_one_proposal() -> None:
    result = select_from_proposals(
        proposal_set=_proposal_set(),
        selection_id="selection-1",
        selected_proposal_id="proposal-1",
        rationale="This path fits the current scope with the lowest assumption burden",
    )

    assert result.selected_proposal_id == "proposal-1"
    assert result.non_selection_outcome is None


def test_selection_non_selection_outcomes_remain_explicit() -> None:
    result = select_from_proposals(
        proposal_set=_proposal_set(),
        selection_id="selection-2",
        non_selection_outcome="defer",
        rationale="Current uncertainty is too high for an honest choice",
    )

    assert result.selected_proposal_id is None
    assert result.non_selection_outcome == "defer"


def test_selection_cannot_choose_more_than_one_path_or_become_permission() -> None:
    with pytest.raises(ValueError, match="exactly one proposal or one explicit non-selection"):
        SelectionResult(
            selection_id="selection-3",
            considered_proposal_ids=("proposal-1", "proposal-2"),
            selected_proposal_id="proposal-1",
            non_selection_outcome="reject_all",
            rationale="Invalid mixed outcome",
        )

    with pytest.raises(TypeError, match="ActionEntryDecision"):
        may_start_now(
            select_from_proposals(
                proposal_set=_proposal_set(),
                selection_id="selection-4",
                selected_proposal_id="proposal-1",
                rationale="Choice is not permission",
            ),
        )  # type: ignore[arg-type]
