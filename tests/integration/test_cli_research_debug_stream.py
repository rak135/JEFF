from dataclasses import dataclass, field
from pathlib import Path

import pytest

from jeff.cognitive import ResearchArtifactStore, ResearchProvenanceValidationError
from jeff.cognitive.research import synthesis as research_synthesis_module
from jeff.interface import JeffCLI, InterfaceContext
from jeff.infrastructure import (
    AdapterRegistry,
    InfrastructureServices,
    ModelInvocationStatus,
    ModelMalformedOutputError,
    ModelRequest,
    ModelResponse,
    ModelUsage,
)
from jeff.main import _run_interactive
from jeff.memory import InMemoryMemoryStore

from tests.fixtures.cli import build_state_with_runs


def test_live_debug_stream_shows_formatter_fallback_after_deterministic_transform_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    cli, document = _build_docs_cli(tmp_path, script=(_valid_bounded_text(), _valid_formatter_json()))
    original_transform = research_synthesis_module.transform_step1_bounded_text_to_candidate_payload

    def failing_transform(_: str) -> dict[str, object]:
        raise research_synthesis_module.ResearchSynthesisValidationError(
            "forced structural transform failure for formatter",
        )

    research_synthesis_module.transform_step1_bounded_text_to_candidate_payload = failing_transform
    _install_inputs(
        monkeypatch,
        [
            "/project use project-1",
            "/work use wu-1",
            "/mode debug",
            f'/research docs "What does the bounded plan support?" "{document}"',
            "quit",
        ],
    )

    try:
        exit_code = _run_interactive(cli)
    finally:
        research_synthesis_module.transform_step1_bounded_text_to_candidate_payload = original_transform
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out.index("[debug][research] deterministic_transform_failed") < captured.out.index(
        "[debug][research] formatter_fallback_started"
    )
    assert captured.out.index("[debug][research] formatter_fallback_started") < captured.out.index(
        "[debug][research] formatter_fallback_succeeded"
    )
    assert captured.out.index("[debug][research] formatter_fallback_succeeded") < captured.out.index("RESEARCH docs")


def test_live_debug_stream_shows_formatter_failure_without_false_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    cli, document = _build_docs_cli(
        tmp_path,
        script=(
            _valid_bounded_text(),
            {
                "summary": "Repaired summary.",
                "findings": [{"text": "Observed fact", "source_refs": ["S9"]}],
                "inferences": ["A bounded next step remains supported."],
                "uncertainties": ["No live validation was performed."],
                "recommendation": "Proceed with the bounded path.",
            },
        ),
    )
    original_transform = research_synthesis_module.transform_step1_bounded_text_to_candidate_payload

    def failing_transform(_: str) -> dict[str, object]:
        raise research_synthesis_module.ResearchSynthesisValidationError(
            "forced structural transform failure for formatter",
        )

    research_synthesis_module.transform_step1_bounded_text_to_candidate_payload = failing_transform
    _install_inputs(
        monkeypatch,
        [
            "/project use project-1",
            "/work use wu-1",
            "/mode debug",
            f'/research docs "What does the bounded plan support?" "{document}"',
            "quit",
        ],
    )

    try:
        exit_code = _run_interactive(cli)
    finally:
        research_synthesis_module.transform_step1_bounded_text_to_candidate_payload = original_transform
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "[debug][research] formatter_fallback_started" in captured.out
    assert "[debug][research] formatter_fallback_succeeded" in captured.out
    assert "[debug][research] citation_remap_failed" in captured.out
    assert "unknown citation refs" in captured.err


