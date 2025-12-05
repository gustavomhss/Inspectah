from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


class IncidentState:
    OPEN = "OPEN"
    TRIAGE = "TRIAGE"
    MITIGATING = "MITIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    TERMINAL = {RESOLVED, CLOSED}


class IncidentSeverity:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    ALL = {LOW, MEDIUM, HIGH, CRITICAL}


ALLOWED_TRANSITIONS = {
    IncidentState.OPEN: {IncidentState.TRIAGE, IncidentState.MITIGATING},
    IncidentState.TRIAGE: {IncidentState.MITIGATING, IncidentState.RESOLVED},
    IncidentState.MITIGATING: {IncidentState.RESOLVED},
    IncidentState.RESOLVED: {IncidentState.CLOSED},
    IncidentState.CLOSED: set(),
}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Incident:
    id: str
    title: str
    description: str
    severity: str
    state: str = IncidentState.OPEN
    component_id: str | None = None
    slo_ids: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=utcnow)
    updated_at: str = field(default_factory=utcnow)
    resolved_at: Optional[str] = None
    closed_at: Optional[str] = None


class IncidentService:
    """Simple SQLite-backed Incident service (atualizado para S34)."""

    def __init__(self, db_path: Path | str = "out/databases/s34_ops.sqlite"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _ensure_schema(self):
        # schema created by migration, but ensure for tests
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS ops_incidents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    state TEXT NOT NULL,
                    component_id TEXT,
                    slo_ids TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    resolved_at TEXT,
                    closed_at TEXT
                );
                """
            )

    def create_incident(self, incident: Incident) -> Incident:
        if incident.severity not in IncidentSeverity.ALL:
            raise ValueError("severity inválida")
        if incident.state != IncidentState.OPEN:
            raise ValueError("novo incidente deve iniciar em OPEN")
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO ops_incidents (id, title, description, severity, state, component_id, slo_ids, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?)
                """,
                (
                    incident.id,
                    incident.title,
                    incident.description,
                    incident.severity,
                    incident.state,
                    incident.component_id,
                    ",".join(incident.slo_ids),
                    incident.created_at,
                    incident.updated_at,
                ),
            )
        return incident

    def get(self, incident_id: str) -> Optional[Incident]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM ops_incidents WHERE id=?", (incident_id,)).fetchone()
        if not row:
            return None
        return Incident(
            id=row[0],
            title=row[1],
            description=row[2],
            severity=row[3],
            state=row[4],
            component_id=row[5],
            slo_ids=row[6].split(",") if row[6] else [],
            created_at=row[7],
            updated_at=row[8],
            resolved_at=row[9],
            closed_at=row[10],
        )

    def transition(self, incident_id: str, new_state: str) -> Incident:
        incident = self.get(incident_id)
        if not incident:
            raise ValueError("incidente não encontrado")
        if new_state not in ALLOWED_TRANSITIONS.get(incident.state, set()):
            raise ValueError(f"transição inválida {incident.state} -> {new_state}")
        now = utcnow()
        resolved_at = incident.resolved_at
        closed_at = incident.closed_at
        if new_state == IncidentState.RESOLVED:
            resolved_at = now
        if new_state == IncidentState.CLOSED:
            closed_at = now
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE ops_incidents
                SET state=?, updated_at=?, resolved_at=?, closed_at=?
                WHERE id=?
                """,
                (new_state, now, resolved_at, closed_at, incident_id),
            )
        incident.state = new_state
        incident.updated_at = now
        incident.resolved_at = resolved_at
        incident.closed_at = closed_at
        return incident
