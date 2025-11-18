from __future__ import annotations

from datetime import datetime

import pytest

from app.core import storage
from app.core.models import Item, Source, SourceConfig, SourceStatus
from app.core.pipeline import run_pipeline


@pytest.fixture(autouse=True)
def _sandbox_storage(tmp_path, monkeypatch):
    data_dir = tmp_path / "evidence"
    monkeypatch.setenv("INSPECTAH_DATA_DIR", str(data_dir))
    return data_dir


def _make_source(source_id: str, info_type: str) -> Source:
    return Source(
        id=source_id,
        name=source_id,
        type="precos_api_simples" if info_type.startswith("C1") else "noticias_rss_simplificado",
        info_type=info_type,
        config=SourceConfig(url_base=f"https://sources/{source_id}", params={}, selected_fields=[]),
        status=SourceStatus(),
    )


def _make_item(item_id: str, source_id: str, payload: dict[str, object]) -> Item:
    return Item(
        id=item_id,
        source_id=source_id,
        payload=payload,
        created_at=datetime.utcnow(),
    )


def test_pipeline_marks_insufficient_sources_when_only_one_source():
    source = _make_source("src_unico", "C1_preco_medio")
    storage.save_source(source)
    storage.save_item(
        _make_item(
            "item_unique",
            source.id,
            {"produto": "arroz", "cidade": "São Paulo", "valor": 11.5, "info_type": "preco"},
        )
    )

    response = run_pipeline("Qual o preço médio do arroz em São Paulo?")
    assert response.status == "dados_insuficientes"

    log = storage.load_query_log(response.query_id)
    assert log is not None
    assert log.error_code == "NO_DATA"
    assert log.meta["bundle_path"]


def test_pipeline_out_of_scope_still_creates_querylog_bundle_and_response():
    response = run_pipeline("Quem vai ganhar a copa do mundo daqui 10 anos?")
    assert response.status == "fora_de_escopo"
    assert response.evidence_bundle_id is not None
    log = storage.load_query_log(response.query_id)
    assert log is not None
    assert log.scenario_tag == "OUT_OF_SCOPE"
    assert log.user_response_id == response.id
    assert log.meta["bundle_path"].endswith(f"{response.evidence_bundle_id}.json")
