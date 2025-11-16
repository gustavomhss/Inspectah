from __future__ import annotations
import argparse
import hashlib
import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from field_designer.config_loader import SourceConfig, load_source_configs
from field_designer.dry_run import extract_path, load_sample_records

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = REPO_ROOT / "schema" / "migrations"


def compute_canonical_key(cfg: SourceConfig, record: Dict[str, Any]) -> str:
    parts: List[str] = []
    for path in cfg.dedup_fields:
        value = extract_path(record, path)
        if value:
            parts.append(str(value))
    if not parts:
        payload = json.dumps(record, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return "|".join(parts)


def compute_canonical_url(cfg: SourceConfig, record: Dict[str, Any]) -> str:
    if cfg.canonical_path:
        value = extract_path(record, cfg.canonical_path)
        if value:
            return str(value)
    return compute_canonical_key(cfg, record)


def compute_observed_at(cfg: SourceConfig, record: Dict[str, Any]) -> str:
    if cfg.timestamp_path:
        value = extract_path(record, cfg.timestamp_path)
        if isinstance(value, str) and value.strip():
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return parsed.isoformat()
            except ValueError:
                return value
    return datetime.now(timezone.utc).isoformat()


@dataclass
class IngestionStats:
    items_added: int = 0
    observations_added: int = 0
    versions_added: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {
            "items_added": self.items_added,
            "observations_added": self.observations_added,
            "item_versions_added": self.versions_added,
        }


class PipelineDB:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        if self.db_path.exists():
            self.db_path.unlink()
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._apply_migrations()

    def _apply_migrations(self) -> None:
        scripts = sorted(MIGRATIONS_DIR.glob("V*.sql"))
        if not scripts:
            raise FileNotFoundError("No migrations found for pipeline runner")
        for script in scripts:
            self.conn.executescript(script.read_text(encoding="utf-8"))
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def ensure_source(self, cfg: SourceConfig) -> None:
        payload = json.dumps(cfg.raw)
        self.conn.execute(
            """
            INSERT OR IGNORE INTO sources (id, name, description, source_type, config, status)
            VALUES (?, ?, ?, ?, ?, 'active')
            """,
            (cfg.id, cfg.name, cfg.description or "", cfg.type, payload),
        )
        self.conn.commit()

    def start_run(self, source_id: str) -> str:
        run_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            """
            INSERT INTO source_runs (id, source_id, started_at, status)
            VALUES (?, ?, ?, 'running')
            """,
            (run_id, source_id, now),
        )
        self.conn.commit()
        return run_id

    def finish_run(self, run_id: str, status: str = "completed", error_message: str | None = None) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            "UPDATE source_runs SET finished_at=?, status=?, error_message=? WHERE id=?",
            (now, status, error_message, run_id),
        )
        self.conn.commit()

    def ingest_record(
        self,
        cfg: SourceConfig,
        run_id: str,
        record: Dict[str, Any],
        canonical_key: str,
        canonical_url: str,
        observed_at: str,
    ) -> Tuple[int, int, int]:
        payload = json.dumps(record, sort_keys=True)
        payload_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        existing_item = self.conn.execute(
            "SELECT id, content_hash FROM items WHERE source_id=? AND canonical_key=?",
            (cfg.id, canonical_key),
        ).fetchone()
        if existing_item and existing_item["content_hash"] == payload_hash:
            return (0, 0, 0)
        observation_id = str(uuid.uuid4())
        payload_path = f"memory://{cfg.id}/{observation_id}.json"
        if existing_item is not None:
            observed_at = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            """
            INSERT INTO observations (
                id, source_id, run_id, canonical_key, observed_at, payload_hash, payload_path, payload_mime, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                observation_id,
                cfg.id,
                run_id,
                canonical_key,
                observed_at,
                payload_hash,
                payload_path,
                "application/json",
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        item_id: int
        items_added = 0
        if existing_item is None:
            manifest_path = f"memory://manifest/{observation_id}.json"
            self.conn.execute(
                """
                INSERT INTO items (
                    source_id, canonical_url, canonical_key, content_hash, collected_at,
                    manifest_path, latest_observation_id, confidence_score, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
                """,
                (
                    cfg.id,
                    canonical_url,
                    canonical_key,
                    payload_hash,
                    observed_at,
                    manifest_path,
                    observation_id,
                    observed_at,
                    observed_at,
                ),
            )
            item_id = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            items_added = 1
        else:
            item_id = existing_item["id"]
            self.conn.execute(
                "UPDATE items SET content_hash=?, latest_observation_id=?, updated_at=?, collected_at=? WHERE id=?",
                (payload_hash, observation_id, datetime.now(timezone.utc).isoformat(), observed_at, item_id),
            )
        current_version = self.conn.execute(
            "SELECT COALESCE(MAX(version), 0) FROM item_versions WHERE item_id=?",
            (item_id,),
        ).fetchone()[0]
        version_number = current_version + 1
        self.conn.execute(
            """
            INSERT INTO item_versions (
                id, item_id, observation_id, source_run_id, collected_at, manifest_path, snapshot_path, version, diff_summary, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                item_id,
                observation_id,
                run_id,
                observed_at,
                payload_path,
                None,
                version_number,
                None,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        self.conn.commit()
        return (items_added, 1, 1)

    def record_counts(self) -> Dict[str, int]:
        counts = {}
        for table in ["sources", "source_runs", "observations", "items", "item_versions"]:
            value = self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            counts[table] = int(value)
        return counts

    def lineage_violations(self) -> int:
        violations = 0
        violations += self.conn.execute(
            """
            SELECT COUNT(*) FROM observations o
            LEFT JOIN sources s ON o.source_id = s.id
            WHERE s.id IS NULL
            """
        ).fetchone()[0]
        violations += self.conn.execute(
            """
            SELECT COUNT(*) FROM observations o
            LEFT JOIN source_runs r ON o.run_id = r.id
            WHERE r.id IS NULL
            """
        ).fetchone()[0]
        violations += self.conn.execute(
            """
            SELECT COUNT(*) FROM items i
            LEFT JOIN sources s ON i.source_id = s.id
            WHERE s.id IS NULL
            """
        ).fetchone()[0]
        violations += self.conn.execute(
            """
            SELECT COUNT(*) FROM item_versions v
            LEFT JOIN items i ON v.item_id = i.id
            WHERE i.id IS NULL
            """
        ).fetchone()[0]
        violations += self.conn.execute(
            """
            SELECT COUNT(*) FROM item_versions v
            LEFT JOIN observations o ON v.observation_id = o.id
            WHERE o.id IS NULL
            """
        ).fetchone()[0]
        return int(violations)


class PipelineInvariantRunner:
    def __init__(self, db_path: Path, config_dir: str | Path | None = None) -> None:
        self.db = PipelineDB(db_path)
        self.configs = load_source_configs(config_dir)
        self.records_per_source: Dict[str, int] = {}

    def close(self) -> None:
        self.db.close()

    def _mutate_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        mutated: List[Dict[str, Any]] = []
        for record in records:
            clone = json.loads(json.dumps(record))
            clone["_mutation"] = str(uuid.uuid4())
            mutated.append(clone)
        return mutated

    def ingest(self, mutated: bool = False) -> IngestionStats:
        stats = IngestionStats()
        for cfg in self.configs.values():
            records = load_sample_records(cfg)
            if not mutated and cfg.id not in self.records_per_source:
                self.records_per_source[cfg.id] = len(records)
            if mutated:
                records = self._mutate_records(records)
            self.db.ensure_source(cfg)
            run_id = self.db.start_run(cfg.id)
            try:
                for record in records:
                    canonical_key = compute_canonical_key(cfg, record)
                    canonical_url = compute_canonical_url(cfg, record)
                    observed_at = compute_observed_at(cfg, record)
                    items_added, obs_added, ver_added = self.db.ingest_record(
                        cfg,
                        run_id,
                        record,
                        canonical_key,
                        canonical_url,
                        observed_at,
                    )
                    stats.items_added += items_added
                    stats.observations_added += obs_added
                    stats.versions_added += ver_added
            finally:
                self.db.finish_run(run_id)
        return stats

    def expected_mutations(self) -> int:
        return sum(self.records_per_source.values())

    def run(self) -> Dict[str, Any]:
        initial = self.ingest(mutated=False)
        repeat = self.ingest(mutated=False)
        mutated_stats = self.ingest(mutated=True)
        dedup_violations = repeat.items_added + repeat.observations_added
        expected_versions = self.expected_mutations()
        immutability_violations = 0
        if mutated_stats.versions_added != expected_versions:
            immutability_violations = abs(mutated_stats.versions_added - expected_versions)
        lineage_violations = self.db.lineage_violations()
        return {
            "metrics": {
                "dedup_violations": dedup_violations,
                "immutability_violations": immutability_violations,
                "lineage_violations": lineage_violations,
            },
            "details": {
                "initial": initial.to_dict(),
                "repeat": repeat.to_dict(),
                "mutated": mutated_stats.to_dict(),
                "expected_mutations": expected_versions,
                "records_per_source": self.records_per_source,
            },
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspectah pipeline invariant runner")
    parser.add_argument("--config-dir", default="configs/sources", help="Diretório com configs de fontes")
    parser.add_argument("--db-path", required=True, help="Caminho para o banco SQLite temporário")
    parser.add_argument("--report", required=True, help="Arquivo JSON para salvar o relatório")
    args = parser.parse_args()

    db_path = Path(args.db_path).resolve()
    runner = PipelineInvariantRunner(db_path, args.config_dir)
    try:
        report = runner.run()
        Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
    finally:
        runner.close()


if __name__ == "__main__":  # pragma: no cover
    main()
