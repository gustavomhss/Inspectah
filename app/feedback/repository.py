from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.agents.trace_repository import (
    DEFAULT_DB_PATH,
    MIGRATION_PATH,
    FeedbackOnDecision,
    FeedbackOnTrace,
    _mask_value,
)
from scripts.db.migrate import apply_sql


def _serialize_dt(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt else None


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


class FeedbackRepository:
    """Repositório de FeedbackOnTrace/FeedbackOnDecision com redaction básica."""

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

    def _sanitize_comment(self, text: str) -> str:
        """Previne vazamento de PII simples; aplica máscara se suspeito."""
        if "@" in text or len(text) > 500:
            return _mask_value(text)
        return text

    def record_feedback_on_trace(self, fb: FeedbackOnTrace) -> FeedbackOnTrace:
        comment = self._sanitize_comment(fb.comment)
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO feedback_on_trace (
                    feedback_id, target_type, target_id, authored_by_actor, authored_by_role, origin_surface,
                    feedback_kind, severity, comment, suggested_action, pii_tags, redaction_applied, request_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fb.feedback_id,
                    "trace",
                    fb.target_id,
                    fb.authored_by_actor,
                    fb.authored_by_role,
                    fb.origin_surface,
                    fb.feedback_kind,
                    fb.severity,
                    comment,
                    fb.suggested_action,
                    _json_dumps(fb.pii_tags),
                    int(fb.redaction_applied or comment != fb.comment),
                    fb.request_id,
                    _serialize_dt(fb.created_at),
                ),
            )
            conn.commit()
        return fb

    def record_feedback_on_decision(self, fb: FeedbackOnDecision) -> FeedbackOnDecision:
        comment = self._sanitize_comment(fb.comment)
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO feedback_on_decision (
                    feedback_id, decision_record_id, committee_trace_id, agent_trace_id,
                    authored_by_actor, authored_by_role, origin_surface, feedback_kind, severity,
                    comment, suggested_action, pii_tags, redaction_applied, request_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fb.feedback_id,
                    fb.decision_record_id,
                    fb.committee_trace_id,
                    fb.agent_trace_id,
                    fb.authored_by_actor,
                    fb.authored_by_role,
                    fb.origin_surface,
                    fb.feedback_kind,
                    fb.severity,
                    comment,
                    fb.suggested_action,
                    _json_dumps(fb.pii_tags),
                    int(fb.redaction_applied or comment != fb.comment),
                    fb.request_id,
                    _serialize_dt(fb.created_at),
                ),
            )
            conn.commit()
        return fb

    def list_feedback_for_trace(self, target_id: str) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM feedback_on_trace WHERE target_id=? ORDER BY datetime(created_at) DESC", (target_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    def list_feedback_for_decision(self, decision_record_id: str) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM feedback_on_decision WHERE decision_record_id=? ORDER BY datetime(created_at) DESC",
                (decision_record_id,),
            ).fetchall()
            return [dict(r) for r in rows]
