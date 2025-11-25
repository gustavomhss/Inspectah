from __future__ import annotations

import re
from typing import Dict, List, Optional

DEFAULT_REFRESH_BY_TYPE = {
    "news_rss": 180,
    "sports_api": 120,
    "weather_api": 60,
    "gossip_feed": 720,
    "official_open": 1440,
    "data_api": 240,
}


def extract_url(text: str) -> Optional[str]:
    if not text:
        return None
    match = re.search(r"https?://\S+", text)
    return match.group(0) if match else None


def infer_type_from_url(url: str) -> Optional[str]:
    if not url:
        return None
    lower = url.lower()
    if "rss" in lower or lower.endswith(".xml"):
        return "news_rss"
    if "/api/" in lower or lower.startswith("http://api.") or lower.startswith("https://api.") or any(
        token in lower for token in ["/v1", "/v2", "graphql", "swagger"]
    ):
        return "data_api"
    if any(word in lower for word in ["clima", "tempo", "meteo"]):
        return "weather_api"
    if any(word in lower for word in ["esporte", "sport", "placar"]):
        return "sports_api"
    if any(word in lower for word in ["gov", "ibge", "prefeitura", "dados.gov"]):
        return "official_open"
    return None


def infer_type_from_text(text: str) -> Optional[str]:
    lower = (text or "").lower()
    if any(word in lower for word in ["api de dados", "data api", "api rest", "json", "swagger", "graphql"]):
        return "data_api"
    if any(word in lower for word in ["oficial aberta", "official open", "ibge", "governo", "portal oficial"]):
        return "official_open"
    if any(word in lower for word in ["esporte", "jogo", "campeonato"]):
        return "sports_api"
    if any(word in lower for word in ["clima", "tempo", "meteorologia"]):
        return "weather_api"
    if any(word in lower for word in ["fofoca", "celebridade", "entretenimento"]):
        return "gossip_feed"
    if any(word in lower for word in ["notícia", "notícias", "noticias", "jornal", "portal"]):
        return "news_rss"
    return None


def suggest_endpoint(url: Optional[str], current: Optional[str]) -> Optional[str]:
    if current:
        return current
    return url


def suggest_themes(source_type: Optional[str]) -> List[str]:
    options: Dict[str, List[str]] = {
        "news_rss": ["política", "economia"],
        "sports_api": ["esportes"],
        "weather_api": ["clima"],
        "gossip_feed": ["entretenimento"],
        "official_open": ["economia", "estatisticas"],
        "data_api": ["economia", "estatisticas", "mercados"],
    }
    return options.get(source_type or "", [])


def suggest_info_types(source_type: Optional[str]) -> List[str]:
    options: Dict[str, List[str]] = {
        "news_rss": ["news"],
        "sports_api": ["sports"],
        "weather_api": ["weather"],
        "gossip_feed": ["gossip"],
        "official_open": ["statistics"],
        "data_api": ["data", "statistics"],
    }
    return options.get(source_type or "", [])


def suggest_refresh_interval(source_type: Optional[str]) -> int:
    return DEFAULT_REFRESH_BY_TYPE.get(source_type or "", 1440)


def feed_candidates(url: Optional[str]) -> List[str]:
    """Gera candidatos de feed sem acessar rede."""
    base = (url or "").split("?")[0].rstrip("/")
    if not base:
        return []
    suffixes = ["", "/rss", "/rss.xml", "/feed", "/feeds", "/rss/ultimas", "/rss/noticias", "/index.xml"]
    candidates = []
    for suf in suffixes:
        candidate = f"{base}{suf}"
        if candidate not in candidates:
            candidates.append(candidate)
    return candidates
