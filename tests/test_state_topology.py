from dataclasses import FrozenInstanceError

import pytest

from jeff.core.containers import Project, Run, WorkUnit
from jeff.core.state import GlobalState, bootstrap_global_state


def test_bootstrap_creates_one_global_state_root_with_nested_projects() -> None:
    state = bootstrap_global_state()

    assert isinstance(state, GlobalState)
    assert state.state_meta.state_version == 0
    assert state.projects == {}


def test_projects_live_inside_global_state_not_as_peer_roots() -> None:
    project = Project(project_id="project-1", name="Alpha")
    state = GlobalState(projects={project.project_id: project})

    assert state.projects["project-1"].project_id == "project-1"
    assert not hasattr(project, "projects")


def test_direct_field_mutation_is_not_the_supported_state_api() -> None:
    state = bootstrap_global_state()

    with pytest.raises(FrozenInstanceError):
        state.state_meta = state.state_meta  # type: ignore[misc]


def test_state_rejects_cross_project_topology() -> None:
    run = Run(run_id="run-1", project_id="project-2", work_unit_id="wu-1")

    with pytest.raises(ValueError, match="run.project_id must match"):
        WorkUnit(
            work_unit_id="wu-1",
            project_id="project-1",
            objective="Do something bounded",
            runs={run.run_id: run},
        )
