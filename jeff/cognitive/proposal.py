"""Bounded proposal contracts with honest scarcity rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from jeff.core.schemas import ProposalId, Scope, coerce_proposal_id

from .types import normalize_text_list, normalized_identity, require_text

ProposalType = Literal[
    "direct_action",
    "investigate",
    "clarify",
    "defer",
    "escalate",
    "planning_insertion",
]


@dataclass(frozen=True, slots=True)
class ProposalOption:
    proposal_id: ProposalId
    proposal_type: ProposalType
    option_summary: str
    scope: Scope
    assumptions: tuple[str, ...] = ()
    main_risks: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    planning_needed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "proposal_id",
            coerce_proposal_id(str(self.proposal_id)),
        )
        object.__setattr__(
            self,
            "option_summary",
            require_text(self.option_summary, field_name="option_summary"),
        )
        object.__setattr__(
            self,
            "assumptions",
            normalize_text_list(self.assumptions, field_name="assumptions"),
        )
        object.__setattr__(
            self,
            "main_risks",
            normalize_text_list(self.main_risks, field_name="main_risks"),
        )
        object.__setattr__(
            self,
            "blockers",
            normalize_text_list(self.blockers, field_name="blockers"),
        )


@dataclass(frozen=True, slots=True)
class ProposalSet:
    scope: Scope
    options: tuple[ProposalOption, ...]
    scarcity_reason: str | None = None

    def __post_init__(self) -> None:
        if len(self.options) > 3:
            raise ValueError("proposal generation may return at most 3 serious options")
        if len(self.options) < 2:
            if self.scarcity_reason is None or not self.scarcity_reason.strip():
                raise ValueError("scarcity_reason is required when fewer than 2 serious options exist")
            object.__setattr__(
                self,
                "scarcity_reason",
                require_text(self.scarcity_reason, field_name="scarcity_reason"),
            )
        elif self.scarcity_reason is not None:
            object.__setattr__(
                self,
                "scarcity_reason",
                require_text(self.scarcity_reason, field_name="scarcity_reason"),
            )

        seen_ids: set[str] = set()
        seen_signatures: set[tuple[str, str]] = set()
        for option in self.options:
            if option.scope != self.scope:
                raise ValueError("proposal options must preserve the proposal-set scope")
            option_id = str(option.proposal_id)
            if option_id in seen_ids:
                raise ValueError("proposal ids must be unique inside a proposal set")
            seen_ids.add(option_id)

            signature = (option.proposal_type, normalized_identity(option.option_summary))
            if signature in seen_signatures:
                raise ValueError("proposal generation must not pad near-duplicate serious options")
            seen_signatures.add(signature)
