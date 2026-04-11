"""Cognitive layer contracts for context, research, proposal, selection, planning, and evaluation."""

from .context import ContextPackage, assemble_context_package
from .evaluation import EvaluationResult, deterministic_override_reasons, evaluate_outcome
from .planning import PlanArtifact, create_plan, should_plan
from .proposal import ProposalOption, ProposalSet
from .research import (
    EvidenceItem,
    EvidencePack,
    ResearchArtifact,
    ResearchFinding,
    ResearchRequest,
    ResearchResult,
    ResearchSynthesisError,
    ResearchSynthesisValidationError,
    SourceItem,
    build_document_evidence_pack,
    build_research_model_request,
    collect_document_sources,
    run_document_research,
    synthesize_research,
    synthesize_research_with_runtime,
)
from .selection import SelectionResult

__all__ = [
    "ContextPackage",
    "EvidenceItem",
    "EvidencePack",
    "EvaluationResult",
    "PlanArtifact",
    "ProposalOption",
    "ResearchArtifact",
    "ResearchFinding",
    "ProposalSet",
    "ResearchRequest",
    "ResearchResult",
    "ResearchSynthesisError",
    "ResearchSynthesisValidationError",
    "SelectionResult",
    "SourceItem",
    "assemble_context_package",
    "build_document_evidence_pack",
    "build_research_model_request",
    "collect_document_sources",
    "create_plan",
    "deterministic_override_reasons",
    "evaluate_outcome",
    "run_document_research",
    "should_plan",
    "synthesize_research",
    "synthesize_research_with_runtime",
]
