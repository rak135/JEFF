"""Distinct readiness contract for start-time governance."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from jeff.core.schemas import ActionId, coerce_action_id

ReadinessState = Literal[
    "ready",
    "ready_with_cautions",
    "pending_approval",
    "pending_revalidation",
    "blocked",
    "invalidated",
    "escalated",
]

_REASONS_REQUIRED = {
    "pending_approval",
    "pending_revalidation",
    "blocked",
    "invalidated",
    "escalated",
}


@dataclass(frozen=True, slots=True)
class Readiness:
    action_id: ActionId
    readiness_state: ReadinessState
    checked_at_state_version: int
    reasons: tuple[str, ...] = ()
    cautions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "action_id", coerce_action_id(str(self.action_id)))
        if self.checked_at_state_version < 0:
            raise ValueError("checked_at_state_version must be zero or greater")
        if self.readiness_state in _REASONS_REQUIRED and not self.reasons:
            raise ValueError(
                f"reasons are required when readiness_state is {self.readiness_state}",
            )

    @property
    def allows_start(self) -> bool:
        return self.readiness_state in {"ready", "ready_with_cautions"}
