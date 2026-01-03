"""
Compare current run with historical runs to detect contradictions across time.
"""
from __future__ import annotations

from typing import Dict, Any, List
import os
import json


def _load_runs(storage_dir: str) -> List[Dict[str, Any]]:
    if not os.path.isdir(storage_dir):
        return []
    files = sorted([f for f in os.listdir(storage_dir) if f.endswith('.json')])
    runs: List[Dict[str, Any]] = []
    for fn in files:
        path = os.path.join(storage_dir, fn)
        with open(path, 'r', encoding='utf-8') as fh:
            try:
                runs.append(json.load(fh))
            except Exception:
                continue
    return runs


def detect_contradictions(current_results: Dict[str, Any], storage_dir: str) -> Dict[str, Any]:
    """Return a report of any hypothesis contradictions between latest run and prior ones.

    Simple rule: if a hypothesis id was 'supported' in prior run and now 'unsupported', flag it.
    """
    runs = _load_runs(storage_dir)
    report: Dict[str, Any] = {"contradictions": []}
    if not runs:
        return report
    latest_prior = runs[-1]
    prior_nodes = {n['hypothesis_id']: n['result'] for n in latest_prior.get('results', {}).get('nodes', [])}
    current_nodes = {n.hypothesis_id: n.result for n in current_results.get('nodes', [])}
    for hid, prior_result in prior_nodes.items():
        cur = current_nodes.get(hid)
        if prior_result == 'supported' and cur == 'unsupported':
            report['contradictions'].append({'hypothesis_id': hid, 'prior': prior_result, 'current': cur})
    return report
