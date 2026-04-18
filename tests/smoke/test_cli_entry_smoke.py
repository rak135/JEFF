import json

from tests.fixtures.entrypoint import run_jeff


def test_one_shot_help_reaches_cli_surface() -> None:
    result = run_jeff("--command", "/help")

    assert result.returncode == 0
    assert "Jeff CLI is command-driven." in result.stdout
    assert "/project list" in result.stdout
    assert "Primary flow:" in result.stdout
    assert "/run list" in result.stdout
    assert "/show [run_id]" in result.stdout
    assert "/proposal show" not in result.stdout
    assert "/evaluation show" not in result.stdout


def test_one_shot_project_list_uses_bootstrapped_demo_context() -> None:
    result = run_jeff("--command", "/project list")

    assert result.returncode == 0
    assert "[truth] projects" in result.stdout
    assert "project-1" in result.stdout


def test_one_shot_show_json_exposes_truthful_operator_shape() -> None:
    result = run_jeff("--command", "/show run-1", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["view"] == "run_show"
    assert payload["truth"]["run_id"] == "run-1"
    assert payload["derived"]["flow_visible"] is True
    assert payload["derived"]["active_module"] == "cognitive"
    assert "recent_events" in payload["support"]


def test_unknown_one_shot_command_fails_clearly() -> None:
    result = run_jeff("--command", "/unknown")

    assert result.returncode != 0
    assert "unsupported command" in result.stderr
    assert "use /help" in result.stderr


def test_one_shot_scope_flags_support_show_without_persistent_tty() -> None:
    result = run_jeff("--project", "project-1", "--work", "wu-1", "--command", "/show")

    assert result.returncode == 0
    assert "auto-selected current run: run-1" in result.stdout
    assert "RUN run-1" in result.stdout
    assert "[support][proposal] serious_option_count=2" in result.stdout


def test_repeated_one_shot_commands_share_temporary_session_scope() -> None:
    result = run_jeff(
        "--project",
        "project-1",
        "--work",
        "wu-1",
        "--command",
        "/inspect",
        "--command",
        "/selection show",
    )

    assert result.returncode == 0
    assert "RUN run-1" in result.stdout
    assert "SELECTION REVIEW run_id=run-1" in result.stdout
    assert "[proposal] serious_option_count=2 selected_proposal_id=proposal-1" in result.stdout


def test_repeated_one_shot_commands_make_demo_override_usable() -> None:
    result = run_jeff(
        "--project",
        "project-1",
        "--work",
        "wu-1",
        "--command",
        "/inspect",
        "--command",
        '/selection override proposal-2 --why "Operator wants the alternate bounded demo path."',
    )

    assert result.returncode == 0
    assert "SELECTION OVERRIDE RECORDED run_id=run-1" in result.stdout
    assert "chosen_proposal_id=proposal-2" in result.stdout
