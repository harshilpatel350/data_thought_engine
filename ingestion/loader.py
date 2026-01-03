"""
CSV loader with validation that returns a streaming row generator.
Performs lightweight checks and delegates actual streaming to `stream`.
"""
from __future__ import annotations

from typing import Generator, Dict
import os

from data_thought_engine.core.context import Context
from data_thought_engine.ingestion.stream import row_generator
from data_thought_engine.ingestion.schema import infer_schema
from data_thought_engine.utils.checks import assert_path_exists


def load_and_stream(path: str, context: Context) -> Generator[Dict[str, str], None, None]:
    """Validate CSV and return a generator of rows.

    Validation: file exists, header present, and schema inferred deterministically.
    Does not modify the provided Context (immutable).
    """
    assert_path_exists(path)
    inferred = infer_schema(path)
    if not inferred:
        raise ValueError("Could not infer schema from CSV")
    # Basic validation: if context provided a schema, ensure no incompatible columns
    if context.schema:
        # Only allow missing columns; types are advisory
        missing = set(context.schema).difference(set(inferred))
        if missing:
            raise ValueError(f"Context schema references columns missing in CSV: {sorted(missing)}")
    return row_generator(path)
