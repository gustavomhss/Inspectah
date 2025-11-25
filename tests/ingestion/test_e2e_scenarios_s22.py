import json
from datetime import datetime
from pathlib import Path

import yaml

from app.ingestion.models import IngestionMode, IngestionStatus
from app.ingestion.repository import IngestionRepository
from app.ingestion.services import complete_ingestion_run, fail_ingestion_run, start_ingestion_run
from app.sources.models import Source, SourceState
from metrics import ingestion_s22 as metrics


def _load_fixture(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _source_from_fixture(fx: dict) -> Source:
    src = Source.create(
        id=fx["source_id"],
        slug=fx["source_id"],
        name=fx["source_id"],
        description="fixture",
        type=fx.get("type", "news_rss"),
        category=fx.get("category", "official"),
        themes=[],
        info_types=[fx.get("info_type", "news")],
        refresh_interval=fx.get("interval_minutes", 60),
        protocol="https",
        format=fx.get("format", "json"),
        endpoint="https://example.com",
        auth_type="none",
        auth_config={},
        request_params={},
        headers={},
        frequency="manual",
        timeout_ms=5000,
        retry_policy={},
        parsing_config={},
        redundancy_group=None,
        redundancy_role=None,
        created_by="tester",
    )
    src.state = SourceState.ACTIVE
    return src


def _source_fetcher(src: Source):
    return lambda _: src


def _scenario_files():
    root = Path(__file__).resolve().parents[2] / "data" / "s22_scenarios"
    return sorted(root.glob("**/*.yaml"))


def test_e2e_scenarios(tmp_path):
    metrics.reset()
    repo = IngestionRepository(db_path=tmp_path / "ingestion.sqlite")
    raw_base = tmp_path / "data/ingestion_raw"
    processed = 0
    stored_paths = []
    scenario_files = _scenario_files()
    assert scenario_files, "Fixtures de cenário não encontradas"
    for path in scenario_files:
        fx = _load_fixture(path)
        src = _source_from_fixture(fx)
        mode = IngestionMode(fx.get("mode", "AUTOMATIC"))
        # create config
        from app.ingestion.models import IngestionConfig

        cfg = IngestionConfig.create(
            id=f"cfg_{fx['source_id']}",
            source_id=fx["source_id"],
            source_state=src.state,
            enabled=True,
            mode=mode,
            interval_minutes=fx.get("interval_minutes", 60),
            max_attempts=3,
            timeout_seconds=60,
            created_by="tester",
        )
        repo.save_config(cfg)

        run = start_ingestion_run(
            fx["source_id"],
            trigger_origin="e2e_fixture",
            repo=repo,
            source_fetcher=_source_fetcher(src),
        )
        payload_ref = repo.save_raw_payload(run.id, fx["source_id"], fx.get("items", []), base_dir=raw_base)
        stored_paths.append(payload_ref)
        expect_status = fx.get("expect_status", "SUCCESS")
        if expect_status == "SUCCESS":
            complete_ingestion_run(run.id, items_processed=len(fx.get("items", [])), payload_ref=payload_ref, repo=repo)
        else:
            fail_ingestion_run(
                run.id,
                error_code=fx.get("error_code", "generic_error"),
                error_message=fx.get("error_message", "erro"),
                payload_ref=payload_ref,
                partial=expect_status == "PARTIAL_SUCCESS",
                items_processed=len(fx.get("items", [])),
                repo=repo,
            )
        processed += 1

    assert processed >= 3
    # metrics sanity: at least one success recorded
    assert any(status == "SUCCESS" for (_, status) in metrics.runs_total.keys())
    # evidence: NDJSON files created
    assert any(Path(p).exists() for p in stored_paths)
