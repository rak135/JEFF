import pytest

from jeff.contracts import Action
from jeff.core.schemas import Scope
from jeff.governance import Approval, Policy, Readiness


def test_action_contract_is_narrow_and_binds_material_fields() -> None:
    action = Action(
        action_id="action-1",
        scope=Scope(project_id="project-1", work_unit_id="wu-1"),
        intent_summary="Apply a bounded code edit",
        target_summary="repo:jeff",
        protected_surface="core backbone",
        basis_state_version=3,
    )

    assert action.action_id == "action-1"
    assert action.binding_key

    with pytest.raises(ValueError, match="intent_summary"):
        Action(
            action_id="action-2",
            scope=Scope(project_id="project-1"),
            intent_summary="   ",
            basis_state_version=3,
        )


def test_granted_approval_must_bind_to_a_specific_action() -> None:
    with pytest.raises(ValueError, match="action_binding_key is required"):
        Approval(
            approval_verdict="granted",
            action_id="action-1",
            basis_state_version=3,
        )


def test_readiness_requires_reasons_for_non_startable_states() -> None:
    with pytest.raises(ValueError, match="reasons are required"):
        Readiness(
            action_id="action-1",
            readiness_state="blocked",
            checked_at_state_version=3,
        )


def test_policy_and_governance_objects_remain_distinct() -> None:
    policy = Policy(approval_required=True, protected_surface=True)
    approval = Approval.absent()
    readiness = Readiness(
        action_id="action-1",
        readiness_state="pending_approval",
        checked_at_state_version=3,
        reasons=("required approval is absent",),
    )

    assert policy.approval_required is True
    assert approval.approval_verdict == "absent"
    assert readiness.readiness_state == "pending_approval"
