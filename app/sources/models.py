from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class SourceState(str, Enum):
    PROPOSED = "PROPOSED"
    TESTING = "TESTING"
    ACTIVE = "ACTIVE"
    UNDER_REVIEW = "UNDER_REVIEW"
    SUSPECT = "SUSPECT"
    DISABLED_TEMP = "DISABLED_TEMP"
    DISABLED_PERM = "DISABLED_PERM"


class SourceHealthStatus(str, Enum):
    OK = "OK"
    DEGRADED = "DEGRADED"
    FAIL = "FAIL"


@dataclass
class SourceType:
    id: str
    name: str
    description: str = ""
    defaults: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SourceCategory:
    id: str
    name: str
    description: str = ""


@dataclass
class SourceStateHistory:
    id: str
    source_id: str
    from_state: Optional[SourceState]
    to_state: SourceState
    reason: str
    changed_by: str
    created_at: datetime
    conflict_flag: bool = False
    conflict_types: List[str] = field(default_factory=list)
    conflict_with_sources: List[str] = field(default_factory=list)
    contestations: Dict[str, Any] = field(default_factory=dict)
    evidence_refs: List[str] = field(default_factory=list)


@dataclass
class SourceHealthCheck:
    id: str
    source_id: str
    status: SourceHealthStatus
    latency_ms: int
    checked_at: datetime
    error: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Source:
    id: str
    slug: str
    name: str
    description: str
    type: str
    category: str
    themes: List[str]
    info_types: List[str]
    protocol: str
    format: str
    endpoint: str
    auth_type: str
    auth_config: Dict[str, Any]
    request_params: Dict[str, Any]
    headers: Dict[str, Any]
    frequency: str
    timeout_ms: int
    retry_policy: Dict[str, Any]
    parsing_config: Dict[str, Any]
    redundancy_group: Optional[str]
    redundancy_role: Optional[str]
    state: SourceState
    state_reason: Optional[str]
    state_updated_at: datetime
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str
    last_reviewed_by: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)
    conflict_flags: List[str] = field(default_factory=list)
    conflict_with_sources: List[str] = field(default_factory=list)
    has_open_contestation: bool = False
    last_conflict_at: Optional[datetime] = None
    evidence_refs: List[str] = field(default_factory=list)
    trust_severity: Optional[str] = None

    @classmethod
    def create(
        cls,
        *,
        id: str,
        slug: str,
        name: str,
        description: str,
        type: str,
        category: str,
        themes: List[str],
        info_types: List[str],
        protocol: str,
        format: str,
        endpoint: str,
        auth_type: str,
        auth_config: Dict[str, Any],
        request_params: Dict[str, Any],
        headers: Dict[str, Any],
        frequency: str,
        timeout_ms: int,
        retry_policy: Dict[str, Any],
        parsing_config: Dict[str, Any],
        redundancy_group: Optional[str],
        redundancy_role: Optional[str],
        created_by: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> "Source":
        now = datetime.utcnow()
        return cls(
            id=id,
            slug=slug,
            name=name,
            description=description,
            type=type,
            category=category,
            themes=themes,
            info_types=info_types,
            protocol=protocol,
            format=format,
            endpoint=endpoint,
            auth_type=auth_type,
            auth_config=auth_config,
            request_params=request_params,
            headers=headers,
            frequency=frequency,
            timeout_ms=timeout_ms,
            retry_policy=retry_policy,
            parsing_config=parsing_config,
            redundancy_group=redundancy_group,
            redundancy_role=redundancy_role,
            state=SourceState.PROPOSED,
            state_reason=None,
            state_updated_at=now,
            created_at=now,
            updated_at=now,
            created_by=created_by,
            updated_by=created_by,
            meta=meta or {},
        )

