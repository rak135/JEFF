from jeff.bootstrap import build_demo_interface_context, run_startup_preflight

from tests.entrypoint_test_helpers import run_jeff


def test_demo_context_bootstraps_with_project_run_and_flow() -> None:
    context = build_demo_interface_context()

    assert tuple(context.state.projects.keys()) == ("project-1",)
    assert "wu-1" in context.state.projects["project-1"].work_units
    assert "run-1" in context.state.projects["project-1"].work_units["wu-1"].runs
    assert "run-1" in context.flow_runs


def test_startup_preflight_reports_operator_entry_ready() -> None:
    checks = run_startup_preflight()

    assert "package imports resolved" in checks
    assert "demo interface context bootstrapped" in checks
    assert any("CLI entry surface" in check for check in checks)


def test_module_entry_help_path_boots_cleanly() -> None:
    result = run_jeff("--help")

    assert result.returncode == 0
    assert "python -m jeff --command \"/help\"" in result.stdout
    assert "explicit in-memory demo workspace" in result.stdout


def test_module_entry_non_tty_does_not_hang_and_explains_next_step() -> None:
    result = run_jeff(input_text="")

    assert result.returncode == 0
    assert "No interactive terminal detected. Use --command for one-shot mode." in result.stdout


def test_invalid_startup_flag_combination_fails_clearly() -> None:
    result = run_jeff("--json")

    assert result.returncode != 0
    assert "--json requires --command" in result.stderr
