"""Shared scoped identity helpers for persisted support records."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TypeVar

from jeff.cognitive.post_selection.selection_review_record import SelectionReviewRecord
from jeff.core.containers.models import Run
from jeff.core.schemas import Scope

_SCOPE_KEY_SEPARATOR = "::"

T = TypeVar("T")


def scoped_support_key(*, project_id: str, work_unit_id: str | None, run_id: str | None) -> str:
    project_text, work_unit_text, run_text = _require_scoped_run_components(
        project_id=project_id,
        work_unit_id=work_unit_id,
        run_id=run_id,
    )
    return _SCOPE_KEY_SEPARATOR.join((project_text, work_unit_text, run_text))


def scoped_support_key_for_scope(scope: Scope) -> str:
    return scoped_support_key(
        project_id=str(scope.project_id),
        work_unit_id=scope.work_unit_id,
        run_id=scope.run_id,
    )


def scoped_support_key_for_run(run: Run) -> str:
    return scoped_support_key(
        project_id=str(run.project_id),
        work_unit_id=str(run.work_unit_id),
        run_id=str(run.run_id),
    )


def legacy_run_key(run_id: str | None) -> str:
    if run_id is None or not str(run_id).strip():
        raise ValueError("support lookup requires a non-empty run_id")
    return str(run_id)


def find_support_record(
    records: Mapping[str, T],
    *,
    scope: Scope | None = None,
    run: Run | None = None,
) -> T | None:
    if (scope is None) == (run is None):
        raise ValueError("find_support_record requires exactly one of scope or run")

    if scope is not None:
        scoped_key = scoped_support_key_for_scope(scope)
        legacy_key = legacy_run_key(scope.run_id)
    else:
        scoped_key = scoped_support_key_for_run(run)
        legacy_key = legacy_run_key(run.run_id)

    record = records.get(scoped_key)
    if record is not None:
        return record
    return records.get(legacy_key)


def selection_review_scope(review: SelectionReviewRecord) -> Scope | None:
    if review.proposal_result is not None:
        return review.proposal_result.scope
    if review.action_scope is not None:
        return review.action_scope
    if review.governance_truth is not None:
        return review.governance_truth.scope
    if review.formed_action_result is not None and review.formed_action_result.action is not None:
        return review.formed_action_result.action.scope
    if review.governance_handoff_result is not None and review.governance_handoff_result.action is not None:
        return review.governance_handoff_result.action.scope
    return None


def _require_scoped_run_components(
    *,
    project_id: str,
    work_unit_id: str | None,
    run_id: str | None,
) -> tuple[str, str, str]:
    project_text = str(project_id).strip()
    work_unit_text = "" if work_unit_id is None else str(work_unit_id).strip()
    run_text = "" if run_id is None else str(run_id).strip()
    if not project_text or not work_unit_text or not run_text:
        raise ValueError("scoped support identity requires project_id, work_unit_id, and run_id")
    return project_text, work_unit_text, run_text