from dataclasses import dataclass

import pytest

from jeff.contracts import Action
from jeff.core.schemas import Scope
from jeff.governance import (
    Approval,
    CurrentTruthSnapshot,
    Policy,
    evaluate_action_entry,
    may_start_now,
)


@dataclass(frozen=True)
class SelectionLike:
    selection_id: str
    chosen_summary: str


def _action() -> Action:
    return Action(
        action_id="action-1",
        scope=Scope(project_id="project-1", work_unit_id="wu-1"),
        intent_summary="Apply a bounded code edit",
        target_summary="repo:jeff",
        protected_surface="core backbone",
        basis_state_version=3,
    )


def _truth() -> CurrentTruthSnapshot:
    return CurrentTruthSnapshot(
        scope=Scope(project_id="project-1", work_unit_id="wu-1"),
        state_version=3,
    )


def test_raw_selection_like_object_cannot_enter_governance() -> None:
    with pytest.raises(TypeError, match="bounded Action input"):
        evaluate_action_entry(
            action=SelectionLike(selection_id="selection-1", chosen_summary="Do it"),  # type: ignore[arg-type]
            policy=Policy(),
            approval=None,
            truth=_truth(),
        )


def test_raw_action_without_governance_pass_is_not_startable() -> None:
    with pytest.raises(TypeError, match="ActionEntryDecision"):
        may_start_now(_action())  # type: ignore[arg-type]


def test_vague_or_mismatched_approval_does_not_authorize_start() -> None:
    action = _action()
    mismatched = Approval.granted_for(
        action_id="action-2",
        action_binding_key="different-binding",
        basis_state_version=3,
    )
    decision = evaluate_action_entry(
        action=action,
        policy=Policy(approval_required=True),
        approval=mismatched,
        truth=_truth(),
    )

    assert decision.approval_verdict == "mismatched"
    assert decision.readiness.readiness_state == "invalidated"
    assert decision.allowed_now is False


def test_stale_approval_rejects_until_revalidated() -> None:
    action = _action()
    stale = Approval.granted_for(
        action_id=str(action.action_id),
        action_binding_key=action.binding_key,
        basis_state_version=2,
    )
    decision = evaluate_action_entry(
        action=action,
        policy=Policy(approval_required=True),
        approval=stale,
        truth=_truth(),
    )

    assert decision.approval_verdict == "stale"
    assert decision.readiness.readiness_state == "pending_revalidation"
    assert decision.governance_outcome == "deferred_pending_revalidation"


def test_missing_required_action_fields_reject_cleanly() -> None:
    with pytest.raises(ValueError, match="intent_summary"):
        Action(
            action_id="action-1",
            scope=Scope(project_id="project-1"),
            intent_summary="",
            basis_state_version=3,
        )


def test_workflow_or_plan_existence_does_not_imply_permission() -> None:
    action = _action()
    decision = evaluate_action_entry(
        action=action,
        policy=Policy(approval_required=True, revalidation_required=True),
        approval=Approval.absent(),
        truth=_truth(),
    )

    assert decision.governance_outcome != "allowed_now"
    assert decision.allowed_now is False
