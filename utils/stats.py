"""
Manual deterministic statistical utilities using only the standard library.
All functions accept iterables and avoid hidden randomness.
"""
from __future__ import annotations

from typing import Iterable, List
import math


def mean(values: Iterable[float]) -> float:
    """Compute mean deterministically using a single pass.

    Uses an accumulator to avoid storing all values.
    """
    total = 0.0
    count = 0
    for v in values:
        total += float(v)
        count += 1
    if count == 0:
        raise ValueError("mean() requires at least one value")
    return total / count


def variance(values: Iterable[float]) -> float:
    """Compute population variance via Welford's algorithm (single-pass).

    Deterministic and numerically stable for streaming data.
    """
    mean_v = 0.0
    m2 = 0.0
    count = 0
    for x in values:
        x = float(x)
        count += 1
        delta = x - mean_v
        mean_v += delta / count
        delta2 = x - mean_v
        m2 += delta * delta2
    if count == 0:
        raise ValueError("variance() requires at least one value")
    return m2 / count


def median(values: Iterable[float]) -> float:
    """Compute median by collecting values deterministically.

    This function collects values; callers should avoid passing huge streams.
    """
    vals: List[float] = [float(x) for x in values]
    n = len(vals)
    if n == 0:
        raise ValueError("median() requires at least one value")
    vals.sort()
    mid = n // 2
    if n % 2 == 1:
        return vals[mid]
    return (vals[mid - 1] + vals[mid]) / 2.0


def entropy(values: Iterable[str]) -> float:
    """Compute Shannon entropy for discrete string values deterministically.

    Uses counts and returns entropy in bits.
    """
    counts: dict[str, int] = {}
    total = 0
    for v in values:
        counts[v] = counts.get(v, 0) + 1
        total += 1
    if total == 0:
        raise ValueError("entropy() requires at least one value")
    ent = 0.0
    for c in counts.values():
        p = c / total
        ent -= p * math.log(p, 2)
    return ent
