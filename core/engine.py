"""
Orchestrates the full reasoning lifecycle without embedding business logic.
Calls each stage in the correct order and delegates to modules.
"""
from __future__ import annotations

from typing import Tuple
from data_thought_engine.core.context import Context
from data_thought_engine.core.lifecycle import Stage, validate_sequence
from data_thought_engine.ingestion.loader import load_and_stream
from data_thought_engine.observation.detectors import detect_signals
from data_thought_engine.hypothesis.generator import generate_hypotheses
from data_thought_engine.reasoning.evaluator import evaluate_hypotheses
from data_thought_engine.explanation.narrative import build_narrative
from data_thought_engine.memory.store import persist_run


def run_pipeline(context: Context, stages: Tuple[Stage, ...] = (Stage.INGEST, Stage.OBSERVE, Stage.HYPOTHESIS, Stage.REASON, Stage.EXPLAIN, Stage.PERSIST)) -> None:
    """Run the pipeline stages in order, delegating to modules.

    This function contains orchestration only and no domain logic.
    """
    validate_sequence(stages)

    rows = load_and_stream(context.dataset_path, context)
    signals = detect_signals(rows, context)
    hypotheses = generate_hypotheses(signals, context)
    results = evaluate_hypotheses(hypotheses, context)
    narrative = build_narrative(results, context)
    persist_run(results, narrative, context)
