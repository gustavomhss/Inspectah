import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from ingest.parsers.rss_news_minimal import parse_rss_news_minimal

FIXTURES_DIR = ROOT / "fixtures" / "sprint_4" / "fontes_p0" / "rss_news_minimal"


def test_rss_news_minimal_fixtures():
    samples = []
    for fixture in sorted(FIXTURES_DIR.glob("*.xml")):
        xml_body = fixture.read_text()
        items = parse_rss_news_minimal(xml_body, source_id="rss_news_minimal")
        assert items, f"Parser não retornou itens para {fixture.name}"
        for item in items:
            assert set(item.keys()) >= {"title", "url", "published_at", "source_name"}
            samples.append({k: item.get(k) for k in ("title", "url", "published_at", "summary", "source_name")})
    target_dir = os.environ.get("S4_T3_ITEMS_SAMPLE_DIR")
    if target_dir:
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        (Path(target_dir) / "rss_news_minimal.json").write_text(json.dumps(samples, indent=2, ensure_ascii=False))
