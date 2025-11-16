#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def snapshot(state_path: Path, output: Path):
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    snapshot = {}
    for source_id, entries in state.items():
        keys = sorted(entries.keys())
        snapshot[source_id] = {
            "items_total": len(entries),
            "logical_keys": keys
        }
    output.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    snapshot(args.state, args.output)


if __name__ == "__main__":
    main()
