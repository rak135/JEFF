import pytest

from jeff.cognitive.context import assemble_context_package
from jeff.cognitive.types import SupportInput, TriggerInput
from jeff.core.schemas import Scope
from jeff.core.state import bootstrap_global_state
from jeff.core.transition import TransitionRequest, apply_transition


def _state_with_run():
    state = bootstrap_global_state()
    state = apply_transition(
        state,
        TransitionRequest(
            transition_id="transition-1",
            transition_type="create_project",
            basis_state_version=0,
            scope=Scope(project_id="project-1"),
            payload={"name": "Alpha"},
        ),
    ).state
    state = apply_transition(
        state,
        TransitionRequest(
            transition_id="transition-2",
            transition_type="create_work_unit",
            basis_state_version=1,
            scope=Scope(project_id="project-1"),
            payload={"work_unit_id": "wu-1", "objective": "Ship Phase 3"},
        ),
    ).state
    state = apply_transition(
        state,
        TransitionRequest(
            transition_id="transition-3",
            transition_type="create_run",
            basis_state_version=2,
            scope=Scope(project_id="project-1", work_unit_id="wu-1"),
            payload={"run_id": "run-1"},
        ),
    ).state
    return state


def test_context_anchors_on_current_truth_first() -> None:
    state = _state_with_run()
    context = assemble_context_package(
        trigger=TriggerInput(trigger_summary="Prepare proposal options"),
        purpose="proposal support",
        scope=Scope(project_id="project-1", work_unit_id="wu-1", run_id="run-1"),
        state=state,
    )

    assert [record.truth_family for record in context.truth_records] == ["project", "work_unit", "run"]
    assert context.support_inputs == ()


def test_context_rejects_wrong_project_support() -> None:
    state = _state_with_run()

    with pytest.raises(ValueError, match="current project scope"):
        assemble_context_package(
            trigger=TriggerInput(trigger_summary="Prepare proposal options"),
            purpose="proposal support",
            scope=Scope(project_id="project-1", work_unit_id="wu-1"),
            state=state,
            support_inputs=(
                SupportInput(
                    source_family="research",
                    scope=Scope(project_id="project-2"),
                    summary="Other project note",
                ),
            ),
        )


def test_context_does_not_allow_session_or_archive_residue() -> None:
    with pytest.raises(ValueError, match="not valid context support"):
        SupportInput(
            source_family="session_state",
            scope=Scope(project_id="project-1"),
            summary="UI tab residue",
        )

    with pytest.raises(ValueError, match="full-body or archive-style support"):
        SupportInput(
            source_family="artifact",
            scope=Scope(project_id="project-1"),
            summary="Full archive dump",
            include_full_body=True,
        )
