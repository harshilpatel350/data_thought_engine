"""
Execute hypothesis tests and score support vs contradiction deterministically.
"""
from __future__ import annotations

from typing import List, Dict, Any
from data_thought_engine.hypothesis.hypothesis import Hypothesis
from data_thought_engine.hypothesis.validator import validate_hypotheses
from data_thought_engine.reasoning.node import make_node, Node
from data_thought_engine.reasoning.graph import ReasoningDAG


def evaluate_hypotheses(hypotheses: List[Hypothesis], context) -> Dict[str, Any]:
    """Validate and evaluate hypotheses, returning structured results.

    Evaluation is rule-based: expectations containing a numeric `score`
    are interpreted directly; higher score favors support.
    """
    valid = validate_hypotheses(hypotheses)
    dag = ReasoningDAG()
    results: Dict[str, Any] = {"nodes": [], "summary": {}}
    for h in valid:
        # Simple test: if expectation.score >= 1 -> supported, else weak
        expected = h.expectations.get("score", 0)
        if expected >= 1.0:
            result = "supported"
            score = float(expected)
        elif expected > 0:
            result = "weak_support"
            score = float(expected)
        else:
            result = "unsupported"
            score = float(expected)
        node = make_node(h.id, "expectation_score_test", result, score, {"expectations": h.expectations})
        dag.add_node(node)
        results["nodes"].append(node)
    # Build summary counts
    summary: Dict[str, int] = {"supported": 0, "weak_support": 0, "unsupported": 0}
    for n in results["nodes"]:
        summary.setdefault(n.result, 0)
        summary[n.result] += 1
    results["summary"] = summary
    return results
