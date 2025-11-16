from __future__ import annotations
import argparse
import json
import sys
from typing import Sequence

from .pipeline import run_ingest_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspectah ingest CLI")
    parser.add_argument("--source-id", required=True, help="Source ID from registry")
    parser.add_argument(
        "--use-fixture",
        action="store_true",
        help="Use fixture instead of fetching from the network",
    )
    parser.add_argument(
        "--fixture-path",
        help="Path to fixture file when --use-fixture is set",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = run_ingest_pipeline(
        args.source_id,
        use_fixture=args.use_fixture,
        fixture_path=args.fixture_path,
    )
    print(json.dumps({"source_id": result.source_id, "items_ingested": result.items_ingested}))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
