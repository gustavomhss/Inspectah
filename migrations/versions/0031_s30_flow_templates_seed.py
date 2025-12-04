"""
Sprint 30 — Seed de template canônico de fluxo de notícias.
"""

from __future__ import annotations

import importlib
import json
import sqlite3
from pathlib import Path

flow_schema = importlib.import_module("migrations.versions.0030_s30_flow_model_v15")

DEFAULT_DB_PATH = flow_schema.DEFAULT_DB_PATH


TEMPLATE_ID = "tpl_fluxo_noticias_geral_v1"
TEMPLATE_SLUG = "fluxo_noticias_geral_v1"
TEMPLATE_VERSAO = "1"


def _template_structure() -> dict:
    steps = [
        {"ordem": 1, "tipo_etapa": "interprete", "agent_role": "news_interpreter"},
        {"ordem": 2, "tipo_etapa": "classificador", "agent_role": "news_classifier"},
        {"ordem": 3, "tipo_etapa": "analista", "agent_role": "news_analyst_primary"},
        {"ordem": 4, "tipo_etapa": "analista", "agent_role": "news_analyst_secondary"},
        {"ordem": 5, "tipo_etapa": "debunker", "agent_role": "news_debunker_primary"},
        {"ordem": 6, "tipo_etapa": "debunker", "agent_role": "news_debunker_secondary"},
        {"ordem": 7, "tipo_etapa": "decision_maker", "agent_role": "news_decision_maker"},
    ]
    return {"tipo_entrada": "noticia_texto", "steps": steps, "constraints": {"max_steps": 12}}


def apply_seed(db_path: Path = DEFAULT_DB_PATH) -> None:
    flow_schema.apply_migration(db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        payload = _template_structure()
        with conn:
            existing = conn.execute(
                "SELECT id FROM flow_flow_templates WHERE slug=?", (TEMPLATE_SLUG,)
            ).fetchone()
            if existing:
                return
            conn.execute(
                """
                INSERT INTO flow_flow_templates (
                    id, slug, versao, tipo_entrada, estrutura, ativo, metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 1, ?, datetime('now'), datetime('now'))
                """,
                (
                    TEMPLATE_ID,
                    TEMPLATE_SLUG,
                    TEMPLATE_VERSAO,
                    payload["tipo_entrada"],
                    json.dumps(payload),
                    json.dumps({"owner": "squad_fluxos"}),
                ),
            )
    finally:
        conn.close()


def verify_seed(db_path: Path = DEFAULT_DB_PATH) -> bool:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        row = conn.execute(
            "SELECT id, slug FROM flow_flow_templates WHERE slug=?", (TEMPLATE_SLUG,)
        ).fetchone()
        return bool(row)
    finally:
        conn.close()


if __name__ == "__main__":
    apply_seed()
    ok = verify_seed()
    print(f"[s30] template seed {'ok' if ok else 'missing'} at {DEFAULT_DB_PATH}")
