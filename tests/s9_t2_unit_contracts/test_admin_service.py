from __future__ import annotations

from pathlib import Path

import pytest

from app.admin import service
from app.admin.schemas import SourceCreateRequest
from app.core import storage


@pytest.fixture(autouse=True)
def _sandbox_storage(tmp_path, monkeypatch):
    data_dir = tmp_path / "evidence"
    monkeypatch.setenv("INSPECTAH_DATA_DIR", str(data_dir))
    return data_dir


def test_create_and_toggle_source():
    request = SourceCreateRequest(
        id="custom_src",
        name="Custom Manual Source",
        type="precos_api_simples",
        info_type="C1_preco_medio",
        url_base="fixture://custom",
        selected_fields=["produto", "valor"],
        params={"coverage": "SP"},
    )
    service.create_or_update_source(request)

    sources = service.list_sources()
    assert any(src.id == "custom_src" for src in sources)

    service.set_source_active("custom_src", False)
    source = service.set_source_active("custom_src", True)
    assert source is not None
    assert source.is_active is True


def test_prepare_scenario_sources_guarantees_multi_source():
    prepared = service.prepare_scenario_sources("C1")
    assert len(prepared) >= 2

    statuses = [service.get_source_status(src_id) for src_id in prepared]
    assert all(status and status.last_fetch_status == "ok" for status in statuses)

    bundles_dir = storage.bundles_dir()
    assert bundles_dir.exists()


def test_prepare_sources_for_info_type_maps_scenario():
    result = service.prepare_sources_for_info_type("C3_checagem_factual")
    assert len(result) >= 2
    first_source = storage.get_source(result[0])
    assert first_source is not None
    assert first_source.info_type == "C3_checagem_factual"


def test_prepare_scenario_invalid(monkeypatch):
    spec = service.SCENARIO_SPECS["C1"]
    monkeypatch.setitem(service.SCENARIO_SPECS["C1"], "min_sources", 5)
    with pytest.raises(RuntimeError):
        service.prepare_scenario_sources("C1")
    monkeypatch.setitem(service.SCENARIO_SPECS["C1"], "min_sources", spec["min_sources"])
