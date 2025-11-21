"""Narratives registry for Sprint 13 pilot cases."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from scripts import s13_pilots_registry as registry

DEFAULT_EVIDENCE_DIR = Path("out/evidence/S13_G5")
REQUIRED_FIELDS = ["descricao_curta", "estado_atual", "narrativa_resumo"]


def run_narratives_checks(evidence_dir: Optional[Path] = None) -> Dict[str, object]:
    evidence_dir = evidence_dir or DEFAULT_EVIDENCE_DIR
    evidence_dir.mkdir(parents=True, exist_ok=True)
    narrative_dir = evidence_dir / "narrativas"
    narrative_dir.mkdir(parents=True, exist_ok=True)

    pilots = registry.list_pilots()
    per_domain: Dict[str, Dict[str, int]] = {}
    results: Dict[str, Dict[str, object]] = {}
    ok_count = 0

    for pilot in pilots:
        pilot_id = pilot["id"]
        domain = pilot["dominio"]
        per_domain.setdefault(domain, {"total": 0, "ok": 0})["total"] += 1
        missing = _missing_fields(pilot)
        narrative_path = narrative_dir / f"{pilot_id}.md"
        if not missing:
            ok_count += 1
            per_domain[domain]["ok"] += 1
        results[pilot_id] = {
            "domain": domain,
            "ok": not missing,
            "missing": missing,
            "narrativa_path": str(narrative_path),
        }
        _write_narrative_markdown(pilot, narrative_path)

    total = len(pilots)
    ratio = ok_count / total if total else 1.0
    per_domain_ratio = {
        domain: (stats["ok"] / stats["total"]) if stats["total"] else 1.0
        for domain, stats in per_domain.items()
    }

    report = {
        "narrative_completeness_ratio": round(ratio, 3),
        "per_domain_narrative_ratio": {k: round(v, 3) for k, v in per_domain_ratio.items()},
        "pilots": results,
    }
    (evidence_dir / "narrativas_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return report


def _missing_fields(pilot: Dict[str, object]) -> List[str]:
    missing: List[str] = []
    for field in REQUIRED_FIELDS:
        value = str(pilot.get(field, "")).strip()
        if not value or value.lower().startswith("todo"):
            missing.append(field)
    return missing


def _write_narrative_markdown(pilot: Dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = f"""# {pilot.get('nome', pilot['id'])}

- Caso ID: `{pilot.get('case_key', pilot['id'])}`
- Domínio: {pilot.get('dominio', 'desconhecido')}
- Local: {pilot.get('local', 'n/d')}
- Período: {pilot.get('periodo', 'n/d')}
- Estado atual: {pilot.get('estado_atual', 'n/d')}

## Descrição curta
{pilot.get('descricao_curta', '').strip()}

## Narrativa resumida
{pilot.get('narrativa_resumo', '').strip()}
"""
    path.write_text(content.strip() + "\n", encoding="utf-8")


__all__ = ["run_narratives_checks"]
