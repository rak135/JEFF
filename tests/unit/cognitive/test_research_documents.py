from pathlib import Path

from jeff.cognitive import (
    build_document_evidence_pack,
    collect_document_sources,
)
from jeff.cognitive.research import ResearchRequest


def test_collect_document_sources_reads_only_explicit_paths(tmp_path: Path) -> None:
    included = tmp_path / "included.md"
    included.write_text("Bounded note about the current plan.", encoding="utf-8")
    excluded_dir = tmp_path / "excluded"
    excluded_dir.mkdir()
    (excluded_dir / "excluded.md").write_text("This should not be read.", encoding="utf-8")

    sources = collect_document_sources(
        ResearchRequest(
            question="What does the current plan say?",
            document_paths=(str(included),),
        )
    )

    assert len(sources) == 1
    assert sources[0].title == "included.md"
    assert "excluded.md" not in sources[0].locator


def test_collect_document_sources_skips_unsupported_extensions_safely(tmp_path: Path) -> None:
    supported = tmp_path / "supported.md"
    supported.write_text("Supported text file.", encoding="utf-8")
    unsupported = tmp_path / "unsupported.pdf"
    unsupported.write_text("Not supported in this slice.", encoding="utf-8")

    sources = collect_document_sources(
        ResearchRequest(
            question="What is supported?",
            document_paths=(str(supported), str(unsupported)),
        )
    )

    assert tuple(source.title for source in sources) == ("supported.md",)


def test_collect_document_sources_respects_max_files(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "b.md").write_text("B", encoding="utf-8")
    (docs_dir / "a.md").write_text("A", encoding="utf-8")
    (docs_dir / "c.md").write_text("C", encoding="utf-8")

    sources = collect_document_sources(
        ResearchRequest(
            question="Which files exist?",
            document_paths=(str(docs_dir),),
            max_files=2,
        )
    )

    assert tuple(source.title for source in sources) == ("a.md", "b.md")


def test_collect_document_sources_respects_max_chars_per_file(tmp_path: Path) -> None:
    document = tmp_path / "bounded.md"
    document.write_text(("A" * 20) + ("B" * 20), encoding="utf-8")

    sources = collect_document_sources(
        ResearchRequest(
            question="What is in the file?",
            document_paths=(str(document),),
            max_chars_per_file=20,
        )
    )

    assert sources[0].snippet == "A" * 20


def test_collect_document_sources_keeps_deterministic_order(tmp_path: Path) -> None:
    standalone = tmp_path / "standalone.md"
    standalone.write_text("Standalone first.", encoding="utf-8")
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "z.md").write_text("Z", encoding="utf-8")
    (docs_dir / "a.md").write_text("A", encoding="utf-8")

    sources = collect_document_sources(
        ResearchRequest(
            question="What documents exist?",
            document_paths=(str(standalone), str(docs_dir)),
        )
    )

    assert tuple(source.title for source in sources) == ("standalone.md", "a.md", "z.md")


def test_build_document_evidence_pack_produces_bounded_evidence_with_real_source_refs(
    tmp_path: Path,
) -> None:
    request = ResearchRequest(
        question="What says the current plan about stability?",
        document_paths=(str(tmp_path),),
        max_evidence_items=1,
    )
    (tmp_path / "plan.md").write_text(
        "The current plan keeps the system stable.\n"
        "\n"
        "Stability is the main concern for this slice.\n",
        encoding="utf-8",
    )
    (tmp_path / "notes.md").write_text("General notes without strong overlap.", encoding="utf-8")

    sources = collect_document_sources(request)
    evidence_pack = build_document_evidence_pack(request, sources)

    source_ids = {source.source_id for source in sources}

    assert len(evidence_pack.evidence_items) == 1
    assert evidence_pack.evidence_items[0].source_refs[0] in source_ids
    assert "stable" in evidence_pack.evidence_items[0].text.lower()


def test_build_document_evidence_pack_does_not_invent_evidence_when_query_is_unsupported(
    tmp_path: Path,
) -> None:
    request = ResearchRequest(
        question="What database migration risk exists?",
        document_paths=(str(tmp_path),),
    )
    (tmp_path / "fruit.md").write_text("Apples and oranges are discussed here.", encoding="utf-8")

    sources = collect_document_sources(request)
    evidence_pack = build_document_evidence_pack(request, sources)

    assert evidence_pack.evidence_items == ()
    assert any("No strong evidence found" in item for item in evidence_pack.uncertainties)


def test_build_document_evidence_pack_surfaces_explicit_contradiction_markers(tmp_path: Path) -> None:
    request = ResearchRequest(
        question="What contradiction exists in the current plan?",
        document_paths=(str(tmp_path),),
    )
    (tmp_path / "plan.md").write_text(
        "Contradiction: the current plan conflicts with the documented constraint.\n"
        "The current plan should stay bounded.\n",
        encoding="utf-8",
    )

    sources = collect_document_sources(request)
    evidence_pack = build_document_evidence_pack(request, sources)

    assert evidence_pack.contradictions
    assert sources[0].source_id in evidence_pack.contradictions[0]
