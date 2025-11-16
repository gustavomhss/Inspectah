"""Pipeline baseada em fixtures para executar S0→S4."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

from inspectah.evidence import builder, verifier
from inspectah.equivalence_key import generate_equivalence_key
from inspectah.indexer.indexer import LocalIndexer
from inspectah.models import InspectahItem
from inspectah.normalizer import normalizer
from inspectah.watchers.engine import run_watchers

STATE_ORDER = ["S0", "S1", "S2", "S3", "S4"]


def _default_summary() -> Dict[str, Any]:
    return {
        "items_total": 0,
        "bundles_total": 0,
        "items_by_state": {state: 0 for state in STATE_ORDER},
        "items_by_source": {},
        "failed_bundles": [],
        "failed_normalizer": [],
    }


def _metric_subject_from_item(raw_item: Dict[str, Any]) -> tuple[str, str]:
    meta = raw_item.get("meta", {})
    facts = meta.get("facts", {})
    headline = raw_item.get("headline") or "item"
    metric = facts.get("metric") or headline
    subject = facts.get("subject") or meta.get("declared_subject") or "na"
    return metric, subject


def _text_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_pipeline_with_fixtures(
    *,
    registry_path: str | Path = "inspectah/config/sources_registry.yaml",
    fixtures_base: str | Path = "fixtures/s5",
    evidence_base: str | Path = "data/evidence",
    index_base: str | Path = "data/index",
    summary_path: str | Path | None = None,
) -> Dict[str, Any]:
    """Executa pipeline completa usando apenas fixtures."""

    evidence_dir = Path(evidence_base)
    index_dir = Path(index_base)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    index_dir.mkdir(parents=True, exist_ok=True)

    watcher_result = run_watchers(registry_path, fixtures_base=fixtures_base)
    indexer = LocalIndexer(storage_path=index_dir)

    summary = _default_summary()
    items_serialized: List[Dict[str, Any]] = []
    bundle_paths: List[str] = []

    for run in watcher_result.get("runs", []):
        if run.get("status") != "success":
            continue
        run_id = run.get("run_id", "run")
        for raw_item in run.get("items", []):
            summary["items_total"] += 1
            source_id = raw_item.get("source_id")
            summary["items_by_source"].setdefault(source_id, 0)
            summary["items_by_source"][source_id] += 1
            summary["items_by_state"]["S1"] += 1

            bundle_payload = {
                "source_id": source_id,
                "item_id": raw_item.get("item_id"),
                "run_id": run_id,
                "watcher_type": raw_item.get("meta", {}).get("watcher_type"),
                "fetched_at": raw_item.get("meta", {}).get("fetched_at") or raw_item.get("published_at"),
                "request_url": raw_item.get("meta", {}).get("request_url") or raw_item.get("request_url"),
            }
            raw_content: bytes = raw_item.get("raw_content", b"")
            text_content = raw_item.get("text") or raw_item.get("headline") or ""

            try:
                bundle_info = builder.build_bundle(
                    bundle_payload,
                    raw_content=raw_content,
                    text_content=text_content,
                    base_dir=evidence_dir,
                )
            except Exception as exc:  # pylint: disable=broad-except
                summary["failed_bundles"].append({"source_id": source_id, "item_id": raw_item.get("item_id"), "error": str(exc)})
                continue

            verify_result = verifier.verify_bundle(bundle_info["bundle_path"])
            if verify_result.get("status") != "PASS":
                summary["failed_bundles"].append(
                    {
                        "source_id": source_id,
                        "item_id": raw_item.get("item_id"),
                        "error": verify_result.get("reason", "verifier_fail"),
                    }
                )
                continue

            summary["bundles_total"] += 1
            summary["items_by_state"]["S2"] += 1
            bundle_paths.append(bundle_info["bundle_path"])

            metric, subject = _metric_subject_from_item(raw_item)
            equivalence_key = generate_equivalence_key(
                declared_metric=metric,
                declared_subject=subject,
                published_at=raw_item.get("published_at") or raw_item.get("meta", {}).get("fetched_at"),
            )
            item_dict = {
                "source_id": source_id,
                "item_id": raw_item.get("item_id"),
                "bundle_id": bundle_info["bundle_id"],
                "state": "S2",
                "run_id": run_id,
                "watcher_type": raw_item.get("meta", {}).get("watcher_type"),
                "fetched_at": raw_item.get("meta", {}).get("fetched_at") or raw_item.get("published_at"),
                "request_url": raw_item.get("meta", {}).get("request_url"),
                "status_code": 200,
                "response_size_bytes": len(raw_content),
                "content_type": "application/octet-stream",
                "headline": raw_item.get("headline"),
                "published_at": raw_item.get("published_at"),
                "entities": raw_item.get("entities", []),
                "facts": raw_item.get("meta", {}).get("facts", {}),
                "claims": [],
                "equivalence_key": equivalence_key,
                "confidence_local": 0.7,
                "reasoning_short": None,
                "text_sha256": _text_sha(text_content) if text_content else None,
                "bundle_path": bundle_info["bundle_path"],
            }
            item = InspectahItem.from_dict(item_dict)

            normalized_item = normalizer.normalize_item(
                item,
                text=text_content,
                meta={"facts": raw_item.get("meta", {}).get("facts", {}), "item_id": raw_item.get("item_id")},
            )
            if normalized_item.state != "S3":
                summary["failed_normalizer"].append({"source_id": source_id, "item_id": raw_item.get("item_id")})
                items_serialized.append(_serialize_item(normalized_item, bundle_info["bundle_path"]))
                continue

            summary["items_by_state"]["S3"] += 1
            try:
                indexer.index(normalized_item)
            except Exception as exc:  # pylint: disable=broad-except
                summary["failed_normalizer"].append({"source_id": source_id, "item_id": raw_item.get("item_id"), "error": str(exc)})
                items_serialized.append(_serialize_item(normalized_item, bundle_info["bundle_path"]))
                continue

            summary["items_by_state"]["S4"] += 1
            items_serialized.append(_serialize_item(normalized_item, bundle_info["bundle_path"]))

    if summary_path:
        Path(summary_path).write_text(json.dumps(summary, indent=2))

    return {"summary": summary, "items": items_serialized, "bundle_paths": bundle_paths}


def _serialize_item(item: InspectahItem, bundle_path: str) -> Dict[str, Any]:
    data = item.to_dict()
    data["bundle_path"] = bundle_path
    return data
