#!/usr/bin/env bash
set -euo pipefail

OUT="${ORR_OUTDIR:-out}"
if [[ "$OUT" != /* ]]; then
  OUT="$(pwd)/$OUT"
fi

EVID_DIR="$OUT/evidence/T1_schema"
SCORECARD="$OUT/scorecards/T1_schema.json"
SCHEMA_DUMP="$EVID_DIR/schema_dump.sql"
TABLE_REPORT="$EVID_DIR/tables_report.json"
APPLIED_REPORT="$EVID_DIR/applied_migrations.json"
MANIFEST="$EVID_DIR/MANIFEST.json"

mkdir -p "$EVID_DIR" "$OUT/scorecards"
TMP_DB="$(mktemp "${TMPDIR:-/tmp}/inspectah_t1_XXXXXX.db")"
trap 'rm -f "$TMP_DB"' EXIT

python3 - "$TMP_DB" "$SCORECARD" "$SCHEMA_DUMP" "$TABLE_REPORT" "$APPLIED_REPORT" <<'PY'
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

db_path, scorecard_path, dump_path, table_report_path, applied_report_path = sys.argv[1:6]
migrations_dir = Path("schema/migrations")
ddl_path = Path("schema/inspectah_ddl.sql")
if not migrations_dir.is_dir():
    raise SystemExit("schema/migrations directory not found")
if not ddl_path.is_file():
    raise SystemExit("schema/inspectah_ddl.sql missing")
migrations = sorted(migrations_dir.glob("V*.sql"))
if not migrations:
    raise SystemExit("no migrations found under schema/migrations")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys=ON;")
applied = []
for migration in migrations:
    conn.executescript(migration.read_text(encoding="utf-8"))
    applied.append(migration.name)
Path(applied_report_path).write_text(json.dumps({"applied": applied}, indent=2), encoding="utf-8")

EXPECTED = {
    "sources": {
        "columns": {
            "id": "TEXT",
            "name": "TEXT",
            "description": "TEXT",
            "source_type": "TEXT",
            "config": "TEXT",
            "status": "TEXT",
            "created_at": "TEXT",
            "updated_at": "TEXT",
        },
        "foreign_keys": [],
    },
    "source_runs": {
        "columns": {
            "id": "TEXT",
            "source_id": "TEXT",
            "started_at": "TEXT",
            "finished_at": "TEXT",
            "status": "TEXT",
            "error_message": "TEXT",
        },
        "foreign_keys": [{"from": "source_id", "table": "sources", "to": "id"}],
    },
    "observations": {
        "columns": {
            "id": "TEXT",
            "source_id": "TEXT",
            "run_id": "TEXT",
            "canonical_key": "TEXT",
            "observed_at": "TEXT",
            "payload_hash": "TEXT",
            "payload_path": "TEXT",
            "payload_mime": "TEXT",
            "created_at": "TEXT",
        },
        "foreign_keys": [
            {"from": "source_id", "table": "sources", "to": "id"},
            {"from": "run_id", "table": "source_runs", "to": "id"},
        ],
    },
    "items": {
        "columns": {
            "id": "INTEGER",
            "source_id": "TEXT",
            "canonical_url": "TEXT",
            "canonical_key": "TEXT",
            "content_hash": "TEXT",
            "collected_at": "TEXT",
            "manifest_path": "TEXT",
            "latest_observation_id": "TEXT",
            "confidence_score": "REAL",
            "confidence_profile_id": "TEXT",
            "created_at": "TEXT",
            "updated_at": "TEXT",
        },
        "foreign_keys": [
            {"from": "source_id", "table": "sources", "to": "id"},
            {"from": "latest_observation_id", "table": "observations", "to": "id"},
        ],
    },
    "item_versions": {
        "columns": {
            "id": "TEXT",
            "item_id": "INTEGER",
            "observation_id": "TEXT",
            "source_run_id": "TEXT",
            "collected_at": "TEXT",
            "manifest_path": "TEXT",
            "snapshot_path": "TEXT",
            "version": "INTEGER",
            "diff_summary": "TEXT",
            "created_at": "TEXT",
        },
        "foreign_keys": [
            {"from": "item_id", "table": "items", "to": "id"},
            {"from": "observation_id", "table": "observations", "to": "id"},
            {"from": "source_run_id", "table": "source_runs", "to": "id"},
        ],
    },
    "item_kv": {
        "columns": {
            "id": "INTEGER",
            "item_id": "INTEGER",
            "field_name": "TEXT",
            "field_type": "TEXT",
            "value_string": "TEXT",
            "value_numeric": "REAL",
            "value_timestamp": "TEXT",
            "value_boolean": "INTEGER",
        },
        "foreign_keys": [{"from": "item_id", "table": "items", "to": "id"}],
    },
    "field_definitions": {
        "columns": {
            "id": "TEXT",
            "source_id": "TEXT",
            "version": "INTEGER",
            "status": "TEXT",
            "definition": "TEXT",
            "created_by": "TEXT",
            "created_at": "TEXT",
        },
        "foreign_keys": [{"from": "source_id", "table": "sources", "to": "id"}],
    },
    "evidence_records": {
        "columns": {
            "id": "TEXT",
            "source_id": "TEXT",
            "item_id": "INTEGER",
            "item_version_id": "TEXT",
            "evidence_type": "TEXT",
            "collected_at": "TEXT",
            "ingested_at": "TEXT",
            "storage_key": "TEXT",
            "hash_alg": "TEXT",
            "hash_value": "TEXT",
            "lgpd_tags": "TEXT",
            "size_bytes": "INTEGER",
            "checksum_status": "TEXT",
        },
        "foreign_keys": [
            {"from": "source_id", "table": "sources", "to": "id"},
            {"from": "item_id", "table": "items", "to": "id"},
            {"from": "item_version_id", "table": "item_versions", "to": "id"},
        ],
    },
}

def upper_or_none(value: str | None) -> str | None:
    return value.upper() if value else value

cursor = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
)
actual_tables = {row["name"] for row in cursor.fetchall()}

table_details = {}
missing_tables = []
missing_columns = 0
constraint_violations = 0

for table_name, spec in EXPECTED.items():
    if table_name not in actual_tables:
        missing_tables.append(table_name)
        table_details[table_name] = {
            "present": False,
            "missing_columns": sorted(spec["columns"].keys()),
            "missing_foreign_keys": [fk for fk in spec.get("foreign_keys", [])],
            "extra_columns": [],
        }
        missing_columns += len(spec["columns"])
        constraint_violations += len(spec.get("foreign_keys", []))
        continue

    pragma_info = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    columns = {row["name"]: upper_or_none(row["type"]) for row in pragma_info}
    missing_cols = [
        column for column in spec["columns"] if column not in columns
    ]
    missing_columns += len(missing_cols)
    extra_columns = sorted(set(columns) - set(spec["columns"]))

    fk_rows = conn.execute(f"PRAGMA foreign_key_list({table_name})").fetchall()
    fk_entries = [
        {"from": row["from"], "table": row["table"], "to": row["to"]}
        for row in fk_rows
    ]
    expected_fks = spec.get("foreign_keys", [])
    missing_fks = [fk for fk in expected_fks if fk not in fk_entries]
    constraint_violations += len(missing_fks)

    table_details[table_name] = {
        "present": True,
        "missing_columns": missing_cols,
        "extra_columns": extra_columns,
        "missing_foreign_keys": missing_fks,
        "column_types": columns,
    }

tables_expected = len(EXPECTED)
tables_found = len([t for t in EXPECTED if table_details[t]["present"]])

with open(dump_path, "w", encoding="utf-8") as handle:
    for statement in conn.iterdump():
        handle.write(f"{statement}\n")

conn.close()

table_report = {
    "tables": table_details,
    "metrics": {
        "tables_expected": tables_expected,
        "tables_found": tables_found,
        "missing_tables": len(missing_tables),
        "missing_columns": missing_columns,
        "constraint_violations": constraint_violations,
    },
    "applied_migrations": applied,
    "ddl_path": str(ddl_path),
    "db_engine": "sqlite",
}
Path(table_report_path).write_text(json.dumps(table_report, indent=2), encoding="utf-8")

status = "PASS"
if table_report["metrics"]["missing_tables"] > 0 or missing_columns > 0 or constraint_violations > 0:
    status = "FAIL"

scorecard = {
    "gate": "T1",
    "name": "schema",
    "version": "v1",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "metrics": table_report["metrics"],
    "thresholds": {
        "missing_tables": "== 0",
        "missing_columns": "== 0",
        "constraint_violations": "== 0",
    },
    "details": {
        "db_engine": "sqlite",
        "tables": table_details,
        "applied_migrations": applied,
    },
}
Path(scorecard_path).write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    sys.stderr.write("T1 schema check failed; see tables_report.json for details\n")
    sys.exit(1)
PY

# Maintain backward compatibility for legacy aggregators expecting T1_structure.
cp "$SCORECARD" "$OUT/scorecards/T1_structure.json"

python3 - <<'PY' "$EVID_DIR" "$MANIFEST"
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
manifest_path = Path(sys.argv[2])
files = []
for path in sorted(root.rglob("*")):
    if path.is_file():
        rel = path.relative_to(root).as_posix()
        files.append(
            {
                "path": rel,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
            }
        )
manifest_path.write_text(json.dumps({"files": files}, indent=2), encoding="utf-8")
PY

echo "[T1] Schema check scorecard written to $SCORECARD"
