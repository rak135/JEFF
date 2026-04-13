from jeff.cognitive import (
    EvidenceItem,
    EvidencePack,
    ResearchRequest,
    SourceItem,
    synthesize_research_with_runtime,
)
from jeff.infrastructure import (
    AdapterFactoryConfig,
    AdapterProviderKind,
    ModelAdapterRuntimeConfig,
    build_infrastructure_services,
)


def test_runtime_default_fake_adapter_can_drive_research_synthesis() -> None:
    services = build_infrastructure_services(
        ModelAdapterRuntimeConfig(
            default_adapter_id="fake-default",
            adapters=(
                AdapterFactoryConfig(
                    provider_kind=AdapterProviderKind.FAKE,
                    adapter_id="fake-default",
                    model_name="fake-model",
                    fake_text_response=_bounded_text(
                        summary="Default adapter summary.",
                        findings=(("Bounded fact", "S1"),),
                        inference="Bounded inference",
                        uncertainty="Known uncertainty",
                        recommendation="Stay bounded.",
                    ),
                ),
            ),
        )
    )

    artifact = synthesize_research_with_runtime(
        research_request=_request(),
        evidence_pack=_evidence_pack(),
        infrastructure_services=services,
    )

    assert artifact.summary == "Default adapter summary."
    assert artifact.source_ids == ("source-a",)


def test_runtime_explicit_adapter_selection_works_with_multiple_fake_adapters() -> None:
    services = build_infrastructure_services(
        ModelAdapterRuntimeConfig(
            default_adapter_id="fake-default",
            adapters=(
                AdapterFactoryConfig(
                    provider_kind=AdapterProviderKind.FAKE,
                    adapter_id="fake-default",
                    model_name="fake-model",
                    fake_text_response=_bounded_text(
                        summary="Default summary.",
                        findings=(("Default fact", "S1"),),
                        inference="Default inference",
                        uncertainty="Default uncertainty",
                        recommendation="Default recommendation.",
                    ),
                ),
                AdapterFactoryConfig(
                    provider_kind=AdapterProviderKind.FAKE,
                    adapter_id="fake-secondary",
                    model_name="fake-model-2",
                    fake_text_response=_bounded_text(
                        summary="Secondary summary.",
                        findings=(("Secondary fact", "S2"),),
                        inference="Secondary inference",
                        uncertainty="Secondary uncertainty",
                        recommendation="Use secondary.",
                    ),
                ),
            ),
        )
    )

    artifact = synthesize_research_with_runtime(
        research_request=_request(),
        evidence_pack=_evidence_pack(),
        infrastructure_services=services,
        adapter_id="fake-secondary",
    )

    assert artifact.summary == "Secondary summary."
    assert artifact.findings[0].source_refs == ("source-b",)


def _bounded_text(
    *,
    summary: str,
    findings: tuple[tuple[str, str], ...],
    inference: str,
    uncertainty: str,
    recommendation: str,
) -> str:
    finding_lines: list[str] = []
    for text, citation_key in findings:
        finding_lines.extend([f"- text: {text}", f"  cites: {citation_key}"])

    return "\n".join(
        [
            "SUMMARY:",
            summary,
            "",
            "FINDINGS:",
            *finding_lines,
            "",
            "INFERENCES:",
            f"- {inference}",
            "",
            "UNCERTAINTIES:",
            f"- {uncertainty}",
            "",
            "RECOMMENDATION:",
            recommendation,
        ]
    )


def _request() -> ResearchRequest:
    return ResearchRequest(
        question="What does the prepared evidence support?",
        project_id="project-1",
        work_unit_id="wu-1",
        run_id="run-1",
        constraints=("Remain bounded.",),
    )


def _evidence_pack() -> EvidencePack:
    return EvidencePack(
        question="What does the prepared evidence support?",
        sources=(
            SourceItem(source_id="source-a", source_type="document", title="A", locator="doc://a", snippet="A"),
            SourceItem(source_id="source-b", source_type="document", title="B", locator="doc://b", snippet="B"),
        ),
        evidence_items=(
            EvidenceItem(text="Fact from source A.", source_refs=("source-a",)),
            EvidenceItem(text="Fact from source B.", source_refs=("source-b",)),
        ),
    )
