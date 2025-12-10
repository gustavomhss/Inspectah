from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from app.core import storage
from app.core.models import Item, Source, SourceConfig, SourceStatus
from app.core.query_types import InfoType
from app.observability import metrics_s9

from .schemas import (
    SourceCreateRequest,
    SourceResponse,
    SourceStatusResponse,
    SourceTestResult,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures"

SCENARIO_SPECS: Dict[str, Dict[str, Any]] = {
    "C1": {
        "info_type": "C1_preco_medio",
        "fixture_dir": FIXTURE_ROOT / "s9_preco_medio",
        "min_sources": 2,
        "max_sources": 3,
    },
    "C2": {
        "info_type": "C2_comparacao_simples",
        "fixture_dir": FIXTURE_ROOT / "s9_comparacao",
        "min_sources": 2,
        "max_sources": 3,
    },
    "C3": {
        "info_type": "C3_checagem_factual",
        "fixture_dir": FIXTURE_ROOT / "s9_checagem_factual",
        "min_sources": 2,
        "max_sources": 3,
    },
}
INFO_TYPE_TO_SCENARIO = {spec["info_type"]: scenario for scenario, spec in SCENARIO_SPECS.items()}


def create_or_update_source(payload: SourceCreateRequest) -> Source:
    existing = storage.get_source(payload.id)
    status = existing.status if existing else SourceStatus()
    params = dict(payload.params)
    params["info_type"] = payload.info_type
    source = Source(
        id=payload.id,
        name=payload.name,
        type=payload.type,
        info_type=payload.info_type,  # type: ignore[arg-type]
        is_active=payload.is_active,
        config=SourceConfig(
            url_base=payload.url_base,
            auth_token=payload.auth_token,
            params=params,
            selected_fields=payload.selected_fields,
        ),
        status=status,
    )
    storage.save_source(source)
    metrics_s9.record_admin_action(
        "create_or_update_source", info_type=payload.info_type, scenario_id=_scenario_from_info_type(payload.info_type)
    )
    return source


def list_sources() -> List[SourceResponse]:
    output: List[SourceResponse] = []
    for src in storage.list_sources():
        info_type = getattr(src, "info_type", src.config.params.get("info_type", "fora_de_escopo"))
        output.append(
            SourceResponse(
                id=src.id,
                name=src.name,
                type=src.type,
                info_type=info_type,
                url_base=src.config.url_base,
                selected_fields=src.config.selected_fields,
                params=src.config.params,
                is_active=getattr(src, "is_active", True),
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


def set_source_active(source_id: str, active: bool) -> Optional[Source]:
    source = storage.get_source(source_id)
    if not source:
        return None
    source.is_active = active
    storage.save_source(source)
    metrics_s9.record_admin_action(
        "set_source_active",
        info_type=getattr(source, "info_type", None),
        scenario_id=_scenario_from_info_type(getattr(source, "info_type", None)),
    )
    return source


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

    records = _load_fixture_records_for_source(source_id)
    now = datetime.now(timezone.utc)
    preview: List[Dict[str, Any]] = []
    ingested = 0
    for record in records:
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
    metrics_s9.record_admin_action(
        "trigger_source_test",
        info_type=getattr(source, "info_type", None),
        scenario_id=_scenario_from_info_type(getattr(source, "info_type", None)),
    )

    status = "ok" if ingested else "erro"
    notes = None if ingested else "Verifique fixtures para esta fonte."
    return SourceTestResult(
        source_id=source_id,
        items_ingested=ingested,
        preview_items=preview,
        status=status,
        notes=notes,
    )


def ensure_default_sources() -> None:
    for scenario_id in ("C1", "C2", "C3"):
        prepare_scenario_sources(scenario_id)


def prepare_scenario_sources(scenario_id: str) -> List[str]:
    spec = SCENARIO_SPECS.get(scenario_id)
    if not spec:
        raise ValueError(f"Scenario {scenario_id} não configurado")
    fixture_dir: Path = spec["fixture_dir"]
    info_type: InfoType = spec["info_type"]  # type: ignore[assignment]
    min_sources = spec["min_sources"]
    max_sources = spec.get("max_sources", 2)
    candidates = sorted(fixture_dir.glob("*.json"))
    total_available = min(len(candidates), max_sources)
    if min_sources > total_available:
        metrics_s9.record_error("admin", "prepare_scenario_insufficient_sources")
        raise RuntimeError(f"Scenario {scenario_id} não possui fixtures suficientes (precisa de {min_sources}, disponíveis {total_available})")

    prepared: List[str] = []
    for fixture_path in candidates:
        meta, items = _load_fixture_payload(fixture_path)
        request = SourceCreateRequest(
            id=meta["id"],
            name=meta["name"],
            type=meta["type"],
            info_type=info_type,
            url_base=meta.get("url_base", f"fixture://{meta['id']}"),
            selected_fields=meta.get(
                "selected_fields",
                ["produto", "cidade", "bairro", "valor", "moeda", "pessoa", "caso", "status"],
            ),
            params=meta.get("params", {}),
            auth_token=meta.get("auth_token"),
            is_active=meta.get("is_active", True),
        )
        source = create_or_update_source(request)
        _ingest_items(source.id, items)
        prepared.append(source.id)
        if len(prepared) >= max_sources:
            break

    if len(prepared) < min_sources:
        metrics_s9.record_error("admin", "prepare_scenario_insufficient_sources")
        raise RuntimeError(f"Scenario {scenario_id} não possui fixtures suficientes (precisa de {min_sources}, carregados {len(prepared)})")
    metrics_s9.record_admin_action("prepare_scenario", info_type=info_type, scenario_id=scenario_id)
    return prepared


def prepare_sources_for_info_type(info_type: InfoType) -> List[str]:
    scenario_id = INFO_TYPE_TO_SCENARIO.get(info_type)
    if not scenario_id:
        raise ValueError(f"InfoType {info_type} não mapeado para cenário")
    return prepare_scenario_sources(scenario_id)


def ensure_fixture_sources(sources: Iterable[Source]) -> None:
    for source in sources:
        storage.save_source(source)


def _load_fixture_records_for_source(source_id: str) -> List[Dict[str, Any]]:
    for spec in SCENARIO_SPECS.values():
        candidate = spec["fixture_dir"] / f"{source_id}.json"
        if candidate.exists():
            data = json.loads(candidate.read_text(encoding="utf-8"))
            return data.get("items", [])
    return []


def _load_fixture_payload(path: Path) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "source" in data:
        return data["source"], data.get("items", [])

    # Fallback para fixtures antigas que só trazem source_id/info_type/items
    source_id = data.get("source_id") or path.stem
    info_type = data.get("info_type")
    params = data.get("params", {})
    if info_type:
        params.setdefault("info_type", info_type)
    source_meta = {
        "id": source_id,
        "name": data.get("source_name", source_id),
        "type": data.get("source_type", "precos_api_simples"),
        "url_base": data.get("url_base", f"fixture://{source_id}"),
        "selected_fields": data.get("selected_fields"),
        "params": params,
        "auth_token": data.get("auth_token"),
        "is_active": data.get("is_active", True),
    }
    if not source_meta["selected_fields"]:
        items = data.get("items", [])
        if items:
            source_meta["selected_fields"] = list(items[0].keys())
    return source_meta, data.get("items", [])


def _ingest_items(source_id: str, items: List[Dict[str, Any]]) -> None:
    now = datetime.now(timezone.utc)
    ingested = 0
    for record in items:
        item = Item(
            id=record.get("id") or storage.generate_entity_id("item"),
            source_id=source_id,
            payload=record,
            created_at=_parse_created_at(record.get("coletado_em")) or now,
        )
        storage.save_item(item)
        ingested += 1
    source = storage.get_source(source_id)
    if source:
        source.status = SourceStatus(
            last_fetch_at=now,
            last_fetch_status="ok" if ingested else "erro",
            last_fetch_error=None if ingested else "Sem itens carregados das fixtures",
            recent_items_count=ingested,
        )
        storage.save_source(source)
        metrics_s9.record_admin_action(
            "ingest_fixture_items",
            info_type=getattr(source, "info_type", None),
            scenario_id=_scenario_from_info_type(getattr(source, "info_type", None)),
        )


def _scenario_from_info_type(info_type: str | None) -> str | None:
    if not info_type:
        return None
    for scenario, spec in SCENARIO_SPECS.items():
        if spec["info_type"] == info_type:
            return scenario
    return None


def _parse_created_at(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
