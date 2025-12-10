#!/usr/bin/env python3
"""Inspectah Ingestor — deterministic polling + backpressure + Evidence Vault."""
from __future__ import annotations

import json
import queue
import random
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
VAULT_SCRIPT = ROOT / "scripts/evidence_vault.py"
VAULT_PAYLOAD = ROOT / "tests/fixtures/unit/evidence_vault/sample_payload.json"
VAULT_METADATA = ROOT / "tests/fixtures/unit/evidence_vault/sample_metadata.json"
EVIDENCE_DIR = ROOT / "out/evidence/T3_property"


@dataclass
class SourceConfig:
    source_id: str
    poll_interval: int
    last_poll: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    jitter: float = 0.15


@dataclass
class IngestItem:
    source_id: str
    canonical_url: str
    content_hash: str
    extractor_version: str
    payload_path: Path
    metadata_path: Path
    event_time: datetime


class BackpressureQueue:
    def __init__(self, maxsize: int = 100) -> None:
        self.q: queue.Queue[IngestItem] = queue.Queue(maxsize=maxsize)
        self.timestamps: List[float] = []

    def put(self, item: IngestItem) -> None:
        self.q.put(item)
        self.timestamps.append(time.time())

    def get(self) -> IngestItem:
        item = self.q.get()
        self.timestamps.pop(0)
        return item

    def depth(self) -> int:
        return self.q.qsize()

    def age_seconds(self) -> float:
        if not self.timestamps:
            return 0.0
        return time.time() - self.timestamps[0]


class Ingestor:
    def __init__(self) -> None:
        self.sources = [SourceConfig("source-alpha", poll_interval=60)]
        self.queue = BackpressureQueue(maxsize=50)
        self.dedupe: Dict[str, datetime] = {}
        self.metrics = {
            "items_fetched_total": 0,
            "items_indexed_total": 0,
            "queue_depth": 0,
            "queue_age_seconds": 0,
        }
        self.output_dir = EVIDENCE_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_cycle(self, cycles: int = 10) -> None:
        for _ in range(cycles):
            self.poll_sources()
            self.drain_queue()
            time.sleep(0.1)
        self.write_metrics()

    def poll_sources(self) -> None:
        now = datetime.now(timezone.utc)
        for source in self.sources:
            jitter = random.uniform(1 - source.jitter, 1 + source.jitter)
            next_allowed = source.last_poll + timedelta(seconds=source.poll_interval * jitter)
            if now >= next_allowed:
                item = self.fetch_item(source)
                if item:
                    dedupe_key = self.dedupe_key(item)
                    if dedupe_key not in self.dedupe:
                        self.queue.put(item)
                        self.metrics["items_fetched_total"] += 1
                        self.dedupe[dedupe_key] = datetime.now(timezone.utc)
                source.last_poll = now
        self.metrics_update()

    def fetch_item(self, source: SourceConfig) -> Optional[IngestItem]:
        payload_path = VAULT_PAYLOAD
        metadata = json.loads(VAULT_METADATA.read_text())
        metadata["source_id"] = source.source_id
        metadata["event_time"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        meta_path = self.output_dir / "tmp_metadata.json"
        meta_path.write_text(json.dumps(metadata), encoding="utf-8")
        return IngestItem(
            source_id=source.source_id,
            canonical_url=metadata["canonical_url"],
            content_hash="hash-" + metadata["canonical_url"],
            extractor_version="1.0.0",
            payload_path=payload_path,
            metadata_path=meta_path,
            event_time=datetime.now(timezone.utc),
        )

    def dedupe_key(self, item: IngestItem) -> str:
        return f"{item.source_id}|{item.canonical_url}|{item.content_hash}|{item.extractor_version}"

    def drain_queue(self) -> None:
        while self.queue.depth() > 0:
            item = self.queue.get()
            self.persist_item(item)
            self.metrics["items_indexed_total"] += 1
        self.metrics_update()

    def metrics_update(self) -> None:
        self.metrics["queue_depth"] = self.queue.depth()
        self.metrics["queue_age_seconds"] = self.queue.age_seconds()

    def persist_item(self, item: IngestItem) -> None:
        import subprocess

        subprocess.run(
            [
                "python3",
                str(VAULT_SCRIPT),
                "--payload",
                str(item.payload_path),
                "--metadata",
                str(item.metadata_path),
                "--out-dir",
                str(self.output_dir / "vault"),
            ],
            check=True,
        )

    def write_metrics(self) -> None:
        metrics_path = self.output_dir / "series_ingest.json"
        metrics_path.write_text(json.dumps(self.metrics, indent=2), encoding="utf-8")


def main() -> None:
    ingestor = Ingestor()
    ingestor.run_cycle(cycles=20)


if __name__ == "__main__":
    main()
