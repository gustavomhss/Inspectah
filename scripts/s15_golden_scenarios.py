"""Cenários golden da S15 usando fixtures multi-domínio."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from inspectah.debunker.engine import analyze_claim

DOMAIN_DIRS = {
    "esporte": "S15_T4_golden_esporte",
    "politica": "S15_T4_golden_politica",
    "clima": "S15_T4_golden_clima",
    "fofoca": "S15_T4_golden_fofoca",
    "mandatos": "S15_T4_golden_mandatos",
    "projetos": "S15_T4_golden_projetos",
    "ciencia": "S15_T4_golden_ciencia",
}

FIXTURE_DIR = Path("inspectah/debunker/fixtures")


def run_golden_suite(base_dir: Path | None = None) -> Dict[str, object]:
    base_dir = base_dir or Path("out/evidence")
    metrics: Dict[str, Dict[str, int | float]] = {}
    coverage: Dict[str, str] = {}
    for fixture_path in sorted(FIXTURE_DIR.glob("*.json")):
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        domain = payload.get("domain", fixture_path.stem)
        evidence_dir = base_dir / DOMAIN_DIRS.get(domain, f"S15_T4_golden_{domain}")
        evidence_dir.mkdir(parents=True, exist_ok=True)
        reports_dir = evidence_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        counts = {"claims": 0, "high_risk": 0, "disputes": 0}
        for claim in payload.get("claims", []):
            counts["claims"] += 1
            report = analyze_claim(claim, context={"prior_disputes_ratio": claim.get("history_risk", 0.0)})
            if report.risk.value == "high":
                counts["high_risk"] += 1
            if report.recommendation.value in {"open_dispute", "questioned"}:
                counts["disputes"] += 1
            report_path = reports_dir / f"{claim.get('id', claim.get('claim_id', counts['claims']))}.json"
            report_path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        metrics[domain] = counts
        coverage[domain] = str(evidence_dir)

    summary = {
        "domains": len(metrics),
        "metrics": metrics,
        "coverage": coverage,
    }
    summary_path = base_dir / "S15_T4_golden_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


__all__ = ["run_golden_suite"]
