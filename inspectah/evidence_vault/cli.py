from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from . import EvidenceVaultError, fetch_evidence, store_evidence


def _parse_collected_at(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise EvidenceVaultError(f"Invalid ISO8601 timestamp: {value}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _cmd_write(args: argparse.Namespace) -> int:
    payload_path = Path(args.file)
    if not payload_path.exists():
        raise EvidenceVaultError(f"Payload file {payload_path} not found.")
    collected_at = _parse_collected_at(args.collected_at)
    record = store_evidence(
        source_id=args.source_id,
        evidence_type=args.evidence_type,
        collected_at=collected_at,
        lgpd_tags=args.lgpd_tag,
        payload_path=payload_path,
    )
    output = {
        "evidence_id": record.evidence_id,
        "source_id": record.source_id,
        "evidence_type": record.evidence_type,
        "hash_alg": record.hash_alg,
        "hash_value": record.hash_value,
        "size_bytes": record.size_bytes,
        "lgpd_tags": list(record.lgpd_tags),
        "storage_key": record.storage_key,
        "checksum_status": record.checksum_status,
    }
    print(json.dumps(output))
    return 0


def _cmd_read(args: argparse.Namespace) -> int:
    result = fetch_evidence(args.id, with_payload=args.with_payload)
    payload_loaded = result.payload is not None
    payload_size = len(result.payload) if result.payload else 0
    record = result.record
    output = {
        "evidence_id": record.evidence_id,
        "source_id": record.source_id,
        "evidence_type": record.evidence_type,
        "hash_alg": record.hash_alg,
        "hash_value": record.hash_value,
        "size_bytes": record.size_bytes,
        "lgpd_tags": list(record.lgpd_tags),
        "storage_key": record.storage_key,
        "checksum_status": record.checksum_status,
        "payload_loaded": payload_loaded,
        "payload_size_bytes": payload_size,
    }
    print(json.dumps(output))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspectah Evidence Vault CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    write_parser = subparsers.add_parser("write", help="Store a new evidence payload")
    write_parser.add_argument("--file", required=True, help="Path to the payload file")
    write_parser.add_argument("--source-id", required=True)
    write_parser.add_argument("--evidence-type", required=True)
    write_parser.add_argument(
        "--lgpd-tag",
        required=True,
        action="append",
        help="LGPD tag (can be repeated)",
    )
    write_parser.add_argument("--collected-at", help="ISO8601 timestamp")
    write_parser.set_defaults(func=_cmd_write)

    read_parser = subparsers.add_parser("read", help="Fetch evidence metadata")
    read_parser.add_argument("--id", required=True, help="Evidence ID to fetch")
    read_parser.add_argument(
        "--with-payload",
        action="store_true",
        help="Also retrieve the payload bytes (not printed)",
    )
    read_parser.set_defaults(func=_cmd_read)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except EvidenceVaultError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
