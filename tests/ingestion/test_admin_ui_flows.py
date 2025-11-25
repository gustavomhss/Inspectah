from datetime import datetime, timedelta

from app.admin.ingestion import views
from app.ingestion.models import IngestionConfig, IngestionMode, IngestionRun, IngestionStatus, IngestionTrigger
from app.ingestion.repository import IngestionRepository
from app.sources.models import Source, SourceState


def _make_source(source_id: str = "src_ui") -> Source:
    src = Source.create(
        id=source_id,
        slug="src-ui",
        name="Fonte UI",
        description="",
        type="news_rss",
        category="official",
        themes=["politica"],
        info_types=["news"],
        refresh_interval=180,
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


def _seed_config_and_run(repo: IngestionRepository, source: Source) -> IngestionRun:
    cfg = IngestionConfig.create(
        id="ingcfg_ui",
        source_id=source.id,
        source_state=source.state,
        enabled=True,
        mode=IngestionMode.AUTOMATIC,
        interval_minutes=60,
        max_attempts=3,
        timeout_seconds=60,
        created_by="tester",
    )
    repo.save_config(cfg)
    run = IngestionRun.create(
        id="run_ui",
        config=cfg,
        trigger=IngestionTrigger.MANUAL,
        status=IngestionStatus.RUNNING,
        started_at=datetime.utcnow() - timedelta(minutes=5),
    )
    run.status = IngestionStatus.SUCCESS
    run.finished_at = datetime.utcnow()
    run.items_processed = 10
    run.payload_ref = "data/ingestion_raw/src_ui/run_ui.ndjson"
    repo.insert_run(run)
    repo.set_last_run(cfg.id, run.id)
    return run


def test_admin_list_and_detail_views(tmp_path):
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    source = _make_source()
    _seed_config_and_run(repo, source)

    listing = views.list_ingestion_sources(repo=repo, source_fetcher=lambda sid: source)
    assert listing
    entry = listing[0]
    assert entry["source_id"] == source.id
    assert entry["last_run_status"] in ("Sucesso", "Parcial", "Falha")

    detail = views.get_ingestion_detail(source.id, repo=repo, source_fetcher=lambda sid: source)
    assert detail["config"]["mode"] == IngestionMode.AUTOMATIC.value
    assert len(detail["runs"]) == 1


def test_admin_trigger_manual_ingestion(tmp_path):
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    source = _make_source()
    _seed_config_and_run(repo, source)

    new_run = views.trigger_manual_ingestion(source.id, repo=repo, source_fetcher=lambda sid: source)
    assert new_run.status == IngestionStatus.RUNNING
    runs = repo.list_runs_by_source(source.id)
    assert len(runs) >= 2
