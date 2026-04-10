import pytest

from jeff.cognitive.proposal import ProposalOption, ProposalSet
from jeff.core.schemas import Scope


def test_proposal_set_enforces_honest_cardinality_and_scarcity() -> None:
    scope = Scope(project_id="project-1", work_unit_id="wu-1")
    one_option = ProposalSet(
        scope=scope,
        options=(
            ProposalOption(
                proposal_id="proposal-1",
                proposal_type="direct_action",
                option_summary="Implement the bounded core change",
                scope=scope,
            ),
        ),
        scarcity_reason="Only one serious path survives current constraints",
    )

    assert len(one_option.options) == 1
    assert one_option.scarcity_reason is not None

    with pytest.raises(ValueError, match="at most 3 serious options"):
        ProposalSet(
            scope=scope,
            options=tuple(
                ProposalOption(
                    proposal_id=f"proposal-{index}",
                    proposal_type="investigate",
                    option_summary=f"Option {index}",
                    scope=scope,
                )
                for index in range(4)
            ),
            scarcity_reason=None,
        )


def test_proposal_set_rejects_padded_near_duplicates() -> None:
    scope = Scope(project_id="project-1", work_unit_id="wu-1")

    with pytest.raises(ValueError, match="near-duplicate"):
        ProposalSet(
            scope=scope,
            options=(
                ProposalOption(
                    proposal_id="proposal-1",
                    proposal_type="direct_action",
                    option_summary="Apply the safe patch now",
                    scope=scope,
                ),
                ProposalOption(
                    proposal_id="proposal-2",
                    proposal_type="direct_action",
                    option_summary="Apply   the safe patch now.",
                    scope=scope,
                ),
            ),
        )
