from __future__ import annotations

from typing import Callable, Dict, List, Optional

from app.admin.ingestion import adapters
from app.ingestion import services
from app.ingestion.models import IngestionRun, IngestionTrigger
from app.ingestion.repository import IngestionRepository
from app.sources.models import Source
from app.sources.service import get_source_detail, list_sources


def list_ingestion_sources(
    *,
    repo: Optional[IngestionRepository] = None,
    source_fetcher: Callable[[str], Optional[Source]] = get_source_detail,
) -> List[Dict]:
    repo = repo or IngestionRepository()
    configs = repo.list_configs()
    results: List[Dict] = []
    for cfg in configs:
        src = source_fetcher(cfg.source_id)
        last_runs = repo.list_runs_by_source(cfg.source_id, limit=1)
        last_run = last_runs[0] if last_runs else None
        results.append(adapters.config_to_view(cfg, last_run=last_run, source_name=getattr(src, "name", None), source_type=getattr(src, "type", None)))
    return results


def get_ingestion_detail(
    source_id: str,
    *,
    repo: Optional[IngestionRepository] = None,
    source_fetcher: Callable[[str], Optional[Source]] = get_source_detail,
) -> Dict:
    repo = repo or IngestionRepository()
    cfg = repo.get_config(source_id)
    src = source_fetcher(source_id)
    runs = repo.list_runs_by_source(source_id, limit=20)
    runs_view = [adapters.run_to_view(run) for run in runs]
    return {
        "config": adapters.config_to_view(cfg, last_run=runs[0] if runs else None, source_name=getattr(src, "name", None), source_type=getattr(src, "type", None)) if cfg else None,
        "runs": runs_view,
    }


def trigger_manual_ingestion(
    source_id: str,
    *,
    repo: Optional[IngestionRepository] = None,
    source_fetcher: Callable[[str], Optional[Source]] = get_source_detail,
) -> IngestionRun:
    repo = repo or IngestionRepository()
    return services.start_ingestion_run(source_id, trigger=IngestionTrigger.MANUAL, trigger_origin="admin_ui", repo=repo, source_fetcher=source_fetcher)


def list_sources_for_config() -> List[Dict]:
    """Helper to show eligible sources for configuring ingestion."""
    from dataclasses import asdict

    return [asdict(s) for s in list_sources()]
