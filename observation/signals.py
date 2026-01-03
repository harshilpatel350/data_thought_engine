"""
Signal data structures that represent observations worth reasoning about.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any
import uuid


@dataclass(frozen=True)
class Signal:
    """A concise representation of an observed anomaly or pattern.

    `score` is a simple numeric strength; `details` holds contextual values.
    """
    id: str
    kind: str
    column: str
    score: float
    details: Dict[str, Any] = field(default_factory=dict)


def make_signal(kind: str, column: str, score: float, details: Dict[str, Any] | None = None) -> Signal:
    """Factory to create a Signal with a stable unique id.

    Using uuid4 would introduce randomness; instead use deterministic uuid
    derived from the tuple (kind, column, score) for repeatability.
    """
    # Deterministic id based on content
    base = f"{kind}:{column}:{score}"
    uid = uuid.uuid5(uuid.NAMESPACE_DNS, base).hex
    return Signal(id=uid, kind=kind, column=column, score=score, details=details or {})
