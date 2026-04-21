"""InterfaceContext/runtime-store wrappers around selection review records."""

from __future__ import annotations

from jeff.core.schemas import Scope
from jeff.core.containers.models import Run
from jeff.orchestrator import FlowRunResult

from jeff.cognitive.post_selection.selection_review import materialize_selection_review_from_available_data
from jeff.cognitive.post_selection.selection_review_record import SelectionReviewRecord
from jeff.runtime_support_identity import (
    find_support_record,
    scoped_support_key_for_scope,
    selection_review_scope,
)

from ..models import InterfaceContext


def ensure_selection_review_for_run(
    *,
    context: InterfaceContext,
    run: Run,
    flow_run: FlowRunResult | None,
) -> tuple[InterfaceContext, SelectionReviewRecord | None]:
    return _selection_review_for_run_with_context_update(
        context=context,
        run=run,
        flow_run=flow_run,
        persist=True,
    )


def materialize_selection_review_for_run(
    *,
    context: InterfaceContext,
    run: Run,
    flow_run: FlowRunResult | None,
) -> tuple[InterfaceContext, SelectionReviewRecord | None]:
    return _selection_review_for_run_with_context_update(
        context=context,
        run=run,
        flow_run=flow_run,
        persist=False,
    )


def replace_selection_review(
    *,
    context: InterfaceContext,
    run_id: str,
    selection_review: SelectionReviewRecord,
) -> InterfaceContext:
    return _store_selection_review_in_context(
        context=context,
        run_id=run_id,
        selection_review=selection_review,
        persist=True,
    )


def _selection_review_for_run_with_context_update(
    *,
    context: InterfaceContext,
    run: Run,
    flow_run: FlowRunResult | None,
    persist: bool,
) -> tuple[InterfaceContext, SelectionReviewRecord | None]:
    run_id = str(run.run_id)
    existing_review = find_selection_review_for_run(context, run)
    selection_review = materialize_selection_review_from_available_data(
        existing_review=existing_review,
        flow_run=flow_run,
    )
    if selection_review is None:
        return context, None
    if existing_review == selection_review:
        return context, selection_review
    return _store_selection_review_in_context(
        context=context,
        run_id=run_id,
        selection_review=selection_review,
        persist=persist,
    ), selection_review


def _store_selection_review_in_context(
    *,
    context: InterfaceContext,
    run_id: str,
    selection_review: SelectionReviewRecord,
    persist: bool,
) -> InterfaceContext:
    if persist and context.runtime_store is not None:
        context.runtime_store.save_selection_review(run_id, selection_review)
    next_reviews = dict(context.selection_reviews)
    review_scope = selection_review_scope(selection_review)
    record_key = run_id if review_scope is None else scoped_support_key_for_scope(review_scope)
    next_reviews[record_key] = selection_review
    return InterfaceContext(
        state=context.state,
        flow_runs=context.flow_runs,
        selection_reviews=next_reviews,
        infrastructure_services=context.infrastructure_services,
        research_artifact_store=context.research_artifact_store,
        research_archive_store=context.research_archive_store,
        knowledge_store=context.knowledge_store,
        memory_store=context.memory_store,
        research_memory_handoff_enabled=context.research_memory_handoff_enabled,
        runtime_store=context.runtime_store,
        startup_summary=context.startup_summary,
    )


def _selection_review_for_context(*, context: InterfaceContext, scope: Scope) -> SelectionReviewRecord | None:
    if scope.run_id is None:
        return None

    review = find_support_record(context.selection_reviews, scope=scope)
    if review is None:
        return None
    review_scope = selection_review_scope(review)
    if review_scope is not None and not _scope_matches_scope(review_scope, scope):
        raise ValueError(
            "persisted selection review scope mismatch: "
            f"requested project_id={scope.project_id} work_unit_id={scope.work_unit_id} run_id={scope.run_id}, "
            f"but stored support belongs to project_id={review_scope.project_id} "
            f"work_unit_id={review_scope.work_unit_id} run_id={review_scope.run_id}."
        )
    return materialize_selection_review_from_available_data(
        existing_review=review,
        flow_run=find_support_record(context.flow_runs, scope=scope),
    )


def find_selection_review_for_run(context: InterfaceContext, run: Run) -> SelectionReviewRecord | None:
    review = find_support_record(context.selection_reviews, run=run)
    if review is None:
        return None
    review_scope = selection_review_scope(review)
    if review_scope is None or _scope_matches_run(review_scope, run):
        return review
    raise ValueError(
        "persisted selection review scope mismatch: "
        f"requested project_id={run.project_id} work_unit_id={run.work_unit_id} run_id={run.run_id}, "
        f"but stored support belongs to project_id={review_scope.project_id} "
        f"work_unit_id={review_scope.work_unit_id} run_id={review_scope.run_id}."
    )

def _scope_matches_run(scope: Scope, run: Run) -> bool:
    return _scope_matches_scope(
        scope,
        Scope(
            project_id=str(run.project_id),
            work_unit_id=str(run.work_unit_id),
            run_id=str(run.run_id),
        ),
    )


def _scope_matches_scope(left: Scope, right: Scope) -> bool:
    return (
        str(left.project_id) == str(right.project_id)
        and str(left.work_unit_id) == str(right.work_unit_id)
        and str(left.run_id) == str(right.run_id)
    )