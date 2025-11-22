"""Checagens estruturais do Threat Model da Sprint 16."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


REQUIRED_SECTIONS = (
    "visão geral",
    "ativos protegidos",
    "atores",
    "ameaças principais",
    "mitigações",
    "riscos residuais",
    "mapeamento ameaça",
)

REQUIRED_REFERENCES: Tuple[Tuple[str, str], ...] = (
    ("inspectah/debunker", "inspectah/debunker/engine.py"),
    ("inspectah/committees", "inspectah/committees/v1_validator.py"),
    ("inspectah/anchors", "inspectah/anchors/batcher.py"),
    ("inspectah/commands", "inspectah/commands/__init__.py"),
    ("bin/s16_t0_sanity.sh", "bin/s16_t0_sanity.sh"),
    ("scripts/s16_attack_scenarios.py", "scripts/s16_attack_scenarios.py"),
)


def _parse_sections(text: str) -> List[str]:
    headings: List[str] = []
    for line in text.splitlines():
        if line.startswith("#"):
            heading = re.sub(r"^#+", "", line).strip().lower()
            if heading:
                headings.append(heading)
    return headings


def run_checks(
    threat_model_path: Path = Path("docs/sprint_16_threat_model.md"),
    evidence_dir: Path | None = None,
) -> Dict[str, object]:
    evidence_dir = evidence_dir or Path("out/evidence/S16_T1_threat_model")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    result: Dict[str, object] = {"path": str(threat_model_path)}

    if not threat_model_path.exists():
        result.update({"status": "FAIL", "error": "threat_model_missing"})
        (evidence_dir / "MANIFEST.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    text = threat_model_path.read_text(encoding="utf-8")
    headings = _parse_sections(text)
    missing_sections = [section for section in REQUIRED_SECTIONS if not any(section in h for h in headings)]
    references_found: List[str] = []
    references_missing: List[str] = []
    for marker, path in REQUIRED_REFERENCES:
        if marker.lower() in text.lower() and Path(path).exists():
            references_found.append(path)
        else:
            references_missing.append(path)

    status = "PASS" if not missing_sections and not references_missing else "FAIL"
    result.update(
        {
            "status": status,
            "missing_sections": missing_sections,
            "references_found": references_found,
            "references_missing": references_missing,
            "line_count": len(text.splitlines()),
        }
    )

    (evidence_dir / "sections.json").write_text(
        json.dumps({"headings": headings, "missing": missing_sections}, indent=2),
        encoding="utf-8",
    )
    (evidence_dir / "references.json").write_text(
        json.dumps(
            {"expected": [path for _, path in REQUIRED_REFERENCES], "found": references_found, "missing": references_missing},
            indent=2,
        ),
        encoding="utf-8",
    )
    manifest = {"status": status, "files": ["sections.json", "references.json"], "path": str(threat_model_path)}
    (evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Checa Threat Model da Sprint 16")
    parser.add_argument("--threat-model", default="docs/sprint_16_threat_model.md")
    parser.add_argument("--evidence-dir", default="out/evidence/S16_T1_threat_model")
    args = parser.parse_args()
    result = run_checks(Path(args.threat_model), Path(args.evidence_dir))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
