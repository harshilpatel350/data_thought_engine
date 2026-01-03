"""
Generate human-like explanations from reasoning results.
Uses algorithmic composition rather than fixed templates to explain findings.
Implements v1.1: Historical consistency check narratives.
"""
from __future__ import annotations

from typing import Dict, Any, List


def _phrase_for_node(node) -> str:
    """Compose a phrase for a single reasoning node.

    This composes from node attributes rather than using a fixed template,
    creating variation while remaining deterministic.
    """
    result = node.result
    score = getattr(node, 'score', 0.0)
    parts: List[str] = []
    if result == 'supported':
        parts.append('This finds strong support')
    elif result == 'weak_support':
        parts.append('There is limited support')
    else:
        parts.append('Findings do not support')
    # Explain what was tested
    t = node.test.replace('_', ' ')
    parts.append(f"the hypothesis through {t}")
    # Add quantitative flavor deterministically
    parts.append(f"(score={score:.2f})")
    return ' '.join(parts)


def _historical_consistency_narrative(history_comparison: Dict[str, Any]) -> str:
    """Generate narrative for historical consistency check.

    Produces human-readable explanation of how current reasoning aligns with history.
    """
    status = history_comparison.get('status', 'unknown')
    if status == 'no_prior_runs':
        return "Historical Context: No prior reasoning runs exist for comparison."
    elif status == 'no_valid_history':
        return "Historical Context: Prior reasoning could not be reconstructed for comparison."
    elif status == 'different_dataset':
        return "Historical Context: Dataset has changed since the last run; direct comparison is not valid."
    elif status == 'exact_match':
        return "Historical Context: This reasoning is identical to the prior run on the same dataset, indicating consistent and reproducible analysis."
    elif status == 'dominant_changed':
        prior = history_comparison.get('prior_dominant', 'unknown')
        curr = history_comparison.get('current_dominant', 'unknown')
        return f"Historical Context: The dominant explanation has shifted from {prior[:8]} to {curr[:8]}, indicating a contradictory conclusion compared to prior reasoning."
    elif status == 'partial_reinforcement':
        shared = history_comparison.get('shared_supported', [])
        count = len(shared)
        return f"Historical Context: {count} supported hypothesis/hypotheses overlap with prior reasoning, indicating partial consistency."
    elif status == 'reasoning_diverged':
        return "Historical Context: Reasoning has diverged significantly from prior conclusions, suggesting different explanatory pathways."
    else:
        return f"Historical Context: {history_comparison.get('message', 'Unknown historical status.')}"


def build_narrative(results: Dict[str, Any], context, history_comparison: Dict[str, Any] | None = None) -> str:
    """Produce a multi-sentence narrative explaining overall outcomes with optional historical context.

    The function composes sentences for each node, a summary, and historical consistency check.
    """
    nodes = results.get('nodes', [])
    if not nodes:
        narrative = "No notable patterns detected."
    else:
        sentences: List[str] = []
        for n in nodes:
            sentences.append(_phrase_for_node(n))
        # Summarize counts
        summary = results.get('summary', {})
        summary_parts = []
        for k in ('supported', 'weak_support', 'unsupported'):
            v = summary.get(k, 0)
            summary_parts.append(f"{v} {k.replace('_', ' ')}")
        sentences.append("Summary: " + '; '.join(summary_parts) + '.')
        narrative = ' '.join(sentences)
    # Append historical consistency section if available
    if history_comparison:
        hist_narrative = _historical_consistency_narrative(history_comparison)
        narrative = narrative + " " + hist_narrative
    return narrative

