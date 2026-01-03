"""
Convert observed Signals into competing Hypotheses with testable expectations.
Generates multiple explanatory hypotheses for each signal type deterministically.
"""
from __future__ import annotations

from typing import List, Dict, Any
from data_thought_engine.observation.signals import Signal
from data_thought_engine.hypothesis.hypothesis import make_hypothesis
from data_thought_engine.core.context import Context


def _generate_for_variance_spike(signal: Signal) -> List:
    """Generate competing hypotheses for a variance spike signal.

    Competing explanations:
    1. Pricing or discount volatility caused variance
    2. External shock or demand surge caused variance
    """
    col = signal.column
    score = signal.score
    hypotheses = []
    # Hypothesis 1: Pricing/discount changes explain variance
    h1 = make_hypothesis(
        statement=f"Variance spike in {col} is explained by pricing or discount changes",
        assumptions=[f"discount_column_exists", "discount_changes_are_tracked"],
        expectations={"score": min(score * 0.6, 2.0), "mechanism": "pricing"},
        origin_signals=[signal.id],
    )
    hypotheses.append(h1)
    # Hypothesis 2: External shock (demand/supply) explains variance
    h2 = make_hypothesis(
        statement=f"Variance spike in {col} is caused by external demand or supply shock",
        assumptions=["market_conditions_affect_outcomes"],
        expectations={"score": min(score * 0.7, 2.0), "mechanism": "external_shock"},
        origin_signals=[signal.id],
    )
    hypotheses.append(h2)
    return hypotheses


def _generate_for_monotonic_break(signal: Signal) -> List:
    """Generate competing hypotheses for a monotonic break signal.

    Competing explanations:
    1. Cumulative process change (e.g., delivery delays worsening)
    2. Regime shift in operations or policy
    """
    col = signal.column
    hypotheses = []
    # Hypothesis 1: Gradual process degradation
    h1 = make_hypothesis(
        statement=f"Monotonic trend break in {col} reflects gradual process degradation",
        assumptions=["processes_gradually_degrade", "no_sudden_policy_changes"],
        expectations={"score": 1.5, "mechanism": "degradation"},
        origin_signals=[signal.id],
    )
    hypotheses.append(h1)
    # Hypothesis 2: Operational regime shift
    h2 = make_hypothesis(
        statement=f"Monotonic trend break in {col} indicates a sudden operational regime shift",
        assumptions=["operational_policies_can_change_abruptly"],
        expectations={"score": 1.6, "mechanism": "regime_shift"},
        origin_signals=[signal.id],
    )
    hypotheses.append(h2)
    return hypotheses


def _generate_for_distribution_shift(signal: Signal) -> List:
    """Generate competing hypotheses for distribution shift signals.

    Competing explanations:
    1. Data collection or measurement method changed
    2. Underlying population or process actually changed
    """
    col = signal.column
    hypotheses = []
    # Hypothesis 1: Measurement artifact
    h1 = make_hypothesis(
        statement=f"Distribution shift in {col} is due to measurement or collection method change",
        assumptions=["measurement_methods_can_change"],
        expectations={"score": 0.8, "mechanism": "measurement_artifact"},
        origin_signals=[signal.id],
    )
    hypotheses.append(h1)
    # Hypothesis 2: Real underlying change
    h2 = make_hypothesis(
        statement=f"Distribution shift in {col} reflects a real change in the underlying process",
        assumptions=["underlying_processes_can_shift"],
        expectations={"score": 1.2, "mechanism": "real_change"},
        origin_signals=[signal.id],
    )
    hypotheses.append(h2)
    return hypotheses


def generate_hypotheses(signals: List[Signal], context: Context) -> List:
    """Convert observed Signals into competing Hypotheses.

    Each signal type triggers generation of multiple plausible competing
    explanations. Expectations include numeric scores for evaluation.

    Returns list of Hypothesis objects with deterministic ids.
    """
    all_hypotheses = []
    for sig in signals:
        if sig.kind == "variance_spike":
            all_hypotheses.extend(_generate_for_variance_spike(sig))
        elif sig.kind == "monotonic_break":
            all_hypotheses.extend(_generate_for_monotonic_break(sig))
        elif sig.kind in ("distribution_low_entropy", "distribution_high_entropy"):
            all_hypotheses.extend(_generate_for_distribution_shift(sig))
    return all_hypotheses
