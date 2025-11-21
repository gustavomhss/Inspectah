"""
Sprint 14 migrations and cleanup (G4).

Aponta migrações/cleanups leves de forma idempotente e segura, sem
remover arquivos. O objetivo é evidenciar sanidade do kernel e preparar
diretórios da S14 para as próximas waves.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parent.parent
EVIDENCE_DIR = ROOT_DIR / "out" / "evidence" / "S14_G4"
REPORT_PATH = EVIDENCE_DIR / "migrations_report.json"
PLAN_PATH = EVIDENCE_DIR / "migrations_plan.md"

REQUIRED_PATHS = [
    ROOT_DIR / "out" / "evidence" / "S12_G2",
    ROOT_DIR / "out" / "evidence" / "S12_G4",
    ROOT_DIR / "out" / "evidence" / "S13_G2",
    ROOT_DIR / "out" / "evidence" / "S13_G4",
    ROOT_DIR / "config" / "s13_pilotos.yml",
]


def _existing_required() -> List[str]:
    return [str(p) for p in REQUIRED_PATHS if p.exists()]


def _missing_required() -> List[str]:
    return [str(p) for p in REQUIRED_PATHS if not p.exists()]


def _ensure_s14_dirs() -> List[str]:
    created: List[str] = []
    for gate in ["S14_G0", "S14_G1", "S14_G2", "S14_G3", "S14_G4", "S14_G5", "S14_G6", "S14_G7", "S14_G8"]:
        path = ROOT_DIR / "out" / "evidence" / gate
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(str(path))
    return created


def _cleanup_candidates() -> List[str]:
    candidates: List[str] = []
    runtime_feedback = ROOT_DIR / "out" / "runtime" / "s12_feedback_store.json"
    if runtime_feedback.exists():
        candidates.append(str(runtime_feedback))
    legacy_cache = ROOT_DIR / "inspectah.db"
    if legacy_cache.exists():
        candidates.append(str(legacy_cache))
    return candidates


def _planned_actions() -> Dict[str, Any]:
    return {
        "normalize_domains": "Confirmar domínios S13/S14 alinhados em configs e snapshots (ver s13_pilotos.yml).",
        "cleanup_feedback_runtime": "Reset controlado do store de feedback via gates (já feito em G3).",
        "preserve_snapshots": "Snapshots S12/S13 são imutáveis; novas evidências S14 devem ir para pastas próprias.",
    }


def _render_plan(markdown_path: Path, report: Dict[str, Any]) -> None:
    lines = ["# Sprint 14 – Migrações e Cleanup", "", "## Resumo"]
    lines.append(f"- Caminhos obrigatórios ausentes: {len(report['missing_required_paths'])}")
    if report["created_dirs"]:
        lines.append(f"- Diretórios criados: {len(report['created_dirs'])}")
    lines.append("\n## Ações planejadas")
    for key, desc in report["planned_actions"].items():
        lines.append(f"- **{key}**: {desc}")
    lines.append("\n## Recomendações de cleanup (manual)")
    if report["cleanup_candidates"]:
        for c in report["cleanup_candidates"]:
            lines.append(f"- Avaliar remoção/reset controlado: {c}")
    else:
        lines.append("- Nenhum candidato crítico encontrado.")
    markdown_path.write_text("\n".join(lines), encoding="utf-8")


def run() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    created_dirs = _ensure_s14_dirs()
    missing_required = _missing_required()
    cleanup = _cleanup_candidates()

    critical_issues = len(missing_required)
    status = "PASS" if critical_issues == 0 else "FAIL"

    report = {
        "status": status,
        "missing_required_paths": missing_required,
        "existing_required_paths": _existing_required(),
        "created_dirs": created_dirs,
        "cleanup_candidates": cleanup,
        "planned_actions": _planned_actions(),
        "metrics": {
            "missing_required_count": critical_issues,
            "created_dirs_count": len(created_dirs),
            "cleanup_candidates_count": len(cleanup),
        },
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    _render_plan(PLAN_PATH, report)


def main() -> None:
    run()


if __name__ == "__main__":
    main()