def test_live_debug_stream_shows_provenance_stage_failure_checkpoint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    cli, document = _build_docs_cli(tmp_path, script=(_valid_bounded_text(),))
    original_validate = research_synthesis_module.validate_research_provenance

    def failing_validate(**kwargs):  # type: ignore[no-untyped-def]
        raise ResearchProvenanceValidationError("forced provenance failure for debug")

    monkeypatch.setattr(research_synthesis_module, "validate_research_provenance", failing_validate)
    _install_inputs(
        monkeypatch,
        [
            "/project use project-1",
            "/work use wu-1",
            "/mode debug",
            f'/research docs "What does the bounded plan support?" "{document}"',
            "quit",
        ],
    )

    try:
        exit_code = _run_interactive(cli)
    finally:
        monkeypatch.setattr(research_synthesis_module, "validate_research_provenance", original_validate)
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "[debug][research] provenance_validation_started" in captured.out
    assert "[debug][research] provenance_validation_failed" in captured.out
    assert "forced provenance failure for debug" in captured.err


def _build_docs_cli(tmp_path: Path, *, script: tuple[object, ...]) -> tuple[JeffCLI, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    document = tmp_path / "plan.md"
    document.write_text(
        "The bounded plan keeps the rollout stable.\n"
        "The bounded plan avoids widening the surface.\n",
        encoding="utf-8",
    )
    state, _ = build_state_with_runs(run_specs=())
    adapter = _ScriptedAdapter(script=script)
    registry = AdapterRegistry()
    registry.register(adapter)
    return (
        JeffCLI(
            context=InterfaceContext(
                state=state,
                infrastructure_services=InfrastructureServices(
                    model_adapter_registry=registry,
                    default_model_adapter_id=adapter.adapter_id,
                ),
                research_artifact_store=ResearchArtifactStore(tmp_path),
                memory_store=InMemoryMemoryStore(),
            )
        ),
        document,
    )


def _install_inputs(monkeypatch: pytest.MonkeyPatch, commands: list[str]) -> None:
    iterator = iter(commands)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(iterator))


@dataclass(slots=True)
class _ScriptedAdapter:
    script: tuple[object, ...]
    adapter_id: str = "debug-research"
    provider_name: str = "fake"
    model_name: str = "research-model"
    requests: list[ModelRequest] = field(default_factory=list)

    def invoke(self, request_model: ModelRequest) -> ModelResponse:
        self.requests.append(request_model)
        step = self.script[len(self.requests) - 1]
        if isinstance(step, Exception):
            raise step
        if request_model.response_mode.value == "TEXT":
            assert isinstance(step, str)
            return ModelResponse(
                request_id=request_model.request_id,
                adapter_id=self.adapter_id,
                provider_name=self.provider_name,
                model_name=self.model_name,
                status=ModelInvocationStatus.COMPLETED,
                output_text=step,
                output_json=None,
                usage=ModelUsage(input_tokens=1, output_tokens=1, total_tokens=2, estimated_cost=0.0, latency_ms=1),
                warnings=(),
                raw_response_ref=f"fake://{self.adapter_id}/{request_model.request_id}",
            )
        assert isinstance(step, dict)
        return ModelResponse(
            request_id=request_model.request_id,
            adapter_id=self.adapter_id,
            provider_name=self.provider_name,
            model_name=self.model_name,
            status=ModelInvocationStatus.COMPLETED,
            output_text=None,
            output_json=step,
            usage=ModelUsage(input_tokens=1, output_tokens=1, total_tokens=2, estimated_cost=0.0, latency_ms=1),
            warnings=(),
            raw_response_ref=f"fake://{self.adapter_id}/{request_model.request_id}",
        )


def _valid_bounded_text() -> str:
    return "\n".join(
        [
            "SUMMARY:",
            "The documents support a bounded rollout.",
            "",
            "FINDINGS:",
            "- text: The plan emphasizes bounded rollout.",
            "  cites: S1",
            "",
            "INFERENCES:",
            "- A bounded next step remains supported.",
            "",
            "UNCERTAINTIES:",
            "- No live validation was performed.",
            "",
            "RECOMMENDATION:",
            "Proceed with the bounded path.",
        ]
    )


def _valid_formatter_json() -> dict[str, object]:
    return {
        "summary": "Repaired summary.",
        "findings": [{"text": "Observed fact", "source_refs": ["S1"]}],
        "inferences": ["A bounded next step remains supported."],
        "uncertainties": ["No live validation was performed."],
        "recommendation": "Proceed with the bounded path.",
    }
