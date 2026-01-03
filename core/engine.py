"""
Orchestrates the full reasoning lifecycle without embedding business logic.
Calls each stage in the correct order and delegates to modules.
Implements v1.1: Cross-run reasoning consistency integration.
"""
from __future__ import annotations

from typing import Tuple
import os
from data_thought_engine.core.context import Context
from data_thought_engine.core.lifecycle import Stage, validate_sequence
from data_thought_engine.ingestion.loader import load_and_stream
from data_thought_engine.observation.detectors import detect_signals
from data_thought_engine.hypothesis.generator import generate_hypotheses
from data_thought_engine.reasoning.evaluator import evaluate_hypotheses
from data_thought_engine.explanation.narrative import build_narrative
from data_thought_engine.memory.store import persist_run
from data_thought_engine.memory.history import _compute_reasoning_signature, compare_with_history


def run_pipeline(context: Context, stages: Tuple[Stage, ...] = (Stage.INGEST, Stage.OBSERVE, Stage.HYPOTHESIS, Stage.REASON, Stage.EXPLAIN, Stage.PERSIST)) -> None:
    """Run the pipeline stages in order, delegating to modules.

    This function contains orchestration only and no domain logic.
    v1.1 extension: Computes reasoning signature and performs historical consistency check.
    """
    validate_sequence(stages)

    rows = load_and_stream(context.dataset_path, context)
    signals = detect_signals(rows, context)
    hypotheses = generate_hypotheses(signals, context)
    results = evaluate_hypotheses(hypotheses, context)
    
    # v1.1: Compute reasoning signature and check historical consistency
    sig = _compute_reasoning_signature(context.dataset_path, results)
    storage_dir = os.path.join(os.getcwd(), "dte_runs")
    history_comparison = compare_with_history(sig, storage_dir)
    
    narrative = build_narrative(results, context, history_comparison)
    persist_run(results, narrative, context)

