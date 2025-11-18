from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .schemas import CanonicalRecord, ConsolidatedDecision, EvidencePackage, FieldSchema, SourceSchema


@dataclass(slots=True)
class FlashMessage:
    level: str
    text: str


@dataclass(slots=True)
class AdminSourcesView:
    sources: List[SourceSchema]
    selected: Optional[SourceSchema] = None
    flashes: List[FlashMessage] = field(default_factory=list)


@dataclass(slots=True)
class ModelFieldsView:
    fields: List[FieldSchema]
    samples_by_source: dict[str, List[CanonicalRecord]] = field(default_factory=dict)


@dataclass(slots=True)
class QueryView:
    filters: dict[str, str]
    records: List[CanonicalRecord]
    decision: Optional[ConsolidatedDecision] = None
    flashes: List[FlashMessage] = field(default_factory=list)


@dataclass(slots=True)
class EvidenceView:
    record: Optional[CanonicalRecord]
    packages: List[EvidencePackage] = field(default_factory=list)
    missing: bool = False
