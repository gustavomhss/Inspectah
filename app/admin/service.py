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
LEGACY_FIXTURE_DIRS = [
    REPO_ROOT / "tests" / "fixtures" / "s8_preco_medio",
    REPO_ROOT / "tests" / "fixtures" / "s8_comparacao",
    REPO_ROOT / "tests" / "fixtures" / "s8_checagem_factual",
]

DEFAULT_SELECTED_FIELDS = [
    "produto",
    "cidade",
    "bairro",
    "valor",
    "valor_medio",
    "moeda",
    "pessoa",
    "caso",
    "status",
    "observado_pct",
]

SCENARIO_SPECS: Dict[str, Dict[str, object]] = {
    "C1": {
        "scenario_id": "C1",
        "info_type": "C1_preco_medio",
        "query_type": "preco_medio",
        "fixture_dir": REPO_ROOT / "tests" / "fixtures" / "s9_preco_medio",
        "min_active_sources": 2,
        "sources": [
            {
                "id": "s9_c1_painel_seae",
                "name": "Painel de Preços SEAE",
                "type": "precos_api_simples",
                "url_base": "https://fixtures.inspectah/s9/preco_medio/painel_seae",
            },
            {
                "id": "s9_c1_pao_de_acucar",
                "name": "Encarte Digital Pão de Açúcar",
                "type": "precos_api_simples",
                "url_base": "https://fixtures.inspectah/s9/preco_medio/pao_de_acucar",
            },
            {
                "id": "s9_c1_mobile_auditoria",
                "name": "Coletor Mobile Inspectah",
                "type": "precos_api_simples",
                "url_base": "https://fixtures.inspectah/s9/preco_medio/mobile",
            },
        ],
    },
    "C2": {
        "scenario_id": "C2",
        "info_type": "C2_comparacao_simples",
        "query_type": "comparacao_simples",
        "fixture_dir": REPO_ROOT / "tests" / "fixtures" / "s9_comparacao",
        "min_active_sources": 2,
        "sources": [
            {
                "id": "s9_c2_anp_glp",
                "name": "ANP Preços GLP RJ",
                "type": "precos_api_simples",
                "url_base": "https://fixtures.inspectah/s9/comparacao/anp",
            },
            {
                "id": "s9_c2_sindigas",
                "name": "Sindigás Monitor",
                "type": "precos_api_simples",
                "url_base": "https://fixtures.inspectah/s9/comparacao/sindigas",
            },
            {
                "id": "s9_c2_secretaria",
                "name": "Secretaria RJ Custos Internos",
                "type": "precos_api_simples",
                "url_base": "https://fixtures.inspectah/s9/comparacao/secretaria",
            },
        ],
    },
    "C3": {
        "scenario_id": "C3",
        "info_type": "C3_checagem_factual",
        "query_type": "checagem_factual",
        "fixture_dir": REPO_ROOT / "tests" / "fixtures" / "s9_checagem_factual",
        "min_active_sources": 2,
        "sources": [
            {
                "id": "s9_c3_diario_oficial",
                "name": "Diário Oficial BH Diesel",
                "type": "noticias_rss_simplificado",
                "url_base": "https://fixtures.inspectah/s9/factual/diario_oficial",
            },
            {
                "id": "s9_c3_portal_transparencia",
                "name": "Portal Transparência Minas",
                "type": "noticias_rss_simplificado",
                "url_base": "https://fixtures.inspectah/s9/factual/portal_transparencia",
            },
            {
                "id": "s9_c3_anp_diesel",
                "name": "ANP Diesel BH 30d",
                "type": "noticias_rss_simplificado",
                "url_base": "https://fixtures.inspectah/s9/factual/anp",
            },
        ],
    },
}

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
    params.setdefault("info_type", payload.info_type)
    source = Source(
        id=payload.id,
        name=payload.name,
        type=payload.type,
        info_type=payload.info_type,
        config=SourceConfig(
            url_base=payload.url_base,
            auth_token=payload.auth_token,
            params=params,
            selected_fields=payload.selected_fields or DEFAULT_SELECTED_FIELDS,
        ),
        status=status,
    )
    storage.save_source(source)
    return source


def list_sources() -> List[SourceResponse]:
    output: List[SourceResponse] = []
    for src in storage.list_sources():
        info_type = src.info_type or src.config.params.get("info_type", "")
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


def prepare_scenario_sources(scenario_id: str) -> List[Source]:
    scenario = SCENARIO_SPECS.get(scenario_id)
    if not scenario:
        raise ValueError(f"Cenário desconhecido: {scenario_id}")

    prepared: List[Source] = []
    for definition in scenario["sources"]:
        request = _build_source_request(definition, scenario)
        source = create_or_update_source(request)
        result = trigger_source_test(source.id)
        if result.status != "ok":
            raise RuntimeError(f"Fonte {source.id} sem dados para {scenario_id}")
        prepared.append(storage.get_source(source.id) or source)

    _validate_multi_source(scenario_id, prepared, scenario.get("min_active_sources", 2))
    return prepared


def prepare_sources_for_info_type(info_type: str) -> List[Source]:
    for scenario_id, spec in SCENARIO_SPECS.items():
        if spec["info_type"] == info_type:
            return prepare_scenario_sources(scenario_id)
    raise ValueError(f"InfoType não suportado: {info_type}")


def _build_source_request(source_def: Dict[str, object], scenario: Dict[str, object]) -> SourceCreateRequest:
    params = {"scenario_id": scenario["scenario_id"]}
    params.update(source_def.get("params", {}))
    return SourceCreateRequest(
        id=source_def["id"],
        name=source_def["name"],
        type=source_def["type"],
        info_type=scenario["info_type"],
        url_base=source_def["url_base"],
        selected_fields=source_def.get("selected_fields") or DEFAULT_SELECTED_FIELDS,
        params=params,
    )


def _validate_multi_source(scenario_id: str, sources: List[Source], minimum: int) -> None:
    ok_sources = 0
    for source in sources:
        status = source.status
        if status.last_fetch_status == "ok" and status.recent_items_count > 0:
            ok_sources += 1
    if ok_sources < minimum:
        raise RuntimeError(
            f"Cenário {scenario_id} precisa de {minimum} fontes ativas; apenas {ok_sources} carregadas."
        )


def _load_fixture_records(source_id: str) -> List[Dict[str, object]]:
    path = _fixture_path_for_source(source_id)
    if path and path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("items", [])

    for directory in LEGACY_FIXTURE_DIRS:
        candidate = directory / f"{source_id}.json"
        if candidate.exists():
            data = json.loads(candidate.read_text(encoding="utf-8"))
            return data.get("items", [])
    return []


def _fixture_path_for_source(source_id: str) -> Optional[Path]:
    for spec in SCENARIO_SPECS.values():
        fixture_dir = spec["fixture_dir"]
        candidate = fixture_dir / f"{source_id}.json"
        if candidate.exists():
            return candidate
    return None


def _parse_created_at(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
