"""
Manual schema inference: type detection and column roles.
Does not depend on in-memory data structures beyond a small sample.
"""
from __future__ import annotations

from typing import Dict, Tuple
import datetime


def _detect_type(value: str) -> str:
    """Detect a primitive type from a string deterministically.

    Order: int -> float -> datetime -> bool -> str
    """
    v = value.strip()
    if v == "":
        return "null"
    # Integer detection
    if v.lstrip("+-").isdigit():
        return "int"
    # Float detection
    try:
        float(v)
        if "." in v or "e" in v.lower():
            return "float"
    except Exception:
        pass
    # Datetime detection for common ISO forms
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d"):
        try:
            datetime.datetime.strptime(v, fmt)
            return "datetime"
        except Exception:
            continue
    if v.lower() in ("true", "false"):
        return "bool"
    return "str"


def infer_schema(path: str, max_rows: int = 200) -> Dict[str, str]:
    """Infer a minimal schema mapping column -> detected type.

    Reads up to `max_rows` rows deterministically to determine the most
    specific common type observed per column.
    """
    from data_thought_engine.ingestion.stream import row_generator

    counters: Dict[str, Dict[str, int]] = {}
    rows_read = 0
    for row in row_generator(path):
        rows_read += 1
        for k, v in row.items():
            typ = _detect_type(v)
            counters.setdefault(k, {}).setdefault(typ, 0)
            counters[k][typ] += 1
        if rows_read >= max_rows:
            break
    schema: Dict[str, str] = {}
    for col, counts in counters.items():
        # Choose the most frequent non-null type observed
        preferred = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        schema[col] = preferred
    return schema
