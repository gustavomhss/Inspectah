from __future__ import annotations

from typing import Dict

from .schemas import SourceConfigHTTPAPI, SourceConfigRSS, SourceConfigStaticDataset, SourceCreate

MIN_REFRESH_INTERVAL = 15
MAX_REFRESH_INTERVAL = 10080
OFFICIAL_OPEN_TYPE = "official_open"
DATA_API_TYPE = "data_api"

REQUIRED_BY_TYPE = {
    "news_rss": ["endpoint"],
    "gossip_feed": ["endpoint"],
    "sports_api": ["endpoint"],
    "weather_api": ["endpoint"],
    "gov_record": ["endpoint"],
    "legislation": ["endpoint"],
    "science_dataset": ["endpoint"],
    "static_dataset": ["endpoint"],
    OFFICIAL_OPEN_TYPE: ["endpoint"],
    DATA_API_TYPE: ["endpoint"],
}


def validate_source_config(source_type: str, config: Dict) -> Dict:
    """Valida a config conforme o tipo; retorna config normalizada."""
    normalized = dict(config or {})
    endpoint_val = normalized.get("endpoint") or normalized.get("url_base")
    required = REQUIRED_BY_TYPE.get(source_type, [])
    missing = [field for field in required if not endpoint_val and not normalized.get(field)]
    # Em desenvolvimento, permitimos que endpoints sejam validados adiante para não bloquear criação simples
    if missing and endpoint_val:
        missing = []

    if source_type in {"news_rss", "gossip_feed"}:
        SourceConfigRSS(**normalized)
    elif source_type in {"sports_api", "weather_api", "gov_record", "legislation"}:
        SourceConfigHTTPAPI(**normalized)
    elif source_type in {"science_dataset", "static_dataset"}:
        SourceConfigStaticDataset(**normalized)
    else:
        # fallback genérico
        SourceConfigHTTPAPI(**normalized)
    return normalized


def validate_source_payload(payload: SourceCreate) -> None:
    """Valida payload de criação/edição conforme ontologia básica."""
    if not payload.name.strip():
        raise ValueError("Nome da fonte é obrigatório")
    if not payload.type:
        raise ValueError("Tipo da fonte é obrigatório")
    if payload.redundancy_role and not payload.redundancy_group:
        raise ValueError("redundancy_role exige redundancy_group")
    if payload.refresh_interval is not None:
        if payload.refresh_interval < MIN_REFRESH_INTERVAL or payload.refresh_interval > MAX_REFRESH_INTERVAL:
            raise ValueError("refresh_interval fora do intervalo permitido")
    if payload.type == OFFICIAL_OPEN_TYPE:
        if not payload.description.strip():
            raise ValueError("Fontes oficiais abertas exigem descrição")
        if not payload.endpoint:
            raise ValueError("Fontes oficiais abertas exigem endpoint público")
        if payload.auth_type not in ("none", "", None):
            raise ValueError("Fontes oficiais abertas não devem exigir autenticação")
    if payload.type == DATA_API_TYPE:
        if not payload.endpoint:
            raise ValueError("APIs de dados exigem um endpoint público ou documentado.")
        lowered = payload.endpoint.lower()
        if "api" not in lowered and "/v1" not in lowered and "/v2" not in lowered and "?" not in lowered:
            raise ValueError("Endpoint de API de dados parece inválido; inclua um caminho de API (ex.: /api/v1/...).")
