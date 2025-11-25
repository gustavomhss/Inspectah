from datetime import datetime, timedelta

from app.ingestion.models import (
    IngestionConfig,
    IngestionMode,
    IngestionRun,
    IngestionStatus,
    IngestionTrigger,
    validate_run_invariants,
)
from app.ingestion.repository import IngestionRepository
from app.sources.models import SourceState


def _seed_config(repo: IngestionRepository, source_id: str = "src_persist") -> IngestionConfig:
    cfg = IngestionConfig.create(
        id="ingcfg_persist",
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


def _seed_run(repo: IngestionRepository, cfg: IngestionConfig, started_at: datetime, run_id: str = "run_persist") -> IngestionRun:
    run = IngestionRun.create(
        id=run_id,
        config=cfg,
        trigger=IngestionTrigger.MANUAL,
        status=IngestionStatus.RUNNING,
        started_at=started_at,
    )
    validate_run_invariants(run, cfg)
    repo.insert_run(run)
    return run


def test_save_and_load_payload(tmp_path):
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    cfg = _seed_config(repo)
    run = _seed_run(repo, cfg, datetime.utcnow() - timedelta(minutes=1))
    payload_items = [{"id": 1, "title": "foo"}, {"id": 2, "title": "bar"}]
    ref = repo.save_raw_payload(run.id, run.source_id, payload_items, base_dir=tmp_path / "data/ingestion_raw")
    run.payload_ref = ref
    run.status = IngestionStatus.SUCCESS
    run.finished_at = datetime.utcnow()
    repo.update_run(run)

    loaded = repo.load_raw_payload(run.id, run.source_id, base_dir=tmp_path / "data/ingestion_raw")
    assert len(loaded) == 2
    assert loaded[0]["id"] == 1


def test_list_runs_by_source_and_period(tmp_path):
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    cfg = _seed_config(repo)
    now = datetime.utcnow()
    run1 = _seed_run(repo, cfg, now - timedelta(hours=2), run_id="run_persist_1")
    run2 = _seed_run(repo, cfg, now - timedelta(hours=1), run_id="run_persist_2")
    run2.status = IngestionStatus.SUCCESS
    run2.finished_at = now - timedelta(minutes=50)
    repo.update_run(run2)

    runs_window = repo.list_runs_by_source_between(cfg.source_id, now - timedelta(hours=3), now)
    assert len(runs_window) >= 2
    ids = {r.id for r in runs_window}
    assert run1.id in ids and run2.id in ids


def test_run_chain_source_to_payload(tmp_path):
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    cfg = _seed_config(repo, source_id="src_chain")
    run = _seed_run(repo, cfg, datetime.utcnow())
    repo.save_raw_payload(run.id, run.source_id, [{"id": "x"}], base_dir=tmp_path / "data/ingestion_raw")
    run.payload_ref = f"{tmp_path}/data/ingestion_raw/{run.source_id}/{datetime.utcnow():%Y/%m/%d}/{run.id}.ndjson"
    run.status = IngestionStatus.SUCCESS
    run.finished_at = datetime.utcnow()
    repo.update_run(run)

    fetched = repo.get_run(run.id)
    assert fetched is not None
    assert fetched.payload_ref.endswith(".ndjson")
