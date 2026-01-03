"""
Entry point for Data Thought Engine (DTE).
Wires the CLI and engine together with an explicit context.
"""
from __future__ import annotations

from typing import Optional
from data_thought_engine.cli.think import cli_run


def main(argv: Optional[list[str]] = None) -> int:
    """Start point for running from Python directly.

    Returns an exit code integer.
    """
    cli_run(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
