import importlib.util
import sqlite3
import tempfile
from pathlib import Path


def _load_migration():
    root = Path(__file__).resolve().parents[2]
    path = root / "migrations/versions/0034_s32_truthdb_blocks.py"
    spec = importlib.util.spec_from_file_location("s32_truthdb_blocks", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _expect_integrity_error(func):
    try:
        func()
    except sqlite3.IntegrityError:
        return
    raise AssertionError("Expected IntegrityError")


def run_tests():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "s32.sqlite"
        s32_migration = _load_migration()

        # test_migration_applies
        s32_migration.apply_migration(db_path)
        info = s32_migration.verify_schema(db_path)
        assert info["tables"] == 5

        # test_no_orphan_blocks
        s32_migration.apply_migration(db_path)
        conn = _connect(db_path)
        with conn:
            conn.execute(
                "INSERT INTO fact_blocks (id, claim_id, content_hash, created_at) VALUES (?,?,?,?)",
                ("fact1", "claim-1", "hash", "2025-01-01T00:00:00Z"),
            )
        _expect_integrity_error(
            lambda: conn.execute(
                "INSERT INTO evidence_blocks (id, fact_block_id, evidence_type, created_at) VALUES (?,?,?,?)",
                ("ev1", "missing", "source", "2025-01-01T00:01:00Z"),
            )
        )
        _expect_integrity_error(
            lambda: conn.execute(
                "INSERT INTO truth_states (id, claim_id, fact_block_id, status, created_at, updated_at) VALUES (?,?,?,?,?,?)",
                ("ts-missing", "claim-x", "missing", "PENDING", "2025-01-01T00:02:00Z", "2025-01-01T00:02:00Z"),
            )
        )

        # test_final_states_require_decision
        with conn:
            conn.execute("DELETE FROM truth_states")
            conn.execute("DELETE FROM contest_records")
            conn.execute("DELETE FROM decision_blocks")
            conn.execute("DELETE FROM evidence_blocks")
            conn.execute("DELETE FROM fact_blocks")
            conn.execute(
                "INSERT INTO fact_blocks (id, claim_id, content_hash, created_at) VALUES (?,?,?,?)",
                ("fact1", "claim-1", "hash", "2025-01-01T00:00:00Z"),
            )
        _expect_integrity_error(
            lambda: conn.execute(
                "INSERT INTO truth_states (id, claim_id, fact_block_id, status, created_at, updated_at) VALUES (?,?,?,?,?,?)",
                ("ts1", "claim-1", "fact1", "TRUE", "2025-01-01T00:03:00Z", "2025-01-01T00:03:00Z"),
            )
        )
        with conn:
            conn.execute(
                "INSERT INTO decision_blocks (id, fact_block_id, decision_type, created_at) VALUES (?,?,?,?)",
                ("dec1", "fact1", "promote_true", "2025-01-01T00:04:00Z"),
            )
            conn.execute(
                "INSERT INTO truth_states (id, claim_id, fact_block_id, status, current_decision_block_id, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
                ("ts2", "claim-1", "fact1", "TRUE", "dec1", "2025-01-01T00:05:00Z", "2025-01-01T00:05:00Z"),
            )

        # test_history_monotonic_and_fk_integrity
        with conn:
            conn.execute("DELETE FROM truth_states")
            conn.execute("DELETE FROM contest_records")
            conn.execute("DELETE FROM decision_blocks")
            conn.execute("DELETE FROM evidence_blocks")
            conn.execute("DELETE FROM fact_blocks")
            conn.execute(
                "INSERT INTO fact_blocks (id, claim_id, content_hash, created_at) VALUES (?,?,?,?)",
                ("fact1", "claim-1", "hash", "2025-01-01T00:00:00Z"),
            )
            conn.execute(
                "INSERT INTO decision_blocks (id, fact_block_id, decision_type, created_at) VALUES (?,?,?,?)",
                ("dec-initial", "fact1", "initial", "2025-01-01T00:01:00Z"),
            )
            conn.execute(
                "INSERT INTO truth_states (id, claim_id, fact_block_id, status, current_decision_block_id, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
                ("ts-initial", "claim-1", "fact1", "PENDING", "dec-initial", "2025-01-01T00:02:00Z", "2025-01-01T00:02:00Z"),
            )

        _expect_integrity_error(
            lambda: conn.execute(
                "INSERT INTO contest_records (id, truth_state_id, reason, status, created_at) VALUES (?,?,?,?,?)",
                ("contest-missing", "missing", "invalid", "PENDING", "2025-01-01T00:03:00Z"),
            )
        )

        with conn:
            conn.execute(
                "INSERT INTO contest_records (id, truth_state_id, reason, status, created_at) VALUES (?,?,?,?,?)",
                ("contest-1", "ts-initial", "challenge", "PENDING", "2025-01-01T00:04:00Z"),
            )
            conn.execute(
                "INSERT INTO decision_blocks (id, fact_block_id, decision_type, created_at) VALUES (?,?,?,?)",
                ("dec-final", "fact1", "upheld", "2025-01-01T00:05:00Z"),
            )
            conn.execute(
                "UPDATE contest_records SET status=?, processed_decision_block_id=?, processed_at=? WHERE id=?",
                ("UPHELD", "dec-final", "2025-01-01T00:06:00Z", "contest-1"),
            )
            conn.execute(
                "UPDATE truth_states SET status=?, current_decision_block_id=?, updated_at=? WHERE id=?",
                ("TRUE", "dec-final", "2025-01-01T00:07:00Z", "ts-initial"),
            )

        counts = conn.execute("SELECT (SELECT COUNT(*) FROM decision_blocks), (SELECT COUNT(*) FROM truth_states), (SELECT COUNT(*) FROM contest_records)").fetchone()
        decision_count, truth_count, contest_count = counts
        assert decision_count >= 2
        assert truth_count == 1
        assert contest_count == 1


if __name__ == "__main__":
    run_tests()
