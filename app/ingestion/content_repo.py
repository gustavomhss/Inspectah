from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "out/databases/s31_content.sqlite"


def _serialize(payload) -> str:
    return json.dumps(payload or {}, ensure_ascii=False)


def _deserialize(payload: Optional[str]):
    if payload is None:
        return {}
    try:
        return json.loads(payload)
    except (json.JSONDecodeError, TypeError, ValueError):
        return {}


class ContentRepository:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
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

    def _ensure_schema(self) -> None:
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS content_items (
                    content_id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    title TEXT,
                    text TEXT,
                    url TEXT NOT NULL,
                    published_at TEXT,
                    language TEXT,
                    country TEXT,
                    provider_id TEXT,
                    profile_id TEXT,
                    categories TEXT,
                    tags TEXT,
                    payload TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_content_url ON content_items(url);
                CREATE INDEX IF NOT EXISTS idx_content_provider_profile ON content_items(provider_id, profile_id);
                """
            )

    def save_items(self, items: List[Dict]) -> int:
        """Save items using bulk insert for better performance."""
        if not items:
            return 0

        now = datetime.now(timezone.utc).isoformat()

        # Prepare all data for bulk insert
        data = [
            (
                item.get("content_id"),
                item.get("kind"),
                item.get("title"),
                item.get("text"),
                item.get("url"),
                item.get("published_at"),
                item.get("language"),
                item.get("country"),
                item.get("provider_id"),
                item.get("profile_id"),
                _serialize(item.get("categories", [])),
                _serialize(item.get("tags", [])),
                _serialize(item.get("payload")),
                now,
            )
            for item in items
        ]

        with self._conn() as conn:
            cursor = conn.executemany(
                """
                INSERT OR IGNORE INTO content_items (
                    content_id, kind, title, text, url, published_at, language, country,
                    provider_id, profile_id, categories, tags, payload, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                data,
            )
            conn.commit()
            return cursor.rowcount if cursor.rowcount > 0 else len(items)

    def list_items(self, limit: int = 20) -> List[Dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM content_items ORDER BY datetime(created_at) DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "content_id": r["content_id"],
                "kind": r["kind"],
                "title": r["title"],
                "text": r["text"],
                "url": r["url"],
                "published_at": r["published_at"],
                "language": r["language"],
                "country": r["country"],
                "provider_id": r["provider_id"],
                "profile_id": r["profile_id"],
                "categories": _deserialize(r["categories"]),
                "tags": _deserialize(r["tags"]),
                "payload": _deserialize(r["payload"]),
                "created_at": r["created_at"],
            }
            for r in rows
        ]
