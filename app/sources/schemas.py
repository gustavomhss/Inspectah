from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict

from .models import SourceHealthStatus, SourceState


class SourceConfigBase(BaseModel):
    endpoint: str = Field("", alias="url_base")
    protocol: str = "https"
    format: str = "json"
    auth_type: str = "none"
    auth_config: Dict[str, Any] = Field(default_factory=dict)
    request_params: Dict[str, Any] = Field(default_factory=dict)
    headers: Dict[str, Any] = Field(default_factory=dict)
    frequency: str = "manual"
    timeout_ms: int = 10000
    retry_policy: Dict[str, Any] = Field(default_factory=dict)
    parsing_config: Dict[str, Any] = Field(default_factory=dict)


class SourceConfigRSS(SourceConfigBase):
    format: str = "rss"
    protocol: str = "https"
    parsing_config: Dict[str, Any] = Field(default_factory=lambda: {"item_selector": None})


class SourceConfigHTTPAPI(SourceConfigBase):
    format: str = "json"
    protocol: str = "https"
    frequency: str = "hourly"


class SourceConfigStaticDataset(SourceConfigBase):
    format: str = "csv"
    protocol: str = "https"
    frequency: str = "monthly"
    parsing_config: Dict[str, Any] = Field(default_factory=lambda: {"checksum": None, "schema_version": None})


class SourceBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    slug: str
    name: str
    description: str = ""
    type: str
    category: str
    themes: List[str] = Field(default_factory=list)
    info_types: List[str] = Field(default_factory=list)
    protocol: str = "https"
    format: str = "json"
    endpoint: str = Field("", alias="url_base")
    auth_type: str = "none"
    auth_config: Dict[str, Any] = Field(default_factory=dict)
    request_params: Dict[str, Any] = Field(default_factory=dict)
    headers: Dict[str, Any] = Field(default_factory=dict)
    frequency: str = "manual"
    timeout_ms: int = 10000
    retry_policy: Dict[str, Any] = Field(default_factory=dict)
    parsing_config: Dict[str, Any] = Field(default_factory=dict)
    redundancy_group: Optional[str] = None
    redundancy_role: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)


class SourceCreate(SourceBase):
    created_by: str = "system"


class SourceUpdate(SourceBase):
    updated_by: str = "system"
    state: Optional[SourceState] = None
    state_reason: Optional[str] = None


class SourceRead(SourceBase):
    id: str
    state: SourceState
    state_reason: Optional[str]
    state_updated_at: datetime
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str
    last_reviewed_by: Optional[str] = None
    conflict_flags: List[str] = Field(default_factory=list)
    conflict_with_sources: List[str] = Field(default_factory=list)
    has_open_contestation: bool = False
    last_conflict_at: Optional[datetime] = None
    evidence_refs: List[str] = Field(default_factory=list)
    trust_severity: Optional[str] = None
    last_health_status: Optional[str] = None
    last_health_error: Optional[str] = None
    last_health_at: Optional[datetime] = None
    recent_items_count: int = 0


class SourceFilter(BaseModel):
    type: Optional[str] = None
    category: Optional[str] = None
    state: Optional[SourceState] = None
    theme: Optional[str] = None
    redundancy_group: Optional[str] = None


class SourceTypeRead(BaseModel):
    id: str
    name: str
    description: str = ""
    defaults: Dict[str, Any] = Field(default_factory=dict)


class SourceCategoryRead(BaseModel):
    id: str
    name: str
    description: str = ""


class SourceHealthCheckRead(BaseModel):
    id: str
    source_id: str
    status: SourceHealthStatus
    latency_ms: int
    checked_at: datetime
    error: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
