"""Medições simples de performance e custo da S15."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Dict

from scripts.s15_anchor_and_guard import run_anchor_and_guard_suite
from scripts.s15_debunker_offline import run_debunker_suite


def measure_performance(evidence_dir: Path | None = None) -> Dict[str, object]:
    evidence_dir = evidence_dir or Path("out/evidence/S15_T5_performance_and_cost")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    debunker_metrics = run_debunker_suite(evidence_dir / "debunker_perf")
    elapsed_debunker = time.perf_counter() - start

    anchor_start = time.perf_counter()
    anchor_metrics = run_anchor_and_guard_suite(evidence_dir / "anchors_perf")
    elapsed_anchor = time.perf_counter() - anchor_start

    total_claims = debunker_metrics["metrics"]["total_claims"]
    throughput = total_claims / elapsed_debunker if elapsed_debunker else float("inf")
    perf = {
        "debunker_seconds": round(elapsed_debunker, 4),
        "anchor_seconds": round(elapsed_anchor, 4),
        "throughput_claims_per_sec": round(throughput, 3),
        "anchors_total": anchor_metrics.get("anchors_total", 0),
    }
    (evidence_dir / "performance.json").write_text(
        __import__("json").dumps(perf, indent=2),
        encoding="utf-8",
    )
    return {"metrics": perf, "debunker": debunker_metrics, "anchors": anchor_metrics}


__all__ = ["measure_performance"]
