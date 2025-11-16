import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from ingest.parsers.api_market_prices import parse_api_market_prices

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "sprint_4" / "fontes_p0" / "api_market_prices"


def test_api_market_prices_fixtures(tmp_path):
    samples = []
    for fixture in sorted(FIXTURES_DIR.glob("*.json")):
        payload = json.loads(fixture.read_text())
        items = parse_api_market_prices(
            payload["items"],
            source_id=payload["source_id"],
            collected_at=payload["collected_at"]
        )
        assert items, f"Parser retornou lista vazia para {fixture.name}"
        for item in items:
            assert set(item.keys()) >= {"sku", "product", "price", "currency", "region", "last_update"}
            assert isinstance(item["price"], (int, float)), item
            samples.append({k: item[k] for k in ("sku", "product", "price", "currency", "region", "last_update")})
    target_dir = os.environ.get("S4_T3_ITEMS_SAMPLE_DIR")
    if target_dir:
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        (Path(target_dir) / "api_market_prices.json").write_text(
            json.dumps(samples, indent=2, ensure_ascii=False)
        )
