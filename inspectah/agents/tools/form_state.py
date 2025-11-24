from __future__ import annotations

from typing import Any, Dict, List

ALLOWED_TYPES = {"news_rss", "sports_api", "weather_api", "gossip_feed"}
ALLOWED_CATEGORIES = {"official", "community", "monitoring"}
THEMES_BY_TYPE = {
    "news_rss": ["política", "governo", "economia"],
    "sports_api": ["esportes", "campeonatos", "resultados"],
    "weather_api": ["clima", "alertas", "meteorologia"],
    "gossip_feed": ["celebridades", "entretenimento"],
}
INFO_TYPES_BY_TYPE = {
    "news_rss": ["news", "headlines"],
    "sports_api": ["sports", "placares", "estatisticas"],
    "weather_api": ["weather", "alertas_clima"],
    "gossip_feed": ["gossip", "entretenimento"],
}


def normalize_form_state(form_state: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(form_state or {})
    slug = data.get("slug") or ""
    data["slug"] = slug.strip().lower().replace(" ", "-")
    name = data.get("name") or ""
    data["name"] = name.strip()
    ftype = (data.get("type") or "").strip()
    data["type"] = ftype
    category = (data.get("category") or "").strip() or "official"
    data["category"] = category
    themes = data.get("themes") or []
    info_types = data.get("info_types") or []
    if isinstance(themes, str):
        themes = [t.strip() for t in themes.split(",") if t.strip()]
    if isinstance(info_types, str):
        info_types = [t.strip() for t in info_types.split(",") if t.strip()]
    data["themes"] = list(themes)
    data["info_types"] = list(info_types)
    endpoint = data.get("endpoint") or ""
    data["endpoint"] = endpoint.strip()
    description = data.get("description") or ""
    data["description"] = description.strip()
    return data


def validate_form_state(form_state: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    ftype = form_state.get("type")
    if not ftype:
        issues.append("Tipo da fonte é obrigatório.")
    elif ftype not in ALLOWED_TYPES:
        issues.append("Tipo de fonte inválido para a Fase 1.")
    category = form_state.get("category")
    if category and category not in ALLOWED_CATEGORIES:
        issues.append("Categoria informada não é reconhecida.")
    endpoint = form_state.get("endpoint")
    if not endpoint:
        issues.append("Endpoint/URL base é obrigatório.")
    themes = form_state.get("themes") or []
    if ftype in THEMES_BY_TYPE:
        allowed = set(THEMES_BY_TYPE[ftype])
        invalid = [t for t in themes if t not in allowed]
        if invalid:
            issues.append("Temas não compatíveis com o tipo selecionado.")
    info_types = form_state.get("info_types") or []
    if ftype in INFO_TYPES_BY_TYPE:
        allowed_info = set(INFO_TYPES_BY_TYPE[ftype])
        invalid_info = [t for t in info_types if t not in allowed_info]
        if invalid_info:
            issues.append("Info types não compatíveis com o tipo selecionado.")
    return issues
