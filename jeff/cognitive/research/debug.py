"""Shared research debug and support formatting helpers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


ResearchDebugEmitter = Callable[[dict[str, object]], None]

RESEARCH_DEBUG_CHECKPOINTS: tuple[str, ...] = (
    "source_key_map_built",
    "content_generation_started",
    "content_generation_succeeded",
    "content_generation_failed",
    "syntax_precheck_failed",
    "deterministic_transform_started",
    "deterministic_transform_succeeded",
    "deterministic_transform_failed",
    "formatter_fallback_started",
    "formatter_fallback_succeeded",
    "formatter_fallback_failed",
    "citation_remap_started",
    "citation_remap_succeeded",
    "citation_remap_failed",
    "provenance_validation_started",
    "provenance_validation_succeeded",
    "provenance_validation_failed",
)


def emit_research_debug_event(
    emitter: ResearchDebugEmitter | None,
    checkpoint: str,
    **payload: object,
) -> None:
    """Emit a research debug event if an emitter is provided.

    This is the canonical implementation for research debug event emission.
    All research modules should use this helper instead of duplicating logic.
    """
    if emitter is None:
        return
    emitter(
        {
            "domain": "research",
            "checkpoint": checkpoint,
            "payload": payload,
        }
    )


def summarize_values(values: tuple[str, ...], *, limit: int = 5) -> list[str]:
    """Summarize a tuple of string values for debug output.

    Returns the values up to the limit, with a "+N more" suffix if truncated.
    """
    items = list(values)
    if len(items) <= limit:
        return items
    return [*items[:limit], f"+{len(items) - limit} more"]


def finding_source_refs_summary(findings: tuple[Any, ...], *, limit: int = 4) -> list[str]:
    """Summarize source_refs from research findings for debug output.

    Each finding is expected to have a `source_refs` attribute (tuple of strings).
    Returns a list of comma-separated source_refs strings, truncated if necessary.
    """
    summary = [",".join(finding.source_refs) for finding in findings]
    return summarize_values(tuple(summary), limit=limit)
