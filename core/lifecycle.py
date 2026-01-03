"""
Defines valid pipeline stages and enforces execution order.
"""
from __future__ import annotations

from enum import Enum
from typing import Tuple


class Stage(Enum):
    INGEST = "ingest"
    OBSERVE = "observe"
    HYPOTHESIS = "hypothesis"
    REASON = "reason"
    EXPLAIN = "explain"
    PERSIST = "persist"


_VALID_SEQUENCE: Tuple[Stage, ...] = (
    Stage.INGEST,
    Stage.OBSERVE,
    Stage.HYPOTHESIS,
    Stage.REASON,
    Stage.EXPLAIN,
    Stage.PERSIST,
)


def validate_sequence(order: Tuple[Stage, ...]) -> None:
    """Ensure provided order is a prefix of the valid pipeline.

    This prevents invalid execution ordering.
    """
    if not order:
        raise ValueError("Execution order cannot be empty")
    if any(s not in _VALID_SEQUENCE for s in order):
        raise ValueError("Unknown stage in execution order")
    # Ensure relative ordering matches allowed sequence
    idxs = [_VALID_SEQUENCE.index(s) for s in order]
    if idxs != sorted(idxs):
        raise ValueError("Stages must follow the defined lifecycle order")
