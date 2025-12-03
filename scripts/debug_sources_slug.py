from __future__ import annotations

import argparse
import os
from typing import Optional

from app.ingestion.repository import IngestionRepository
from app.sources import service
from app.sources.models import Source


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Debug de fontes por slug.")
    parser.add_argument("--db-path", help="Caminho para o banco de fontes (INSPECTAH_S21_DB_PATH).")
    parser.add_argument("--slugs", nargs="*", default=["valor-eco", "valor-economico"], help="Slugs a inspecionar")
    return parser.parse_args()


def _format_source(src: Source, repo: IngestionRepository) -> str:
    cfg = repo.get_config(src.id)
    ingestion = f"mode={cfg.mode.value}, enabled={cfg.enabled}" if cfg else "no-config"
    meta = src.meta if src.meta else {}
    return (
        f"state={src.state.value}, format={src.format}, endpoint={src.endpoint}, "
        f"meta={meta}, ingestion={ingestion}"
    )


def main() -> int:
    args = _parse_args()
    if args.db_path:
        os.environ["INSPECTAH_S21_DB_PATH"] = args.db_path
    repo = IngestionRepository()
    all_sources = service.list_sources()
    by_slug = {s.slug: s for s in all_sources}
    for slug in args.slugs:
        src: Optional[Source] = by_slug.get(slug)
        if not src:
            print(f"{slug}: NOT FOUND")
            continue
        print(f"{slug}: FOUND -> {_format_source(src, repo)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
