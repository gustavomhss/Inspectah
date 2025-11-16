from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .config import SourceConfig


def load_records(source: SourceConfig) -> List[Dict[str, Any]]:
    loaders = {
        "rss": _load_rss,
        "api": _load_api,
        "api_json": _load_api,
        "html": _load_html,
        "html_plain": _load_html,
    }
    loader = loaders.get(source.type)
    if loader is None:
        raise ValueError(f"unsupported source type {source.type}")
    return loader(source.sample_file)


def _load_rss(path: Path) -> List[Dict[str, Any]]:
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    channel = root.find("channel")
    if channel is None:
        raise ValueError("rss feed missing channel element")
    records: List[Dict[str, Any]] = []
    for item in channel.findall("item"):
        records.append(
            {
                "item": {
                    "title": _text(item.findtext("title")),
                    "guid": _text(item.findtext("guid") or item.findtext("link")),
                    "link": _text(item.findtext("link")),
                    "category": _text(item.findtext("category")),
                    "unit": _text(item.findtext("unit")),
                    "price": _text(item.findtext("price")),
                    "region": _text(item.findtext("region")),
                    "published": _normalize_datetime(item.findtext("pubDate")),
                    "notes": _text(item.findtext("notes") or item.findtext("description")),
                }
            }
        )
    return records


def _load_api(path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        if isinstance(payload.get("items"), list):
            data = payload["items"]
        else:
            data = next(iter(payload.values())) if payload else []
    elif isinstance(payload, list):
        data = payload
    else:
        raise ValueError("api payload must be list or contain list")
    return [{"payload": item} for item in data if isinstance(item, dict)]


def _load_html(path: Path) -> List[Dict[str, Any]]:
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    records: List[Dict[str, Any]] = []
    for node in root.findall(".//div[@class='product']"):
        records.append(
            {
                "product": {
                    "item_id": node.get("data-item-id", "").strip(),
                    "category": node.get("data-category", "").strip(),
                    "region": node.get("data-region", "").strip(),
                    "name": _child_text(node, "span[@class='name']"),
                    "unit": _child_text(node, "span[@class='unit']"),
                    "price": _child_text(node, "span[@class='price']"),
                    "observed_at": _normalize_datetime(_child_text(node, "time[@class='observed']")),
                    "source_url": _child_attr(node, "a[@class='source']", "href"),
                    "notes": _child_text(node, "p[@class='notes']"),
                }
            }
        )
    return records


def _child_text(node: ET.Element, selector: str) -> str:
    found = node.find(selector)
    return (found.text or "").strip() if found is not None else ""


def _child_attr(node: ET.Element, selector: str, attr: str) -> str:
    found = node.find(selector)
    if found is None:
        return ""
    return (found.get(attr) or "").strip()


def _text(value: str | None) -> str:
    return value.strip() if isinstance(value, str) else ""


def _normalize_datetime(value: str | None) -> str:
    text = _text(value)
    if not text:
        return ""
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).isoformat()
    except ValueError:
        return text
