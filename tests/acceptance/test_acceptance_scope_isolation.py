import pytest
import json

from jeff.bootstrap import build_startup_interface_context
from jeff.cognitive import ProposalResult, ProposalResultOption, SelectionResult, assemble_context_package
from jeff.cognitive.post_selection.selection_review_record import SelectionReviewRecord
from jeff.cognitive.types import TriggerInput
from jeff.contracts import Action
from jeff.core.schemas import Scope
from jeff.core.state import bootstrap_global_state
from jeff.core.transition import TransitionRequest, apply_transition
from jeff.interface import InterfaceContext, JeffCLI
from jeff.orchestrator import run_flow
from tests.fixtures.cli import build_flow_run


def _proposal_result(*, scope):
    return ProposalResult(
        request_id="proposal-request-1",
        scope=scope,
        options=(
            ProposalResultOption(
                option_index=1,
                proposal_id="proposal-1",
                proposal_type="direct_action",
                title="Attempt the action.",
                why_now="This is the only bounded path under current scope.",
                summary="Attempt the action.",
                constraints=("Stay inside current project scope",),
            ),
        ),
        scarcity_reason="Only one serious bounded option is available.",
    )


def _state_with_projects_and_runs(*, duplicate_run_ids: bool) -> object:
    state = bootstrap_global_state()
    project_specs = (
        ("project-1", "Alpha", "wu-1", "run-1"),
        ("project-2", "Beta", "wu-2", "run-1" if duplicate_run_ids else "run-2"),
    )
    for project_id, name, work_unit_id, run_id in project_specs:
        state = apply_transition(
            state,
            TransitionRequest(
                transition_id=f"transition-{project_id}",
                transition_type="create_project",
                basis_state_version=state.state_meta.state_version,
                scope=Scope(project_id=project_id),
                payload={"name": name},
            ),
        ).state
        state = apply_transition(
            state,
            TransitionRequest(
                transition_id=f"transition-{work_unit_id}",
                transition_type="create_work_unit",
                basis_state_version=state.state_meta.state_version,
                scope=Scope(project_id=project_id),
                payload={"work_unit_id": work_unit_id, "objective": f"Work in {name}"},
            ),
        ).state
        state = apply_transition(
            state,
            TransitionRequest(
                transition_id=f"transition-{project_id}-{run_id}",
                transition_type="create_run",
                basis_state_version=state.state_meta.state_version,
                scope=Scope(project_id=project_id, work_unit_id=work_unit_id),
                payload={"run_id": run_id},
            ),
        ).state
    return state


def test_wrong_scope_flow_is_invalidated_cleanly() -> None:
    state = _state_with_projects_and_runs(duplicate_run_ids=False)
    flow_scope = Scope(project_id="project-1", work_unit_id="wu-1")
    wrong_scope = Scope(project_id="project-2", work_unit_id="wu-2")

    result = run_flow(
        flow_id="flow-wrong-scope",
        flow_family="blocked_or_escalation",
        scope=flow_scope,
        stage_handlers={
            "context": lambda _input: assemble_context_package(
                trigger=TriggerInput(trigger_summary="Attempt a wrong-project action."),
                purpose="bounded decision support",
                scope=flow_scope,
                state=state,
            ),
            "proposal": lambda _context: _proposal_result(scope=flow_scope),
            "selection": lambda _proposal: SelectionResult(
                selection_id="selection-1",
                considered_proposal_ids=("proposal-1",),
                selected_proposal_id="proposal-1",
                rationale="Use the selected option.",
            ),
            "action": lambda _selection: Action(
                action_id="action-1",
                scope=wrong_scope,
                intent_summary="This action points at the wrong project.",
                basis_state_version=state.state_meta.state_version,
            ),
            "governance": lambda _action: pytest.fail("governance should not run"),
        },
    )

    assert result.lifecycle.lifecycle_state == "invalidated"
    assert tuple(result.outputs.keys()) == ("context", "proposal", "selection")
    assert result.routing_decision is not None
    assert result.routing_decision.routed_outcome == "invalidated"


def test_cli_rejects_wrong_project_run_lookup_under_current_scope() -> None:
    state = _state_with_projects_and_runs(duplicate_run_ids=False)
    cli = JeffCLI(context=InterfaceContext(state=state))
    cli.run_one_shot("/project use project-2")

    with pytest.raises(ValueError, match="current project scope"):
        cli.run_one_shot("/show run-1")


def test_cli_rejects_ambiguous_global_run_lookup_without_scope() -> None:
    state = _state_with_projects_and_runs(duplicate_run_ids=True)
    cli = JeffCLI(context=InterfaceContext(state=state))

    with pytest.raises(ValueError, match="ambiguous run_id"):
        cli.run_one_shot("/show run-1")


def test_cli_trace_fails_closed_when_persisted_flow_support_belongs_to_wrong_scope() -> None:
    state = _state_with_projects_and_runs(duplicate_run_ids=True)
    cli = JeffCLI(
        context=InterfaceContext(
            state=state,
            flow_runs={
                "run-1": build_flow_run(
                    Scope(project_id="project-2", work_unit_id="wu-2", run_id="run-1")
                )
            },
        )
    )
    cli.run_one_shot("/project use project-1")
    cli.run_one_shot("/work use wu-1")

    with pytest.raises(ValueError, match="persisted orchestrator flow result scope mismatch"):
        cli.run_one_shot("/trace run-1")


