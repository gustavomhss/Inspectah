from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Dict, List

from field_designer.config_loader import SourceConfig
from field_designer.dry_run import extract_path
from inspectah.config import load_evidence_vault_settings
from watchers.pipeline_runner import compute_canonical_key

from .profiles import ConfidenceProfile, load_profiles


@dataclass
class ConfidenceResult:
    score: float
    profile_id: str
    factors: Dict[str, float]
    weights: Dict[str, float]
    explanation: List[str]
    sources_considered: List[str]


def _normalize(value: float, min_value: float, max_value: float) -> float:
    if max_value == min_value:
        return 0.0
    return max(0.0, min(1.0, (value - min_value) / (max_value - min_value)))


def compute_confidence(
    record: Dict[str, object],
    cfg: SourceConfig,
    *,
    profile_id: str = "default",
    profiles: Dict[str, ConfidenceProfile] | None = None,
) -> ConfidenceResult:
    profile_table = profiles or load_profiles()
    profile = profile_table.get(profile_id, profile_table["default"])

    sources = record.get("sources") or [cfg.id]
    source_count = len(sources)
    agreement = float(record.get("agreement", 1.0))
    recency_days = float(record.get("recency_days", 0.0))
    evidence_complete = float(record.get("evidence_score", 1.0))

    factors = {
        "source_count": _normalize(source_count, 1, 5),
        "agreement": agreement,
        "recency": _normalize(max(0.0, 30 - recency_days), 0, 30),
        "evidence": evidence_complete,
    }
    weighted = sum(profile.weights.get(name, 0.0) * value for name, value in factors.items())
    score = weighted * 100

    if source_count == 1:
        score = min(score, profile.limits.get("single_source_cap", 70))
    if record.get("low_quality_source"):
        score = min(score, profile.limits.get("low_quality_cap", 60))

    score = max(0.0, min(100.0, score))
    explanation = [
        f"profile={profile_id}",
        f"sources={source_count}",
        f"agreement={agreement:.2f}",
        f"recency_days={recency_days}",
        f"evidence_score={evidence_complete:.2f}",
    ]
    return ConfidenceResult(
        score=score,
        profile_id=profile_id,
        factors=factors,
        weights=profile.weights,
        explanation=explanation,
        sources_considered=list(sources),
    )
