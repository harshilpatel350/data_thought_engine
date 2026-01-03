"""
Logic-only detectors for variance spikes, monotonic breaks, and distribution shifts.
These functions operate deterministically on column value sequences.
"""
from __future__ import annotations

from typing import Iterable, Dict, List
from data_thought_engine.observation.signals import make_signal, Signal
from data_thought_engine.observation.metrics import column_metrics
from data_thought_engine.core.context import Context


def _as_list(values: Iterable[str]) -> List[str]:
    return [v for v in values]


def detect_variance_spike(column: str, values: Iterable[str]) -> Signal | None:
    """Detect a variance spike when variance substantially exceeds squared mean.

    Rationale: large variance relative to mean magnitude suggests instability.
    """
    vals = _as_list(values)
    metrics = column_metrics(vals)
    var = metrics.get("variance")
    mean = metrics.get("mean")
    if var is None or mean is None:
        return None
    # Deterministic threshold: variance > 4 * mean^2
    if var > 4.0 * (mean ** 2):
        score = var / (mean ** 2 + 1e-12)
        return make_signal("variance_spike", column, float(score), {"metrics": metrics})
    return None


def detect_monotonic_break(column: str, values: Iterable[str]) -> Signal | None:
    """Detect monotonic trend breaks: look for a sustained direction change.

    Rationale: monotonic flows that change direction indicate structural shift.
    """
    nums: List[float] = []
    for v in values:
        try:
            nums.append(float(v))
        except Exception:
            continue
    if len(nums) < 3:
        return None
    # compute differences signs
    signs: List[int] = []
    for a, b in zip(nums, nums[1:]):
        diff = b - a
        signs.append(0 if diff == 0 else (1 if diff > 0 else -1))
    # count sign changes
    changes = 0
    for x, y in zip(signs, signs[1:]):
        if x != 0 and y != 0 and x != y:
            changes += 1
    if changes >= 1:
        score = float(changes)
        return make_signal("monotonic_break", column, score, {"changes": changes})
    return None


def detect_distribution_shift(column: str, values: Iterable[str]) -> Signal | None:
    """Detect distribution shift via entropy extremes.

    Rationale: extremely low or high entropy may indicate a shift worth exploring.
    """
    vals = _as_list(values)
    metrics = column_metrics(vals)
    ent = metrics.get("entropy")
    if ent is None:
        return None
    # Deterministic thresholds: low entropy < 0.5 bits, high entropy > 4 bits
    if ent < 0.5:
        return make_signal("distribution_low_entropy", column, float(0.5 - ent), {"metrics": metrics})
    if ent > 4.0:
        return make_signal("distribution_high_entropy", column, float(ent - 4.0), {"metrics": metrics})
    return None


def detect_signals(rows: Iterable[Dict[str, str]], context: Context) -> List[Signal]:
    """Top-level detector that consumes streamed rows and returns Signals.

    For simplicity and determinism we collect modest per-column lists; this
    keeps logic clear while remaining memory-conscious for typical datasets.
    """
    # Collect values per column up to a reasonable limit
    collectors: Dict[str, List[str]] = {}
    max_collect = 1000
    count = 0
    for row in rows:
        for k, v in row.items():
            collectors.setdefault(k, []).append(v)
        count += 1
        if count >= max_collect:
            break
    signals: List[Signal] = []
    for col, vals in collectors.items():
        for detector in (detect_variance_spike, detect_monotonic_break, detect_distribution_shift):
            sig = detector(col, vals)
            if sig is not None:
                signals.append(sig)
    return signals
