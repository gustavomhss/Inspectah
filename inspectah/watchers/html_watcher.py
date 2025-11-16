"""Watcher HTML baseado em fixtures locais."""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Any, Dict, List

ARTICLE_PATTERN = re.compile(
    r"<article[^>]*data-id=\"(?P<id>[^\"]+)\"[^>]*data-date=\"(?P<date>[^\"]+)\"[^>]*>.*?<h1>(?P<title>[^<]+)</h1>.*?<p>(?P<body>[^<]+)</p>",
    re.IGNORECASE | re.DOTALL,
)


def collect(source: Dict[str, Any], *, fixtures_base: Path) -> List[Dict[str, Any]]:
    fixture = source.get("parse_spec", {}).get("fixture")
    if not fixture:
        raise ValueError("parse_spec.fixture obrigatório para watcher HTML")
    path = fixtures_base / fixture
    html = path.read_text()
    items: List[Dict[str, Any]] = []
    for match in ARTICLE_PATTERN.finditer(html):
        body = match.group("body").strip()
        published_at = match.group("date")
        items.append(
            {
                "source_id": source["id"],
                "item_id": match.group("id"),
                "headline": match.group("title").strip(),
                "published_at": published_at,
                "raw_content": body.encode("utf-8"),
                "text": body,
                "meta": {
                    "watcher_type": "html",
                    "fetched_at": published_at,
                    "request_url": source.get("url"),
                },
            }
        )
    return items
