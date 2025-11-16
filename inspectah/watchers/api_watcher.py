"""Watcher API baseado em fixtures JSON."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List


def collect(source: Dict[str, Any], *, fixtures_base: Path) -> List[Dict[str, Any]]:
    fixture = source.get("parse_spec", {}).get("fixture")
    if not fixture:
        raise ValueError("parse_spec.fixture obrigatório para watcher API")
    path = fixtures_base / fixture
    payload = json.loads(path.read_text())
    if not isinstance(payload, list):
        raise ValueError("Fixture API deve ser uma lista de itens")
    items: List[Dict[str, Any]] = []
    for idx, entry in enumerate(payload):
        item_id = entry.get("id") or f"api-{idx}"
        headline = entry.get("headline") or "Sem título"
        text = entry.get("summary") or ""
        published_at = entry.get("published_at") or dt.datetime.utcnow().isoformat() + "Z"
        items.append(
            {
                "source_id": source["id"],
                "item_id": item_id,
                "headline": headline,
                "published_at": published_at,
                "raw_content": json.dumps(entry).encode("utf-8"),
                "text": text,
                "meta": {
                    "watcher_type": "api",
                    "fetched_at": published_at,
                    "request_url": source.get("url"),
                    "facts": entry.get("facts", {}),
                },
            }
        )
    return items
