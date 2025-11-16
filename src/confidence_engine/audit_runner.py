from __future__ import annotations
import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from field_designer.config_loader import load_source_configs
from watchers.pipeline_runner import PipelineInvariantRunner

from .core import compute_confidence


@dataclass
class AuditCase:
    case_id: str
    expected_order: int
    record: Dict[str, object]
    profile_id: str = "default"


class ConfidenceAudit:
    def __init__(self, db_path: Path, config_dir: Path, *, calibration_path: Path):
        self.db_path = db_path
        self.config_dir = config_dir
        self.calibration_path = calibration_path
        self.configs = load_source_configs(config_dir)
        self.runner = PipelineInvariantRunner(db_path, config_dir)
        self.cases: List[AuditCase] = []

    def close(self) -> None:
        self.runner.close()

    def setup_cases(self) -> None:
        # Example synthetic cases; in real use we'd query DB for items/observations
        self.cases = [
            AuditCase("multi_source_agree", 1, {"sources": ["a", "b"], "agreement": 1.0, "recency_days": 1, "evidence_score": 1.0}),
            AuditCase("single_source", 2, {"sources": ["a"], "agreement": 1.0, "recency_days": 1, "evidence_score": 1.0}),
            AuditCase("multi_source_conflict", 3, {"sources": ["a", "b"], "agreement": 0.4, "recency_days": 2, "evidence_score": 1.0}),
            AuditCase("stale_data", 4, {"sources": ["a", "b"], "agreement": 0.8, "recency_days": 45, "evidence_score": 0.9}),
        ]

    def run(self) -> Dict[str, object]:
        self.runner.ingest(mutated=False)
        self.setup_cases()
        results = []
        monotonic_pairs = 0
        monotonic_ok = 0
        coverage_count = 0
        low_bucket = 0
        high_bucket = 0
        for case in self.cases:
            cfg = next(iter(self.configs.values()))
            result = compute_confidence(case.record, cfg, profile_id=case.profile_id)
            coverage_count += 1 if result.score > 0 else 0
            if result.score < 10:
                low_bucket += 1
            if result.score > 90:
                high_bucket += 1
            results.append({
                "case_id": case.case_id,
                "score": result.score,
                "profile": result.profile_id,
                "factors": result.factors,
                "explanation": result.explanation,
            })
        for idx, case_a in enumerate(self.cases):
            for case_b in self.cases[idx + 1 :]:
                monotonic_pairs += 1
                score_a = next(r for r in results if r["case_id"] == case_a.case_id)["score"]
                score_b = next(r for r in results if r["case_id"] == case_b.case_id)["score"]
                expected_relation = case_a.expected_order - case_b.expected_order
                if expected_relation == 0:
                    ok = abs(score_a - score_b) < 1e-6
                elif expected_relation < 0:  # case_a should be higher
                    ok = score_a >= score_b
                else:
                    ok = score_a <= score_b
                if ok:
                    monotonic_ok += 1
        coverage = coverage_count / max(1, len(self.cases))
        calibration = [
            {
                "case_id": case.case_id,
                "expected_order": case.expected_order,
                "profile_id": case.profile_id,
                "features": case.record,
                "score": next(r for r in results if r["case_id"] == case.case_id)["score"],
            }
            for case in self.cases
        ]
        self.calibration_path.write_text(json.dumps(calibration, indent=2), encoding="utf-8")
        return {
            "coverage": coverage,
            "monotonicity_ok_rate": monotonic_ok / max(1, monotonic_pairs),
            "score_saturation_low": low_bucket / max(1, len(self.cases)),
            "score_saturation_high": high_bucket / max(1, len(self.cases)),
            "cases": results,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Confidence engine audit runner")
    parser.add_argument("--config-dir", default="configs/sources", help="Directory with source configs")
    parser.add_argument("--db-path", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--calibration", required=True)
    args = parser.parse_args()

    db_path = Path(args.db_path)
    config_dir = Path(args.config_dir)
    calibration_path = Path(args.calibration)
    runner = ConfidenceAudit(db_path, config_dir, calibration_path=calibration_path)
    try:
        report = runner.run()
    finally:
        runner.close()
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
