"""Case service implementation for Sprint 12."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


_STATUS_PRIORITY = {"suspeito": 3, "incerto": 2, "aceito": 1, "informativo": 0}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class Case:
    """Represents a Caso in Sprint 12."""

    id_caso: str
    dominio: str
    titulo: str
    descricao: str
    status: str = "incerto"
    metadata: Dict[str, object] = field(default_factory=dict)
    created_at: str = field(default_factory=_utcnow)
    updated_at: str = field(default_factory=_utcnow)

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class CaseService:
    """Manage cases for the ingestion pipeline and Explorer."""

    def __init__(self) -> None:
        self._cases: Dict[str, Case] = {}

    def reset(self) -> None:
        self._cases.clear()

    def get_or_create_case(self, normalized_event: Dict[str, object]) -> Case:
        case_id = normalized_event.get("case_key")
        if not case_id:
            raise ValueError("Evento normalizado sem case_key definido")
        dominio = normalized_event.get("dominio", "desconhecido")
        case = self._cases.get(case_id)
        if case:
            return case
        titulo = normalized_event.get("titulo", case_id)
        descricao = normalized_event.get("resumo", "Caso criado automaticamente pela ingestão contínua")
        metadata = {
            "source_id": normalized_event.get("source_id"),
            "created_from_event": normalized_event.get("id_evento"),
        }
        case = Case(id_caso=case_id, dominio=dominio, titulo=titulo, descricao=descricao, metadata=metadata)
        self._cases[case_id] = case
        return case
    def get_case(self, case_id: str) -> Optional[Case]:
        return self._cases.get(case_id)

    def update_status_from_decision(self, case_id: str, decision: str) -> None:
        case = self._cases.get(case_id)
        if not case:
            return
        decision = decision or case.status
        current_rank = _STATUS_PRIORITY.get(case.status, 0)
        new_rank = _STATUS_PRIORITY.get(decision, current_rank)
        if new_rank >= current_rank:
            case.status = decision
            case.updated_at = _utcnow()

    def list_cases(self) -> List[Case]:
        return list(self._cases.values())

    def search_cases(self, query: str) -> List[Case]:
        query_lower = query.lower()
        return [case for case in self._cases.values() if query_lower in case.titulo.lower()]

    def export_snapshot(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = [case.to_dict() for case in self._cases.values()]
        path.write_text(_json_dumps(data), encoding="utf-8")

    def integrity_ratio(self, events: List[Dict[str, object]]) -> float:
        if not events:
            return 1.0
        valid = 0
        for event in events:
            case_id = event.get("case_id") or event.get("case_key")
            case = self._cases.get(case_id)
            if not case:
                continue
            if not case_id.startswith(f"{case.dominio}:"):
                continue
            if event.get("dominio") != case.dominio:
                continue
            valid += 1
        return valid / len(events)

    def to_dict(self) -> Dict[str, Dict[str, object]]:
        return {case_id: case.to_dict() for case_id, case in self._cases.items()}


def _json_dumps(payload: object) -> str:
    import json

    return json.dumps(payload, indent=2, ensure_ascii=False)


DEFAULT_CASE_SERVICE = CaseService()


def validate_cases_snapshot(cases_snapshot: List[Dict[str, object]]) -> Dict[str, object]:
    """Basic validation helpers for gate G4."""

    violations: List[str] = []
    for case in cases_snapshot:
        case_id = case.get("id_caso", "")
        domain = case.get("dominio")
        if domain and not case_id.startswith(f"{domain}:"):
            violations.append(f"I2 violada: {case_id} não segue prefixo do domínio {domain}")
    ratio = 1.0 if not cases_snapshot else (len(cases_snapshot) - len(violations)) / len(cases_snapshot)
    return {"case_integrity_ratio": ratio, "violations": violations}
