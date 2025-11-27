from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from app.debunk.models import (
    DebunkDecision,
    DebunkDecisionType,
    DebunkIssue,
    DebunkIssueEvent,
    DebunkIssueStatus,
    DebunkIssueTarget,
    DebunkRiskLevel,
    DebunkTask,
    DebunkTaskStatus,
    DebunkTaskType,
    RecommendedTruthAction,
)
from scripts.db.migrate import apply_sql

DEFAULT_DB_PATH = Path(os.environ.get("INSPECTAH_S24_DB_PATH", "out/databases/s24_debunk.sqlite"))
MIGRATION_PATH = Path(__file__).resolve().parents[2] / "db" / "migrations" / "025_sprint24_debunk.sql"


def _serialize_dt(dt: datetime) -> str:
    return dt.isoformat()


def _deserialize_dt(raw: str) -> datetime:
    return datetime.fromisoformat(raw)


def gen_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


class DebunkRepository:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self._ensure_db()

    def _ensure_db(self) -> None:
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

    # Issues
    def create_issue(self, issue: DebunkIssue) -> DebunkIssue:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO debunk_issues (
                    id, target_type, target_id, question, reason, risk_level, priority,
                    status, origin, opened_by, created_at, updated_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    issue.id,
                    issue.target_type.value,
                    issue.target_id,
                    issue.question,
                    issue.reason,
                    issue.risk_level.value,
                    issue.priority,
                    issue.status.value,
                    issue.origin,
                    issue.opened_by,
                    _serialize_dt(issue.created_at),
                    _serialize_dt(issue.updated_at),
                    json.dumps(issue.metadata, ensure_ascii=False),
                ),
            )
            conn.commit()
        return issue

    def update_issue(self, issue: DebunkIssue) -> DebunkIssue:
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE debunk_issues SET
                    question=?, reason=?, risk_level=?, priority=?, status=?, origin=?, opened_by=?, updated_at=?, metadata=?
                WHERE id=?
                """,
                (
                    issue.question,
                    issue.reason,
                    issue.risk_level.value,
                    issue.priority,
                    issue.status.value,
                    issue.origin,
                    issue.opened_by,
                    _serialize_dt(issue.updated_at),
                    json.dumps(issue.metadata, ensure_ascii=False),
                    issue.id,
                ),
            )
            conn.commit()
        return issue

    def get_issue(self, issue_id: str) -> Optional[DebunkIssue]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM debunk_issues WHERE id=?", (issue_id,)).fetchone()
        return self._row_to_issue(row) if row else None

    def find_open_issue_for_target(self, target_type: DebunkIssueTarget, target_id: str) -> Optional[DebunkIssue]:
        open_statuses = (
            DebunkIssueStatus.OPEN.value,
            DebunkIssueStatus.TRIAGED.value,
            DebunkIssueStatus.IN_REVIEW.value,
            DebunkIssueStatus.PENDING_ADDITIONAL_EVIDENCE.value,
            DebunkIssueStatus.READY_FOR_DECISION.value,
            DebunkIssueStatus.ESCALATED.value,
        )
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT * FROM debunk_issues
                WHERE target_type=? AND target_id=? AND status IN ({})
                ORDER BY datetime(created_at) ASC
                """.format(",".join("?" * len(open_statuses))),
                (target_type.value, target_id, *open_statuses),
            ).fetchone()
        return self._row_to_issue(row) if row else None

    def list_issues(self, statuses: Optional[Sequence[DebunkIssueStatus]] = None) -> List[DebunkIssue]:
        query = "SELECT * FROM debunk_issues WHERE 1=1"
        params: list = []
        if statuses:
            query += " AND status IN ({})".format(",".join("?" * len(statuses)))
            params.extend([s.value for s in statuses])
        query += " ORDER BY priority DESC, datetime(created_at) ASC"
        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_issue(r) for r in rows]

    # Tasks
    def create_task(self, task: DebunkTask) -> DebunkTask:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO debunk_tasks (id, issue_id, task_type, instructions, status, assigned_to, result, created_at, updated_at, due_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.id,
                    task.issue_id,
                    task.task_type.value,
                    task.instructions,
                    task.status.value,
                    task.assigned_to,
                    task.result,
                    _serialize_dt(task.created_at),
                    _serialize_dt(task.updated_at),
                    _serialize_dt(task.due_at) if task.due_at else None,
                ),
            )
            conn.commit()
        return task

    def list_tasks(self, issue_id: str) -> List[DebunkTask]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM debunk_tasks WHERE issue_id=? ORDER BY datetime(created_at)", (issue_id,)).fetchall()
        return [self._row_to_task(r) for r in rows]

    def update_task(self, task: DebunkTask) -> DebunkTask:
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE debunk_tasks SET status=?, assigned_to=?, result=?, updated_at=?, due_at=?
                WHERE id=?
                """,
                (
                    task.status.value,
                    task.assigned_to,
                    task.result,
                    _serialize_dt(task.updated_at),
                    _serialize_dt(task.due_at) if task.due_at else None,
                    task.id,
                ),
            )
            conn.commit()
        return task

    # Decisions
    def record_decision(self, decision: DebunkDecision) -> DebunkDecision:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO debunk_decisions (
                    id, issue_id, decision_type, confidence, rationale, recommended_truth_action,
                    evidence_refs, residual_uncertainties, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision.id,
                    decision.issue_id,
                    decision.decision_type.value,
                    decision.confidence,
                    decision.rationale,
                    decision.recommended_truth_action.value,
                    json.dumps(decision.evidence_refs, ensure_ascii=False),
                    json.dumps(decision.residual_uncertainties, ensure_ascii=False),
                    decision.created_by,
                    _serialize_dt(decision.created_at),
                ),
            )
            conn.commit()
        return decision

    def list_decisions(self, issue_id: str) -> List[DebunkDecision]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM debunk_decisions WHERE issue_id=? ORDER BY datetime(created_at)", (issue_id,)).fetchall()
        return [self._row_to_decision(r) for r in rows]

    # Events
    def append_event(self, event: DebunkIssueEvent) -> DebunkIssueEvent:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO debunk_issue_events (id, issue_id, event_type, payload, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.issue_id,
                    event.event_type,
                    json.dumps(event.payload, ensure_ascii=False),
                    event.created_by,
                    _serialize_dt(event.created_at),
                ),
            )
            conn.commit()
        return event

    def list_events(self, issue_id: str) -> List[DebunkIssueEvent]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM debunk_issue_events WHERE issue_id=? ORDER BY datetime(created_at)", (issue_id,)
            ).fetchall()
        return [self._row_to_event(r) for r in rows]

    # Helpers
    def _row_to_issue(self, row: sqlite3.Row) -> DebunkIssue:
        return DebunkIssue(
            id=row["id"],
            target_type=DebunkIssueTarget(row["target_type"]),
            target_id=row["target_id"],
            question=row["question"],
            reason=row["reason"],
            risk_level=DebunkRiskLevel(row["risk_level"]),
            priority=int(row["priority"]),
            status=DebunkIssueStatus(row["status"]),
            origin=row["origin"],
            opened_by=row["opened_by"],
            created_at=_deserialize_dt(row["created_at"]),
            updated_at=_deserialize_dt(row["updated_at"]),
            metadata=json.loads(row["metadata"] or "{}"),
        )

    def _row_to_task(self, row: sqlite3.Row) -> DebunkTask:
        return DebunkTask(
            id=row["id"],
            issue_id=row["issue_id"],
            task_type=DebunkTaskType(row["task_type"]),
            instructions=row["instructions"],
            status=DebunkTaskStatus(row["status"]),
            assigned_to=row["assigned_to"],
            result=row["result"],
            created_at=_deserialize_dt(row["created_at"]),
            updated_at=_deserialize_dt(row["updated_at"]),
            due_at=_deserialize_dt(row["due_at"]) if row["due_at"] else None,
        )

    def _row_to_decision(self, row: sqlite3.Row) -> DebunkDecision:
        return DebunkDecision(
            id=row["id"],
            issue_id=row["issue_id"],
            decision_type=DebunkDecisionType(row["decision_type"]),
            confidence=row["confidence"],
            rationale=row["rationale"],
            recommended_truth_action=RecommendedTruthAction(row["recommended_truth_action"]),
            evidence_refs=json.loads(row["evidence_refs"] or "[]"),
            residual_uncertainties=json.loads(row["residual_uncertainties"] or "[]"),
            created_by=row["created_by"],
            created_at=_deserialize_dt(row["created_at"]),
        )

    def _row_to_event(self, row: sqlite3.Row) -> DebunkIssueEvent:
        return DebunkIssueEvent(
            id=row["id"],
            issue_id=row["issue_id"],
            event_type=row["event_type"],
            payload=json.loads(row["payload"] or "{}"),
            created_by=row["created_by"],
            created_at=_deserialize_dt(row["created_at"]),
        )

    def queue_snapshot(self) -> List[Tuple[int, DebunkIssue]]:
        """Return prioritized issues for queue consumption."""
        issues = self.list_issues(
            statuses=[
                DebunkIssueStatus.OPEN,
                DebunkIssueStatus.TRIAGED,
                DebunkIssueStatus.IN_REVIEW,
                DebunkIssueStatus.PENDING_ADDITIONAL_EVIDENCE,
                DebunkIssueStatus.READY_FOR_DECISION,
            ]
        )
        weights = {
            DebunkRiskLevel.CRITICAL: 100,
            DebunkRiskLevel.HIGH: 50,
            DebunkRiskLevel.MEDIUM: 20,
            DebunkRiskLevel.LOW: 10,
        }
        scored = []
        for issue in issues:
            score = weights.get(issue.risk_level, 0) - max(0, 10 - issue.priority)
            scored.append((score, issue))
        scored.sort(key=lambda pair: (-pair[0], pair[1].created_at))
        return scored