def test_persisted_scoped_support_readback_survives_restart_without_cross_scope_drift(tmp_path) -> None:
    startup = build_startup_interface_context(base_dir=tmp_path)
    assert startup.runtime_store is not None

    state = startup.runtime_store.apply_transition(
        startup.state,
        TransitionRequest(
            transition_id="transition-run-project-1-run-1",
            transition_type="create_run",
            basis_state_version=startup.state.state_meta.state_version,
            scope=Scope(project_id="project-1", work_unit_id="wu-1"),
            payload={"run_id": "run-1"},
        ),
    ).state
    state = startup.runtime_store.apply_transition(
        state,
        TransitionRequest(
            transition_id="transition-project-2",
            transition_type="create_project",
            basis_state_version=state.state_meta.state_version,
            scope=Scope(project_id="project-2"),
            payload={"name": "Project Two"},
        ),
    ).state
    state = startup.runtime_store.apply_transition(
        state,
        TransitionRequest(
            transition_id="transition-work-unit-project-2",
            transition_type="create_work_unit",
            basis_state_version=state.state_meta.state_version,
            scope=Scope(project_id="project-2"),
            payload={"work_unit_id": "wu-2", "objective": "Scope-isolated persisted support"},
        ),
    ).state
    startup.runtime_store.apply_transition(
        state,
        TransitionRequest(
            transition_id="transition-run-project-2-run-1",
            transition_type="create_run",
            basis_state_version=state.state_meta.state_version,
            scope=Scope(project_id="project-2", work_unit_id="wu-2"),
            payload={"run_id": "run-1"},
        ),
    )

    first_scope = Scope(project_id="project-1", work_unit_id="wu-1", run_id="run-1")
    second_scope = Scope(project_id="project-2", work_unit_id="wu-2", run_id="run-1")
    startup.runtime_store.save_flow_run("run-1", build_flow_run(first_scope, selected_proposal_id="proposal-1"))
    startup.runtime_store.save_flow_run("run-1", build_flow_run(second_scope, selected_proposal_id="proposal-2"))
    startup.runtime_store.save_selection_review("run-1", _selection_review_for_scope(first_scope, selected_proposal_id="proposal-1"))
    startup.runtime_store.save_selection_review("run-1", _selection_review_for_scope(second_scope, selected_proposal_id="proposal-2"))

    cli = JeffCLI(context=build_startup_interface_context(base_dir=tmp_path))

    cli.run_one_shot("/project use project-1")
    cli.run_one_shot("/work use wu-1")
    first_show = json.loads(cli.run_one_shot("/show run-1", json_output=True))
    first_selection = json.loads(cli.run_one_shot("/selection show run-1", json_output=True))
    first_inspect = json.loads(cli.run_one_shot("/inspect", json_output=True))

    cli.run_one_shot("/project use project-2")
    cli.run_one_shot("/work use wu-2")
    second_show = json.loads(cli.run_one_shot("/show run-1", json_output=True))
    second_selection = json.loads(cli.run_one_shot("/selection show run-1", json_output=True))
    second_inspect = json.loads(cli.run_one_shot("/inspect", json_output=True))

    assert first_show["truth"]["project_id"] == "project-1"
    assert first_show["truth"]["work_unit_id"] == "wu-1"
    assert first_show["truth"]["run_id"] == "run-1"
    assert first_show["support"]["proposal_summary"]["selected_proposal_id"] == "proposal-1"
    assert first_selection["selection"]["selected_proposal_id"] == "proposal-1"
    assert first_inspect["support"]["proposal_summary"]["selected_proposal_id"] == "proposal-1"

    assert second_show["truth"]["project_id"] == "project-2"
    assert second_show["truth"]["work_unit_id"] == "wu-2"
    assert second_show["truth"]["run_id"] == "run-1"
    assert second_show["support"]["proposal_summary"]["selected_proposal_id"] == "proposal-2"
    assert second_selection["selection"]["selected_proposal_id"] == "proposal-2"
    assert second_inspect["support"]["proposal_summary"]["selected_proposal_id"] == "proposal-2"


def _selection_review_for_scope(scope: Scope, *, selected_proposal_id: str) -> SelectionReviewRecord:
    proposal_result = ProposalResult(
        request_id=f"proposal-request-{scope.project_id}-{scope.work_unit_id}-{scope.run_id}",
        scope=scope,
        options=(
            ProposalResultOption(
                option_index=1,
                proposal_id=selected_proposal_id,
                proposal_type="direct_action",
                title=f"Selected option for {scope.project_id}",
                why_now="Support must stay in the requested scope.",
                summary=f"Selected option for {scope.project_id}",
            ),
            ProposalResultOption(
                option_index=2,
                proposal_id=f"fallback-{scope.project_id}",
                proposal_type="clarify",
                title=f"Fallback option for {scope.project_id}",
                why_now="Fallback support remains available.",
                summary=f"Fallback option for {scope.project_id}",
            ),
        ),
    )
    return SelectionReviewRecord(
        selection_result=SelectionResult(
            selection_id=f"selection-{scope.project_id}-{scope.work_unit_id}-{scope.run_id}",
            considered_proposal_ids=(selected_proposal_id, f"fallback-{scope.project_id}"),
            selected_proposal_id=selected_proposal_id,
            rationale="Persisted selection review must remain scope-bound.",
        ),
        proposal_result=proposal_result,
        action_scope=scope,
    )
