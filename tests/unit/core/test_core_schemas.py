import pytest

from jeff.core.schemas import (
    EnvelopeMetadata,
    InternalEnvelope,
    Scope,
    ValidationIssue,
    coerce_memory_id,
    coerce_project_id,
    coerce_run_id,
    coerce_transition_id,
    coerce_work_unit_id,
)


def test_typed_ids_require_non_empty_strings() -> None:
    assert coerce_project_id("project-1") == "project-1"
    assert coerce_work_unit_id("wu-1") == "wu-1"
    assert coerce_run_id("run-1") == "run-1"
    assert coerce_transition_id("transition-1") == "transition-1"
    assert coerce_memory_id("memory-1") == "memory-1"

    with pytest.raises(ValueError):
        coerce_project_id("   ")


def test_scope_requires_work_unit_when_run_is_present() -> None:
    with pytest.raises(ValueError, match="run_id requires work_unit_id"):
        Scope(project_id="project-1", run_id="run-1")


def test_internal_envelope_accepts_exactly_one_body_shape() -> None:
    scope = Scope(project_id="project-1")
    request_envelope = InternalEnvelope(
        module="core.transition",
        scope=scope,
        metadata=EnvelopeMetadata(),
        payload={"transition": "create_project"},
    )
    result_envelope = InternalEnvelope(
        module="core.transition",
        scope=scope,
        result={"transition_result": "committed"},
    )

    assert request_envelope.payload == {"transition": "create_project"}
    assert result_envelope.result == {"transition_result": "committed"}

    with pytest.raises(ValueError, match="exactly one of payload or result"):
        InternalEnvelope(module="core.transition", scope=scope, payload={}, result={})


def test_validation_issue_requires_machine_usable_fields() -> None:
    issue = ValidationIssue(code="invalid_scope", message="scope is invalid")

    assert issue.code == "invalid_scope"
    assert issue.message == "scope is invalid"
