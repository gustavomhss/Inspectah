"""
Sprint 31 — Seeds iniciais de providers/perfis piloto.
"""

from __future__ import annotations

import importlib
import json
import sqlite3
from pathlib import Path

base = importlib.import_module("migrations.versions.0032_s31_providers")
DB_PATH = base.DEFAULT_DB_PATH  # Reuse same DB


def seed() -> None:
    base.apply_migration(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        now = "2025-12-04T00:00:00Z"
        providers = [
            (
                "prov_news_default",
                "Default News Provider",
                "news_provider",
                "Provider piloto BR/PT",
                json.dumps({"api_key": "demo_news_key"}),
                json.dumps({"base_url": "https://news-api.local", "region": "BR"}),
                json.dumps({"daily_calls": 1000}),
                "active",
                now,
                now,
                "planner",
                "planner",
            ),
            (
                "prov_social_default",
                "Default Social Provider",
                "social_provider",
                "Provider piloto social",
                json.dumps({"api_key": "demo_social_key"}),
                json.dumps({"base_url": "https://social-api.local", "region": "BR"}),
                json.dumps({"daily_calls": 500}),
                "active",
                now,
                now,
                "planner",
                "planner",
            ),
        ]
        profiles = [
            (
                "prof_br_pt_hard_news",
                "prov_news_default",
                "BR/PT Hard News",
                "br_pt_hard_news",
                "news",
                "BR",
                "pt",
                json.dumps(["politics", "economy"]),
                json.dumps(["governo", "eleição", "economia"]),
                json.dumps({"country": "BR", "language": "pt"}),
                60,
                500,
                10000,
                1,
                "active",
                json.dumps({"pilot": True}),
                now,
                now,
                "planner",
                "planner",
            ),
            (
                "prof_latam_es_politics",
                "prov_news_default",
                "Latam ES Politics",
                "latam_es_politics",
                "news",
                "LATAM",
                "es",
                json.dumps(["politics"]),
                json.dumps(["elecciones", "presidente", "corrupcion"]),
                json.dumps({"region": "LATAM", "language": "es"}),
                120,
                300,
                6000,
                1,
                "active",
                json.dumps({"pilot": True}),
                now,
                now,
                "planner",
                "planner",
            ),
            (
                "prof_social_br_politica",
                "prov_social_default",
                "Social BR Política",
                "social_br_politica",
                "social",
                "BR",
                "pt",
                json.dumps(["politics"]),
                json.dumps(["#politica", "#eleicao"]),
                json.dumps({"stream": "hashtags", "language": "pt"}),
                30,
                200,
                4000,
                1,
                "active",
                json.dumps({"pilot": True}),
                now,
                now,
                "planner",
                "planner",
            ),
        ]
        conn.executemany(
            """
            INSERT OR REPLACE INTO providers (
                id, name, kind, description, auth, config, limits, status,
                created_at, updated_at, created_by, updated_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            providers,
        )
        conn.executemany(
            """
            INSERT OR REPLACE INTO ingestion_profiles (
                id, provider_id, name, slug, kind, country, language, categories, keywords,
                filters, frequency_minutes, budget_daily_calls, budget_monthly_calls,
                enabled, status, metadata, created_at, updated_at, created_by, updated_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            profiles,
        )
        conn.commit()
    finally:
        conn.close()


def _main() -> None:
    seed()
    print(f"[s31] seed applied at {DB_PATH}")


if __name__ == "__main__":
    _main()
