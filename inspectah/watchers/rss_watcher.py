"""Watcher RSS usando fixtures locais."""
from __future__ import annotations

import datetime as dt
import email.utils
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List


def collect(source: Dict[str, Any], *, fixtures_base: Path) -> List[Dict[str, Any]]:
    fixture = source.get("parse_spec", {}).get("fixture")
    if not fixture:
        raise ValueError("parse_spec.fixture obrigatório para watcher RSS")
    path = fixtures_base / fixture
    tree = ET.parse(path)
    root = tree.getroot()
    items: List[Dict[str, Any]] = []
    for idx, item in enumerate(root.findall(".//item")):
        guid = item.findtext("guid") or f"rss-{idx}"
        title = item.findtext("title") or "Sem título"
        published_raw = item.findtext("pubDate")
        published_at = _parse_pubdate(published_raw)
        description = item.findtext("description") or ""
        items.append(
            {
                "source_id": source["id"],
                "item_id": guid,
                "headline": title,
                "published_at": published_at,
                "raw_content": description.encode("utf-8"),
                "text": description,
                "meta": {
                    "watcher_type": "rss",
                    "fetched_at": published_at,
                    "request_url": source.get("url"),
                },
            }
        )
    return items


def _parse_pubdate(value: str | None) -> str:
    if not value:
        return dt.datetime.utcnow().isoformat() + "Z"
    try:
        parsed = email.utils.parsedate_to_datetime(value)
    except Exception:
        return dt.datetime.utcnow().isoformat() + "Z"
    return parsed.replace(tzinfo=dt.timezone.utc).isoformat().replace("+00:00", "Z")
