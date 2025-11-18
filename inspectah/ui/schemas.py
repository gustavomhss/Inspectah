from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str
    runtime_s6_available: bool


class SourceSchema(BaseModel):
    id: str
    name: str
    type: str
    description: Optional[str] = None
    path: str
    transport_url: Optional[str] = None
    enabled: bool = True
    notes: List[str] = Field(default_factory=list)
    raw: Dict[str, Any] = Field(default_factory=dict)


class FieldSchema(BaseModel):
    name: str
    title: str | None = None
    type: str
    required: bool
    description: str
    sources: Dict[str, str]


class FieldSample(BaseModel):
    source_id: str
    item_id: str | None = None
    product_name: str | None = None
    price_brl: float | None = None
    region: str | None = None
    reported_at: str | None = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class EvidencePackage(BaseModel):
    source_id: str
    item_id: str | None = None
    manifest_path: str | None = None
    evidence_path: str | None = None
    collected_at: str | None = None
    hash_sha256: str | None = None


class CanonicalRecord(BaseModel):
    item_id: str
    product_name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    price_brl: Optional[float] = None
    region: Optional[str] = None
    reported_at: Optional[str] = None
    source_url: Optional[str] = None
    notes: Optional[str] = None
    supporting_sources: List[Dict[str, Any]] = Field(default_factory=list)
    sources_count: Optional[int] = None


class QueryFilters(BaseModel):
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    categoria: Optional[str] = None
    regiao: Optional[str] = None
    fonte: Optional[str] = None
    search: Optional[str] = None


class ConsolidatedDecision(BaseModel):
    strategy: Literal["median"]
    currency: str = "BRL"
    value: Optional[float] = None
    sample_count: int = 0
    sources_used: List[str] = Field(default_factory=list)
    explanation: str = ""
    supporting_records: List[str] = Field(default_factory=list)
