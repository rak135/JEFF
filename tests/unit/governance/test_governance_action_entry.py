from jeff.contracts import Action
from jeff.core.schemas import Scope
from jeff.governance import (
    Approval,
    CurrentTruthSnapshot,
    Policy,
    evaluate_action_entry,
    may_start_now,
)


def _action(*, basis_state_version: int = 3) -> Action:
    return Action(
        action_id="action-1",
        scope=Scope(project_id="project-1", work_unit_id="wu-1"),
        intent_summary="Apply a bounded code edit",
        target_summary="repo:jeff",
        protected_surface="core backbone",
        basis_state_version=basis_state_version,
    )


def _truth(*, state_version: int = 3, **overrides: object) -> CurrentTruthSnapshot:
    return CurrentTruthSnapshot(
        scope=Scope(project_id="project-1", work_unit_id="wu-1"),
        state_version=state_version,
        **overrides,
    )


def test_action_entry_allows_start_when_policy_and_readiness_both_pass() -> None:
    action = _action()
    decision = evaluate_action_entry(
        action=action,
        policy=Policy(approval_required=False, protected_surface=True),
        approval=None,
        truth=_truth(),
    )

    assert decision.policy_verdict == "allowed"
    assert decision.approval_verdict == "not_required"
    assert decision.readiness.readiness_state == "ready_with_cautions"
    assert decision.governance_outcome == "allowed_now"
    assert may_start_now(decision) is True


def test_action_entry_requires_approval_when_policy_demands_it() -> None:
    action = _action()
    decision = evaluate_action_entry(
        action=action,
        policy=Policy(approval_required=True),
        approval=None,
        truth=_truth(),
    )

    assert decision.policy_verdict == "approval_required"
    assert decision.approval_verdict == "absent"
    assert decision.readiness.readiness_state == "pending_approval"
    assert decision.governance_outcome == "approval_required"
    assert decision.allowed_now is False


def test_granted_approval_does_not_override_blocked_readiness() -> None:
    action = _action()
    approval = Approval.granted_for(
        action_id=str(action.action_id),
        action_binding_key=action.binding_key,
        basis_state_version=3,
    )
    decision = evaluate_action_entry(
        action=action,
        policy=Policy(approval_required=True),
        approval=approval,
        truth=_truth(blocked_reasons=("run is currently blocked",)),
    )

    assert decision.approval_verdict == "granted"
    assert decision.readiness.readiness_state == "blocked"
    assert decision.governance_outcome == "blocked"
    assert decision.allowed_now is False


def test_stale_action_basis_forces_revalidation() -> None:
    action = _action(basis_state_version=2)
    decision = evaluate_action_entry(
        action=action,
        policy=Policy(),
        approval=None,
        truth=_truth(state_version=3),
    )

    assert decision.readiness.readiness_state == "pending_revalidation"
    assert decision.governance_outcome == "deferred_pending_revalidation"
    assert decision.allowed_now is False


def test_direction_sensitive_action_invalidates_when_current_truth_changes() -> None:
    action = _action()
    decision = evaluate_action_entry(
        action=action,
        policy=Policy(direction_sensitive=True),
        approval=None,
        truth=_truth(direction_ok=False),
    )

    assert decision.readiness.readiness_state == "invalidated"
    assert decision.governance_outcome == "invalidated"
    assert decision.allowed_now is False
