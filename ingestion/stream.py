"""
Generator abstraction for streaming CSV rows as dictionaries.
Implements a simple, memory-efficient row generator using the csv module.
"""
from __future__ import annotations

import csv
from typing import Generator, Dict


def row_generator(path: str) -> Generator[Dict[str, str], None, None]:
    """Yield rows from a CSV file as dictionaries without loading whole file.

    This is intentionally simple and deterministic; it yields strings only.
    """
    with open(path, "r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row")
        for row in reader:
            yield {k: (v if v is not None else "") for k, v in row.items()}
