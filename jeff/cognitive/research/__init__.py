"""Research contracts and bounded acquisition/synthesis paths."""

from .contracts import EvidenceItem, EvidencePack, ResearchArtifact, ResearchFinding, ResearchRequest, SourceItem
from .documents import build_document_evidence_pack, collect_document_sources, run_document_research
from .errors import ResearchSynthesisError, ResearchSynthesisValidationError
from .legacy import ResearchResult
from .synthesis import build_research_model_request, synthesize_research, synthesize_research_with_runtime

__all__ = [
    "EvidenceItem",
    "EvidencePack",
    "ResearchArtifact",
    "ResearchFinding",
    "ResearchRequest",
    "ResearchResult",
    "ResearchSynthesisError",
    "ResearchSynthesisValidationError",
    "SourceItem",
    "build_document_evidence_pack",
    "build_research_model_request",
    "collect_document_sources",
    "run_document_research",
    "synthesize_research",
    "synthesize_research_with_runtime",
]
