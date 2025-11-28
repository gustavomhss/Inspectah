from datetime import datetime, timedelta

import pytest

from app.ingestion.models import (
    IngestionConfig,
    IngestionMode,
    IngestionRun,
    IngestionStatus,
    IngestionTrigger,
    validate_run_invariants,
)
from app.sources.models import SourceState


def _sample_config(
    mode: IngestionMode = IngestionMode.AUTOMATIC,
    source_state: SourceState = SourceState.ACTIVE,
    interval_minutes: int = 60,
    max_attempts: int = 3,
    timeout_seconds: int = 30,
) -> IngestionConfig:
    return IngestionConfig.create(
        id="ingcfg_test",
        source_id="src_1",
        source_state=source_state,
        enabled=True,
        mode=mode,
        interval_minutes=interval_minutes,
        max_attempts=max_attempts,
        timeout_seconds=timeout_seconds,
        created_by="tester",
    )


def test_config_allows_valid_interval_and_mode():
    cfg = _sample_config()
    assert cfg.mode == IngestionMode.AUTOMATIC
    assert cfg.interval_minutes == 60
    assert cfg.timeout_seconds == 30


@pytest.mark.parametrize("interval", [5, 20000])
def test_config_interval_out_of_bounds(interval):
    with pytest.raises(ValueError):
        _sample_config(mode=IngestionMode.MANUAL_ONLY, source_state=SourceState.ACTIVE, interval_minutes=interval)


def test_config_disallows_automatic_for_disabled_source():
    with pytest.raises(ValueError):
        _sample_config(mode=IngestionMode.AUTOMATIC, source_state=SourceState.DISABLED_PERM)


def test_run_must_start_pending_or_running():
    cfg = _sample_config()
    with pytest.raises(ValueError):
        IngestionRun.create(
            id="run_bad",
            config=cfg,
            trigger=IngestionTrigger.MANUAL,
            status=IngestionStatus.SUCCESS,
        )


def test_run_final_requires_finished_at_and_payload():
    cfg = _sample_config()
    run = IngestionRun.create(
        id="run_ok",
        config=cfg,
        trigger=IngestionTrigger.MANUAL,
        status=IngestionStatus.RUNNING,
        started_at=datetime.utcnow() - timedelta(minutes=1),
    )
    run.status = IngestionStatus.SUCCESS
    run.finished_at = datetime.utcnow()
    run.payload_ref = "data/ingestion_raw/src_1/run_ok.ndjson"
    validate_run_invariants(run, cfg)


def test_run_final_without_payload_fails():
    cfg = _sample_config()
    run = IngestionRun.create(
        id="run_fail",
        config=cfg,
        trigger=IngestionTrigger.MANUAL,
        status=IngestionStatus.RUNNING,
        started_at=datetime.utcnow() - timedelta(minutes=1),
    )
    run.status = IngestionStatus.PARTIAL_SUCCESS
    run.finished_at = datetime.utcnow()
    run.error_code = "partial_missing"
    with pytest.raises(ValueError):
        validate_run_invariants(run, cfg)


def test_run_with_error_requires_message():
    cfg = _sample_config()
    run = IngestionRun.create(
        id="run_error",
        config=cfg,
        trigger=IngestionTrigger.MANUAL,
        status=IngestionStatus.RUNNING,
    )
    run.status = IngestionStatus.FAIL
    run.finished_at = datetime.utcnow()
    with pytest.raises(ValueError):
        validate_run_invariants(run, cfg)


def test_run_running_conflict_detected():
    cfg = _sample_config()
    run = IngestionRun.create(
        id="run_running",
        config=cfg,
        trigger=IngestionTrigger.AUTOMATIC,
        status=IngestionStatus.RUNNING,
    )
    with pytest.raises(ValueError):
        validate_run_invariants(run, cfg, running_count_for_source=1)
