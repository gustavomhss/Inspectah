"""Checagens de observabilidade de segurança e forense (S16)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

from inspectah.commands import audit_trail


def _load_manifest(path: Path) -> Dict[str, object]:
    if not path.exists():
        return {"status": "not_available", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "path": str(path), "error": str(exc)}


def run_checks(evidence_dir: Path | None = None) -> Dict[str, object]:
    evidence_dir = evidence_dir or Path("out/evidence/S16_T6_security_observability")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    lookups = {
        "t3_decisions": Path("out/evidence/S16_T3_debunker_and_committees/MANIFEST.json"),
        "t4_anchors": Path("out/evidence/S16_T4_anchors_and_anti_canetada/MANIFEST.json"),
        "t5_stress": Path("out/evidence/S16_T5_stress_and_degradation/MANIFEST.json"),
    }
    observations: List[Dict[str, object]] = []
    available = 0
    missing = 0
    for label, path in lookups.items():
        manifest = _load_manifest(path)
        manifest["label"] = label
        if manifest.get("status") in {None, "PASS"} or "results" in manifest or "anchors" in manifest:
            available += 1
            manifest["status"] = manifest.get("status") or "available"
        elif manifest.get("status") == "not_available":
            missing += 1
        else:
            missing += 1
        observations.append(manifest)

    trail = audit_trail()
    audit_snapshot = {"events": len(trail), "last_event": trail[-1] if trail else None}
    (evidence_dir / "audit_trail.json").write_text(json.dumps(audit_snapshot, indent=2), encoding="utf-8")

    summary = {
        "available_manifests": available,
        "missing_manifests": missing,
        "audit_events": len(trail),
    }
    (evidence_dir / "observations.json").write_text(json.dumps({"observations": observations}, indent=2), encoding="utf-8")
    (evidence_dir / "MANIFEST.json").write_text(
        json.dumps({"summary": summary, "observations": [o.get("label") for o in observations]}, indent=2),
        encoding="utf-8",
    )
    return {"status": "PASS" if missing == 0 else "WARN", "summary": summary, "observations": observations}


def main() -> None:
    parser = argparse.ArgumentParser(description="Consultas de observabilidade de segurança (S16)")
    parser.add_argument("--evidence-dir", default="out/evidence/S16_T6_security_observability")
    args = parser.parse_args()
    result = run_checks(Path(args.evidence_dir))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
