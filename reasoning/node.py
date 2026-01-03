"""
Atomic reasoning step: Observation -> Test -> Result.
A Node captures a single test applied to a hypothesis.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any
import hashlib


@dataclass(frozen=True)
class Node:
    """Immutable result of applying one test to a hypothesis.

    Id is deterministic based on hypothesis id and test name.
    """
    id: str
    hypothesis_id: str
    test: str
    result: str
    score: float
    details: Dict[str, Any] = field(default_factory=dict)


def make_node(hypothesis_id: str, test: str, result: str, score: float, details: Dict[str, Any] | None = None) -> Node:
    key = f"{hypothesis_id}:{test}:{result}:{score}"
    nid = hashlib.sha1(key.encode('utf-8')).hexdigest()
    return Node(id=nid, hypothesis_id=hypothesis_id, test=test, result=result, score=float(score), details=details or {})
