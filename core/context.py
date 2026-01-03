"""
Immutable execution context for a DTE run.
Holds dataset metadata and timestamps. Passed explicitly everywhere.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any


@dataclass(frozen=True)
class Context:
    """Immutable run context containing dataset metadata.

    Use dataclass immutability to prevent global mutable state.
    """
    dataset_path: str
    num_rows_sampled: int
    schema: Dict[str, str]
    start_time: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
