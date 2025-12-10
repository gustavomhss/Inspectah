from __future__ import annotations
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from field_designer.config_loader import SourceConfig, load_source_configs
from field_designer.dry_run import extract_path, load_sample_records
from inspectah.evidence_vault.writer import store_evidence
from inspectah.evidence_vault.metadata import EvidenceRecord

from watchers.pipeline_runner import (
    compute_canonical_key,
    compute_canonical_url,
    compute_observed_at,
)

EVIDENCE_TYPES: Tuple[str, ...] = ("raw_payload", "metadata_manifest")


@dataclass
class SourceBundleSummary:
    source_id: str
    records_processed: int
    evidence_created: int
    expected_evidence: int
    evidence_ids: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "records_processed": self.records_processed,
            "evidence_created": self.evidence_created,
            "expected_evidence": self.expected_evidence,
            "evidence_ids": self.evidence_ids,
        }


class EvidenceBundleBuilder:
    def __init__(self, db_path: Path | str, config_dir: str | Path | None = None) -> None:
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.configs = load_source_configs(config_dir)

    def close(self) -> None:
        self.conn.close()

    def _latest_item_version(self, item_id: int) -> str | None:
        row = self.conn.execute(
            "SELECT id FROM item_versions WHERE item_id = ? ORDER BY version DESC LIMIT 1",
            (item_id,),
        ).fetchone()
        return row["id"] if row else None

    def _item_id_for_key(self, source_id: str, canonical_key: str) -> int | None:
        row = self.conn.execute(
            "SELECT id FROM items WHERE source_id = ? AND canonical_key = ?",
            (source_id, canonical_key),
        ).fetchone()
        return row["id"] if row else None

    def _bundle_payloads(
        self,
        cfg: SourceConfig,
        record: Dict[str, Any],
        canonical_key: str,
        canonical_url: str,
        observed_at: str,
        item_id: int,
        item_version_id: str | None,
    ) -> List[EvidenceRecord]:
        raw_payload = json.dumps(record, ensure_ascii=False, sort_keys=True).encode("utf-8")
        manifest = {
            "source_id": cfg.id,
            "canonical_key": canonical_key,
            "canonical_url": canonical_url,
            "observed_at": observed_at,
            "fields": self._extract_fields(cfg, record),
        }
        manifest_bytes = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
        evidences: List[EvidenceRecord] = []
        try:
            collected_dt = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        except ValueError:
            collected_dt = datetime.now(timezone.utc)
        evidences.append(
            store_evidence(
                source_id=cfg.id,
                evidence_type="raw_payload",
                collected_at=collected_dt,
                lgpd_tags=["lgpd.anonymized"],
                payload_bytes=raw_payload,
                item_id=item_id,
                item_version_id=item_version_id,
            )
        )
        evidences.append(
            store_evidence(
                source_id=cfg.id,
                evidence_type="metadata_manifest",
                collected_at=collected_dt,
                lgpd_tags=["lgpd.anonymized"],
                payload_bytes=manifest_bytes,
                item_id=item_id,
                item_version_id=item_version_id,
            )
        )
        return evidences

    def _extract_fields(self, cfg: SourceConfig, record: Dict[str, Any]) -> Dict[str, Any]:
        details: Dict[str, Any] = {}
        for field in cfg.fields:
            details[field.name] = extract_path(record, field.path)
        return details

    def build(self) -> Dict[str, SourceBundleSummary]:
        summaries: Dict[str, SourceBundleSummary] = {}
        for cfg in self.configs.values():
            records = load_sample_records(cfg)
            created: List[EvidenceRecord] = []
            for record in records:
                canonical_key = compute_canonical_key(cfg, record)
                item_id = self._item_id_for_key(cfg.id, canonical_key)
                if item_id is None:
                    continue
                canonical_url = compute_canonical_url(cfg, record)
                observed_at = compute_observed_at(cfg, record)
                version_id = self._latest_item_version(item_id)
                evidences = self._bundle_payloads(cfg, record, canonical_key, canonical_url, observed_at, item_id, version_id)
                created.extend(evidences)
            summaries[cfg.id] = SourceBundleSummary(
                source_id=cfg.id,
                records_processed=len(records),
                evidence_created=len(created),
                expected_evidence=len(records) * len(EVIDENCE_TYPES),
                evidence_ids=[ev.evidence_id for ev in created],
            )
        return summaries
