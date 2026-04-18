from jeff.cognitive.post_selection import (
    ActionFormationRequest,
    ActionGovernanceHandoffRequest,
    OperatorSelectionOverrideRequest,
    SelectionActionResolutionRequest,
    SelectionEffectiveProposalRequest,
)
from jeff.cognitive.post_selection.action_formation import form_action_from_materialized_proposal
from jeff.cognitive.post_selection.action_resolution import resolve_selection_action_basis
from jeff.cognitive.post_selection.effective_proposal import materialize_effective_proposal
from jeff.cognitive.post_selection.governance_handoff import handoff_action_to_governance
from jeff.cognitive.post_selection.override import build_operator_selection_override


def test_post_selection_package_surface_exposes_bridge_request_types() -> None:
    assert OperatorSelectionOverrideRequest.__module__ == "jeff.cognitive.post_selection.override"
    assert SelectionActionResolutionRequest.__module__ == "jeff.cognitive.post_selection.action_resolution"
    assert SelectionEffectiveProposalRequest.__module__ == "jeff.cognitive.post_selection.effective_proposal"
    assert ActionFormationRequest.__module__ == "jeff.cognitive.post_selection.action_formation"
    assert ActionGovernanceHandoffRequest.__module__ == "jeff.cognitive.post_selection.governance_handoff"


def test_post_selection_modules_resolve_through_new_package_layout() -> None:
    assert callable(build_operator_selection_override)
    assert callable(resolve_selection_action_basis)
    assert callable(materialize_effective_proposal)
    assert callable(form_action_from_materialized_proposal)
    assert callable(handoff_action_to_governance)
