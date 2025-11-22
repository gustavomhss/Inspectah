"""Stress tests e observação de modos de falha da Sprint 16."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict

from inspectah.anchors.batcher import Batcher
from inspectah.debunker.engine import analyze_claim
from inspectah.debunker.report_models import Recommendation, RiskLevel
from inspectah.committees.v1_validator import validate_submission
from inspectah.committees.v2_multibrain import run_v2_panel
from inspectah.committees.v3_coherence import check_coherence


def _stress_debunker_and_committees(iterations: int) -> Dict[str, object]:
    errors = 0
    escalations = 0
    blocked = 0
    start = time.perf_counter()
    for idx in range(iterations):
        claim = {
            "id": f"stress-{idx}",
            "domain": "politica" if idx % 2 else "esporte",
            "summary": "claim sob stress",
            "impact": 0.6 + (0.05 * (idx % 3)),
            "novelty": 0.4,
            "history_risk": 0.3,
            "evidence": [{"id": f"ev-{idx}", "stance": "against", "summary": "contestacao"}] if idx % 4 == 0 else [],
        }
        submission = {
            "case_id": f"case-{idx}",
            "fact_id": f"fact-{idx%5}",
            "domain": claim["domain"],
            "current_state": "incerto",
            "proposed_state": "confirmado",
            "evidence_count": 1 if claim["evidence"] else 0,
            "claim": claim,
            "related": [],
        }
        try:
            report = analyze_claim(claim)
            v1 = validate_submission(dict(submission))
            v2 = run_v2_panel(submission, report)
            v3 = check_coherence(submission, submission.get("related", []))
            if report.recommendation in {Recommendation.OPEN_DISPUTE, Recommendation.ESCALATE}:
                escalations += 1
            if v3.status.value == "blocked":
                blocked += 1
        except Exception:
            errors += 1
    elapsed = time.perf_counter() - start
    throughput = iterations / elapsed if elapsed else float("inf")
    return {
        "iterations": iterations,
        "errors": errors,
        "elapsed_seconds": round(elapsed, 4),
        "throughput_ops_per_sec": round(throughput, 2),
        "escalations": escalations,
        "blocked": blocked,
    }


def _stress_anchors(batch_entries: int) -> Dict[str, object]:
    batcher = Batcher(max_entries=5, max_age_seconds=1)
    batches = []
    failures = 0
    for idx in range(batch_entries):
        batcher.add_entry(f"anchor-fact-{idx}")
        try:
            res = batcher.flush()
        except Exception:  # noqa: BLE001
            failures += 1
            continue
        batches.append({"anchor_id": res.anchor_id, "items": list(res.items), "tx_hash": res.receipt.tx_hash})
    return {"batches": batches, "failures": failures}


def run_stress(evidence_dir: Path | None = None, *, iterations: int = 80, smoke: bool = False) -> Dict[str, object]:
    evidence_dir = evidence_dir or Path("out/evidence/S16_T5_stress_and_degradation")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    iter_count = max(20, iterations // 2) if smoke else iterations
    debunker_metrics = _stress_debunker_and_committees(iter_count)
    anchor_metrics = _stress_anchors(15 if not smoke else 6)

    summary = {
        "debunker_throughput": debunker_metrics["throughput_ops_per_sec"],
        "debunker_errors": debunker_metrics["errors"],
        "committee_escalations": debunker_metrics["escalations"],
        "anchor_batches": len(anchor_metrics["batches"]),
        "anchor_failures": anchor_metrics["failures"],
    }
    status = "PASS"
    notes = []
    if debunker_metrics["throughput_ops_per_sec"] < 25:
        status = "FAIL"
        notes.append("Throughput abaixo do mínimo esperado (25 ops/s)")
    if debunker_metrics["errors"] > 0 or anchor_metrics["failures"] > 0:
        notes.append("Falhas observadas durante stress")
    evidence = {
        "debunker_and_committees": debunker_metrics,
        "anchors": anchor_metrics,
        "status": status,
        "notes": notes,
    }
    (evidence_dir / "stress_summary.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    (evidence_dir / "MANIFEST.json").write_text(json.dumps({"status": status, "files": ["stress_summary.json"]}, indent=2), encoding="utf-8")
    return {"status": status, "metrics": summary, "details": evidence}


def main() -> None:
    parser = argparse.ArgumentParser(description="Stress e modos de degradação (S16)")
    parser.add_argument("--evidence-dir", default="out/evidence/S16_T5_stress_and_degradation")
    parser.add_argument("--iterations", type=int, default=80)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    result = run_stress(Path(args.evidence_dir), iterations=args.iterations, smoke=args.smoke)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
