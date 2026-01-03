"""
Persist reasoning results and narrative as JSON files for replay and audit.
"""
from __future__ import annotations

from typing import Any, Dict
import json
import os
from datetime import datetime
from data_thought_engine.core.context import Context


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def persist_run(results: Dict[str, Any], narrative: str, context: Context, storage_dir: str | None = None) -> str:
    """Persist results and narrative to a JSON file and return its path.

    Uses deterministic filename based on the context start time to avoid
    random identifiers.
    """
    base = storage_dir or os.path.join(os.getcwd(), "dte_runs")
    _ensure_dir(base)
    ts = context.start_time.isoformat().replace(":", "-")
    fname = f"run_{ts}.json"
    path = os.path.join(base, fname)
    payload = {
        "start_time": context.start_time.isoformat(),
        "dataset_path": context.dataset_path,
        "results": {
            "summary": results.get("summary"),
            "nodes": [{
                "id": n.id,
                "hypothesis_id": n.hypothesis_id,
                "test": n.test,
                "result": n.result,
                "score": n.score,
                "details": getattr(n, "details", {}),
            } for n in results.get("nodes", [])]
        },
        "narrative": narrative,
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=str)
    return path
