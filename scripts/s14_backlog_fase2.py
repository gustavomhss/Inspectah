"""
Sprint 14 backlog Fase 2 (G5).

Lê o backlog estruturado em docs/sprint_14_backlog_fase2.md e valida
consistência básica (campos obrigatórios, domínios válidos, IDs únicos).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

DOC_PATH = Path("docs/sprint_14_backlog_fase2.md")
EVIDENCE_DIR = Path("out/evidence/S14_G5")
PARSED_PATH = EVIDENCE_DIR / "backlog_fase2_parsed.json"
REPORT_PATH = EVIDENCE_DIR / "backlog_fase2_report.json"

BEGIN = "<!-- S14_BACKLOG_FASE2:BEGIN -->"
END = "<!-- S14_BACKLOG_FASE2:END -->"
VALID_DOMAINS = {"obra_publica", "evento_climatico", "projeto_lei", "carreira_politica", "influencer", "atleta", "infra"}
VALID_SIZES = {"S", "M", "L"}


class BacklogParseError(RuntimeError):
    """Erro de parse/backlog inconsistente."""


def _load_block() -> List[Dict[str, Any]]:
    if not DOC_PATH.exists():
        raise BacklogParseError(f"Documento não encontrado: {DOC_PATH}")
    text = DOC_PATH.read_text(encoding="utf-8")
    begin = text.find(BEGIN)
    end = text.find(END)
    if begin == -1 or end == -1 or end <= begin:
        raise BacklogParseError("Marcadores S14_BACKLOG_FASE2 não encontrados")
    block = text[begin:end]
    match = re.search(r"```json\s*(.*?)```", block, re.S)
    if not match:
        raise BacklogParseError("Bloco JSON não encontrado no backlog")
    try:
        items = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise BacklogParseError(f"JSON inválido no backlog: {exc}") from exc
    if not isinstance(items, list):
        raise BacklogParseError("Backlog deve ser uma lista de itens")
    return items  # type: ignore[return-value]


def _validate_items(items: List[Dict[str, Any]]) -> Tuple[List[str], Dict[str, Any]]:
    issues: List[str] = []
    seen_ids = set()
    domains_present = set()
    sizes_count: Dict[str, int] = {}
    for item in items:
        item_id = item.get("id")
        domain = item.get("domain")
        size = item.get("size")
        if not item_id or not isinstance(item_id, str):
            issues.append("Item sem id válido")
        elif item_id in seen_ids:
            issues.append(f"ID duplicado: {item_id}")
        else:
            seen_ids.add(item_id)
        if not domain or domain not in VALID_DOMAINS:
            issues.append(f"Domínio inválido: {domain}")
        else:
            domains_present.add(domain)
        if size not in VALID_SIZES:
            issues.append(f"Tamanho inválido: {size}")
        else:
            sizes_count[size] = sizes_count.get(size, 0) + 1
        required_fields = ["type", "description", "justification", "dependencies"]
        for field in required_fields:
            if not item.get(field):
                issues.append(f"{item_id or 'item'} sem campo obrigatório: {field}")
    coverage_ratio = len((VALID_DOMAINS - {"infra"}).intersection(domains_present)) / 6.0
    metrics = {
        "total_items": len(items),
        "items_by_domain": {dom: sum(1 for it in items if it.get("domain") == dom) for dom in VALID_DOMAINS},
        "items_by_size": sizes_count,
        "coverage_ratio": round(coverage_ratio, 3),
        "issues_count": len(issues),
    }
    return issues, metrics


def run() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        items = _load_block()
        issues, metrics = _validate_items(items)
        status = (
            "PASS"
            if metrics["coverage_ratio"] >= 1.0 and metrics["issues_count"] == 0
            else ("WARN" if metrics["issues_count"] <= 2 else "FAIL")
        )
    except BacklogParseError as exc:
        items = []
        metrics = {
            "total_items": 0,
            "items_by_domain": {},
            "items_by_size": {},
            "coverage_ratio": 0.0,
            "issues_count": 1,
        }
        issues = [str(exc)]
        status = "FAIL"

    PARSED_PATH.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")

    report = {
        "status": status,
        "metrics": metrics,
        "issues": issues,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    run()
