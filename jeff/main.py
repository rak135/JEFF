"""Stable package entrypoint for the current Jeff v1 operator surface."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from jeff import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m jeff",
        description=(
            "Start the current Jeff v1 CLI-first backbone. "
            "This startup path bootstraps an explicit in-memory demo workspace and does not persist state."
        ),
        epilog=(
            "Examples:\n"
            "  python -m jeff --help\n"
            "  python -m jeff --bootstrap-check\n"
            "  python -m jeff --command \"/help\"\n"
            "  python -m jeff --command \"/show run-1\" --json\n"
            "  python -m jeff"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="store_true", help="show the current package version and exit")
    parser.add_argument(
        "--bootstrap-check",
        action="store_true",
        help="run deterministic startup checks and exit",
    )
    parser.add_argument(
        "--command",
        metavar="COMMAND",
        help="run one CLI command against the explicit in-memory demo context and exit",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="render one-shot command output as JSON where the command supports it",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"jeff {__version__}")
        return 0
    if args.json and args.command is None:
        parser.error("--json requires --command")

    try:
        from jeff.bootstrap import build_demo_interface_context, run_startup_preflight
        from jeff.interface import JeffCLI
    except Exception as exc:
        return _print_error(f"startup imports failed: {exc}")

    try:
        checks = run_startup_preflight()
        if args.bootstrap_check:
            print("bootstrap checks passed")
            for check in checks:
                print(f"- {check}")
            print("- startup path uses explicit in-memory demo state only")
            return 0

        context = build_demo_interface_context()
        cli = JeffCLI(context=context)

        if args.command is not None:
            output = cli.run_one_shot(args.command, json_output=args.json)
            if output:
                print(output)
            return 0

        if not sys.stdin.isatty():
            parser.print_help()
            print("\nNo interactive terminal detected. Use --command for one-shot mode.")
            return 0

        return _run_interactive(cli)
    except KeyboardInterrupt:
        print("\ninterrupted")
        return 130
    except Exception as exc:
        return _print_error(str(exc))


def _run_interactive(cli) -> int:
    print("Jeff v1 interactive shell")
    print("Startup bootstrapped an explicit in-memory demo workspace with no persistence.")
    print("Use /help for commands. Type 'exit' or 'quit' to leave.")

    while True:
        try:
            command_line = input(f"{cli.prompt} ")
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print()
            return 130

        normalized = command_line.strip()
        if not normalized:
            continue
        if normalized in {"exit", "quit"}:
            return 0

        try:
            output = cli.run_one_shot(normalized)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            continue
        if output:
            print(output)


def _print_error(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 2
