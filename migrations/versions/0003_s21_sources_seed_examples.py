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
        "refresh_interval": 180,
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
        "refresh_interval": 720,
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
        "refresh_interval": 120,
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
        "refresh_interval": 60,
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
        "refresh_interval": 720,
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
        "refresh_interval": 10080,
        "protocol": "https",
        "format": "csv",
        "endpoint": "mock://ok",
        "state": "ACTIVE",
    },
    {
        "id": "seed_official_open",
        "slug": "ibge-open",
        "name": "Portal IBGE Estatísticas",
        "description": "Portal oficial aberto sem API dedicada",
        "type": "official_open",
        "category": "official",
        "themes": ["economia"],
        "info_types": ["statistics"],
        "refresh_interval": 1440,
        "protocol": "https",
        "format": "html",
        "endpoint": "https://www.ibge.gov.br/indicadores",
        "state": "PROPOSED",
    },
    {
        "id": "seed_data_api",
        "slug": "ibge-api",
        "name": "API de dados IBGE",
        "description": "API REST de agregados do IBGE (exemplo)",
        "type": "data_api",
        "category": "official",
        "themes": ["economia", "estatisticas"],
        "info_types": ["data"],
        "refresh_interval": 240,
        "protocol": "https",
        "format": "json",
        "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados",
        "state": "TESTING",
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
        "refresh_interval",
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
                        seed.get("refresh_interval", 1440),
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
