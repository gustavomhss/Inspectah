from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from app.incidents.models import Incident


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class IncidentRepository:
    def __init__(self, db_path: Path | None = None):
        resolved = db_path or Path(os.environ.get("INSPECTAH_S25_TRUTH_DB_PATH", "out/databases/s25_truth.sqlite"))
        self.db_path = Path(resolved)
        self._ensure_schema()

    @contextmanager
    def _conn(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _ensure_schema(self):
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    ref_truth_record_id TEXT,
                    ref_case_id TEXT,
                    signals TEXT,
                    summary TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            conn.commit()

    def upsert(self, incident: Incident) -> Incident:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO incidents (
                    id, type, domain, severity, status, ref_truth_record_id, ref_case_id,
                    signals, summary, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    incident.id,
                    incident.type,
                    incident.domain,
                    incident.severity,
                    incident.status,
                    incident.ref_truth_record_id,
                    incident.ref_case_id,
                    json.dumps(incident.threat_signals, ensure_ascii=False),
                    incident.summary,
                    incident.created_at,
                    incident.updated_at,
                ),
            )
            conn.commit()
        return incident

    def list(self, status: Optional[str] = None, domain: Optional[str] = None, severity: Optional[str] = None) -> List[Incident]:
        clauses = []
        params: list[str] = []
        if status:
            clauses.append("status=?")
            params.append(status)
        if domain:
            clauses.append("domain=?")
            params.append(domain)
        if severity:
            clauses.append("severity=?")
            params.append(severity)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"SELECT * FROM incidents {where} ORDER BY datetime(created_at) DESC"
        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_incident(r) for r in rows]

    def get(self, incident_id: str) -> Optional[Incident]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM incidents WHERE id=?", (incident_id,)).fetchone()
        return self._row_to_incident(row) if row else None

    def update_status(self, incident_id: str, new_status: str) -> Optional[Incident]:
        inc = self.get(incident_id)
        if not inc:
            return None
        inc.status = new_status
        inc.updated_at = utcnow()
        return self.upsert(inc)

    def _row_to_incident(self, row) -> Incident:
        return Incident(
            id=row["id"],
            title=row["summary"] or row["id"],
            summary=row["summary"] or "",
            domain=row["domain"],
            severity=row["severity"],
            status=row["status"],
            related_claims=[],
            threat_signals=json.loads(row["signals"] or "[]"),
            created_at=row["created_at"],
        )


def gen_incident_id() -> str:
    return f"inc_{uuid4().hex[:10]}"


def create_incident_from_signal(
    signal: dict,
    domain: str,
    summary: str,
    ref_truth_record_id: str | None = None,
    ref_case_id: str | None = None,
    repo: Optional[IncidentRepository] = None,
) -> Incident:
    repository = repo or IncidentRepository()
    incident = Incident(
        id=gen_incident_id(),
        title=summary,
        summary=summary,
        domain=domain,
        severity=signal.get("severity", "medium"),
        status="OPEN",
        related_claims=[],
        threat_signals=[signal],
        created_at=utcnow(),
    )
    incident.ref_truth_record_id = ref_truth_record_id
    incident.ref_case_id = ref_case_id
    return repository.upsert(incident)
