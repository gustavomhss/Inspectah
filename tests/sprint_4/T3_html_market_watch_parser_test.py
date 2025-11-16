import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from ingest.parsers.html_market_watch import parse_html_market_watch

FIXTURES_DIR = ROOT / "fixtures" / "sprint_4" / "fontes_p0" / "html_market_watch"


def test_html_market_watch_fixtures():
    samples = []
    for fixture in sorted(FIXTURES_DIR.glob("*.html")):
        html = fixture.read_text()
        items = parse_html_market_watch(html, source_id="html_market_watch", collected_at="2025-11-01T00:00:00Z")
        assert items, f"Parser não retornou itens para {fixture.name}"
        for item in items:
            assert set(item.keys()) >= {"sku", "product", "location", "observed_at"}
            if "price" in item and item["price"] is not None:
                assert isinstance(item["price"], (int, float))
            samples.append({k: item.get(k) for k in ("sku", "product", "price", "location", "observed_at")})
    target_dir = os.environ.get("S4_T3_ITEMS_SAMPLE_DIR")
    if target_dir:
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        (Path(target_dir) / "html_market_watch.json").write_text(
            json.dumps(samples, indent=2, ensure_ascii=False)
        )
