from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import datetime
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .config_loader import FieldMapping, SourceConfig


@dataclass(slots=True)
class PreviewResult:
    source_id: str
    ok: bool
    records: int
    fields_total: int
    fields_resolved: int
    field_success: float
    samples: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "ok": self.ok,
            "metrics": {
                "records": self.records,
                "fields_total": self.fields_total,
                "fields_resolved": self.fields_resolved,
                "field_success": self.field_success,
            },
            "samples": self.samples,
            "errors": self.errors,
        }


def run_dry_run(config: SourceConfig, sample_size: int = 5) -> PreviewResult:
    try:
        raw_records = load_sample_records(config)
    except Exception as exc:  # pragma: no cover - defensive
        return PreviewResult(
            source_id=config.id,
            ok=False,
            records=0,
            fields_total=0,
            fields_resolved=0,
            field_success=0.0,
            errors=[str(exc)],
        )
    limited_records = raw_records[:sample_size]
    samples: List[Dict[str, Any]] = []
    fields_total = len(config.fields) * len(limited_records)
    fields_resolved = 0
    for idx, record in enumerate(limited_records):
        preview_entry: Dict[str, Any] = {"record_index": idx}
        resolved_for_record = 0
        for mapping in config.fields:
            value = extract_path(record, mapping.path)
            if value is None and mapping.default is not None:
                value = mapping.default
            typed_value = _coerce_value(value, mapping.type)
            if typed_value is not None:
                resolved_for_record += 1
            preview_entry[mapping.name] = typed_value
        fields_resolved += resolved_for_record
        samples.append(preview_entry)
    field_success = (fields_resolved / fields_total) if fields_total else 0.0
    ok = bool(limited_records) and field_success >= 0.95
    return PreviewResult(
        source_id=config.id,
        ok=ok,
        records=len(limited_records),
        fields_total=fields_total,
        fields_resolved=fields_resolved,
        field_success=field_success,
        samples=samples,
        errors=[],
    )


def load_sample_records(config: SourceConfig) -> List[Dict[str, Any]]:
    return _load_records(config)


def _load_records(config: SourceConfig) -> List[Dict[str, Any]]:
    sample_path = config.sample_file
    if not sample_path.exists():
        raise FileNotFoundError(f"sample file not found for {config.id}: {sample_path}")
    loaders = {
        "rss": _load_rss,
        "api": _load_api,
        "html": _load_html,
    }
    loader = loaders.get(config.type)
    if loader is None:
        raise ValueError(f"unsupported source type {config.type}")
    return loader(sample_path, config)


def _load_rss(path: Path, config: SourceConfig) -> List[Dict[str, Any]]:
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    channel = root.find("channel")
    if channel is None:
        raise ValueError("RSS feed missing channel element")
    records: List[Dict[str, Any]] = []
    for item in channel.findall("item"):
        entry = {
            "item": {
                "title": (item.findtext("title") or "").strip(),
                "link": (item.findtext("link") or "").strip(),
                "published": (item.findtext("pubDate") or item.findtext("published") or "").strip(),
                "description": (item.findtext("description") or "").strip(),
            },
            "metadata": {
                "source_name": config.name,
            },
        }
        records.append(entry)
    return records


def _load_api(path: Path, config: SourceConfig) -> List[Dict[str, Any]]:  # noqa: ARG001 - config reserved for future options
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        if "items" in payload and isinstance(payload["items"], list):
            data = payload["items"]
        else:
            data = list(payload.values())[0] if payload else []
    elif isinstance(payload, list):
        data = payload
    else:
        raise ValueError("API sample must be list or list inside 'items'")
    if not isinstance(data, list):
        raise ValueError("API payload does not contain a list of items")
    records: List[Dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        records.append({"payload": item})
    return records


def _load_html(path: Path, config: SourceConfig) -> List[Dict[str, Any]]:  # noqa: ARG001 - config reserved
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    elements = root.findall(".//div[@class='product']")
    records: List[Dict[str, Any]] = []
    for elem in elements:
        record = {
            "product": {
                "sku": elem.get("data-sku", "").strip(),
                "name": (elem.findtext("span[@class='name']") or "").strip(),
                "price": (elem.findtext("span[@class='price']") or "").strip(),
                "location": (elem.findtext("span[@class='location']") or "").strip(),
                "observed_at": (elem.findtext("time[@class='observed']") or "").strip(),
            }
        }
        records.append(record)
    return records


def extract_path(container: Any, path: str) -> Any:
    current = container
    for raw_part in path.split('.'):
        part, index = _split_index(raw_part)
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
        if index is not None:
            if isinstance(current, list) and 0 <= index < len(current):
                current = current[index]
            else:
                return None
    return current


def _split_index(part: str) -> Tuple[str, int | None]:
    if '[' in part and part.endswith(']'):
        name, idx = part[:-1].split('[', 1)
        try:
            return name, int(idx)
        except ValueError:
            return part, None
    return part, None


def _coerce_value(value: Any, target_type: str) -> Any:
    if value is None:
        return None
    target = target_type.lower()
    if target in {"string", "text"}:
        text = str(value).strip()
        return text or None
    if target in {"number", "float"}:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    if target in {"integer", "int"}:
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None
    if target in {"datetime", "timestamp"}:
        text = str(value).strip()
        if not text:
            return None
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            return parsed.isoformat()
        except ValueError:
            return text
    if target in {"boolean", "bool"}:
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text in {"true", "1", "yes"}:
            return True
        if text in {"false", "0", "no"}:
            return False
        return None
    return value
