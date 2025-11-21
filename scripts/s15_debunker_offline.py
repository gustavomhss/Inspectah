"""Runner offline do Debunker v1 para T2."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from inspectah.debunker.engine import analyze_claim
from inspectah.debunker.report_models import DebunkerReport

FIXTURE_DIR = Path("inspectah/debunker/fixtures")


def _load_fixture_files() -> List[Path]:
    return sorted(path for path in FIXTURE_DIR.glob("*.json") if path.is_file())


def _render_report(report: DebunkerReport) -> Dict[str, object]:
    data = report.to_dict()
    return data


def run_debunker_suite(evidence_dir: Path | None = None) -> Dict[str, object]:
    evidence_dir = evidence_dir or Path("out/evidence/S15_T2_debunker_offline")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    reports_dir = evidence_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    fixtures = _load_fixture_files()
    total = 0
    risk_matches = 0
    recommendation_matches = 0
    summaries: List[Dict[str, object]] = []

    for fixture in fixtures:
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        domain = payload.get("domain", fixture.stem)
        for claim in payload.get("claims", []):
            report = analyze_claim(claim, context={"prior_disputes_ratio": claim.get("history_risk", 0.0)})
            total += 1
            expected_risk = str(claim.get("expected_risk"))
            expected_reco = str(claim.get("expected_recommendation"))
            risk_match = expected_risk == report.risk.value
            reco_match = expected_reco == report.recommendation.value
            risk_matches += 1 if risk_match else 0
            recommendation_matches += 1 if reco_match else 0
            rendered = _render_report(report)
            rendered["expected_risk"] = expected_risk
            rendered["expected_recommendation"] = expected_reco
            rendered["domain"] = domain
            summaries.append(rendered)
            (reports_dir / f"{claim.get('id', claim.get('claim_id', total))}.json").write_text(
                json.dumps(rendered, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    accuracy_risk = risk_matches / total if total else 1.0
    accuracy_reco = recommendation_matches / total if total else 1.0
    summary_path = evidence_dir / "summary.json"
    summary_payload = {
        "total_claims": total,
        "risk_matches": risk_matches,
        "recommendation_matches": recommendation_matches,
        "risk_accuracy": round(accuracy_risk, 3),
        "recommendation_accuracy": round(accuracy_reco, 3),
        "reports": [s.get("claim_id") for s in summaries],
    }
    summary_path.write_text(json.dumps(summary_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"metrics": summary_payload, "reports_dir": str(reports_dir)}


__all__ = ["run_debunker_suite"]
