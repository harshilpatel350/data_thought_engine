"""
Generate human-like explanations from reasoning results.
Uses algorithmic composition rather than fixed templates to explain findings.
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


def build_narrative(results: Dict[str, Any], context) -> str:
    """Produce a multi-sentence narrative explaining overall outcomes.

    The function composes sentences for each node and a concise summary.
    """
    nodes = results.get('nodes', [])
    if not nodes:
        return "No notable patterns detected."
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
    return ' '.join(sentences)
