from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from app.flows.models import FlowVersion


class FlowVersioning:
    def __init__(self, conn: sqlite3.Connection, limits: Dict):
        self.conn = conn
        self.limits = limits

    def create_version(self, flow_id: str, template_slug: str, version_id: str, estado: str = "ativo") -> FlowVersion:
        ver_row = self.conn.execute(
            "SELECT id FROM flow_flow_versions WHERE flow_id=? AND version_id=?", (flow_id, version_id)
        ).fetchone()
        if ver_row:
            version_pk = ver_row["id"]
        else:
            version_pk = f"ver_{flow_id[:6]}_{version_id}"
            self.conn.execute(
                """
                INSERT INTO flow_flow_versions (id, flow_id, version_id, template_slug, estado, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, '{}', datetime('now'), datetime('now'))
                """,
                (version_pk, flow_id, version_id, template_slug, estado),
            )
        self._enforce_version_retention(flow_id)
        row = self.conn.execute("SELECT * FROM flow_flow_versions WHERE id=?", (version_pk,)).fetchone()
        return self._row_to_version(row)

    def set_version_state(self, version_id: str, estado: str) -> None:
        self.conn.execute(
            "UPDATE flow_flow_versions SET estado=?, updated_at=datetime('now') WHERE id=?",
            (estado, version_id),
        )

    def _row_to_version(self, row) -> FlowVersion:
        return FlowVersion(
            id=row["id"],
            flow_id=row["flow_id"],
            version_id=row["version_id"],
            template_slug=row["template_slug"],
            estado=row["estado"],
            metadata={},
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def _enforce_version_retention(self, flow_id: str) -> None:
        max_versions = int(self.limits.get("max_versions_to_keep", 10))
        rows = self.conn.execute(
            "SELECT id FROM flow_flow_versions WHERE flow_id=? ORDER BY created_at DESC", (flow_id,)
        ).fetchall()
        if len(rows) <= max_versions:
            return
        for row in rows[max_versions:]:
            self.conn.execute("DELETE FROM flow_flow_versions WHERE id=?", (row["id"],))


def count_rollbacks_last_hour(conn: sqlite3.Connection, flow_id: str) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
    rows = conn.execute(
        "SELECT created_at FROM flow_flow_operation_logs WHERE flow_id=? AND operacao='rollback'",
        (flow_id,),
    ).fetchall()
    total = 0
    for r in rows:
        try:
            ts = datetime.fromisoformat(r["created_at"])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts >= cutoff:
                total += 1
        except Exception:
            continue
    return total
