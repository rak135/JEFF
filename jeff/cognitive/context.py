"""Truth-first context package and assembler."""

from __future__ import annotations

from dataclasses import dataclass

from jeff.core.state import GlobalState
from jeff.core.schemas import Scope

from .types import SupportInput, TriggerInput, TruthRecord, require_text


@dataclass(frozen=True, slots=True)
class ContextPackage:
    purpose: str
    trigger: TriggerInput
    scope: Scope
    truth_records: tuple[TruthRecord, ...]
    support_inputs: tuple[SupportInput, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "purpose", require_text(self.purpose, field_name="purpose"))
        if not self.truth_records:
            raise ValueError("context package must anchor on current truth records")


def assemble_context_package(
    *,
    trigger: TriggerInput,
    purpose: str,
    scope: Scope,
    state: GlobalState,
    support_inputs: tuple[SupportInput, ...] | None = None,
) -> ContextPackage:
    truth_records = _extract_truth_records(state=state, scope=scope)
    validated_support = tuple(_validate_support(scope=scope, support=support) for support in (support_inputs or ()))

    return ContextPackage(
        purpose=purpose,
        trigger=trigger,
        scope=scope,
        truth_records=truth_records,
        support_inputs=validated_support,
    )


def _extract_truth_records(*, state: GlobalState, scope: Scope) -> tuple[TruthRecord, ...]:
    project = state.projects.get(scope.project_id)
    if project is None:
        raise ValueError("context scope project_id does not exist in canonical truth")

    records: list[TruthRecord] = [
        TruthRecord(
            truth_family="project",
            scope=Scope(project_id=project.project_id),
            summary=f"project:{project.project_id} {project.name} [{project.project_lifecycle_state}]",
        ),
    ]

    if scope.work_unit_id is not None:
        work_unit = project.work_units.get(scope.work_unit_id)
        if work_unit is None:
            raise ValueError("context scope work_unit_id does not exist in canonical truth")
        records.append(
            TruthRecord(
                truth_family="work_unit",
                scope=Scope(project_id=project.project_id, work_unit_id=work_unit.work_unit_id),
                summary=(
                    f"work_unit:{work_unit.work_unit_id} {work_unit.objective} "
                    f"[{work_unit.work_unit_lifecycle_state}]"
                ),
            ),
        )

        if scope.run_id is not None:
            run = work_unit.runs.get(scope.run_id)
            if run is None:
                raise ValueError("context scope run_id does not exist in canonical truth")
            records.append(
                TruthRecord(
                    truth_family="run",
                    scope=Scope(
                        project_id=project.project_id,
                        work_unit_id=work_unit.work_unit_id,
                        run_id=run.run_id,
                    ),
                    summary=f"run:{run.run_id} [{run.run_lifecycle_state}]",
                ),
            )

    return tuple(records)


def _validate_support(*, scope: Scope, support: SupportInput) -> SupportInput:
    if support.scope.project_id != scope.project_id:
        raise ValueError("context support must stay inside the current project scope")

    if scope.work_unit_id is None and support.scope.work_unit_id is not None:
        raise ValueError("work-unit-scoped support cannot be injected into project-only context")
    if scope.work_unit_id is not None and support.scope.work_unit_id not in {None, scope.work_unit_id}:
        raise ValueError("context support must stay inside the current work_unit scope")

    if scope.run_id is None and support.scope.run_id is not None:
        raise ValueError("run-scoped support cannot be injected into broader context")
    if scope.run_id is not None and support.scope.run_id not in {None, scope.run_id}:
        raise ValueError("context support must stay inside the current run scope")

    return support
