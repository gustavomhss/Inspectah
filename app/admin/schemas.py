from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class SourceCreateRequest:
    id: str
    name: str
    type: str
    info_type: str
    url_base: str
    selected_fields: List[str]
    auth_token: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SourceResponse:
    id: str
    name: str
    type: str
    info_type: str
    url_base: str
    selected_fields: List[str]
    params: Dict[str, Any]


@dataclass
class SourceStatusResponse:
    source_id: str
    last_fetch_at: Optional[datetime]
    last_fetch_status: str
    last_fetch_error: Optional[str]
    recent_items_count: int


@dataclass
class SourceTestResult:
    source_id: str
    items_ingested: int
    preview_items: List[Dict[str, Any]]
    status: str
    notes: Optional[str] = None
