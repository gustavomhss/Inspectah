from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.core import storage
from app.core.models import Item, Source, SourceConfig, SourceStatus

from .schemas import (
    AdminCaseDetail,
    AdminCaseSummary,
    AdminHealth,
    AdminAnchorSummary,
    AdminAnchorsSection,
    AdminCaseXRay,
    AdminCommitteeDecision,
    AdminCommitteesSection,
    AdminDebunkerSection,
    AdminEvidenceSection,
    AdminEvidenceSummary,
    AdminSourceDetail,
    AdminSourceHistoryEntry,
    AdminSourceStatus,
    AdminSourceSummary,
    AdminTimelineEvent,
    AdminTimelineResponse,
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
S19_FIXTURE_DIR = REPO_ROOT / "Sprint 19" / "fixtures"

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


def _parse_datetime(value: Union[str, datetime, None]) -> Optional[datetime]:
    """Parse ISO-like datetime strings, returning None on failure."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def _map_severity(raw_status: Optional[str]) -> Optional[str]:
    if not raw_status:
        return None
    status = str(raw_status).lower()
    if status in {"critical", "critico", "falha", "failed", "ancora_falhou"}:
        return "critical"
    if status in {"incerto", "contestacao", "warning", "atencao", "degraded"}:
        return "warning"
    return "info"


def _build_timeline_event(entry: Dict[str, Any], case_id: str) -> AdminTimelineEvent:
    ts = _parse_datetime(entry.get("timestamp") or entry.get("event_timestamp"))
    event_type = entry.get("event_type") or entry.get("tipo_evento") or entry.get("titulo") or "evento"
    severity = entry.get("severity") or _map_severity(entry.get("status_debunker"))
    summary = entry.get("summary") or entry.get("resumo") or entry.get("titulo") or ""
    source = entry.get("source") or entry.get("fonte") or entry.get("source_id")
    base_id = (
        entry.get("id")
        or entry.get("id_evento")
        or f"{case_id}:{event_type}:{ts.isoformat() if ts else 'sem_timestamp'}"
    )
    return AdminTimelineEvent(
        id=str(base_id),
        case_id=entry.get("case_id") or entry.get("id_caso") or case_id,
        timestamp=ts or datetime.utcnow(),
        event_type=str(event_type),
        severity=severity,
        source=source,
        summary=str(summary),
    )


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


# --- S18 admin console helpers ---


def _map_source_status(status: SourceStatus) -> AdminSourceStatus:
    health = "healthy"
    if status.last_fetch_status and status.last_fetch_status not in {"ok", "success"}:
        health = "degraded"
    return AdminSourceStatus(
        status=health,
        last_checked_at=status.last_fetch_at,
        recent_items_count=status.recent_items_count,
        last_error=status.last_fetch_error,
    )


def list_admin_sources() -> List[AdminSourceSummary]:
    entries: List[AdminSourceSummary] = []
    for src in storage.list_sources():
        entries.append(
            AdminSourceSummary(
                id=src.id,
                name=src.name,
                type=src.type,
                info_type=src.info_type or src.config.params.get("info_type", ""),
                is_active=getattr(src, "is_active", True),
                status=_map_source_status(src.status),
            )
        )
    return entries


def get_admin_source(source_id: str) -> Optional[AdminSourceDetail]:
    src = storage.get_source(source_id)
    if not src:
        return None
    history = [
        AdminSourceHistoryEntry(
            checked_at=src.status.last_fetch_at,
            status=_map_source_status(src.status).status,
            error=src.status.last_fetch_error,
        )
    ]
    return AdminSourceDetail(
        id=src.id,
        name=src.name,
        type=src.type,
        info_type=src.info_type or src.config.params.get("info_type", ""),
        is_active=getattr(src, "is_active", True),
        status=_map_source_status(src.status),
        url_base=src.config.url_base,
        history=history,
    )


def _cases_snapshot_path() -> Path:
    return REPO_ROOT / "out" / "evidence" / "S12_G2" / "cases_snapshot.json"


def _timelines_snapshot_path() -> Path:
    return REPO_ROOT / "out" / "evidence" / "S12_G2" / "timelines_snapshot.json"


def _load_cases_snapshot() -> List[Dict[str, Any]]:
    path = _cases_snapshot_path()
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _load_timelines_snapshot() -> Dict[str, List[Dict[str, Any]]]:
    path = _timelines_snapshot_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _sanitize_case_id(case_id: str) -> str:
    return case_id.replace(":", "_").replace("/", "_").replace("-", "_")


def _load_json_if_exists(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _load_timeline_fixture(case_id: str) -> Optional[Dict[str, Any]]:
    filename = f"timeline_expected_{_sanitize_case_id(case_id)}.json"
    return _load_json_if_exists(S19_FIXTURE_DIR / filename)


def _load_xray_fixture(case_id: str) -> Optional[Dict[str, Any]]:
    filename = f"xray_expected_{_sanitize_case_id(case_id)}.json"
    return _load_json_if_exists(S19_FIXTURE_DIR / filename)


def list_admin_cases() -> List[AdminCaseSummary]:
    cases = _load_cases_snapshot()
    timelines = _load_timelines_snapshot()
    summaries: List[AdminCaseSummary] = []
    for entry in cases:
        case_id = entry.get("id_caso", "")
        timeline = timelines.get(case_id, [])
        key_sources = sorted({ev.get("fonte", "") for ev in timeline if ev.get("fonte")})
        summaries.append(
            AdminCaseSummary(
                id=case_id,
                title=entry.get("titulo", ""),
                category=entry.get("dominio", ""),
                status=entry.get("status", "incerto"),
                risk=entry.get("metadata", {}).get("risk"),
                updated_at=_parse_datetime(entry.get("updated_at")),
                key_sources=key_sources,
            )
        )
    return summaries


def get_admin_case(case_id: str) -> Optional[AdminCaseDetail]:
    cases = {entry.get("id_caso"): entry for entry in _load_cases_snapshot()}
    entry = cases.get(case_id)
    if not entry:
        return None
    timelines = _load_timelines_snapshot()
    timeline = timelines.get(case_id, [])
    top_evidence = timeline[:5]
    summary = AdminCaseSummary(
        id=case_id,
        title=entry.get("titulo", ""),
        category=entry.get("dominio", ""),
        status=entry.get("status", "incerto"),
        risk=entry.get("metadata", {}).get("risk"),
        updated_at=_parse_datetime(entry.get("updated_at")),
        key_sources=sorted({ev.get("fonte", "") for ev in timeline if ev.get("fonte")}),
    )
    summary_dict = dict(summary.__dict__)
    return AdminCaseDetail(
        **summary_dict,
        description=entry.get("descricao", ""),
        top_evidence=top_evidence,
    )


def list_case_timeline(case_id: str) -> Optional[AdminTimelineResponse]:
    fixture = _load_timeline_fixture(case_id)
    raw_events: List[Dict[str, Any]]
    if fixture:
        raw_events = fixture.get("events", [])
    else:
        raw_events = _load_timelines_snapshot().get(case_id, [])
    if not raw_events:
        return None

    events = [_build_timeline_event(entry, case_id) for entry in raw_events]
    events.sort(key=lambda ev: ev.timestamp)
    return AdminTimelineResponse(case_id=case_id, events=events)


def get_admin_health() -> AdminHealth:
    sources = list_admin_sources()
    cases = list_admin_cases()
    healthy = sum(1 for src in sources if src.status.status == "healthy")
    degraded = len(sources) - healthy
    cases_attention = sum(1 for c in cases if c.status not in {"estavel", "ok"})
    cases_stable = len(cases) - cases_attention
    integrations = {
        "truth_db": "ok",
        "watchers": "ok" if degraded == 0 else "warn",
    }
    return AdminHealth(
        sources_total=len(sources),
        sources_healthy=healthy,
        sources_degraded=degraded,
        cases_total=len(cases),
        cases_attention=cases_attention,
        cases_stable=cases_stable,
        integrations=integrations,
    )


def _build_debunker_section(data: Dict[str, Any], fallback_risk: Optional[str]) -> AdminDebunkerSection:
    explanation = data.get("explanation") or data.get("resumo") or "Avaliação indisponível no momento."
    flags = data.get("flags") or []
    return AdminDebunkerSection(
        risk_level=data.get("risk_level") or fallback_risk,
        explanation=str(explanation),
        flags=flags if isinstance(flags, list) else [str(flags)],
        last_evaluated_at=_parse_datetime(data.get("last_evaluated_at")),
    )


def _build_committees_section(data: Dict[str, Any]) -> AdminCommitteesSection:
    decisions_payload = data.get("decisions") or []
    decisions: List[AdminCommitteeDecision] = []
    for decision in decisions_payload:
        decisions.append(
            AdminCommitteeDecision(
                name=str(decision.get("name", "comite")),
                verdict=str(decision.get("verdict", "indefinido")),
                confidence=None if decision.get("confidence") is None else str(decision.get("confidence")),
                rationale=decision.get("rationale"),
                decided_at=_parse_datetime(decision.get("decided_at")),
            )
        )
    summary = data.get("summary") or "Sem deliberações registradas."
    return AdminCommitteesSection(summary=str(summary), decisions=decisions)


def _build_anchors_section(data: Dict[str, Any]) -> AdminAnchorsSection:
    anchors_data = data.get("anchors") or []
    anchors: List[AdminAnchorSummary] = []
    for anchor in anchors_data:
        issues = anchor.get("issues") or []
        anchors.append(
            AdminAnchorSummary(
                name=str(anchor.get("name", "ancora")),
                status=str(anchor.get("status", "desconhecido")),
                last_check=_parse_datetime(anchor.get("last_check")),
                reliability=anchor.get("reliability"),
                issues=issues if isinstance(issues, list) else [str(issues)],
            )
        )
    summary = data.get("summary") or "Sem dados de âncoras disponíveis."
    return AdminAnchorsSection(summary=str(summary), anchors=anchors)


def _build_evidence_section(data: Dict[str, Any], timeline_events: List[AdminTimelineEvent]) -> AdminEvidenceSection:
    evidences_data = data.get("evidences") or []
    evidences: List[AdminEvidenceSummary] = []
    for entry in evidences_data:
        evidences.append(
            AdminEvidenceSummary(
                id=str(entry.get("id", "")),
                type=str(entry.get("type", "desconhecido")),
                source=entry.get("source"),
                title=entry.get("title"),
                snippet=entry.get("snippet"),
                url=entry.get("url"),
                captured_at=_parse_datetime(entry.get("captured_at")),
            )
        )
    if not evidences and timeline_events:
        for ev in timeline_events[:3]:
            evidences.append(
                AdminEvidenceSummary(
                    id=ev.id,
                    type=ev.event_type,
                    source=ev.source,
                    title=ev.summary or ev.event_type,
                    snippet=ev.summary,
                    captured_at=ev.timestamp,
                )
            )
    summary = data.get("summary") or "Evidências principais consolidadas da timeline."
    return AdminEvidenceSection(summary=str(summary), evidences=evidences)


def _build_xray_from_dict(
    payload: Dict[str, Any], case_entry: Optional[Dict[str, Any]], timeline: Optional[AdminTimelineResponse]
) -> AdminCaseXRay:
    case_id = payload.get("case_id") or (case_entry or {}).get("id_caso") or "desconhecido"
    title = payload.get("title") or (case_entry or {}).get("titulo") or case_id
    category = payload.get("category") or (case_entry or {}).get("dominio")
    status = payload.get("status") or (case_entry or {}).get("status") or "incerto"
    risk = payload.get("risk") or (case_entry or {}).get("metadata", {}).get("risk")
    summary = payload.get("summary") or (case_entry or {}).get("descricao") or ""

    debunker = _build_debunker_section(payload.get("debunker", {}), risk)
    committees = _build_committees_section(payload.get("committees", {}))
    anchors = _build_anchors_section(payload.get("anchors", {}))
    evidences = _build_evidence_section(payload.get("evidences", {}), timeline.events if timeline else [])

    return AdminCaseXRay(
        case_id=case_id,
        title=title,
        category=category,
        status=status,
        risk=risk,
        summary=summary,
        debunker=debunker,
        committees=committees,
        anchors=anchors,
        evidences=evidences,
    )


def _build_default_xray(case_entry: Dict[str, Any], timeline: Optional[AdminTimelineResponse]) -> AdminCaseXRay:
    case_id = case_entry.get("id_caso", "")
    risk = case_entry.get("metadata", {}).get("risk")
    debunker = AdminDebunkerSection(
        risk_level=risk,
        explanation="Avaliação consolidada a partir de snapshots do Sistema de Blocos.",
        flags=[],
        last_evaluated_at=_parse_datetime(case_entry.get("updated_at")),
    )
    committees = AdminCommitteesSection(
        summary="Decisões consolidadas não detalhadas no snapshot da S12.",
        decisions=[],
    )
    anchors = AdminAnchorsSection(
        summary="Sem âncoras detalhadas disponíveis; exibindo estado padrão.",
        anchors=[],
    )
    evidences = _build_evidence_section({"summary": "Evidências derivadas da timeline."}, timeline.events if timeline else [])
    return AdminCaseXRay(
        case_id=case_id,
        title=case_entry.get("titulo", case_id),
        category=case_entry.get("dominio"),
        status=case_entry.get("status", "incerto"),
        risk=risk,
        summary=case_entry.get("descricao", ""),
        debunker=debunker,
        committees=committees,
        anchors=anchors,
        evidences=evidences,
    )


def get_case_xray(case_id: str) -> Optional[AdminCaseXRay]:
    cases = {entry.get("id_caso"): entry for entry in _load_cases_snapshot()}
    case_entry = cases.get(case_id)
    timeline = list_case_timeline(case_id)

    fixture = _load_xray_fixture(case_id)
    if fixture:
        return _build_xray_from_dict(fixture, case_entry, timeline)

    if not case_entry:
        return None

    return _build_default_xray(case_entry, timeline)


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
