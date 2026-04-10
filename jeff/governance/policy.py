"""Minimal policy representation for governance."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Policy:
    approval_required: bool = False
    action_forbidden: bool = False
    protected_surface: bool = False
    destructive: bool = False
    direction_sensitive: bool = False
    freshness_sensitive: bool = True
    revalidation_required: bool = False

