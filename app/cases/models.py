from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class CaseClaim:
    claim_id: str
    description: str
    truth_state: Optional[str] = None
    debunk_target_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class CaseDefinition:
    case_id: str
    title: str
    summary: str
    theme: str
    tags: List[str]
    claims: List[CaseClaim]
    timeline: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class CaseCollectionDefinition:
    collection_id: str
    title: str
    description: str
    case_ids: List[str]
    tags: List[str] = field(default_factory=list)
