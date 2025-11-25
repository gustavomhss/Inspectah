from datetime import datetime

import pytest

from app.ingestion.errors import (
    ConfigNotFoundError,
    ModeIncompatibleError,
    RunInProgressError,
    RunNotFoundError,
    SourceNotEligibleError,
)
from app.ingestion.models import (
    IngestionConfig,
    IngestionMode,
    IngestionRun,
    IngestionStatus,
    IngestionTrigger,
    validate_run_invariants,
)
from app.ingestion.repository import IngestionRepository
from app.ingestion.services import (
    complete_ingestion_run,
    fail_ingestion_run,
    reprocess_run,
    start_ingestion_run,
    toggle_ingestion_mode,
)
from app.sources.models import Source, SourceState


def _make_source(state: SourceState = SourceState.ACTIVE) -> Source:
    src = Source.create(
        id="src_1",
        slug="src-1",
        name="Fonte Demo",
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
    src.state = state
    return src


def _seed_config(repo: IngestionRepository, source: Source, *, mode: IngestionMode = IngestionMode.AUTOMATIC) -> IngestionConfig:
    cfg = IngestionConfig.create(
        id="ingcfg_seed",
        source_id=source.id,
        source_state=source.state,
        enabled=True,
        mode=mode,
        interval_minutes=30,
        max_attempts=3,
        timeout_seconds=60,
        created_by="tester",
    )
    repo.save_config(cfg)
    return cfg


def test_start_run_happy_path(tmp_path):
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    source = _make_source()
    _seed_config(repo, source)
    run = start_ingestion_run(
        source_id=source.id,
        repo=repo,
        source_fetcher=lambda sid: source,
    )
    assert run.status == IngestionStatus.RUNNING
    stored = repo.get_run(run.id)
    assert stored is not None
    assert stored.status == IngestionStatus.RUNNING


def test_start_run_blocks_parallel(tmp_path):
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    source = _make_source()
    cfg = _seed_config(repo, source)
    existing = IngestionRun.create(
        id="run_existing",
        config=cfg,
        trigger=IngestionTrigger.MANUAL,
        status=IngestionStatus.RUNNING,
    )
    repo.insert_run(existing)
    with pytest.raises(RunInProgressError):
        start_ingestion_run(source_id=source.id, repo=repo, source_fetcher=lambda sid: source)


def test_start_run_respects_mode(tmp_path):
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    source = _make_source()
    _seed_config(repo, source, mode=IngestionMode.MANUAL_ONLY)
    with pytest.raises(ModeIncompatibleError):
        start_ingestion_run(
            source_id=source.id,
            trigger=IngestionTrigger.AUTOMATIC,
            repo=repo,
            source_fetcher=lambda sid: source,
        )


def test_start_run_requires_config(tmp_path):
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    source = _make_source()
    run = start_ingestion_run(source_id=source.id, repo=repo, source_fetcher=lambda sid: source if sid == source.id else None)
    assert run.status == IngestionStatus.RUNNING


def test_complete_run_success(tmp_path):
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    source = _make_source()
    _seed_config(repo, source)
    run = start_ingestion_run(source_id=source.id, repo=repo, source_fetcher=lambda sid: source)
    completed = complete_ingestion_run(
        run.id,
        items_processed=5,
        payload_ref="data/ingestion_raw/src_1/run.ndjson",
        repo=repo,
    )
    assert completed.status == IngestionStatus.SUCCESS
    assert completed.items_processed == 5


def test_fail_run_records_error(tmp_path):
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    source = _make_source()
    _seed_config(repo, source)
    run = start_ingestion_run(source_id=source.id, repo=repo, source_fetcher=lambda sid: source)
    failed = fail_ingestion_run(
        run.id,
        error_code="network_error",
        error_message="timeout ao chamar fonte",
        repo=repo,
    )
    assert failed.status == IngestionStatus.FAIL
    assert failed.error_code == "network_error"


def test_reprocess_run_creates_new_run(tmp_path):
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    source = _make_source()
    cfg = _seed_config(repo, source)
    run = IngestionRun.create(id="run_done", config=cfg, trigger=IngestionTrigger.MANUAL, status=IngestionStatus.RUNNING)
    run.status = IngestionStatus.SUCCESS
    run.finished_at = datetime.utcnow()
    run.payload_ref = "data/ingestion_raw/src_1/run_done.ndjson"
    validate_run_invariants(run, cfg)
    repo.insert_run(run)
    new_run = reprocess_run(run.id, repo=repo, source_fetcher=lambda sid: source)
    assert new_run.trigger == IngestionTrigger.REPROCESS
    assert new_run.status == IngestionStatus.RUNNING


def test_toggle_ingestion_mode_creates_config(tmp_path):
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    source = _make_source()
    cfg = toggle_ingestion_mode(
        source.id,
        new_mode=IngestionMode.AUTOMATIC,
        enabled=True,
        updated_by="tester",
        repo=repo,
        source_fetcher=lambda sid: source,
    )
    assert cfg.source_id == source.id
    assert cfg.mode == IngestionMode.AUTOMATIC


def test_source_disabled_blocks_ingestion(tmp_path):
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    source = _make_source(state=SourceState.DISABLED_PERM)
    _seed_config(repo, source, mode=IngestionMode.MANUAL_ONLY)
    with pytest.raises(SourceNotEligibleError):
        start_ingestion_run(source_id=source.id, repo=repo, source_fetcher=lambda sid: source)


def test_complete_unknown_run_errors(tmp_path):
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    with pytest.raises(RunNotFoundError):
        complete_ingestion_run("missing", items_processed=1, payload_ref="x", repo=repo)


# --- HTTP layer tests ---


def _build_app(repo: IngestionRepository, source: Source):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.api.ingestion.routes import get_repo, get_source_fetcher, router as ingestion_router

    app = FastAPI()
    app.dependency_overrides[get_repo] = lambda: repo
    app.dependency_overrides[get_source_fetcher] = lambda: (lambda sid: source if sid == source.id else None)
    app.include_router(ingestion_router)
    return TestClient(app)


def test_http_trigger_and_list_runs(tmp_path):
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    source = _make_source()
    _seed_config(repo, source)
    client = _build_app(repo, source)

    resp = client.post(f"/admin/ingestion/{source.id}/run", json={"trigger_origin": "ui"})
    assert resp.status_code == 201
    run_id = resp.json()["run_id"]

    resp_runs = client.get(f"/admin/ingestion/{source.id}/runs")
    assert resp_runs.status_code == 200
    runs = resp_runs.json()["runs"]
    assert any(r["id"] == run_id for r in runs)

    resp_detail = client.get(f"/admin/ingestion/runs/{run_id}")
    assert resp_detail.status_code == 200
    assert resp_detail.json()["id"] == run_id


def test_http_toggle_mode_and_errors(tmp_path):
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    source = _make_source()
    _seed_config(repo, source)
    client = _build_app(repo, source)

    resp_toggle = client.post(f"/admin/ingestion/{source.id}/toggle-mode", json={"mode": "MANUAL_ONLY", "enabled": True})
    assert resp_toggle.status_code == 200
    assert resp_toggle.json()["mode"] == "MANUAL_ONLY"

    # run in progress should yield 409
    client.post(f"/admin/ingestion/{source.id}/run", json={"trigger_origin": "ui"})
    resp_conflict = client.post(f"/admin/ingestion/{source.id}/run", json={"trigger_origin": "ui"})
    assert resp_conflict.status_code == 409

    resp_missing = client.post("/admin/ingestion/missing-source/run", json={"trigger_origin": "ui"})
    assert resp_missing.status_code == 404
