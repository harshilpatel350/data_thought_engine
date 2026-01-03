"""
Compare current run with historical runs to detect contradictions across time.
Implements v1.1: Cross-run reasoning consistency and contradiction detection.
"""
from __future__ import annotations

from typing import Dict, Any, List
import os
import json
import hashlib


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


def _hash_dataset(path: str) -> str:
    """Compute deterministic hash of dataset file.

    This is used to identify if reasoning applies to the same input.
    """
    try:
        with open(path, 'rb') as fh:
            content = fh.read()
            return hashlib.sha256(content).hexdigest()[:16]
    except Exception:
        return "unknown"


def _compute_reasoning_signature(dataset_path: str, results: Dict[str, Any]) -> Dict[str, Any]:
    """Create a deterministic signature of reasoning outcomes.

    Signature includes: dataset hash, supported/rejected hypothesis IDs, dominant explanation.
    """
    dataset_hash = _hash_dataset(dataset_path)
    nodes = results.get('nodes', [])
    supported_ids = sorted([n.hypothesis_id for n in nodes if n.result == 'supported'])
    rejected_ids = sorted([n.hypothesis_id for n in nodes if n.result == 'unsupported'])
    weak_ids = sorted([n.hypothesis_id for n in nodes if n.result == 'weak_support'])
    dominant = None
    max_score = -1
    for n in nodes:
        if n.score > max_score:
            max_score = n.score
            dominant = n.hypothesis_id
    return {
        'dataset_hash': dataset_hash,
        'supported_ids': supported_ids,
        'rejected_ids': rejected_ids,
        'weak_ids': weak_ids,
        'dominant_hypothesis': dominant,
        'dominant_score': max_score,
    }


def compare_with_history(current_signature: Dict[str, Any], storage_dir: str) -> Dict[str, Any]:
    """Compare current reasoning signature against prior runs.

    Returns a structured comparison result with consistency status and explanation.
    """
    runs = _load_runs(storage_dir)
    if not runs:
        return {
            'has_history': False,
            'status': 'no_prior_runs',
            'message': 'No prior reasoning runs found.',
        }
    # Load and compute signatures for prior runs
    prior_sigs = []
    for run in runs:
        dataset_path = run.get('dataset_path')
        if dataset_path:
            # Recompute signature from stored results
            sig_data = {
                'dataset_hash': _hash_dataset(dataset_path),
                'supported_ids': sorted([n['hypothesis_id'] for n in run.get('results', {}).get('nodes', []) if n.get('result') == 'supported']),
                'rejected_ids': sorted([n['hypothesis_id'] for n in run.get('results', {}).get('nodes', []) if n.get('result') == 'unsupported']),
            }
            dominant = max((n for n in run.get('results', {}).get('nodes', [])), key=lambda x: x.get('score', 0), default=None)
            if dominant:
                sig_data['dominant_hypothesis'] = dominant['hypothesis_id']
                sig_data['dominant_score'] = dominant['score']
            prior_sigs.append(sig_data)
    if not prior_sigs:
        return {
            'has_history': False,
            'status': 'no_valid_history',
            'message': 'No valid prior reasoning could be reconstructed.',
        }
    # Compare current with latest prior
    latest_prior = prior_sigs[-1]
    dataset_match = current_signature['dataset_hash'] == latest_prior.get('dataset_hash')
    if not dataset_match:
        return {
            'has_history': True,
            'status': 'different_dataset',
            'message': 'Dataset changed since last reasoning run.',
        }
    # Check for exact match
    if (current_signature['supported_ids'] == latest_prior.get('supported_ids', []) and
        current_signature['rejected_ids'] == latest_prior.get('rejected_ids', []) and
        current_signature['dominant_hypothesis'] == latest_prior.get('dominant_hypothesis')):
        return {
            'has_history': True,
            'status': 'exact_match',
            'message': 'Reasoning is identical to prior run on same dataset.',
        }
    # Check for dominant explanation change (contradiction)
    if (current_signature['dominant_hypothesis'] != latest_prior.get('dominant_hypothesis')):
        return {
            'has_history': True,
            'status': 'dominant_changed',
            'prior_dominant': latest_prior.get('dominant_hypothesis'),
            'current_dominant': current_signature['dominant_hypothesis'],
            'message': 'Dominant explanation contradicts prior reasoning.',
        }
    # Check for partial reinforcement (some overlap)
    curr_supported = set(current_signature['supported_ids'])
    prior_supported = set(latest_prior.get('supported_ids', []))
    overlap = curr_supported & prior_supported
    if overlap:
        return {
            'has_history': True,
            'status': 'partial_reinforcement',
            'shared_supported': sorted(overlap),
            'message': 'Some supported hypotheses are consistent with prior reasoning.',
        }
    # Default: reasoning diverged
    return {
        'has_history': True,
        'status': 'reasoning_diverged',
        'message': 'Reasoning diverged from prior conclusions.',
    }


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
