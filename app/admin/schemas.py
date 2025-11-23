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


# --- S18 admin console schemas ---


@dataclass
class AdminSourceStatus:
    status: str
    last_checked_at: Optional[datetime]
    recent_items_count: int
    last_error: Optional[str] = None


@dataclass
class AdminSourceSummary:
    id: str
    name: str
    type: str
    info_type: str
    is_active: bool
    status: AdminSourceStatus


@dataclass
class AdminSourceHistoryEntry:
    checked_at: Optional[datetime]
    status: str
    error: Optional[str] = None


@dataclass
class AdminSourceDetail(AdminSourceSummary):
    url_base: str = ""
    history: List[AdminSourceHistoryEntry] = field(default_factory=list)


@dataclass
class AdminCaseSummary:
    id: str
    title: str
    category: str
    status: str
    risk: Optional[str]
    updated_at: Optional[datetime]
    key_sources: List[str] = field(default_factory=list)


@dataclass
class AdminCaseDetail(AdminCaseSummary):
    description: str = ""
    top_evidence: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AdminHealth:
    sources_total: int
    sources_healthy: int
    sources_degraded: int
    cases_total: int
    cases_attention: int
    cases_stable: int
    integrations: Dict[str, str] = field(default_factory=dict)


# --- S19 timeline e raio-x ---


@dataclass
class AdminTimelineEvent:
    id: str
    case_id: str
    timestamp: datetime
    event_type: str
    severity: Optional[str] = None
    source: Optional[str] = None
    summary: str = ""


@dataclass
class AdminTimelineResponse:
    case_id: str
    events: List[AdminTimelineEvent] = field(default_factory=list)


@dataclass
class AdminDebunkerSection:
    risk_level: Optional[str]
    explanation: str
    flags: List[str] = field(default_factory=list)
    last_evaluated_at: Optional[datetime] = None


@dataclass
class AdminCommitteeDecision:
    name: str
    verdict: str
    confidence: Optional[str] = None
    rationale: Optional[str] = None
    decided_at: Optional[datetime] = None


@dataclass
class AdminCommitteesSection:
    summary: str
    decisions: List[AdminCommitteeDecision] = field(default_factory=list)


@dataclass
class AdminAnchorSummary:
    name: str
    status: str
    last_check: Optional[datetime] = None
    reliability: Optional[str] = None
    issues: List[str] = field(default_factory=list)


@dataclass
class AdminAnchorsSection:
    summary: str
    anchors: List[AdminAnchorSummary] = field(default_factory=list)


@dataclass
class AdminEvidenceSummary:
    id: str
    type: str
    source: Optional[str] = None
    title: Optional[str] = None
    snippet: Optional[str] = None
    url: Optional[str] = None
    captured_at: Optional[datetime] = None


@dataclass
class AdminEvidenceSection:
    summary: str
    evidences: List[AdminEvidenceSummary] = field(default_factory=list)


@dataclass
class AdminCaseXRay:
    case_id: str
    title: str
    category: Optional[str]
    status: str
    risk: Optional[str]
    summary: str
    debunker: AdminDebunkerSection
    committees: AdminCommitteesSection
    anchors: AdminAnchorsSection
    evidences: AdminEvidenceSection


def to_dict(model: Any) -> Dict[str, Any]:
    """Helper to convert dataclasses (including nested) to plain dicts."""
    return asdict(model)
