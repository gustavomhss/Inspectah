from datetime import datetime, timedelta

from app.ingestion import observability
from app.ingestion.models import (
    IngestionConfig,
    IngestionMode,
    IngestionRun,
    IngestionStatus,
    IngestionTrigger,
)
from app.ingestion.repository import IngestionRepository
from app.ingestion.services import fail_ingestion_run, start_ingestion_run
from app.sources.models import SourceState
from metrics import ingestion_s22 as metrics


def _cfg(repo: IngestionRepository, source_id: str = "src_obs") -> IngestionConfig:
    cfg = IngestionConfig.create(
        id=f"ingcfg_{source_id}",
        source_id=source_id,
        source_state=SourceState.ACTIVE,
        enabled=True,
        mode=IngestionMode.AUTOMATIC,
        interval_minutes=60,
        max_attempts=3,
        timeout_seconds=60,
        created_by="tester",
    )
    repo.save_config(cfg)
    return cfg


def _source_fetcher(source_id: str):
    from app.sources.models import Source

    src = Source.create(
        id=source_id,
        slug=source_id,
        name="Fonte Obs",
        description="",
        type="news_rss",
        category="official",
        themes=[],
        info_types=["news"],
        refresh_interval=60,
        protocol="https",
        format="rss",
        endpoint="https://example.com/rss",
        auth_type="none",
        auth_config={},
        request_params={},
        headers={},
        frequency="daily",
        timeout_ms=5000,
        retry_policy={},
        parsing_config={},
        redundancy_group=None,
        redundancy_role=None,
        created_by="tester",
    )
    src.state = SourceState.ACTIVE
    return src


def test_success_updates_metrics(tmp_path):
    metrics.reset()
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    cfg = _cfg(repo)
    run = start_ingestion_run(cfg.source_id, repo=repo, source_fetcher=_source_fetcher)
    run.finished_at = datetime.utcnow()
    run.status = IngestionStatus.SUCCESS
    run.items_processed = 5
    observability.log_run_end(run)
    assert metrics.runs_total[(cfg.source_id, "RUNNING")] >= 1
    assert metrics.runs_total[(cfg.source_id, "SUCCESS")] >= 1
    assert cfg.source_id in metrics.last_success_ts


def test_failure_updates_error_metrics(tmp_path):
    metrics.reset()
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    cfg = _cfg(repo)
    run = start_ingestion_run(cfg.source_id, repo=repo, source_fetcher=_source_fetcher)
    fail_ingestion_run(run.id, error_code="network_error", error_message="fail", repo=repo)
    assert metrics.runs_fail_total[cfg.source_id] >= 1
    assert cfg.source_id in metrics.last_failure_ts


def test_sources_without_recent_runs(tmp_path):
    metrics.reset()
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    cfg = _cfg(repo, source_id="src_stale")
    # create stale run
    run = IngestionRun.create(
        id="run_old",
        config=cfg,
        trigger=IngestionTrigger.MANUAL,
        status=IngestionStatus.RUNNING,
        started_at=datetime.utcnow() - timedelta(days=2),
    )
    run.status = IngestionStatus.SUCCESS
    run.finished_at = run.started_at + timedelta(minutes=1)
    repo.insert_run(run)
    repo.update_run(run)
    stale = observability.sources_without_recent_runs(repo, threshold_minutes=60)
    assert "src_stale" in stale
