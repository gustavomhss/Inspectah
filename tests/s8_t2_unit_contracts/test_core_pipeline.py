from __future__ import annotations

from datetime import datetime

import pytest

from app.core import storage
from app.core.evidence_bundle_builder import build_evidence_bundle
from app.core.models import Item, Source, SourceConfig, SourceStatus
from app.core.pipeline import run_pipeline
from app.core.query_parser import parse_query


@pytest.fixture(autouse=True)
def _sandbox_storage(tmp_path, monkeypatch):
    data_dir = tmp_path / "evidence"
    monkeypatch.setenv("INSPECTAH_DATA_DIR", str(data_dir))
    return data_dir


def _make_source(source_id: str, source_type: str = "precos_api_simples", reliability: str = "alta") -> Source:
    return Source(
        id=source_id,
        name=source_id,
        type=source_type,
        config=SourceConfig(
            url_base=f"https://example.com/{source_id}",
            params={"confiabilidade": reliability},
            selected_fields=["produto", "cidade", "valor"],
        ),
        status=SourceStatus(),
    )


def _make_price_item(item_id: str, source_id: str, produto: str, cidade: str, valor: float) -> Item:
    return Item(
        id=item_id,
        source_id=source_id,
        payload={
            "produto": produto,
            "cidade": cidade,
            "valor": valor,
            "moeda": "BRL",
            "info_type": "preco",
        },
        created_at=datetime.utcnow(),
    )


def _seed_price_sources(produto: str = "arroz", cidade: str = "São Paulo"):
    src1 = _make_source("src_preco_1")
    src2 = _make_source("src_preco_2")
    for src in (src1, src2):
        storage.save_source(src)
    storage.save_item(_make_price_item("item_1", src1.id, produto, cidade, 10.0))
    storage.save_item(_make_price_item("item_2", src2.id, produto, cidade, 12.0))
    return src1, src2


def test_save_and_get_source_roundtrip():
    source = _make_source("src_roundtrip")
    storage.save_source(source)
    loaded = storage.get_source("src_roundtrip")
    assert loaded is not None
    assert loaded.id == source.id
    assert loaded.config.url_base == source.config.url_base


def test_list_items_by_filter_returns_items_from_multiple_sources():
    _seed_price_sources()
    filters = {"produto": "arroz", "cidade": "São Paulo", "source_types": ["precos_api_simples"]}
    items = storage.list_items_by_filter(filters)
    assert len(items) == 2
    assert {item.source_id for item in items} == {"src_preco_1", "src_preco_2"}


def test_parse_query_detects_all_main_types():
    agg = parse_query("Qual o preço médio do arroz em São Paulo?")
    comp = parse_query("Onde o arroz está mais barato em São Paulo?")
    fact = parse_query("Político João Silva foi condenado no caso Lava Jato?")
    out = parse_query("Quem vai ganhar a eleição ano que vem?")

    assert agg.query_type == "agregacao_simples"
    assert comp.query_type == "comparacao_simples"
    assert fact.query_type == "checagem_factual_simples"
    assert out.query_type == "fora_de_escopo"


def test_build_evidence_bundle_counts_sources():
    _seed_price_sources()
    parsed = parse_query("Qual o preço médio do arroz em São Paulo?")
    items = storage.list_items_by_filter(parsed.filters)
    bundle = build_evidence_bundle(parsed, items)

    assert bundle.meta["num_sources"] == 2
    assert bundle.meta["num_items"] == 2
    assert set(bundle.items_by_source.keys()) == {"src_preco_1", "src_preco_2"}


def test_pipeline_run_pipeline_persists_querylog():
    _seed_price_sources()
    response = run_pipeline("Qual o preço médio do arroz em São Paulo?")

    assert response.status == "ok"
    assert response.evidence_bundle_id is not None
    assert response.summary.get("num_sources") == 2
    log = storage.load_query_log(response.query_id)
    assert log is not None
    assert log.evidence_bundle_id == response.evidence_bundle_id
