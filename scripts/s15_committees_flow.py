"""Fluxo integrado V1 -> V2 -> V3 para T3."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from inspectah.committees.v1_validator import validate_submission
from inspectah.committees.v2_multibrain import run_v2_panel
from inspectah.committees.v3_coherence import check_coherence
from inspectah.debunker.engine import analyze_claim


def _sample_submissions() -> List[Dict[str, object]]:
    return [
        {
            "case_id": "case-v1-reject",
            "fact_id": "f1",
            "domain": "esporte",
            "current_state": "planejado",
            "proposed_state": "concluido",
            "evidence_count": 0,
            "claim": {
                "id": "claim-v1",
                "domain": "esporte",
                "summary": "Promover vencedor sem provas",
                "impact": 0.7,
                "novelty": 0.5,
                "evidence": [],
            },
            "related": [],
        },
        {
            "case_id": "case-v2-need-evidence",
            "fact_id": "f2",
            "domain": "politica",
            "current_state": "planejado",
            "proposed_state": "confirmado",
            "evidence_count": 2,
            "claim": {
                "id": "claim-v2",
                "domain": "politica",
                "summary": "Resultado de eleição sob contestação",
                "impact": 0.9,
                "novelty": 0.8,
                "history_risk": 0.5,
                "evidence": [
                    {"id": "ev1", "stance": "for", "summary": "Boletim oficial"},
                    {"id": "ev2", "stance": "against", "summary": "Contestação da oposição"},
                ],
            },
            "related": [],
        },
        {
            "case_id": "case-v3-conflict",
            "fact_id": "f3",
            "domain": "esporte",
            "scope": "campeonato-x",
            "current_state": "planejado",
            "proposed_state": "confirmado",
            "evidence_count": 2,
            "claim": {
                "id": "claim-v3",
                "domain": "esporte",
                "summary": "Outro time reivindica título já atribuído",
                "impact": 0.85,
                "novelty": 0.6,
                "evidence": [
                    {"id": "ev3", "stance": "for", "summary": "Placar publicado"},
                    {"id": "ev4", "stance": "against", "summary": "Ata da federação confirma rival"},
                ],
            },
            "related": [
                {"fact_id": "f9", "scope": "campeonato-x", "current_state": "confirmado"},
            ],
        },
    ]


def run_committees_flow(evidence_dir: Path | None = None) -> Dict[str, object]:
    evidence_dir = evidence_dir or Path("out/evidence/S15_T3_committees_flow")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    records_dir = evidence_dir / "records"
    records_dir.mkdir(parents=True, exist_ok=True)

    metrics = {"v1_rejected": 0, "v2_escalated": 0, "v3_blocked": 0, "total": 0}
    cases: List[Dict[str, object]] = []

    for submission in _sample_submissions():
        metrics["total"] += 1
        v1 = validate_submission(submission)
        report = analyze_claim(submission["claim"], context={"prior_disputes_ratio": submission.get("history_risk", 0.0)})
        v2 = run_v2_panel(submission, report)
        v3 = check_coherence(submission, submission.get("related", []))

        if v1.status.value == "rejected":
            metrics["v1_rejected"] += 1
        if v2.status.value in {"escalate", "need_more_evidence"}:
            metrics["v2_escalated"] += 1
        if v3.status.value == "blocked":
            metrics["v3_blocked"] += 1

        case_record = {
            "submission": submission,
            "v1": v1.to_dict(),
            "debunker": report.to_dict(),
            "v2": v2.to_dict(),
            "v3": v3.to_dict(),
        }
        cases.append(case_record)
        (records_dir / f"{submission['case_id']}.json").write_text(
            json.dumps(case_record, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    summary_path = evidence_dir / "summary.json"
    summary_payload = {**metrics, "cases": [c["submission"]["case_id"] for c in cases]}
    summary_path.write_text(json.dumps(summary_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"metrics": metrics, "cases": cases}


__all__ = ["run_committees_flow"]
