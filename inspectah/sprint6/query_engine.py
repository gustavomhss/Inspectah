from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from .config import load_domain_config


@dataclass
class QueryResult:
    total: int
    page: int
    page_size: int
    items: List[Dict[str, object]]


def load_canonical_records(domain: str = "dominio_piloto") -> List[Dict[str, object]]:
    cfg = load_domain_config(domain)
    if not cfg.canonical_records_path.exists():
        raise FileNotFoundError("canonical data not found; execute collect")
    return json.loads(cfg.canonical_records_path.read_text(encoding="utf-8"))


def run_query(
    domain: str = "dominio_piloto",
    *,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    categoria: str | None = None,
    regiao: str | None = None,
    fonte: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> QueryResult:
    cfg = load_domain_config(domain)
    records = load_canonical_records(domain)
    filtered = _apply_filters(
        records,
        from_date=from_date,
        to_date=to_date,
        categoria=categoria,
        regiao=regiao,
        fonte=fonte,
        search=search,
        search_fields=cfg.search_fields or ["product_name", "notes"],
    )
    filtered.sort(key=lambda item: item.get("reported_at") or "", reverse=True)
    page = max(page, 1)
    page_size = max(min(page_size, 100), 1)
    start = (page - 1) * page_size
    end = start + page_size
    return QueryResult(total=len(filtered), page=page, page_size=page_size, items=list(filtered[start:end]))


def export_results(items: Sequence[Dict[str, object]], fmt: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    elif fmt == "csv":
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=["item_id", "product_name", "category", "unit", "price_brl", "region", "reported_at", "source_url", "notes", "sources_count"])
        writer.writeheader()
        for item in items:
            writer.writerow({field: item.get(field, "") for field in writer.fieldnames})
        path.write_text(output.getvalue(), encoding="utf-8")
    else:
        raise ValueError(f"unsupported export format {fmt}")


def format_table(items: Sequence[Dict[str, object]]) -> str:
    rows = []
    for item in items:
        price = item.get("price_brl")
        price_text = f"R$ {price:.2f}" if isinstance(price, (int, float)) else str(price)
        rows.append(
            " - ".join(
                [
                    str(item.get("item_id")),
                    str(item.get("product_name", "")),
                    price_text,
                    str(item.get("region", "")),
                    str(item.get("reported_at", "")),
                ]
            )
        )
    return "\n".join(rows)


def _apply_filters(
    records: Iterable[Dict[str, object]],
    *,
    from_date: datetime | None,
    to_date: datetime | None,
    categoria: str | None,
    regiao: str | None,
    fonte: str | None,
    search: str | None,
    search_fields: Sequence[str],
) -> List[Dict[str, object]]:
    filtered: List[Dict[str, object]] = []
    categoria_lower = categoria.lower() if categoria else None
    regiao_lower = regiao.lower() if regiao else None
    fonte_lower = fonte.lower() if fonte else None
    needle = search.lower() if search else None
    for record in records:
        reported = _parse_datetime(record.get("reported_at"))
        if from_date and (reported is None or reported < from_date):
            continue
        if to_date and (reported is None or reported > to_date):
            continue
        if categoria_lower and (record.get("category") or "").lower() != categoria_lower:
            continue
        if regiao_lower and (record.get("region") or "").lower() != regiao_lower:
            continue
        if fonte_lower:
            supporting = [entry.get("source_id", "").lower() for entry in record.get("supporting_sources", [])]
            if fonte_lower not in supporting:
                continue
        if needle:
            haystack = []
            for field in search_fields:
                value = record.get(field)
                if isinstance(value, list):
                    haystack.extend([str(item).lower() for item in value])
                elif value is not None:
                    haystack.append(str(value).lower())
            if not any(needle in fragment for fragment in haystack):
                continue
        filtered.append(record)
    return filtered


def _parse_datetime(value: object) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
