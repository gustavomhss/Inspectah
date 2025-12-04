from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.providers.models import IngestionProfile, ProfileKind, Provider, ProviderKind, ProviderStatus
from migrations.versions import _0032_s31_providers as mig  # type: ignore

DEFAULT_DB_PATH = mig.DEFAULT_DB_PATH


def _deserialize(payload: Optional[str]):
    if payload is None:
        return {}
    try:
        return json.loads(payload)
    except Exception:
        return {}


class ProviderService:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH

    @contextmanager
    def _conn(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        mig.apply_migration(self.db_path)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def list_providers(self) -> List[Provider]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM providers ORDER BY updated_at DESC").fetchall()
        return [_row_to_provider(r) for r in rows]

    def get_provider(self, provider_id: str) -> Optional[Provider]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM providers WHERE id=?", (provider_id,)).fetchone()
        return _row_to_provider(row) if row else None

    def save_provider(self, provider: Provider) -> Provider:
        now = datetime.utcnow().isoformat()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO providers (
                    id, name, kind, description, auth, config, limits, status,
                    created_at, updated_at, created_by, updated_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    provider.id,
                    provider.name,
                    provider.kind.value,
                    provider.description,
                    json.dumps(provider.auth or {}, ensure_ascii=False),
                    json.dumps(provider.config or {}, ensure_ascii=False),
                    json.dumps(provider.limits or {}, ensure_ascii=False),
                    provider.status.value,
                    provider.created_at.isoformat(),
                    now,
                    provider.created_by,
                    provider.updated_by or provider.created_by,
                ),
            )
            conn.commit()
        provider.updated_at = datetime.fromisoformat(now.replace("Z", "+00:00") if "Z" in now else now)
        return provider

    def list_profiles(self) -> List[IngestionProfile]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM ingestion_profiles ORDER BY updated_at DESC").fetchall()
        return [_row_to_profile(r) for r in rows]

    def get_profile(self, profile_id: str) -> Optional[IngestionProfile]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM ingestion_profiles WHERE id=?", (profile_id,)).fetchone()
        return _row_to_profile(row) if row else None

    def save_profile(self, profile: IngestionProfile) -> IngestionProfile:
        now = datetime.utcnow().isoformat()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO ingestion_profiles (
                    id, provider_id, name, slug, kind, country, language, categories, keywords,
                    filters, frequency_minutes, budget_daily_calls, budget_monthly_calls,
                    enabled, status, metadata, created_at, updated_at, created_by, updated_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile.id,
                    profile.provider_id,
                    profile.name,
                    profile.slug,
                    profile.kind.value,
                    profile.country,
                    profile.language,
                    json.dumps(profile.categories or [], ensure_ascii=False),
                    json.dumps(profile.keywords or [], ensure_ascii=False),
                    json.dumps(profile.filters or {}, ensure_ascii=False),
                    profile.frequency_minutes,
                    profile.budget_daily_calls,
                    profile.budget_monthly_calls,
                    1 if profile.enabled else 0,
                    profile.status.value,
                    json.dumps(profile.metadata or {}, ensure_ascii=False),
                    profile.created_at.isoformat(),
                    now,
                    profile.created_by,
                    profile.updated_by or profile.created_by,
                ),
            )
            conn.commit()
        profile.updated_at = datetime.fromisoformat(now.replace("Z", "+00:00") if "Z" in now else now)
        return profile


def _row_to_provider(row: sqlite3.Row) -> Provider:
    return Provider(
        id=row["id"],
        name=row["name"],
        kind=ProviderKind(row["kind"]),
        description=row["description"] or "",
        auth=_deserialize(row["auth"]),
        config=_deserialize(row["config"]),
        limits=_deserialize(row["limits"]),
        status=ProviderStatus(row["status"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
        created_by=row["created_by"],
        updated_by=row["updated_by"],
    )


def _row_to_profile(row: sqlite3.Row) -> IngestionProfile:
    return IngestionProfile(
        id=row["id"],
        provider_id=row["provider_id"],
        name=row["name"],
        slug=row["slug"],
        kind=ProfileKind(row["kind"]),
        country=row["country"],
        language=row["language"],
        categories=json.loads(row["categories"]) if row["categories"] else [],
        keywords=json.loads(row["keywords"]) if row["keywords"] else [],
        filters=_deserialize(row["filters"]),
        frequency_minutes=row["frequency_minutes"],
        budget_daily_calls=row["budget_daily_calls"],
        budget_monthly_calls=row["budget_monthly_calls"],
        enabled=bool(row["enabled"]),
        status=ProviderStatus(row["status"]),
        metadata=_deserialize(row["metadata"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
        created_by=row["created_by"],
        updated_by=row["updated_by"],
    )
