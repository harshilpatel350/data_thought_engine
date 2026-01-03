"""
CLI-friendly output formatting for narratives and run summaries.
"""
from __future__ import annotations

from typing import Dict, Any


def format_output(narrative: str, results: Dict[str, Any]) -> str:
    """Return a human-friendly multi-line string for CLI display.

    Keeps formatting logic isolated from narrative generation.
    """
    lines = [narrative, "", "Results summary:"]
    summary = results.get('summary', {})
    for k, v in summary.items():
        lines.append(f"- {k.replace('_', ' ')}: {v}")
    return '\n'.join(lines)
