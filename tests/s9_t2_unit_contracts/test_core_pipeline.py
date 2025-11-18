from __future__ import annotations

from datetime import datetime
from pathlib import Path

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


def _make_source(source_id: str, info_type: str = "C1_preco_medio") -> Source:
    return Source(
        id=source_id,
        name=source_id,
        type="precos_api_simples",
        info_type=info_type,
        config=SourceConfig(
            url_base=f"https://example.com/{source_id}",
            params={"owner": source_id},
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


def _seed_price_sources(produto: str = "arroz", cidade: str = "São Paulo") -> tuple[Source, Source]:
    src1 = _make_source("src_preco_1")
    src2 = _make_source("src_preco_2")
    storage.save_source(src1)
    storage.save_source(src2)
    storage.save_item(_make_price_item("item_1", src1.id, produto, cidade, 10.0))
    storage.save_item(_make_price_item("item_2", src2.id, produto, cidade, 12.0))
    return src1, src2


def test_parse_query_assigns_info_type():
    agg = parse_query("Qual o preço médio do arroz em São Paulo?")
    comp = parse_query("Onde o arroz está mais barato em São Paulo?")
    fact = parse_query("É verdade que João Silva foi condenado no caso Lava Jato?")
    out = parse_query("Quem vai ganhar a eleição ano que vem?")

    assert agg.query_type == "preco_medio" and agg.info_type == "C1_preco_medio"
    assert comp.query_type == "comparacao_simples" and comp.info_type == "C2_comparacao_simples"
    assert fact.query_type == "checagem_factual" and fact.info_type == "C3_checagem_factual"
    assert out.query_type == "fora_de_escopo" and out.info_type == "fora_de_escopo"


def test_build_evidence_bundle_captures_sources_and_meta():
    _seed_price_sources()
    parsed = parse_query("Qual o preço médio do arroz em São Paulo?")
    items = storage.list_items_by_filter(parsed.filters)
    bundle = build_evidence_bundle(parsed, items)

    assert bundle.meta["num_sources"] == 2
    assert bundle.meta["num_items"] == 2
    assert bundle.meta["info_type"] == "C1_preco_medio"
    assert set(bundle.items_by_source.keys()) == {"src_preco_1", "src_preco_2"}


def test_run_pipeline_persists_full_triple(tmp_path):
    _seed_price_sources()
    response = run_pipeline("Qual o preço médio do arroz em São Paulo?")

    assert response.status == "ok"
    assert response.summary["num_sources"] == 2
    assert response.evidence_bundle_id is not None
    assert response.info_type == "C1_preco_medio"

    log = storage.load_query_log(response.query_id)
    assert log is not None
    assert log.evidence_bundle_id == response.evidence_bundle_id
    assert log.user_response_id == response.id
    assert log.meta["bundle_path"]
    assert Path(log.meta["bundle_path"]).exists()
    assert Path(log.meta["response_path"]).exists()

    bundle_path = Path(log.meta["bundle_path"])
    bundle_data = storage.load_evidence_bundle(response.evidence_bundle_id)
    assert bundle_data is not None and bundle_data.meta["num_sources"] == 2
    assert bundle_path.exists()
