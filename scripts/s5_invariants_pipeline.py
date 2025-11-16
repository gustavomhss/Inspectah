#!/usr/bin/env python3
"""Verifica invariantes principais da pipeline de fixtures."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from inspectah.evidence import verifier
from inspectah.pipeline.pipeline_fixtures import run_pipeline_with_fixtures


def main() -> int:
    evidence_tmp = tempfile.TemporaryDirectory()
    index_tmp = tempfile.TemporaryDirectory()
    try:
        result = run_pipeline_with_fixtures(
            evidence_base=evidence_tmp.name,
            index_base=index_tmp.name,
        )
        summary = result["summary"]
        errors: list[str] = []

        if summary["items_total"] == 0:
            errors.append("nenhum item produzido")
        if summary["bundles_total"] != summary["items_total"]:
            errors.append("bundles_total diferente de items_total")

        for item in result["items"]:
            state = item.get("state")
            if state not in {"S2", "S3", "S4"}:
                errors.append(f"state inválido para item {item.get('item_id')}: {state}")
            if not item.get("equivalence_key"):
                errors.append(f"equivalence_key vazio para {item.get('item_id')}")
            bundle_path = item.get("bundle_path")
            if bundle_path:
                verify_result = verifier.verify_bundle(bundle_path)
                if verify_result.get("status") != "PASS":
                    errors.append(f"bundle inválido: {bundle_path}")

        if summary["items_by_state"].get("S4", 0) == 0:
            errors.append("nenhum item chegou em S4")

        report = {
            "status": "PASS" if not errors else "FAIL",
            "items_total": summary["items_total"],
            "items_by_state": summary["items_by_state"],
            "errors": errors,
        }
        print(json.dumps(report, indent=2))
        return 0 if not errors else 1
    finally:
        evidence_tmp.cleanup()
        index_tmp.cleanup()


if __name__ == "__main__":
    sys.exit(main())
