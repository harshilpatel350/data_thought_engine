"""
Hypothesis object representing a testable statement with assumptions and expectations.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any
import hashlib


@dataclass(frozen=True)
class Hypothesis:
    """A hypothesis with deterministic id based on its content.

    `expectations` is a simple summary of what the hypothesis predicts.
    """
    id: str
    statement: str
    assumptions: List[str]
    expectations: Dict[str, Any]
    origin_signals: List[str]


def make_hypothesis(statement: str, assumptions: List[str], expectations: Dict[str, Any], origin_signals: List[str]) -> Hypothesis:
    """Deterministically derive an id from the statement text.

    Using a hash ensures reproducible ids across runs with same input.
    """
    h = hashlib.sha1(statement.encode('utf-8')).hexdigest()
    return Hypothesis(id=h, statement=statement, assumptions=list(assumptions), expectations=dict(expectations), origin_signals=list(origin_signals))
