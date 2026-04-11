import pytest

from jeff.core.containers import Project, Run, WorkUnit


def test_work_unit_cannot_belong_to_multiple_projects() -> None:
    work_unit = WorkUnit(
        work_unit_id="wu-1",
        project_id="project-2",
        objective="Bounded implementation effort",
    )

    with pytest.raises(ValueError, match="work_unit.project_id must match"):
        Project(
            project_id="project-1",
            name="Alpha",
            work_units={work_unit.work_unit_id: work_unit},
        )


def test_run_requires_one_owning_project_and_one_owning_work_unit() -> None:
    run = Run(run_id="run-1", project_id="project-1", work_unit_id="wu-2")

    with pytest.raises(ValueError, match="run.work_unit_id must match"):
        WorkUnit(
            work_unit_id="wu-1",
            project_id="project-1",
            objective="Bounded research effort",
            runs={run.run_id: run},
        )


def test_project_owns_work_units_and_work_unit_owns_runs() -> None:
    run = Run(run_id="run-1", project_id="project-1", work_unit_id="wu-1")
    work_unit = WorkUnit(
        work_unit_id="wu-1",
        project_id="project-1",
        objective="Bounded implementation effort",
        runs={run.run_id: run},
    )
    project = Project(
        project_id="project-1",
        name="Alpha",
        work_units={work_unit.work_unit_id: work_unit},
    )

    assert project.work_units["wu-1"].runs["run-1"].run_id == "run-1"
