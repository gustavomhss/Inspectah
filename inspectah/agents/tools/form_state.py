from __future__ import annotations

from typing import Any, Dict, List, Optional

DEFAULT_REFRESH_INTERVAL = 1440

ALLOWED_TYPES = {"news_rss", "sports_api", "weather_api", "gossip_feed", "official_open", "data_api"}
ALLOWED_CATEGORIES = {"official", "community", "monitoring"}
STATUS_STATES = {"PROPOSED", "TESTING", "ACTIVE", "UNDER_REVIEW", "SUSPECT", "DISABLED_TEMP", "DISABLED_PERM"}

THEMES_BY_TYPE = {
    "news_rss": ["política", "governo", "economia"],
    "sports_api": ["esportes", "campeonatos", "resultados"],
    "weather_api": ["clima", "alertas", "meteorologia"],
    "gossip_feed": ["celebridades", "entretenimento"],
    "official_open": ["economia", "estatisticas", "governo"],
    "data_api": ["economia", "estatisticas", "dados"],
}
INFO_TYPES_BY_TYPE = {
    "news_rss": ["news", "headlines"],
    "sports_api": ["sports", "placares", "estatisticas"],
    "weather_api": ["weather", "alertas_clima"],
    "gossip_feed": ["gossip", "entretenimento"],
    "official_open": ["statistics", "government_data"],
    "data_api": ["statistics", "data", "api"],
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
    refresh_interval = data.get("refresh_interval")
    try:
        refresh_val = int(refresh_interval) if refresh_interval is not None else DEFAULT_REFRESH_INTERVAL
    except (TypeError, ValueError):
        refresh_val = DEFAULT_REFRESH_INTERVAL
    data["refresh_interval"] = refresh_val
    state = data.get("state")
    if state and isinstance(state, str) and state not in STATUS_STATES:
        data["state"] = None
    agent_mode = data.get("agent_mode")
    if isinstance(agent_mode, str):
        agent_mode = agent_mode.lower() in ("on", "true", "1")
    data["agent_mode"] = bool(agent_mode) if agent_mode is not None else True
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
    refresh = form_state.get("refresh_interval")
    if refresh is not None and (not isinstance(refresh, int) or refresh <= 0):
        issues.append("refresh_interval inválido.")
    return issues


def infer_type_from_message(user_message: str) -> Optional[str]:
    text = user_message.lower()
    if any(word in text for word in ["esporte", "jogo", "campeonato"]):
        return "sports_api"
    if any(word in text for word in ["clima", "tempo", "meteorologia"]):
        return "weather_api"
    if any(word in text for word in ["fofoca", "celebridade", "entretenimento"]):
        return "gossip_feed"
    if any(word in text for word in ["oficial", "ibge", "governo", "portal oficial"]):
        return "official_open"
    if any(word in text for word in ["notícia", "noticias", "jornal", "portal"]):
        return "news_rss"
    return None
