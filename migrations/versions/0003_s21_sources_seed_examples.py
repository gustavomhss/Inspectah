"""
Sprint 21 — Seeds de fontes exemplo para Console de Fontes.
Ref.: docs/sprint_21_cenarios_uso_fontes.md
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

SEEDS = [
    {
        "id": "seed_news_ok",
        "slug": "news-gov",
        "name": "Agência de Notícias Oficial",
        "description": "Feed de notícias governamentais",
        "type": "news_rss",
        "category": "official",
        "themes": ["politica"],
        "info_types": ["news"],
        "protocol": "https",
        "format": "rss",
        "endpoint": "mock://ok",
        "state": "ACTIVE",
    },
    {
        "id": "seed_gossip",
        "slug": "gossip-feed",
        "name": "Portal de Fofocas",
        "description": "Conteúdo de celebridades",
        "type": "gossip_feed",
        "category": "community",
        "themes": ["celebridades"],
        "info_types": ["gossip"],
        "protocol": "https",
        "format": "rss",
        "endpoint": "mock://degraded",
        "state": "TESTING",
    },
    {
        "id": "seed_sports",
        "slug": "sports-api",
        "name": "LigaPro Score",
        "description": "Resultados esportivos",
        "type": "sports_api",
        "category": "official",
        "themes": ["esportes"],
        "info_types": ["sports"],
        "protocol": "https",
        "format": "json",
        "endpoint": "mock://ok",
        "state": "ACTIVE",
    },
    {
        "id": "seed_weather",
        "slug": "weather-api",
        "name": "Meteo Nacional",
        "description": "API de clima",
        "type": "weather_api",
        "category": "official",
        "themes": ["clima"],
        "info_types": ["weather"],
        "protocol": "https",
        "format": "json",
        "endpoint": "mock://fail",
        "state": "SUSPECT",
    },
    {
        "id": "seed_legislation",
        "slug": "legis-tracker",
        "name": "Legis Tracker",
        "description": "Projeto de lei e andamento legislativo",
        "type": "legislation",
        "category": "official",
        "themes": ["legislacao"],
        "info_types": ["law"],
        "protocol": "https",
        "format": "json",
        "endpoint": "mock://ok",
        "state": "UNDER_REVIEW",
    },
    {
        "id": "seed_science",
        "slug": "sci-data",
        "name": "SciData Hub",
        "description": "Dataset científico",
        "type": "science_dataset",
        "category": "official",
        "themes": ["ciencia"],
        "info_types": ["science"],
        "protocol": "https",
        "format": "csv",
        "endpoint": "mock://ok",
        "state": "ACTIVE",
    },
]


def apply_migration(db_path: Path) -> None:
    now = datetime.utcnow().isoformat()
    columns = [
        "id",
        "slug",
        "name",
        "description",
        "type",
        "category",
        "themes",
        "info_types",
        "protocol",
        "format",
        "endpoint",
        "auth_type",
        "auth_config",
        "request_params",
        "headers",
        "frequency",
        "timeout_ms",
        "retry_policy",
        "parsing_config",
        "redundancy_group",
        "redundancy_role",
        "state",
        "state_reason",
        "state_updated_at",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "last_reviewed_by",
        "meta",
        "conflict_flags",
        "conflict_with_sources",
        "has_open_contestation",
        "last_conflict_at",
        "evidence_refs",
        "trust_severity",
    ]
    placeholders = ",".join(["?"] * len(columns))
    sql = f"INSERT OR REPLACE INTO sources ({','.join(columns)}) VALUES ({placeholders})"
    conn = sqlite3.connect(db_path)
    try:
        with conn:
            for seed in SEEDS:
                conn.execute(
                    sql,
                    [
                        seed["id"],
                        seed["slug"],
                        seed["name"],
                        seed["description"],
                        seed["type"],
                        seed["category"],
                        json.dumps(seed.get("themes", [])),
                        json.dumps(seed.get("info_types", [])),
                        seed.get("protocol", "https"),
                        seed.get("format", "json"),
                        seed.get("endpoint", ""),
                        "none",
                        json.dumps({}),
                        json.dumps({}),
                        json.dumps({}),
                        seed.get("frequency", "daily"),
                        seed.get("timeout_ms", 5000),
                        json.dumps({}),
                        json.dumps({}),
                        seed.get("redundancy_group"),
                        seed.get("redundancy_role"),
                        seed["state"],
                        None,
                        seed.get("state_updated_at") or now,
                        seed.get("created_at") or now,
                        seed.get("updated_at") or now,
                        "seed",
                        "seed",
                        None,
                        json.dumps({}),
                        json.dumps([]),
                        json.dumps([]),
                        0,
                        None,
                        json.dumps([]),
                        None,
                    ],
                )
    finally:
        conn.close()


def _main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else Path("out/databases/s21_sources.sqlite")
    apply_migration(target)
    print(f"Sprint 21 seed migration applied to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
