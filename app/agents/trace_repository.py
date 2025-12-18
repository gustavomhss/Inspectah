from __future__ import annotations

import json
import logging
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from app.truth.models import (
    TraceLinkRefs,
    gen_agent_trace_id,
    gen_committee_trace_id,
    gen_feedback_id,
    gen_reasoning_step_id,
    utcnow,
)
from scripts.db.migrate import apply_sql

logger = logging.getLogger(__name__)

TRACE_SCHEMA_VERSION = "trace_schema_v1"
DEFAULT_DB_PATH = Path(os.environ.get("INSPECTAH_S36_TRACE_DB_PATH", "out/databases/s36_traces.sqlite"))
MIGRATION_PATH = Path(__file__).resolve().parents[2] / "db/migrations/026_sprint36_traces.sql"

# Campos que não podem ser persistidos para evitar vazamento de PII.
PII_BLOCKLIST_FIELDS = {"raw_input", "raw_output", "llm_prompt", "llm_response", "user_email", "ip", "session_id"}


def _mask_value(value: Any) -> str:
    return "[REDACTED]" if value is not None else ""


def _serialize_dt(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt else None


def _deserialize_dt(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    return datetime.fromisoformat(raw)


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def _json_loads(raw: Optional[str]) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        logger.debug("Failed to parse JSON, using None fallback", exc_info=True)
        return None
        


@dataclass
class ReasoningStep:
    step_id: str = field(default_factory=gen_reasoning_step_id)
    order: int = 0
    actor_role: Optional[str] = None
    step_kind: Optional[str] = None
    summary: str = ""
    input_refs: List[Any] = field(default_factory=list)
    output_refs: List[Any] = field(default_factory=list)
    evidence_refs: List[Dict[str, Any]] = field(default_factory=list)
    confidence: Optional[float] = None
    elapsed_ms: Optional[int] = None
    request_id: Optional[str] = None
    redaction_applied: bool = False
    created_at: datetime = field(default_factory=utcnow)
    # Campos brutos opcionais (serão removidos/mascarados)
    raw_input: Optional[str] = None
    raw_output: Optional[str] = None
    full_prompt: Optional[str] = None
    tool_calls: Optional[List[Any]] = None


@dataclass
class AgentTrace:
    agent_trace_id: str = field(default_factory=gen_agent_trace_id)
    truth_record_id: Optional[str] = None
    decision_record_id: Optional[str] = None
    claim_id: Optional[str] = None
    domain: str = "unknown"
    risk_level: Optional[str] = None
    agent_run_id: Optional[str] = None
    committee_trace_id: Optional[str] = None
    trace_schema_version: str = TRACE_SCHEMA_VERSION
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    steps: List[ReasoningStep] = field(default_factory=list)
    input_hash: Optional[str] = None
    redaction_applied: bool = False
    request_id: Optional[str] = None
    created_at: datetime = field(default_factory=utcnow)
    supersedes_trace_id: Optional[str] = None


@dataclass
class CommitteeTrace:
    committee_trace_id: str = field(default_factory=gen_committee_trace_id)
    committee_id: Optional[str] = None
    committee_version: Optional[str] = None
    truth_record_id: Optional[str] = None
    decision_record_id: Optional[str] = None
    claim_id: Optional[str] = None
    agent_trace_ids: List[str] = field(default_factory=list)
    summary: str = ""
    domain: str = "unknown"
    risk_level: Optional[str] = None
    trace_schema_version: str = TRACE_SCHEMA_VERSION
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    redaction_applied: bool = False
    request_id: Optional[str] = None
    created_at: datetime = field(default_factory=utcnow)
    supersedes_trace_id: Optional[str] = None


@dataclass
class FeedbackOnTrace:
    feedback_id: str = field(default_factory=lambda: gen_feedback_id("ft"))
    target_id: str = ""
    authored_by_actor: Optional[str] = None
    authored_by_role: Optional[str] = None
    origin_surface: Optional[str] = None
    feedback_kind: Optional[str] = None
    severity: Optional[str] = None
    comment: str = ""
    suggested_action: Optional[str] = None
    pii_tags: List[str] = field(default_factory=list)
    redaction_applied: bool = False
    request_id: Optional[str] = None
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class FeedbackOnDecision:
    feedback_id: str = field(default_factory=lambda: gen_feedback_id("fd"))
    decision_record_id: str = ""
    committee_trace_id: Optional[str] = None
    agent_trace_id: Optional[str] = None
    authored_by_actor: Optional[str] = None
    authored_by_role: Optional[str] = None
    origin_surface: Optional[str] = None
    feedback_kind: Optional[str] = None
    severity: Optional[str] = None
    comment: str = ""
    suggested_action: Optional[str] = None
    pii_tags: List[str] = field(default_factory=list)
    redaction_applied: bool = False
    request_id: Optional[str] = None
    created_at: datetime = field(default_factory=utcnow)


class TraceRepository:
    """
    Repositório S36 para AgentTrace/CommitteeTrace/ReasoningStep (SQLite).
    Aplica redaction básica para campos sensíveis e garante schema trace_schema_v1.
    """

    def __init__(self, db_path: Path | None = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        apply_sql(MIGRATION_PATH, self.db_path)

    @contextmanager
    def _conn(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _sanitize_text_fields(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        redacted = False
        for field_name in list(payload.keys()):
            if field_name in PII_BLOCKLIST_FIELDS:
                payload[field_name] = _mask_value(payload[field_name])
                redacted = True
        if redacted:
            payload["redaction_applied"] = True
        return payload

    def _sanitize_step(self, step: ReasoningStep) -> ReasoningStep:
        payload = step.__dict__.copy()
        payload = self._sanitize_text_fields(payload)
        sanitized = replace(
            step,
            raw_input=None,
            raw_output=None,
            full_prompt=None,
            tool_calls=None,
            redaction_applied=payload.get("redaction_applied", step.redaction_applied),
        )
        return sanitized

    def save_agent_trace(self, trace: AgentTrace) -> AgentTrace:
        sanitized_steps = [self._sanitize_step(s) for s in trace.steps]
        trace = replace(trace, steps=sanitized_steps)
        steps_payload = [
            {
                "id": s.step_id,
                "order": s.order,
                "summary": s.summary,
                "step_kind": s.step_kind,
            }
            for s in sanitized_steps
        ]
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO agent_traces (
                    agent_trace_id, agent_run_id, committee_trace_id, truth_record_id, decision_record_id, claim_id,
                    domain, risk_level, trace_schema_version, started_at, finished_at, duration_ms,
                    steps_json, input_hash, redaction_applied, request_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trace.agent_trace_id,
                    trace.agent_run_id,
                    trace.committee_trace_id,
                    trace.truth_record_id,
                    trace.decision_record_id,
                    trace.claim_id,
                    trace.domain,
                    trace.risk_level,
                    trace.trace_schema_version,
                    _serialize_dt(trace.started_at),
                    _serialize_dt(trace.finished_at),
                    trace.duration_ms,
                    _json_dumps(steps_payload),
                    trace.input_hash,
                    int(trace.redaction_applied),
                    trace.request_id,
                    _serialize_dt(trace.created_at),
                ),
            )
            conn.execute("DELETE FROM reasoning_steps WHERE agent_trace_id=?", (trace.agent_trace_id,))
            for s in sanitized_steps:
                conn.execute(
                    """
                    INSERT INTO reasoning_steps (
                        step_id, agent_trace_id, order_index, actor_role, step_kind, summary,
                        input_refs, output_refs, evidence_refs, confidence, elapsed_ms, request_id,
                        redaction_applied, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        s.step_id,
                        trace.agent_trace_id,
                        s.order,
                        s.actor_role,
                        s.step_kind,
                        s.summary,
                        _json_dumps(s.input_refs),
                        _json_dumps(s.output_refs),
                        _json_dumps(s.evidence_refs),
                        s.confidence,
                        s.elapsed_ms,
                        s.request_id,
                        int(s.redaction_applied),
                        _serialize_dt(s.created_at),
                    ),
                )
            conn.commit()
        return trace

    def save_committee_trace(self, ct: CommitteeTrace) -> CommitteeTrace:
        ct = replace(ct, redaction_applied=ct.redaction_applied or False)
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO committee_traces (
                    committee_trace_id, committee_id, committee_version, truth_record_id, decision_record_id, claim_id,
                    agent_trace_ids, summary, domain, risk_level, trace_schema_version, started_at, finished_at,
                    duration_ms, redaction_applied, request_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ct.committee_trace_id,
                    ct.committee_id,
                    ct.committee_version,
                    ct.truth_record_id,
                    ct.decision_record_id,
                    ct.claim_id,
                    _json_dumps(ct.agent_trace_ids),
                    ct.summary,
                    ct.domain,
                    ct.risk_level,
                    ct.trace_schema_version,
                    _serialize_dt(ct.started_at),
                    _serialize_dt(ct.finished_at),
                    ct.duration_ms,
                    int(ct.redaction_applied),
                    ct.request_id,
                    _serialize_dt(ct.created_at),
                ),
            )
            conn.commit()
        return ct

    def list_traces_by_decision(self, decision_record_id: str) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM agent_traces WHERE decision_record_id=? ORDER BY datetime(created_at) DESC",
                (decision_record_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def list_traces_by_claim(self, claim_id: str) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM agent_traces WHERE claim_id=? ORDER BY datetime(created_at) DESC",
                (claim_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def list_recent(self, domain: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        clauses: list[str] = []
        params: list = []
        if domain:
            clauses.append("domain=?")
            params.append(domain)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"SELECT * FROM agent_traces {where} ORDER BY datetime(created_at) DESC LIMIT ?"
        params.append(limit)
        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
            items: List[Dict[str, Any]] = []
            for r in rows:
                data = dict(r)
                step_ids = _json_loads(data.get("steps_json")) or []
                data["steps_count"] = len(step_ids) if isinstance(step_ids, list) else 0
                data["step_ids"] = step_ids if isinstance(step_ids, list) else []
                items.append(data)
            return items

    def list_committee_traces(self, decision_record_id: str) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM committee_traces WHERE decision_record_id=? ORDER BY datetime(created_at) DESC",
                (decision_record_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def list_steps_for_trace(self, agent_trace_id: str) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM reasoning_steps WHERE agent_trace_id=? ORDER BY order_index",
                (agent_trace_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_trace(self, agent_trace_id: str) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM agent_traces WHERE agent_trace_id=? LIMIT 1",
                (agent_trace_id,),
            ).fetchone()
            return dict(row) if row else None

    def build_trace_from_links(
        self,
        links: TraceLinkRefs,
        *,
        agent_run_id: Optional[str] = None,
        committee_trace_id: Optional[str] = None,
        steps: Optional[Iterable[ReasoningStep]] = None,
        input_hash: Optional[str] = None,
        risk_level: Optional[str] = None,
    ) -> AgentTrace:
        return AgentTrace(
            truth_record_id=links.truth_record_id,
            decision_record_id=links.decision_record_id,
            claim_id=links.claim_id,
            domain=links.domain or "unknown",
            risk_level=risk_level or links.risk_level,
            agent_run_id=agent_run_id,
            committee_trace_id=committee_trace_id,
            steps=list(steps or []),
            input_hash=input_hash,
            request_id=links.request_id,
        )
