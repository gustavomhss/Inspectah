from __future__ import annotations

import argparse
import os
from datetime import datetime
from typing import Optional

from app.ingestion.repository import IngestionRepository
from app.sources import service as sources_service
from app.sources.models import Source


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mostra detalhes das últimas ingestões de uma fonte.")
    parser.add_argument("--slug", required=True, help="Slug da fonte")
    parser.add_argument("--db-path", help="Caminho para o banco de fontes (INSPECTAH_S21_DB_PATH)")
    parser.add_argument("--limit", type=int, default=5, help="Quantidade de runs a listar (padrão 5)")
    return parser.parse_args()


def _find_source_by_slug(slug: str) -> Optional[Source]:
    for src in sources_service.list_sources():
        if src.slug == slug:
            return src
    return None


def _fmt(dt: Optional[datetime]) -> str:
    return dt.isoformat() if dt else "-"


def _print_run(repo: IngestionRepository, run) -> None:
    print(
        f"run_id={run.id} status={run.status.value} items_processed={run.items_processed} "
        f"payload_ref={run.payload_ref} started_at={_fmt(run.started_at)} finished_at={_fmt(run.finished_at)} "
        f"error_code={run.error_code} error_message={run.error_message}"
    )
    payload = []
    if run.payload_ref:
        payload = repo.load_raw_payload(run.id, run.source_id)
    elif run.items_processed:
        # tentativa de leitura pelo run/source mesmo sem payload_ref
        payload = repo.load_raw_payload(run.id, run.source_id)
    if not payload:
        print("  payload: vazio ou não encontrado")
        return
    print(f"  payload items: {len(payload)}")
    for idx, item in enumerate(payload[:5], start=1):
        title = item.get("title") or item.get("titulo") or item.get("headline")
        guid = item.get("guid") or item.get("id")
        link = item.get("link") or item.get("url")
        print(f"    [{idx}] title={title!r} guid={guid!r} link={link!r}")
    if len(payload) > 5:
        print(f"    ... ({len(payload) - 5} itens adicionais)")


def main() -> int:
    args = _parse_args()
    if args.db_path:
        os.environ["INSPECTAH_S21_DB_PATH"] = args.db_path
    src = _find_source_by_slug(args.slug)
    if not src:
        print(f"{args.slug}: NOT FOUND")
        return 1
    repo = IngestionRepository()
    runs = repo.list_runs_by_source(src.id, limit=args.limit)
    if not runs:
        print(f"{args.slug}: sem runs registradas")
        return 0
    print(f"{args.slug}: {len(runs)} runs encontradas (mostrando até {args.limit})")
    for run in runs:
        _print_run(repo, run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
