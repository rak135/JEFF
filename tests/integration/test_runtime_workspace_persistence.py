import json
from pathlib import Path

from jeff.bootstrap import build_startup_interface_context
from jeff.cognitive import (
    EvidenceItem,
    EvidencePack,
    ResearchArtifact,
    ResearchArtifactStore,
    ResearchFinding,
    ResearchRequest,
    SourceItem,
    build_research_artifact_record,
)
from jeff.core.schemas import Scope
from jeff.core.transition import TransitionRequest
from jeff.interface import JeffCLI


def test_startup_initializes_persisted_runtime_home_when_missing(tmp_path: Path) -> None:
    context = build_startup_interface_context(base_dir=tmp_path)
    runtime_root = tmp_path / ".jeff_runtime"

    assert context.startup_summary == f"Startup is initializing runtime state under {runtime_root}."
    assert (runtime_root / "config" / "runtime.lock.json").exists()
    assert (runtime_root / "state" / "canonical_state.json").exists()
    assert (runtime_root / "state" / "transitions").exists()
    assert (runtime_root / "artifacts" / "research").exists()
    assert (runtime_root / "flows" / "flow_runs" / "run-1.json").exists()
    assert (runtime_root / "reviews" / "selection_reviews" / "run-1.json").exists()
    assert (runtime_root / "cache").exists()
    assert (runtime_root / "logs").exists()
    assert len(tuple((runtime_root / "state" / "transitions").glob("*.json"))) == 3


def test_startup_loads_persisted_canonical_state_instead_of_rebuilding_demo_world(tmp_path: Path) -> None:
    context = build_startup_interface_context(base_dir=tmp_path)
    runtime_store = context.runtime_store
    assert runtime_store is not None

    result = runtime_store.apply_transition(
        context.state,
        TransitionRequest(
            transition_id="transition-project-2",
            transition_type="create_project",
            basis_state_version=context.state.state_meta.state_version,
            scope=Scope(project_id="project-2"),
            payload={"name": "Persisted Project"},
        ),
    )

    reloaded = build_startup_interface_context(base_dir=tmp_path)

    assert result.transition_result == "committed"
    assert reloaded.startup_summary == f"Startup loaded persisted runtime state from {tmp_path / '.jeff_runtime'}."
    assert tuple(reloaded.state.projects.keys()) == ("project-1", "project-2")
    assert reloaded.state.state_meta.state_version == result.state.state_meta.state_version


def test_lawful_transition_updates_persisted_snapshot_and_transition_audit_record(tmp_path: Path) -> None:
    context = build_startup_interface_context(base_dir=tmp_path)
    runtime_store = context.runtime_store
    assert runtime_store is not None

    result = runtime_store.apply_transition(
        context.state,
        TransitionRequest(
            transition_id="transition-project-2",
            transition_type="create_project",
            basis_state_version=context.state.state_meta.state_version,
            scope=Scope(project_id="project-2"),
            payload={"name": "Persisted Project"},
        ),
    )
    canonical_payload = json.loads((tmp_path / ".jeff_runtime" / "state" / "canonical_state.json").read_text(encoding="utf-8"))
    transition_payload = json.loads(
        (tmp_path / ".jeff_runtime" / "state" / "transitions" / "transition-project-2.json").read_text(encoding="utf-8")
    )

    assert result.transition_result == "committed"
    assert canonical_payload["state"]["state_meta"]["state_version"] == 4
    assert canonical_payload["state"]["state_meta"]["last_transition_id"] == "transition-project-2"
    assert "project-2" in canonical_payload["state"]["projects"]
    assert transition_payload["request"]["transition_id"] == "transition-project-2"
    assert transition_payload["result"]["transition_result"] == "committed"


def test_research_artifacts_persist_under_runtime_artifacts_directory(tmp_path: Path) -> None:
    _write_runtime_config(tmp_path, artifact_store_root=".jeff_runtime/research_artifacts")
    context = build_startup_interface_context(base_dir=tmp_path)
    assert context.research_artifact_store is not None

    record = build_research_artifact_record(_research_request(), _evidence_pack(), _artifact())
    path = context.research_artifact_store.save(record)

    assert path.parent == tmp_path / ".jeff_runtime" / "artifacts" / "research"
    assert path.exists()


