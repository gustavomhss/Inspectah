from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import sqlite3
from pathlib import Path
from typing import Any, Dict

from inspectah.config import load_evidence_vault_settings

from evidence_vault.bundle_builder import EvidenceBundleBuilder
from watchers.pipeline_runner import PipelineInvariantRunner


class EvidenceAuditRunner:
    def __init__(self, db_path: Path, config_dir: Path, evidence_dir: Path):
        self.db_path = db_path
        self.config_dir = config_dir
        self.evidence_dir = evidence_dir
        self.settings = load_evidence_vault_settings()

    def _reset_local_store(self) -> None:
        local_root = self.settings.local_root
        if local_root.exists():
            shutil.rmtree(local_root)
        local_root.mkdir(parents=True, exist_ok=True)

    def _run_pipeline(self) -> Dict[str, Any]:
        runner = PipelineInvariantRunner(self.db_path, self.config_dir)
        try:
            return runner.run()
        finally:
            runner.close()

    def _create_bundles(self) -> Dict[str, Dict[str, Any]]:
        builder = EvidenceBundleBuilder(self.db_path, self.config_dir)
        try:
            summaries = builder.build()
            return {sid: summary.to_dict() for sid, summary in summaries.items()}
        finally:
            builder.close()

    def _hash_metrics(self) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            total = conn.execute("SELECT COUNT(*) AS c FROM evidence_records").fetchone()["c"]
            orphan = conn.execute(
                "SELECT COUNT(*) AS c FROM evidence_records WHERE item_id IS NULL OR item_version_id IS NULL"
            ).fetchone()["c"]
            ok = 0
            local_root = self.settings.local_root
            cur = conn.execute("SELECT storage_key, hash_value, hash_alg FROM evidence_records")
            for row in cur.fetchall():
                path = (local_root / row["storage_key"]).resolve()
                if not path.exists():
                    continue
                digest = hashlib.new(row["hash_alg"])
                digest.update(path.read_bytes())
                if digest.hexdigest() == row["hash_value"]:
                    ok += 1
            return {
                "total": total,
                "hash_ok": ok,
                "orphan_evidence": orphan,
            }
        finally:
            conn.close()

    def _write_examples(self) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.execute(
                "SELECT id, source_id, evidence_type, storage_key, size_bytes FROM evidence_records ORDER BY ingested_at LIMIT 10"
            )
            examples = [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        (self.evidence_dir / "samples.json").write_text(json.dumps(examples, indent=2), encoding="utf-8")

    def run(self) -> Dict[str, Any]:
        self._reset_local_store()
        pipeline_metrics = self._run_pipeline()
        bundle_details = self._create_bundles()
        hash_info = self._hash_metrics()
        expected = sum(entry["expected_evidence"] for entry in bundle_details.values())
        actual = sum(entry["evidence_created"] for entry in bundle_details.values())
        completeness = (actual / expected) if expected else 1.0
        hash_rate = (hash_info["hash_ok"] / hash_info["total"]) if hash_info["total"] else 1.0
        report = {
            "metrics": {
                "evidence_completeness": completeness,
                "evidence_hash_valid_rate": hash_rate,
                "orphan_evidence": hash_info["orphan_evidence"],
            },
            "details": {
                "sources": bundle_details,
                "pipeline": pipeline_metrics,
                "hash": hash_info,
                "expected_evidence": expected,
                "actual_evidence": actual,
            },
        }
        self._write_examples()
        return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspectah evidence vault audit runner")
    parser.add_argument("--config-dir", default="configs/sources", help="Diretório de configs de fontes")
    parser.add_argument("--db-path", required=True, help="Arquivo SQLite temporário a ser usado pelo pipeline")
    parser.add_argument("--report", required=True, help="Arquivo JSON para salvar o relatório final")
    parser.add_argument("--evidence-dir", required=True, help="Diretório para anexar evidências auxiliares")
    args = parser.parse_args()

    db_path = Path(args.db_path).resolve()
    config_dir = Path(args.config_dir).resolve()
    evidence_dir = Path(args.evidence_dir).resolve()

    runner = EvidenceAuditRunner(db_path, config_dir, evidence_dir)
    report = runner.run()
    evidence_dir.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
