from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any, Dict

SCORECARD_PATHS = {
    "field_designer": Path("out/scorecards/T2_field_designer.json"),
    "pipeline": Path("out/scorecards/T3_pipeline_invariants.json"),
    "evidence": Path("out/scorecards/T4_evidence_vault.json"),
    "performance": Path("out/scorecards/T5_performance.json"),
    "confidence": Path("out/scorecards/T5_1_confidence.json"),
}


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing scorecard {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def collect_metrics() -> Dict[str, Any]:
    t2 = _load_json(SCORECARD_PATHS["field_designer"])
    t3 = _load_json(SCORECARD_PATHS["pipeline"])
    t4 = _load_json(SCORECARD_PATHS["evidence"])
    t5 = _load_json(SCORECARD_PATHS["performance"])
    t51 = _load_json(SCORECARD_PATHS["confidence"])
    metrics = {
        "inspectah_sources_configured_total": len(t2.get("details", {}).get("sources", {})),
        "inspectah_field_resolution_success": t2.get("metrics", {}).get("field_resolution_success_test", 0.0),
        "inspectah_dedup_violations_total": t3.get("metrics", {}).get("dedup_violations", 0),
        "inspectah_immutability_violations_total": t3.get("metrics", {}).get("immutability_violations", 0),
        "inspectah_lineage_violations_total": t3.get("metrics", {}).get("lineage_violations", 0),
        "inspectah_evidence_completeness_ratio": t4.get("metrics", {}).get("evidence_completeness", 0.0),
        "inspectah_evidence_hash_valid_rate": t4.get("metrics", {}).get("evidence_hash_valid_rate", 0.0),
        "inspectah_orphan_evidence_total": t4.get("metrics", {}).get("orphan_evidence", 0),
        "inspectah_detection_latency_p95_ms": t5.get("metrics", {}).get("detection_latency_p95_ms", 0.0),
        "inspectah_explore_query_p95_ms": t5.get("metrics", {}).get("explore_query_p95_ms", 0.0),
        "inspectah_explore_query_p99_ms": t5.get("metrics", {}).get("explore_query_p99_ms", 0.0),
        "inspectah_run_success_rate": t5.get("metrics", {}).get("run_success_rate", 0.0),
        "inspectah_confidence_coverage_ratio": t51.get("metrics", {}).get("coverage", 0.0),
        "inspectah_confidence_monotonicity_ok_ratio": t51.get("metrics", {}).get("monotonicity_ok_rate", 0.0),
        "inspectah_confidence_saturation_low_ratio": t51.get("metrics", {}).get("score_saturation_low", 0.0),
        "inspectah_confidence_saturation_high_ratio": t51.get("metrics", {}).get("score_saturation_high", 0.0),
    }
    return metrics


def dump_json(output_path: Path) -> None:
    metrics = collect_metrics()
    output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspectah observability metrics aggregator")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    dump_json(Path(args.output))


if __name__ == "__main__":
    main()