def test_startup_keeps_legacy_research_artifact_path_readable_while_writing_new_path(tmp_path: Path) -> None:
    legacy_root = tmp_path / ".jeff_runtime" / "research_artifacts"
    legacy_store = ResearchArtifactStore(legacy_root)
    legacy_record = build_research_artifact_record(_research_request(), _evidence_pack(), _artifact())
    legacy_store.save(legacy_record)
    _write_runtime_config(tmp_path, artifact_store_root=".jeff_runtime/research_artifacts")

    context = build_startup_interface_context(base_dir=tmp_path)
    assert context.research_artifact_store is not None

    loaded = context.research_artifact_store.load(legacy_record.artifact_id)
    listed = context.research_artifact_store.list_records(run_id="run-1")

    assert loaded == legacy_record
    assert listed == (legacy_record,)
    assert context.research_artifact_store.path_for(legacy_record.artifact_id).parent == (
        tmp_path / ".jeff_runtime" / "artifacts" / "research"
    )


def test_flow_run_support_records_persist_and_reload_without_becoming_canonical_truth(tmp_path: Path) -> None:
    build_startup_interface_context(base_dir=tmp_path)
    reloaded = build_startup_interface_context(base_dir=tmp_path)
    canonical_payload = json.loads((tmp_path / ".jeff_runtime" / "state" / "canonical_state.json").read_text(encoding="utf-8"))

    assert "run-1" in reloaded.flow_runs
    assert reloaded.flow_runs["run-1"].lifecycle.flow_id == "flow-demo-1"
    assert "flow_runs" not in canonical_payload
    assert "flows" not in canonical_payload["state"]


def test_selection_review_support_records_persist_and_reload_without_becoming_canonical_truth(tmp_path: Path) -> None:
    build_startup_interface_context(base_dir=tmp_path)
    reloaded = build_startup_interface_context(base_dir=tmp_path)
    cli = JeffCLI(context=reloaded)
    canonical_payload = json.loads((tmp_path / ".jeff_runtime" / "state" / "canonical_state.json").read_text(encoding="utf-8"))

    payload = json.loads(
        cli.run_one_shot(
            '/selection override proposal-2 --why "Use the persisted alternate option." run-1',
            json_output=True,
        )
    )

    assert "run-1" in reloaded.selection_reviews
    assert payload["override"]["chosen_proposal_id"] == "proposal-2"
    assert "selection_reviews" not in canonical_payload
    assert "reviews" not in canonical_payload["state"]


def test_cli_session_scope_is_not_persisted_as_canonical_truth(tmp_path: Path) -> None:
    context = build_startup_interface_context(base_dir=tmp_path)
    cli = JeffCLI(context=context)
    transitions_dir = tmp_path / ".jeff_runtime" / "state" / "transitions"
    initial_state_version = context.state.state_meta.state_version
    initial_transition_count = len(tuple(transitions_dir.glob("*.json")))

    cli.run_one_shot("/project use project-1")
    cli.run_one_shot("/work use wu-1")
    cli.run_one_shot("/run use run-1")

    reloaded = build_startup_interface_context(base_dir=tmp_path)
    canonical_payload = json.loads((tmp_path / ".jeff_runtime" / "state" / "canonical_state.json").read_text(encoding="utf-8"))

    assert reloaded.state.state_meta.state_version == initial_state_version
    assert len(tuple(transitions_dir.glob("*.json"))) == initial_transition_count
    assert "active_context" not in canonical_payload["state"]


def _write_runtime_config(tmp_path: Path, *, artifact_store_root: str) -> Path:
    config_path = tmp_path / "jeff.runtime.toml"
    config_path.write_text(
        f"""
[runtime]
default_adapter_id = "fake-default"

[research]
artifact_store_root = "{artifact_store_root}"
enable_memory_handoff = true

[[adapters]]
adapter_id = "fake-default"
provider_kind = "fake"
model_name = "fake-model"

[[adapters]]
adapter_id = "fake-research"
provider_kind = "fake"
model_name = "fake-research-model"

[purpose_overrides]
research = "fake-research"
""".strip(),
        encoding="utf-8",
    )
    return config_path


def _research_request() -> ResearchRequest:
    return ResearchRequest(
        question="What does the bounded plan support?",
        project_id="project-1",
        work_unit_id="wu-1",
        run_id="run-1",
        source_mode="local_documents",
    )


def _evidence_pack() -> EvidencePack:
    return EvidencePack(
        question="What does the bounded plan support?",
        sources=(
            SourceItem(
                source_id="source-1",
                source_type="document",
                title="Plan",
                locator="doc://plan",
                snippet="Bounded plan snippet",
            ),
        ),
        evidence_items=(EvidenceItem(text="Bounded plan evidence", source_refs=("source-1",)),),
    )


def _artifact() -> ResearchArtifact:
    return ResearchArtifact(
        question="What does the bounded plan support?",
        summary="The bounded plan supports a narrow rollout.",
        findings=(ResearchFinding(text="The plan stays narrow.", source_refs=("source-1",)),),
        inferences=("A bounded rollout is better supported.",),
        uncertainties=("No external validation.",),
        recommendation="Proceed carefully.",
        source_ids=("source-1",),
    )
