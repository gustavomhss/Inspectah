#!/usr/bin/env python3
"""
Minimal Inspectah API server used for D2 smoke tests.

This module exposes both an HTTP server (when networking is allowed) and an
in-process simulation helper so CI can validate contracts deterministically.
"""
from __future__ import annotations

import argparse
import json
import signal
import subprocess
import sys
import tempfile
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_FIXTURE = ROOT / "tests/fixtures/unit/field_designer/example_payload.json"
FIELD_DESIGNER = ROOT / "scripts/field_designer_validate.py"


class InspectahState:
    def __init__(self) -> None:
        self.sources: Dict[str, Dict[str, Any]] = {}
        self.next_source_id = 1
        self.items: List[Dict[str, Any]] = self._load_items_from_vault()

    def _load_items_from_vault(self) -> List[Dict[str, Any]]:
        items = []
        vault_root = ROOT / "out/evidence/T2_unit/evidence_vault"
        if not vault_root.exists():
            return items
        for item_dir in vault_root.iterdir():
            if not item_dir.is_dir():
                continue
            manifest_path = item_dir / "manifest.json"
            if not manifest_path.exists():
                continue
            with manifest_path.open("r", encoding="utf-8") as fh:
                manifest = json.load(fh)
            items.append(
                {
                    "item_id": manifest["item_id"],
                    "source_id": manifest["source_id"],
                    "canonical_url": manifest["canonical_url"],
                    "title": manifest["fields"].get("title", ""),
                    "excerpt": manifest["fields"].get("body", ""),
                    "event_time": manifest["event_time"],
                    "observed_at": manifest["observed_at"],
                    "indexed_at": manifest["indexed_at"],
                    "fields": manifest["fields"],
                    "evidence": {
                        "manifest_path": str(manifest_path),
                        "payload_path": str(item_dir / "payload.json"),
                        "manifest_sha256": manifest["hashes"]["manifest_sha256"],
                        "payload_sha256": manifest["hashes"]["payload_sha256"],
                    },
                }
            )
        return items

    def create_source(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        required = ["name", "kind", "endpoint", "allowlist_proof", "robots_status"]
        missing = [field for field in required if field not in payload]
        if missing:
            raise ValueError(f"missing fields: {missing}")
        for source in self.sources.values():
            if source["endpoint"] == payload["endpoint"]:
                raise ValueError("source already exists")

        source_id = f"source-{self.next_source_id:03d}"
        self.next_source_id += 1
        record = {
            "id": source_id,
            "name": payload["name"],
            "kind": payload["kind"],
            "endpoint": payload["endpoint"],
            "allowlist_proof": payload["allowlist_proof"],
            "robots_status": payload["robots_status"],
            "extractor_version": 1,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "fields": [],
        }
        self.sources[source_id] = record
        return record

    def validate_fields(self, fields_payload: Dict[str, Any]) -> Dict[str, Any]:
        if "fields" not in fields_payload or not fields_payload["fields"]:
            raise ValueError("fields[] required")

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(fields_payload, fh)
            fields_path = Path(fh.name)
        out_file = tempfile.NamedTemporaryFile("w", delete=False)
        out_file.close()

        try:
            subprocess.run(
                [
                    sys.executable,
                    str(FIELD_DESIGNER),
                    "--fields",
                    str(fields_path),
                    "--payload",
                    str(PAYLOAD_FIXTURE),
                    "--out",
                    out_file.name,
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            with open(out_file.name, "r", encoding="utf-8") as fh:
                report = json.load(fh)
        finally:
            fields_path.unlink(missing_ok=True)
            Path(out_file.name).unlink(missing_ok=True)

        errors = [entry for entry in report["fields"] if entry["status"] == "error"]
        if errors:
            raise ValueError(f"field validation failed: {errors}")
        return report

    def update_fields(self, source_id: str, fields_payload: Dict[str, Any]) -> Dict[str, Any]:
        if source_id not in self.sources:
            raise KeyError("source not found")
        report = self.validate_fields(fields_payload)
        self.sources[source_id]["fields"] = fields_payload["fields"]
        self.sources[source_id]["extractor_version"] += 1
        return {
            "extractor_version": self.sources[source_id]["extractor_version"],
            "reindex_scheduled": True,
            "dry_run": report,
        }


def prepare_export(fmt: str) -> Tuple[str, str]:
    vault_dir = ROOT / "out/evidence/T2_unit/evidence_vault"
    manifest = next(vault_dir.glob("*/manifest.json"), None)
    if manifest is None:
        raise ValueError("no evidence manifest available")
    checksum = sha256_file(manifest)
    return str(manifest), checksum


STATE = InspectahState()


class InspectahHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _json_response(self, status: HTTPStatus, body: Dict[str, Any]) -> None:
        encoded = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(length) if length else b""
        try:
            return json.loads(data.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid json: {exc}") from exc

    def do_POST(self) -> None:  # noqa: N802
        try:
            if self.path == "/sources":
                payload = self._read_json()
                record = STATE.create_source(payload)
                self._json_response(HTTPStatus.CREATED, record)
                return
            if self.path.startswith("/sources/") and self.path.endswith("/fields"):
                parts = self.path.split("/")
                source_id = parts[2]
                payload = self._read_json()
                result = STATE.update_fields(source_id, payload)
                self._json_response(HTTPStatus.OK, result)
                return
            if self.path == "/sources/validate":
                payload = self._read_json()
                report = STATE.validate_fields(payload)
                self._json_response(HTTPStatus.OK, {"fields": report["fields"], "errors": []})
                return
            if self.path == "/explore/export":
                payload = self._read_json()
                fmt = payload.get("format", "json")
                if fmt not in {"json", "csv"}:
                    raise ValueError("format must be csv or json")
                artifact_path, checksum = prepare_export(fmt)
                self._json_response(
                    HTTPStatus.ACCEPTED,
                    {"format": fmt, "artifact_path": artifact_path, "checksum": checksum},
                )
                return
            self._json_response(HTTPStatus.NOT_FOUND, {"error": "resource_not_found"})
        except ValueError as exc:
            self._json_response(HTTPStatus.BAD_REQUEST, {"error": "validation_failed", "detail": str(exc)})
        except KeyError:
            self._json_response(HTTPStatus.NOT_FOUND, {"error": "resource_not_found"})

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/explore":
            self._json_response(HTTPStatus.NOT_FOUND, {"error": "resource_not_found"})
            return
        query = parse_qs(parsed.query)
        try:
            page_size = int(query.get("page_size", ["50"])[0])
            if page_size < 1 or page_size > 200:
                raise ValueError("page_size out of bounds")
        except ValueError as exc:
            self._json_response(HTTPStatus.BAD_REQUEST, {"error": "validation_failed", "detail": str(exc)})
            return

        source_filter = query.get("source_id", [None])[0]
        items = STATE.items
        if source_filter:
            items = [item for item in items if item["source_id"] == source_filter]

        response = {"items": items[:page_size], "page": 1, "page_size": page_size, "total": len(items)}
        self._json_response(HTTPStatus.OK, response)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


def sha256_file(path: Path) -> str:
    import hashlib

    with path.open("rb") as fh:
        data = fh.read()
    return hashlib.sha256(data).hexdigest()


def run_smoke_sequence(fields_payload: Dict[str, Any]) -> Dict[str, Any]:
    state = InspectahState()
    source = state.create_source(
        {
            "name": "Inspectah Feed",
            "kind": "rss",
            "endpoint": "https://example.com/rss",
            "allowlist_proof": {
                "domain": "example.com",
                "tos_hash": "c" * 64,
                "fetched_at": "2024-01-01T00:00:00Z",
            },
            "robots_status": {
                "hash": "d" * 64,
                "checked_at": "2024-01-01T00:00:00Z",
            },
        }
    )
    update = state.update_fields(source["id"], fields_payload)
    validation = state.validate_fields(fields_payload)
    explore = {
        "items": state.items[:1],
        "page": 1,
        "page_size": 1,
        "total": len(state.items),
    }
    artifact_path, checksum = prepare_export("json")
    export = {"format": "json", "artifact_path": artifact_path, "checksum": checksum}
    return {
        "source": source,
        "fields_update": update,
        "validation": {"fields": validation["fields"], "errors": []},
        "explore": explore,
        "export": export,
    }


def run_server(host: str, port: int) -> None:
    server = HTTPServer((host, port), InspectahHandler)

    def handle_signal(signum: int, frame: Any) -> None:  # noqa: ANN401
        server.shutdown()

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    print(f"Inspectah API server listening on http://{host}:{port}")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspectah API mock server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8085)
    args = parser.parse_args()
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
