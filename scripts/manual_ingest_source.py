from __future__ import annotations

import argparse
import os
from typing import Optional

from app.ingestion import services as ingestion_services
from app.ingestion.models import IngestionTrigger
from app.ingestion.repository import IngestionRepository
from app.sources import service as sources_service
from app.sources.models import Source


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa uma ingestão manual para uma fonte pelo slug.")
    parser.add_argument("--slug", required=True, help="Slug da fonte a ingerir")
    parser.add_argument("--db-path", help="Caminho para o banco de fontes (INSPECTAH_S21_DB_PATH)")
    return parser.parse_args()


def _find_source_by_slug(slug: str) -> Optional[Source]:
    for src in sources_service.list_sources():
        if src.slug == slug:
            return src
    return None


def main() -> int:
    args = _parse_args()
    if args.db_path:
        os.environ["INSPECTAH_S21_DB_PATH"] = args.db_path

    src = _find_source_by_slug(args.slug)
    if not src:
        print(f"{args.slug}: NOT FOUND")
        return 1
    if src.state.value != "ACTIVE":
        print(f"{args.slug}: NOT ELIGIBLE (state={src.state.value})")
        return 2

    repo = IngestionRepository()
    try:
        run = ingestion_services.start_ingestion_run(
            src.id,
            trigger=IngestionTrigger.MANUAL,
            trigger_origin="manual_script",
            repo=repo,
            source_fetcher=lambda sid: sources_service.get_source_detail(sid),
            execute_inline=True,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"{args.slug}: ERROR starting ingestion -> {exc}")
        return 3

    items = run.items_processed if getattr(run, "items_processed", None) is not None else 0
    status = run.status.value if hasattr(run, "status") else "unknown"
    payload_ref = getattr(run, "payload_ref", None)
    print(f"{args.slug}: INGESTION OK status={status} items_processed={items} payload_ref={payload_ref}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
