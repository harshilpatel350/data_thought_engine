"""
Column-level metric computations: mean, median, variance, entropy wrappers.
Designed to accept iterables and be deterministic.
"""
from __future__ import annotations

from typing import Iterable, Dict, Any
from data_thought_engine.utils import stats


def column_metrics(values: Iterable[str]) -> Dict[str, Any]:
    """Compute numeric and distribution metrics for a column.

    Values are strings; attempt to convert to float for numeric measures.
    Non-numeric entries are included in entropy only.
    """
    vals_list = [v for v in values]
    # compute entropy on raw string values
    ent = stats.entropy(vals_list)
    # try numeric conversion
    numeric = []
    for v in vals_list:
        try:
            numeric.append(float(v))
        except Exception:
            continue
    metrics: Dict[str, Any] = {"entropy": ent, "count": len(vals_list)}
    if numeric:
        metrics.update({
            "mean": stats.mean(numeric),
            "median": stats.median(numeric),
            "variance": stats.variance(numeric),
        })
    else:
        metrics.update({"mean": None, "median": None, "variance": None})
    return metrics
