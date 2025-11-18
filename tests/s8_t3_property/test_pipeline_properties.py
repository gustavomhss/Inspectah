from __future__ import annotations

from datetime import datetime

import pytest

from app.core import storage
from app.core.models import Item, Source, SourceConfig, SourceStatus
from app.core.pipeline import run_pipeline
from app.gpt_client.client import GptAnswer


@pytest.fixture(autouse=True)
def _sandbox_storage(tmp_path, monkeypatch):
    data_dir = tmp_path / "property_evidence"
    monkeypatch.setenv("INSPECTAH_DATA_DIR", str(data_dir))
    return data_dir


@pytest.fixture(autouse=True)
def _mock_gpt(monkeypatch):
    def fake_run_query(bundle, user_query, query_type):
        meta = bundle.meta
        summary = {
            "query_type": query_type,
            "num_sources": meta.get("num_sources", len(bundle.items_by_source)),
            "num_items": meta.get("num_items", 0),
        }
        limitations = []
        if query_type == "fora_de_escopo":
            answer_text = "Pergunta fora do escopo"
        elif summary["num_items"] == 0:
            answer_text = "Dados insuficientes"
        else:
            answer_text = "Resposta mock segura"
        confidence_level = "low" if summary["num_sources"] < 2 else "high"
        confidence = {"level": confidence_level, "reasons": ["mock"]}
        return GptAnswer(
            answer_text=answer_text,
            summary_structured=summary,
            confidence_flags=confidence,
            limitations=limitations,
            prompt_used={},
        )

    monkeypatch.setattr("app.core.pipeline.gpt_run_query", fake_run_query)


def _save_source(source_id: str, reliability: str = "alta") -> Source:
    source = Source(
        id=source_id,
        name=source_id,
        type="precos_api_simples",
        config=SourceConfig(
            url_base="https://example.com",
            params={"confiabilidade": reliability},
            selected_fields=["produto", "cidade", "valor"],
        ),
        status=SourceStatus(),
    )
    storage.save_source(source)
    return source


def _save_item(source: Source, produto: str, valor: float) -> None:
    storage.save_item(
        Item(
            id=f"item_{source.id}_{valor}",
            source_id=source.id,
            payload={
                "produto": produto,
                "cidade": "São Paulo",
                "valor": valor,
                "moeda": "BRL",
                "info_type": "preco",
            },
            created_at=datetime.utcnow(),
        )
    )


def test_pipeline_marks_insufficient_data_when_no_items():
    _save_source("src_sem_dados")
    response = run_pipeline("Qual o preço médio do trigo em Recife?")

    assert response.status == "dados_insuficientes"
    assert "insuficientes" in response.answer_text.lower()


def test_pipeline_flags_low_confidence_for_single_low_source():
    source = _save_source("src_unica", reliability="baixa")
    _save_item(source, produto="arroz", valor=25.0)

    response = run_pipeline("Qual o preço médio do arroz em São Paulo?")

    assert response.status == "ok"
    assert response.confidence.get("level") == "low"
    assert response.summary.get("num_sources") == 1


def test_pipeline_out_of_scope_query():
    response = run_pipeline("Quem vai ganhar a eleição ano que vem?")

    assert response.status == "fora_de_escopo"
    assert "fora do escopo" in response.answer_text.lower()
