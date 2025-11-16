#!/usr/bin/env python3
"""Ingest fixtures for Sprint 4 T5 into a simple Vault state."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from ingest.parsers.api_market_prices import parse_api_market_prices  # noqa: E402
from ingest.parsers.html_market_watch import parse_html_market_watch  # noqa: E402
from ingest.parsers.rss_news_minimal import parse_rss_news_minimal  # noqa: E402


def load_state(path: Path):
    if path.exists():
        return json.loads(path.read_text())
    return {}


def dump_state(path: Path, state):
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def ensure_source(state, source_id):
    if source_id not in state:
        state[source_id] = {}
    return state[source_id]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--fixtures-root", required=True, type=Path)
    parser.add_argument("--collected-at", default="2025-11-01T00:00:00Z")
    args = parser.parse_args()

    state = load_state(args.state)
    fixtures_root = args.fixtures_root

    sources = {
        "api_market_prices": {
            "path": fixtures_root / "api_market_prices",
            "glob": "*.json",
            "loader": lambda p: json.loads(p.read_text()),
            "parser": lambda payload: parse_api_market_prices(
                payload["items"], payload["source_id"], payload["collected_at"]
            ),
            "key": lambda item: f"{item['sku']}|{item['region']}|{item['last_update']}"
        },
        "html_market_watch": {
            "path": fixtures_root / "html_market_watch",
            "glob": "*.html",
            "loader": lambda p: p.read_text(),
            "parser": lambda html: parse_html_market_watch(
                html, source_id="html_market_watch", collected_at=args.collected_at
            ),
            "key": lambda item: f"{item['sku']}|{item.get('observed_at')}"
        },
        "rss_news_minimal": {
            "path": fixtures_root / "rss_news_minimal",
            "glob": "*.xml",
            "loader": lambda p: p.read_text(),
            "parser": lambda xml: parse_rss_news_minimal(xml, source_id="rss_news_minimal"),
            "key": lambda item: item['url']
        }
    }

    for source_id, cfg in sources.items():
        source_state = ensure_source(state, source_id)
        for fixture in sorted(cfg["path"].glob(cfg["glob"])):
            payload = cfg["loader"](fixture)
            items = cfg["parser"](payload)
            for item in items:
                logical_key = cfg["key"](item)
                source_state[logical_key] = item

    dump_state(args.state, state)


if __name__ == "__main__":
    main()
