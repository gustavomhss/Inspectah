from __future__ import annotations

import json
from pathlib import Path
from typing import List

import yaml

BASE = Path(__file__).resolve().parents[1] / "docs" / "cases"


def _load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_case(path: Path) -> dict:
    data = _load(path)
    required_fields = ["case_id", "title", "summary", "claims"]
    missing = [f for f in required_fields if f not in data or data[f] in (None, "")]
    claim_count = len(data.get("claims", []) or [])
    return {
        "path": str(path),
        "missing_fields": missing,
        "claim_count": claim_count,
        "case_id": data.get("case_id", path.stem.replace("case_", "")),
    }


def validate_collections(path: Path) -> dict:
    data = _load(path) or {}
    collections = data.get("collections", []) or []
    return {"path": str(path), "collections_count": len(collections)}


def run_checks() -> dict:
    results = []
    for case_file in sorted(BASE.glob("case_*.yaml")):
        results.append(validate_case(case_file))
    collections_result = validate_collections(BASE / "collections.yaml")
    missing_any = [r for r in results if r["missing_fields"]]
    status = "GO" if not missing_any else "NO_GO"
    return {
        "status": status,
        "cases_checked": len(results),
        "cases": results,
        "collections": collections_result,
    }


if __name__ == "__main__":
    outcome = run_checks()
    print(json.dumps(outcome, indent=2))
