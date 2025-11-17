"""
Sprint 10 Truth-DB core migration.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

SCHEMA_STMTS = [
    """
    CREATE TABLE IF NOT EXISTS bloco_tema (
        id TEXT PRIMARY KEY,
        titulo TEXT NOT NULL,
        descricao_curta TEXT NOT NULL,
        dominio TEXT NOT NULL,
        referencias TEXT,
        hash_conteudo TEXT,
        meta TEXT,
        created_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS fato_registravel (
        id TEXT PRIMARY KEY,
        bloco_id TEXT NOT NULL REFERENCES bloco_tema(id),
        resumo_fato TEXT NOT NULL,
        descricao_detalhada TEXT NOT NULL,
        estado_inicial TEXT NOT NULL,
        evidencias TEXT NOT NULL,
        relatorio_simples TEXT,
        hash_conteudo TEXT,
        ancora_externa TEXT,
        created_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS complemento (
        id TEXT PRIMARY KEY,
        bloco_id TEXT REFERENCES bloco_tema(id),
        fato_id TEXT REFERENCES fato_registravel(id),
        tipo TEXT NOT NULL,
        conteudo TEXT NOT NULL,
        referencias TEXT,
        criado_em TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS versao_fato (
        id TEXT PRIMARY KEY,
        fato_id TEXT NOT NULL REFERENCES fato_registravel(id),
        numero_versao INTEGER NOT NULL,
        descricao TEXT NOT NULL,
        estado TEXT NOT NULL,
        evidencias TEXT NOT NULL,
        hash_conteudo TEXT NOT NULL,
        criada_em TEXT NOT NULL,
        autor TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS estado_fato (
        fato_id TEXT PRIMARY KEY REFERENCES fato_registravel(id),
        estado_atual TEXT NOT NULL,
        atualizado_em TEXT NOT NULL,
        justificativa TEXT NOT NULL
    );
    """,
]


def apply_migration(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        with conn:
            for stmt in SCHEMA_STMTS:
                conn.executescript(stmt)
    finally:
        conn.close()


def verify_schema(db_path: Path) -> dict[str, int]:
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name IN ('bloco_tema','fato_registravel','complemento','versao_fato','estado_fato')"
        )
        names = {row[0] for row in cursor.fetchall()}
        return {"tables": len(names)}
    finally:
        conn.close()


def _main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else Path("out/databases/s10_truthdb.sqlite")
    apply_migration(target)
    info = verify_schema(target)
    print(f"Truth-DB migration applied to {target} ({info['tables']} tables).")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
