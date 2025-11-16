import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from ingest.parsers.html_market_watch import parse_html_market_watch  # noqa: E402

FIXTURES_DIR = ROOT / "fixtures" / "sprint_4" / "fontes_p0" / "html_market_watch"
GOLDENS_DIR = ROOT / "goldens" / "sprint_4" / "fontes_p0" / "html_market_watch"
RESULTS = []


def _record(result):
    RESULTS.append(result)


def _dump():
    target_dir = os.environ.get("S4_T4_RESULTS_DIR")
    if target_dir:
        path = Path(target_dir)
        path.mkdir(parents=True, exist_ok=True)
        (path / "html_market_watch.json").write_text(json.dumps(RESULTS, indent=2, ensure_ascii=False))


def _compare_items(actual, expected):
    diffs = []
    if len(actual) != len(expected):
        diffs.append({
            "type": "length_mismatch",
            "actual_len": len(actual),
            "expected_len": len(expected)
        })
        return diffs
    for curr, gold in zip(actual, expected):
        for field in sorted(set(curr.keys()) | set(gold.keys())):
            if curr.get(field) != gold.get(field):
                diffs.append({"field": field, "actual": curr.get(field), "expected": gold.get(field)})
    return diffs


def test_html_market_watch_goldens():
    try:
        for fixture in sorted(FIXTURES_DIR.glob("*.html")):
            html = fixture.read_text()
            items = parse_html_market_watch(html, source_id="html_market_watch", collected_at="2025-11-01T00:00:00Z")
            items = sorted(items, key=lambda x: x["sku"])
            golden_path = GOLDENS_DIR / (fixture.stem + ".golden.json")
            assert golden_path.exists(), f"Golden inexistente: {golden_path}"
            expected = json.loads(golden_path.read_text())
            diffs = _compare_items(items, expected)
            status = "PASS" if not diffs else "FAIL"
            _record({"fixture": fixture.name, "status": status, "diffs": diffs})
            assert not diffs, f"Diferenças detectadas em {fixture.name}: {diffs}"
    finally:
        _dump()
