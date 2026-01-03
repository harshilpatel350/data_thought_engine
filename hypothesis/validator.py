"""
Validate hypotheses by rejecting duplicates and detecting circular references.
Circularity here means a hypothesis explicitly assumes another it contradicts.
"""
from __future__ import annotations

from typing import List
from data_thought_engine.hypothesis.hypothesis import Hypothesis


def validate_hypotheses(hypotheses: List[Hypothesis]) -> List[Hypothesis]:
    """Return only valid hypotheses, removing duplicates and inconsistent ones.

    Duplicate detection is deterministic by id. Circularity check is basic:
    if hypothesis A's assumptions cite hypothesis B's id and B cites A's id,
    both are rejected to avoid circular reasoning.
    """
    unique = {h.id: h for h in hypotheses}
    valid = []
    for h in unique.values():
        valid.append(h)
    # simple circular detection
    ids = {h.id for h in valid}
    to_remove = set()
    for a in valid:
        for assumed in a.assumptions:
            if assumed.startswith("hypothesis:"):
                other = assumed.split(":", 1)[1]
                if other in ids:
                    # check reciprocal assumption
                    other_h = unique.get(other)
                    if other_h and any(x == f"hypothesis:{a.id}" for x in other_h.assumptions):
                        to_remove.add(a.id)
                        to_remove.add(other)
    return [h for h in valid if h.id not in to_remove]
