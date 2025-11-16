from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Dict, List

from .config_loader import SourceConfig, load_source_configs
from .dry_run import PreviewResult, run_dry_run


def _write_samples(evidence_dir: Path, result: PreviewResult) -> None:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    sample_path = evidence_dir / f"{result.source_id}_sample.json"
    sample_path.write_text(json.dumps(result.samples, indent=2), encoding="utf-8")


def _run_for_sources(configs: Dict[str, SourceConfig], source_ids: List[str], sample_size: int, evidence_dir: Path | None) -> Dict[str, Dict[str, object]]:
    results: Dict[str, Dict[str, object]] = {}
    for source_id in source_ids:
        config = configs[source_id]
        preview = run_dry_run(config, sample_size=sample_size)
        if evidence_dir is not None:
            _write_samples(evidence_dir, preview)
        results[source_id] = preview.to_dict()
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspectah Field Designer dry-run helper")
    parser.add_argument("--source", action="append", dest="sources", help="Source ID to run (can be repeated)")
    parser.add_argument("--all", action="store_true", help="Run all configured sources")
    parser.add_argument("--sample-size", type=int, default=5, help="Sample size per source (default=5)")
    parser.add_argument("--config-dir", help="Override configs directory (defaults to configs/sources)")
    parser.add_argument("--output", required=True, help="Path to JSON report")
    parser.add_argument("--evidence-dir", help="Directory to dump sample previews")
    args = parser.parse_args()

    configs = load_source_configs(args.config_dir)
    if args.sources:
        requested = sorted(set(args.sources))
    elif args.all:
        requested = sorted(configs.keys())
    else:
        parser.error("use --source or --all to select configurations")
    missing = [sid for sid in requested if sid not in configs]
    if missing:
        raise SystemExit(f"unknown sources requested: {', '.join(missing)}")

    evidence_dir = Path(args.evidence_dir).resolve() if args.evidence_dir else None
    results = _run_for_sources(configs, requested, args.sample_size, evidence_dir)
    sources_tested = len(requested)
    sources_passed = sum(1 for data in results.values() if data.get("ok"))
    total_fields = sum(int(data["metrics"]["fields_total"]) for data in results.values())
    total_resolved = sum(int(data["metrics"]["fields_resolved"]) for data in results.values())
    field_success = (total_resolved / total_fields) if total_fields else 0.0
    summary = {
        "sources_tested": sources_tested,
        "sources_passed": sources_passed,
        "field_resolution_success_test": field_success,
        "thresholds": {
            "sources_passed_min": 3,
            "field_resolution_success_test": ">= 0.95",
        },
    }
    output_data = {
        "sources": results,
        "summary": summary,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output_data, indent=2), encoding="utf-8")


if __name__ == "__main__":  # pragma: no cover
    main()
