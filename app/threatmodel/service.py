from __future__ import annotations

import yaml
from pathlib import Path
from typing import Dict, List

from app.context.models import CaseContextDossier
from app.incidents.service import create_incident_from_signal, IncidentRepository
from .computations import compute_flood_score, compute_reversal_rate, compute_source_diversity, evaluate_signals
from .models import ThreatMetricSnapshot, ThreatSignal


def load_thresholds(path: Path = Path("configs/threatmodel/thresholds.yaml")) -> Dict[str, Dict]:
    if not path.exists():
        raise FileNotFoundError(f"Thresholds file not found: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def compute_snapshot_for_case(
    dossier: CaseContextDossier,
    thresholds: Dict[str, Dict],
    incident_repo: IncidentRepository | None = None,
) -> ThreatMetricSnapshot:
    domain = dossier.domain
    domain_thresholds = thresholds.get(domain, thresholds.get("default", {}))
    claims = dossier.claims
    total_claims = len(claims)
    all_sources = [src for claim in claims for src in claim.sources]
    unique_sources = len(set(all_sources))
    events = [event for claim in claims for event in claim.events]

    metrics = {
        "flood_score": compute_flood_score(total_claims, domain_thresholds.get("max_flood", 5)),
        "source_diversity": compute_source_diversity(unique_sources, len(all_sources) or 1),
        "reversal_rate": compute_reversal_rate(events),
    }
    raw_signals = evaluate_signals(metrics, domain_thresholds, domain)
    signals = [ThreatSignal(kind=s["kind"], severity=s["severity"], details=s["details"], domain=s["domain"]) for s in raw_signals]

    repo_inc = incident_repo or IncidentRepository()
    for sig in signals:
        if sig.severity in {"medium", "high", "critical"}:
            create_incident_from_signal(
                signal=sig.__dict__,
                domain=domain,
                summary=f"Sinal {sig.kind} em {dossier.case_id}",
                ref_case_id=dossier.case_id,
                repo=repo_inc,
            )

    return ThreatMetricSnapshot(domain=domain, metrics=metrics, signals=signals)
