from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional


SourceType = Literal["precos_api_simples", "noticias_rss_simplificado", "outros"]
QueryStatus = Literal["ok", "dados_insuficientes", "erro", "fora_de_escopo"]
QueryType = Literal[
    "agregacao_simples",
    "comparacao_simples",
    "checagem_factual_simples",
    "fora_de_escopo",
]


@dataclass
class SourceConfig:
    url_base: str
    auth_token: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    selected_fields: List[str] = field(default_factory=list)


@dataclass
class SourceStatus:
    last_fetch_at: Optional[datetime] = None
    last_fetch_status: Literal["ok", "erro"] = "ok"
    last_fetch_error: Optional[str] = None
    recent_items_count: int = 0


@dataclass
class Source:
    id: str
    name: str
    type: SourceType
    config: SourceConfig
    status: SourceStatus = field(default_factory=SourceStatus)


@dataclass
class Item:
    id: str
    source_id: str
    payload: Dict[str, Any]
    created_at: datetime


@dataclass
class EvidenceItemRef:
    item_id: str
    source_id: str
    key_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceBundle:
    id: str
    query_type: QueryType
    query_filters: Dict[str, Any]
    items_by_source: Dict[str, List[EvidenceItemRef]]
    manifest_paths: Dict[str, str]
    created_at: datetime
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryLog:
    query_id: str
    user_query: str
    query_type: QueryType
    evidence_bundle_id: Optional[str]
    sources: List[str]
    items_used: List[str]
    gpt_response_ref: Optional[str]
    timestamp: datetime
    status: QueryStatus
    error_code: Optional[str] = None


@dataclass
class ParsedQuery:
    raw_query: str
    query_type: QueryType
    entities: Dict[str, Any]
    filters: Dict[str, Any]


@dataclass
class UserResponse:
    query_id: str
    evidence_bundle_id: Optional[str]
    answer_text: str
    summary: Dict[str, Any]
    evidence: Dict[str, Any]
    status: QueryStatus
    gpt_response_id: Optional[str]
    confidence: Dict[str, Any] = field(default_factory=dict)
    limitations: List[str] = field(default_factory=list)
