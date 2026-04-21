import json
from pathlib import Path

from jeff.bootstrap import build_infrastructure_runtime, build_startup_interface_context
from jeff.core.schemas import Scope
from jeff.core.transition import TransitionRequest
from jeff.infrastructure import AdapterFactoryConfig, AdapterProviderKind, ModelAdapterRuntimeConfig, PurposeOverrides
from jeff.interface import JeffCLI
from jeff.interface.commands import InterfaceContext


def test_persisted_proposal_readback_does_not_drift_across_colliding_run_ids(tmp_path: Path) -> None:
    _create_cross_scope_collision(tmp_path)

    primary_cli = _cli_with_fake_proposal(tmp_path, _proposal_text("Primary scope option"))
    primary_cli.run_one_shot("/project use project-1")
    primary_cli.run_one_shot("/work use wu-1")
    primary_cli.run_one_shot("/run use run-1")
    primary_created = json.loads(primary_cli.run_one_shot('/proposal "Primary scope objective"', json_output=True))

    secondary_cli = _cli_with_fake_proposal(tmp_path, _proposal_text("Secondary scope option"))
    secondary_cli.run_one_shot("/project use project-2")
    secondary_cli.run_one_shot("/work use wu-2")
    secondary_cli.run_one_shot("/run use run-1")
    secondary_created = json.loads(secondary_cli.run_one_shot('/proposal "Secondary scope objective"', json_output=True))

    reloaded = build_startup_interface_context(base_dir=tmp_path)
    assert reloaded.runtime_store is not None
    stored_records = reloaded.runtime_store.load_proposal_records()
    bare_run_matches = sorted(
        [record for record in stored_records.values() if str(record.scope.run_id) == "run-1"],
        key=lambda record: (record.created_at, record.proposal_id),
    )

    assert len(bare_run_matches) == 2
    assert {str(record.scope.project_id) for record in bare_run_matches} == {"project-1", "project-2"}
    assert bare_run_matches[-1].proposal_id == secondary_created["truth"]["proposal_id"]

    primary_readback_cli = JeffCLI(context=reloaded)
    primary_readback_cli.run_one_shot("/project use project-1")
    primary_readback_cli.run_one_shot("/work use wu-1")
    primary_readback_cli.run_one_shot("/run use run-1")
    primary_readback = json.loads(primary_readback_cli.run_one_shot("/proposal show run-1", json_output=True))

    secondary_readback_cli = JeffCLI(context=build_startup_interface_context(base_dir=tmp_path))
    secondary_readback_cli.run_one_shot("/project use project-2")
    secondary_readback_cli.run_one_shot("/work use wu-2")
    secondary_readback_cli.run_one_shot("/run use run-1")
    secondary_readback = json.loads(secondary_readback_cli.run_one_shot("/proposal show run-1", json_output=True))

    assert primary_readback["truth"]["scope"] == {
        "project_id": "project-1",
        "work_unit_id": "wu-1",
        "run_id": "run-1",
    }
    assert primary_readback["truth"]["proposal_id"] == primary_created["truth"]["proposal_id"]
    assert primary_readback["truth"]["proposal_id"] != secondary_created["truth"]["proposal_id"]
    assert secondary_readback["truth"]["scope"] == {
        "project_id": "project-2",
        "work_unit_id": "wu-2",
        "run_id": "run-1",
    }
    assert secondary_readback["truth"]["proposal_id"] == secondary_created["truth"]["proposal_id"]
    assert secondary_readback["truth"]["proposal_id"] != primary_created["truth"]["proposal_id"]


def _create_cross_scope_collision(tmp_path: Path) -> None:
    startup = build_startup_interface_context(base_dir=tmp_path)
    assert startup.runtime_store is not None

    state = startup.state
    transitions = (
        TransitionRequest(
            transition_id="transition-create-primary-run",
            transition_type="create_run",
            basis_state_version=state.state_meta.state_version,
            scope=Scope(project_id="project-1", work_unit_id="wu-1"),
            payload={"run_id": "run-1"},
        ),
        TransitionRequest(
            transition_id="transition-create-project-2",
            transition_type="create_project",
            basis_state_version=state.state_meta.state_version + 1,
            scope=Scope(project_id="project-2"),
            payload={"name": "Beta"},
        ),
        TransitionRequest(
            transition_id="transition-create-work-unit-2",
            transition_type="create_work_unit",
            basis_state_version=state.state_meta.state_version + 2,
            scope=Scope(project_id="project-2"),
            payload={"work_unit_id": "wu-2", "objective": "Secondary bounded work"},
        ),
        TransitionRequest(
            transition_id="transition-create-secondary-run",
            transition_type="create_run",
            basis_state_version=state.state_meta.state_version + 3,
            scope=Scope(project_id="project-2", work_unit_id="wu-2"),
            payload={"run_id": "run-1"},
        ),
    )
    for request in transitions:
        result = startup.runtime_store.apply_transition(state, request)
        state = result.state


def _cli_with_fake_proposal(tmp_path: Path, proposal_text: str) -> JeffCLI:
    startup = build_startup_interface_context(base_dir=tmp_path)
    services = build_infrastructure_runtime(
        ModelAdapterRuntimeConfig(
            default_adapter_id="fake-default",
            adapters=(
                AdapterFactoryConfig(
                    provider_kind=AdapterProviderKind.FAKE,
                    adapter_id="fake-default",
                    model_name="default-model",
                    fake_text_response="unused default adapter",
                ),
                AdapterFactoryConfig(
                    provider_kind=AdapterProviderKind.FAKE,
                    adapter_id="fake-proposal",
                    model_name="proposal-model",
                    fake_text_response=proposal_text,
                ),
            ),
            purpose_overrides=PurposeOverrides(proposal="fake-proposal"),
        )
    )
    return JeffCLI(
        context=InterfaceContext(
            state=startup.state,
            flow_runs=startup.flow_runs,
            selection_reviews=startup.selection_reviews,
            infrastructure_services=services,
            research_artifact_store=startup.research_artifact_store,
            research_archive_store=startup.research_archive_store,
            knowledge_store=startup.knowledge_store,
            memory_store=startup.memory_store,
            research_memory_handoff_enabled=startup.research_memory_handoff_enabled,
            runtime_store=startup.runtime_store,
            startup_summary=startup.startup_summary,
        )
    )


def _proposal_text(title: str) -> str:
    return (
        "PROPOSAL_COUNT: 1\n"
        "SCARCITY_REASON: Only one scope-matched option is grounded.\n"
        "OPTION_1_TYPE: direct_action\n"
        f"OPTION_1_TITLE: {title}\n"
        "OPTION_1_SUMMARY: Take the bounded next step inside the selected scope.\n"
        "OPTION_1_WHY_NOW: The explicit scope already contains the bounded context needed for this action.\n"
        "OPTION_1_ASSUMPTIONS: Current support remains scoped correctly\n"
        "OPTION_1_RISKS: A scope mismatch would invalidate the action\n"
        "OPTION_1_CONSTRAINTS: Stay inside the explicit project and work scope\n"
        "OPTION_1_BLOCKERS: No explicit blockers identified from the provided support.\n"
        "OPTION_1_PLANNING_NEEDED: no\n"
        "OPTION_1_FEASIBILITY: High under the current bounded support\n"
        "OPTION_1_REVERSIBILITY: Straightforward rollback\n"
        "OPTION_1_SUPPORT_REFS: ctx-1\n"
    )