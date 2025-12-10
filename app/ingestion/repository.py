from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from app.ingestion.errors import ConfigNotFoundError
from app.ingestion.models import (
    IngestionConfig,
    IngestionMode,
    IngestionRun,
    IngestionStatus,
    IngestionTrigger,
)
from scripts.db.migrate import apply_sql

DEFAULT_DB_PATH = Path(os.environ.get("INSPECTAH_S22_DB_PATH", "out/databases/s22_ingestion.sqlite"))
MIGRATION_PATH = Path(__file__).resolve().parents[2] / "db/migrations/022_sprint22_ingestion.sql"


class IngestionRepository:
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

    # Config operations
    def save_config(self, config: IngestionConfig) -> IngestionConfig:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO ingestion_configs (
                    id, source_id, enabled, mode, interval_minutes, max_attempts,
                    timeout_seconds, last_run_id, created_at, updated_at, created_by, updated_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    config.id,
                    config.source_id,
                    1 if config.enabled else 0,
                    config.mode.value,
                    config.interval_minutes,
                    config.max_attempts,
                    config.timeout_seconds,
                    config.last_run_id,
                    config.created_at.isoformat(),
                    config.updated_at.isoformat(),
                    config.created_by,
                    config.updated_by,
                ),
            )
            conn.commit()
        return config

    def get_config(self, source_id: str) -> Optional[IngestionConfig]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM ingestion_configs WHERE source_id=?", (source_id,)).fetchone()
        return _row_to_config(row) if row else None

    def list_configs(self) -> List[IngestionConfig]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM ingestion_configs ORDER BY updated_at DESC").fetchall()
        return [_row_to_config(row) for row in rows]

    def update_config_mode(self, source_id: str, mode: IngestionMode, enabled: bool, updated_by: str) -> IngestionConfig:
        config = self.get_config(source_id)
        if not config:
            raise ConfigNotFoundError(f"Nenhuma config para source {source_id}")
        now = datetime.now(timezone.utc)
        config.mode = mode
        config.enabled = enabled
        config.updated_by = updated_by
        config.updated_at = now
        return self.save_config(config)

    def set_last_run(self, config_id: str, run_id: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE ingestion_configs SET last_run_id=?, updated_at=? WHERE id=?",
                (run_id, datetime.now(timezone.utc).isoformat(), config_id),
            )
            conn.commit()

    # Run operations
    def insert_run(self, run: IngestionRun) -> IngestionRun:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO ingestion_runs (
                    id, config_id, source_id, trigger, status, started_at, finished_at,
                    items_processed, error_code, error_message, payload_ref, meta,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.id,
                    run.config_id,
                    run.source_id,
                    run.trigger.value,
                    run.status.value,
                    run.started_at.isoformat(),
                    run.finished_at.isoformat() if run.finished_at else None,
                    run.items_processed,
                    run.error_code,
                    run.error_message,
                    run.payload_ref,
                    json.dumps(run.meta or {}, ensure_ascii=False),
                    run.created_at.isoformat(),
                    run.updated_at.isoformat(),
                ),
            )
            conn.commit()
        return run

    def update_run(self, run: IngestionRun) -> IngestionRun:
        run.updated_at = datetime.now(timezone.utc)
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE ingestion_runs
                   SET status=?, finished_at=?, items_processed=?, error_code=?, error_message=?,
                       payload_ref=?, meta=?, updated_at=?
                 WHERE id=?
                """,
                (
                    run.status.value,
                    run.finished_at.isoformat() if run.finished_at else None,
                    run.items_processed,
                    run.error_code,
                    run.error_message,
                    run.payload_ref,
                    json.dumps(run.meta or {}, ensure_ascii=False),
                    run.updated_at.isoformat(),
                    run.id,
                ),
            )
            conn.commit()
        return run

    def get_run(self, run_id: str) -> Optional[IngestionRun]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM ingestion_runs WHERE id=?", (run_id,)).fetchone()
        return _row_to_run(row) if row else None

    def list_runs_by_source(self, source_id: str, limit: int = 20, offset: int = 0) -> List[IngestionRun]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM ingestion_runs WHERE source_id=? ORDER BY datetime(started_at) DESC LIMIT ? OFFSET ?",
                (source_id, limit, offset),
            ).fetchall()
        runs = [_row_to_run(row) for row in rows]
        stale_cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
        healed: List[IngestionRun] = []
        for run in runs:
            if run.status == IngestionStatus.RUNNING and run.started_at < stale_cutoff:
                run.status = IngestionStatus.FAIL
                run.error_code = run.error_code or "timeout"
                run.error_message = run.error_message or "Ingestão excedeu o tempo máximo esperado."
                run.finished_at = datetime.now(timezone.utc)
                self.update_run(run)
                healed.append(run)
        if healed:
            # refresh ordering with healed runs updated
            runs = sorted(runs, key=lambda r: r.started_at, reverse=True)
        return runs

    def list_runs_by_source_between(self, source_id: str, start: datetime, end: datetime) -> List[IngestionRun]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM ingestion_runs WHERE source_id=? AND started_at >= ? AND started_at <= ? ORDER BY started_at DESC",
                (source_id, start.isoformat(), end.isoformat()),
            ).fetchall()
        return [_row_to_run(row) for row in rows]

    def count_running_for_source(self, source_id: str) -> int:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM ingestion_runs WHERE source_id=? AND status='RUNNING'", (source_id,)
            ).fetchone()
        return int(row[0]) if row else 0

    # Payload persistence (NDJSON on disk)
    def save_raw_payload(self, run_id: str, source_id: str, items: Iterable[dict], base_dir: Optional[Path] = None) -> str:
        today = datetime.now(timezone.utc)
        root = base_dir or Path(os.environ.get("INSPECTAH_RAW_BASE", "data/ingestion_raw"))
        base = root / source_id / f"{today:%Y}" / f"{today:%m}" / f"{today:%d}"
        base.mkdir(parents=True, exist_ok=True)
        path = base / f"{run_id}.ndjson"
        with path.open("w", encoding="utf-8") as fh:
            for item in items:
                fh.write(json.dumps(item, ensure_ascii=False) + "\n")
        return str(path)

    def load_raw_payload(self, run_id: str, source_id: str, base_dir: Optional[Path] = None) -> List[dict]:
        root = base_dir or Path(os.environ.get("INSPECTAH_RAW_BASE", "data/ingestion_raw"))
        base = root / source_id
        candidates = list(base.glob(f"**/{run_id}.ndjson"))
        if not candidates:
            return []
        path = candidates[0]
        records: List[dict] = []
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except Exception:
                    continue
        return records


def _row_to_config(row: sqlite3.Row) -> IngestionConfig:
    return IngestionConfig(
        id=row["id"],
        source_id=row["source_id"],
        enabled=bool(row["enabled"]),
        mode=IngestionMode(row["mode"]),
        interval_minutes=int(row["interval_minutes"]),
        max_attempts=int(row["max_attempts"]),
        timeout_seconds=int(row["timeout_seconds"]),
        last_run_id=row["last_run_id"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
        created_by=row["created_by"],
        updated_by=row["updated_by"],
    )


def _row_to_run(row: sqlite3.Row) -> IngestionRun:
    return IngestionRun(
        id=row["id"],
        config_id=row["config_id"],
        source_id=row["source_id"],
        trigger=IngestionTrigger(row["trigger"]),
        status=IngestionStatus(row["status"]),
        started_at=datetime.fromisoformat(row["started_at"]),
        finished_at=datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None,
        items_processed=int(row["items_processed"]),
        error_code=row["error_code"],
        error_message=row["error_message"],
        payload_ref=row["payload_ref"],
        meta=json.loads(row["meta"]) if row["meta"] else {},
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )
