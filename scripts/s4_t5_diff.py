#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def diff(before_path: Path, after_path: Path, txt_output: Path, json_output: Path):
    before = json.loads(before_path.read_text()) if before_path.exists() else {}
    after = json.loads(after_path.read_text()) if after_path.exists() else {}
    sources = sorted(set(before.keys()) | set(after.keys()))
    lines = []
    summary = {}
    for source in sources:
        before_keys = set(before.get(source, {}).get("logical_keys", []))
        after_keys = set(after.get(source, {}).get("logical_keys", []))
        added = sorted(after_keys - before_keys)
        removed = sorted(before_keys - after_keys)
        status = "NO_DIFF"
        if added or removed:
            status = "FAIL"
        summary[source] = {
            "status": status,
            "added": added,
            "removed": removed,
            "before_items": len(before_keys),
            "after_items": len(after_keys)
        }
        if status == "NO_DIFF":
            lines.append(f"[{source}] NO_DIFF ({len(before_keys)} items)")
        else:
            lines.append(
                f"[{source}] DIFF added={len(added)} removed={len(removed)}"
            )
    txt_output.write_text("\n".join(lines) + ("\n" if lines else ""))
    json_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--txt", required=True, type=Path)
    parser.add_argument("--json", required=True, type=Path)
    args = parser.parse_args()
    diff(args.before, args.after, args.txt, args.json)


if __name__ == "__main__":
    main()
