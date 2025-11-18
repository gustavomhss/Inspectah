from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.core import storage
from app.core.models import Item, Source, SourceConfig, SourceStatus

from .schemas import (
    SourceCreateRequest,
    SourceResponse,
    SourceStatusResponse,
    SourceTestResult,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIRS = [
    REPO_ROOT / "tests" / "fixtures" / "s8_preco_medio",
    REPO_ROOT / "tests" / "fixtures" / "s8_comparacao",
    REPO_ROOT / "tests" / "fixtures" / "s8_checagem_factual",
]

DEFAULT_SOURCES = [
    {
        "id": "src_preco_1",
        "name": "Painel de Preços Municipal 1",
        "type": "precos_api_simples",
        "info_type": "preco",
        "url_base": "https://fixtures.inspectah/precos/painel1",
    },
    {
        "id": "src_preco_2",
        "name": "Painel de Preços Municipal 2",
        "type": "precos_api_simples",
        "info_type": "preco",
        "url_base": "https://fixtures.inspectah/precos/painel2",
    },
    {
        "id": "src_fato_1",
        "name": "Monitor Fatos Públicos 1",
        "type": "noticias_rss_simplificado",
        "info_type": "fato",
        "url_base": "https://fixtures.inspectah/fatos/feed1",
    },
    {
        "id": "src_fato_2",
        "name": "Monitor Fatos Públicos 2",
        "type": "noticias_rss_simplificado",
        "info_type": "fato",
        "url_base": "https://fixtures.inspectah/fatos/feed2",
    },
]


def create_or_update_source(payload: SourceCreateRequest) -> Source:
    existing = storage.get_source(payload.id)
    status = existing.status if existing else SourceStatus()
    params = dict(payload.params)
    params["info_type"] = payload.info_type
    source = Source(
        id=payload.id,
        name=payload.name,
        type=payload.type,
        config=SourceConfig(
            url_base=payload.url_base,
            auth_token=payload.auth_token,
            params=params,
            selected_fields=payload.selected_fields,
        ),
        status=status,
    )
    storage.save_source(source)
    return source


def list_sources() -> List[SourceResponse]:
    output: List[SourceResponse] = []
    for src in storage.list_sources():
        info_type = src.config.params.get("info_type", "")
        output.append(
            SourceResponse(
                id=src.id,
                name=src.name,
                type=src.type,
                info_type=info_type,
                url_base=src.config.url_base,
                selected_fields=src.config.selected_fields,
                params=src.config.params,
            )
        )
    return output


def get_source_status(source_id: str) -> Optional[SourceStatusResponse]:
    source = storage.get_source(source_id)
    if not source:
        return None
    status = source.status
    return SourceStatusResponse(
        source_id=source.id,
        last_fetch_at=status.last_fetch_at,
        last_fetch_status=status.last_fetch_status,
        last_fetch_error=status.last_fetch_error,
        recent_items_count=status.recent_items_count,
    )


def trigger_source_test(source_id: str) -> SourceTestResult:
    source = storage.get_source(source_id)
    if not source:
        return SourceTestResult(
            source_id=source_id,
            items_ingested=0,
            preview_items=[],
            status="erro",
            notes="Fonte não encontrada.",
        )

    items = _load_fixture_records(source_id)
    preview: List[Dict[str, object]] = []
    ingested = 0
    now = datetime.utcnow()
    for record in items:
        item = Item(
            id=record.get("id") or storage.generate_entity_id("item"),
            source_id=source_id,
            payload=record,
            created_at=_parse_created_at(record.get("coletado_em")) or now,
        )
        storage.save_item(item)
        ingested += 1
        if len(preview) < 3:
            preview.append(record)

    source.status = SourceStatus(
        last_fetch_at=now,
        last_fetch_status="ok" if ingested else "erro",
        last_fetch_error=None if ingested else "Nenhum item carregado da fixture.",
        recent_items_count=ingested,
    )
    storage.save_source(source)

    result_status = "ok" if ingested else "erro"
    notes = None if ingested else "Verifique fixtures desta fonte."
    return SourceTestResult(
        source_id=source_id,
        items_ingested=ingested,
        preview_items=preview,
        status=result_status,
        notes=notes,
    )


def ensure_default_sources() -> None:
    for definition in DEFAULT_SOURCES:
        request = SourceCreateRequest(
            id=definition["id"],
            name=definition["name"],
            type=definition["type"],
            info_type=definition["info_type"],
            url_base=definition["url_base"],
            selected_fields=[
                "produto",
                "cidade",
                "bairro",
                "valor",
                "moeda",
                "pessoa",
                "caso",
                "status",
            ],
            params={"confiabilidade": "alta"},
        )
        create_or_update_source(request)
        trigger_source_test(definition["id"])


def _load_fixture_records(source_id: str) -> List[Dict[str, object]]:
    for directory in FIXTURE_DIRS:
        candidate = directory / f"{source_id}.json"
        if candidate.exists():
            data = json.loads(candidate.read_text(encoding="utf-8"))
            return data.get("items", [])
    return []


def _parse_created_at(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
