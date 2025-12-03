from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.ingestion.models import IngestionMode
from app.ingestion.repository import IngestionRepository
from app.sources import maintenance, service
from app.sources.models import SourceState
from app.sources.normalizer import LAB_ENDPOINT, normalize_source_payload
from app.sources.schemas import SourceCreate


def _set_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INSPECTAH_S21_DB_PATH", str(tmp_path / "sources.sqlite"))
    monkeypatch.setenv("INSPECTAH_S22_DB_PATH", str(tmp_path / "ingestion.sqlite"))


def _make_payload(
    slug: str,
    *,
    endpoint: str,
    source_type: str = "news_rss",
    category: str = "general",
    format: str = "json",
) -> SourceCreate:
    return SourceCreate(
        slug=slug,
        name=f"Fonte {slug}",
        description="",
        type=source_type,
        category=category,
        themes=[],
        info_types=[],
        format=format,
        endpoint=endpoint,
        auth_type="none",
        auth_config={},
        request_params={},
        headers={},
        frequency="manual",
        timeout_ms=10000,
        retry_policy={},
        parsing_config={},
        created_by="tester",
    )


def test_normalize_payload_sets_rss_for_news_feeds():
    payload = _make_payload("g1-rss", endpoint="https://g1.globo.com/rss", format="json")
    normalized = normalize_source_payload(payload)
    assert normalized.format == "rss"


def test_lab_source_flag_and_ingestion_mode(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    _set_env(tmp_path, monkeypatch)
    payload = _make_payload("lab-src", endpoint=LAB_ENDPOINT, category="official")
    created = service.create_source(payload)
    assert created.category == "internal_test"
    assert created.meta.get("lab_source") is True
    # config de ingestão deve existir e ficar em MANUAL_ONLY desabilitado
    repo = IngestionRepository()
    cfg = repo.get_config(created.id)
    assert cfg is not None
    assert cfg.mode == IngestionMode.MANUAL_ONLY
    assert cfg.enabled is True


def test_deduplicate_marks_duplicates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    _set_env(tmp_path, monkeypatch)
    endpoint = "https://pox.globo.com/rss/valor"
    first = service.create_source(_make_payload("valor-eco", endpoint=endpoint))
    second = service.create_source(_make_payload("valor-dup", endpoint=endpoint))

    result = maintenance.deduplicate_sources(changed_by="tester")
    assert result["deduplicated"] >= 1

    refreshed_first = service.get_source_detail(first.id)
    refreshed_second = service.get_source_detail(second.id)
    assert refreshed_first is not None and refreshed_second is not None
    assert refreshed_second.state == SourceState.DISABLED_PERM
    assert refreshed_second.meta.get("duplicated_into") == refreshed_first.slug
