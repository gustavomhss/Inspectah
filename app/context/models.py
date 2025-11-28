from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class DossierClaim:
    claim_id: str
    domain: str
    description: str = ""
    truth_state: Optional[str] = None
    debunk_issue_ids: List[str] = field(default_factory=list)
    case_ids: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    events: List[Dict] = field(default_factory=list)


@dataclass
class EntityContextDossier:
    entity_id: str
    domain: str
    claims: List[DossierClaim]
    cases: List[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class CaseContextDossier:
    case_id: str
    domain: str
    title: str
    claims: List[DossierClaim]
    entities: List[str] = field(default_factory=list)
    debunk_issue_ids: List[str] = field(default_factory=list)
    truth_events: List[Dict] = field(default_factory=list)
    summary: str = ""
