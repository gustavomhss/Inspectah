from __future__ import annotations

from typing import Iterable, List, Dict


def compute_flood_score(claim_counts: int, threshold: int) -> float:
    return claim_counts / threshold if threshold > 0 else float("inf")


def compute_source_diversity(unique_sources: int, total_sources: int) -> float:
    if total_sources == 0:
        return 0.0
    return unique_sources / total_sources


def compute_reversal_rate(events: List[Dict]) -> float:
    if not events:
        return 0.0
    state_changes = 0
    prev = None
    for ev in events:
        state = ev.get("new_state") or ev.get("new_state".lower()) or ev.get("state")
        if prev is not None and state and state != prev:
            state_changes += 1
        if state:
            prev = state
    return state_changes / max(len(events), 1)


def evaluate_signals(metrics: Dict[str, float], thresholds: Dict[str, float], domain: str) -> List[Dict]:
    signals = []
    if metrics.get("flood_score", 0) > 1:
        signals.append({"kind": "flood", "severity": "medium", "details": {"flood_score": metrics["flood_score"]}})
    if metrics.get("source_diversity", 1) < thresholds.get("min_source_diversity", 0.5):
        signals.append({"kind": "single_source_dependency", "severity": "high", "details": {"source_diversity": metrics["source_diversity"]}})
    if metrics.get("reversal_rate", 0) > thresholds.get("max_reversal_rate", 0.3):
        signals.append({"kind": "reversal_rate_high", "severity": "medium", "details": {"reversal_rate": metrics["reversal_rate"]}})
    for sig in signals:
        sig["domain"] = domain
    return signals
