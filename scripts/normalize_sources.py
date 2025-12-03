from __future__ import annotations

import argparse
import os
from pathlib import Path

from app.sources import maintenance


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normaliza e deduplica fontes.")
    parser.add_argument("--db-path", help="Caminho para o banco de fontes (INSPECTAH_S21_DB_PATH).")
    parser.add_argument("--user", default="normalizer", help="Identificador do usuário responsável.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.db_path:
        os.environ["INSPECTAH_S21_DB_PATH"] = args.db_path
    normalized = maintenance.normalize_all_sources(changed_by=args.user)
    dedup = maintenance.deduplicate_sources(changed_by=args.user)
    print(f"Normalized: {normalized['normalized']} (lab_ingestion_adjusted={normalized['lab_ingestion_adjusted']}), deduplicated: {dedup['deduplicated']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
