"""Narrow transient action contract for governance input."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from jeff.core.schemas import ActionId, Scope, coerce_action_id


def _normalize_optional_text(value: str | None, *, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string or None")

    normalized = value.strip()
    return normalized or None


def _normalize_required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be a non-empty string")

    return normalized


@dataclass(frozen=True, slots=True)
class Action:
    action_id: ActionId
    scope: Scope
    intent_summary: str
    target_summary: str | None = None
    protected_surface: str | None = None
    basis_state_version: int = 0
    basis_label: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "action_id", coerce_action_id(str(self.action_id)))
        object.__setattr__(
            self,
            "intent_summary",
            _normalize_required_text(self.intent_summary, field_name="intent_summary"),
        )
        object.__setattr__(
            self,
            "target_summary",
            _normalize_optional_text(self.target_summary, field_name="target_summary"),
        )
        object.__setattr__(
            self,
            "protected_surface",
            _normalize_optional_text(
                self.protected_surface,
                field_name="protected_surface",
            ),
        )
        object.__setattr__(
            self,
            "basis_label",
            _normalize_optional_text(self.basis_label, field_name="basis_label"),
        )

        if not isinstance(self.basis_state_version, int):
            raise TypeError("basis_state_version must be an integer")
        if self.basis_state_version < 0:
            raise ValueError("basis_state_version must be zero or greater")

    @property
    def binding_key(self) -> str:
        material_shape = {
            "action_id": str(self.action_id),
            "project_id": str(self.scope.project_id),
            "work_unit_id": None if self.scope.work_unit_id is None else str(self.scope.work_unit_id),
            "run_id": None if self.scope.run_id is None else str(self.scope.run_id),
            "intent_summary": self.intent_summary,
            "target_summary": self.target_summary,
            "protected_surface": self.protected_surface,
            "basis_state_version": self.basis_state_version,
        }
        encoded = json.dumps(material_shape, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
