from __future__ import annotations

from typing import Dict

from .schemas import SourceConfigHTTPAPI, SourceConfigRSS, SourceConfigStaticDataset, SourceCreate

REQUIRED_BY_TYPE = {
    "news_rss": ["endpoint"],
    "gossip_feed": ["endpoint"],
    "sports_api": ["endpoint"],
    "weather_api": ["endpoint"],
    "gov_record": ["endpoint"],
    "legislation": ["endpoint"],
    "science_dataset": ["endpoint"],
    "static_dataset": ["endpoint"],
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
