"""Case service skeleton used across Sprint 12 components."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Case:
    """Minimal representation of a case until Wave 2 wires real data sources."""

    id_caso: str
    dominio: str
    titulo: str
    descricao: str
    status: str = "incerto"


class CaseService:
    """Expose case CRUD/search operations for Explorer v0 and gates."""

    def __init__(self) -> None:
        self._cases: Dict[str, Case] = {}

    def register_case(self, case: Case) -> None:
        self._cases[case.id_caso] = case

    def get_case(self, case_id: str) -> Optional[Case]:
        return self._cases.get(case_id)

    def search_cases(self, query: str) -> List[Case]:
        _ = query
        return list(self._cases.values())


DEFAULT_CASE_SERVICE = CaseService()
