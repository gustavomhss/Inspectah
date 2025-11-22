"""Verificações de CI e reprodutibilidade dos gates da Sprint 16."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Tuple


try:
    import yaml  # type: ignore
except Exception:  # noqa: BLE001
    yaml = None  # type: ignore


def _parse_workflow(path: Path) -> Tuple[Dict[str, object], str]:
    if not path.exists():
        return {"exists": False, "error": "missing"}, "missing"
    content = path.read_text(encoding="utf-8")
    parsed: Dict[str, object] = {"exists": True, "has_s16_steps": "s16_" in content}
    if yaml:
        try:
            data = yaml.safe_load(content) or {}
            parsed["name"] = data.get("name")
            parsed["jobs"] = list((data.get("jobs") or {}).keys())
        except Exception as exc:  # noqa: BLE001
            parsed["error"] = f"yaml_error:{exc}"
    else:
        parsed["note"] = "yaml_not_available"
    return parsed, "ok"


def run_checks(evidence_dir: Path | None = None) -> Dict[str, object]:
    evidence_dir = evidence_dir or Path("out/evidence/S16_T7_ci_and_repro")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    gates_info, _ = _parse_workflow(Path(".ci/sprint_16_gates.yml"))
    nightly_info, _ = _parse_workflow(Path(".ci/sprint_16_nightly.yml"))

    scorecards_present = sorted(Path("out/scorecards").glob("S16_T*.json"))
    summary = {
        "workflows": {
            "gates": gates_info,
            "nightly": nightly_info,
        },
        "local_scorecards": [path.name for path in scorecards_present],
    }
    status = "PASS"
    notes = []
    if not gates_info.get("exists"):
        status = "FAIL"
        notes.append("Workflow sprint_16_gates ausente")
    if not nightly_info.get("exists"):
        notes.append("Workflow sprint_16_nightly ausente")
        status = "FAIL"
    if gates_info.get("exists") and not gates_info.get("has_s16_steps"):
        status = "FAIL"
        notes.append("Workflow sprint_16_gates sem comandos s16_*")

    payload = {"status": status, "notes": notes, **summary}
    (evidence_dir / "ci_checks.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (evidence_dir / "MANIFEST.json").write_text(json.dumps({"files": ["ci_checks.json"], "status": status}, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Checa workflows de CI da Sprint 16")
    parser.add_argument("--evidence-dir", default="out/evidence/S16_T7_ci_and_repro")
    args = parser.parse_args()
    result = run_checks(Path(args.evidence_dir))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
