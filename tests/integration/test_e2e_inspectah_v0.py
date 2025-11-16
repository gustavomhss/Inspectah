from __future__ import annotations
import json
import shutil
import unittest

from inspectah.config import EVIDENCE_DIR
from inspectah.ingest.pipeline import run_ingest_pipeline
from inspectah.metrics import get_snapshot, reset_metrics
from inspectah.models import init_db, reset_db
from inspectah.explore.api import query_items


class InspectahE2ETestCase(unittest.TestCase):
    def setUp(self):
        reset_db()
        if EVIDENCE_DIR.exists():
            shutil.rmtree(EVIDENCE_DIR)
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        init_db()
        reset_metrics()

    def tearDown(self):
        reset_db()

    def test_end_to_end_demo_flow(self):
        fixture = 'tests/fixtures/rss_sample.xml'
        result = run_ingest_pipeline('rss_news_minimal', use_fixture=True, fixture_path=fixture)
        assert result.items_ingested >= 1

        response = query_items()
        assert len(response['items']) >= 1
        first_item = response['items'][0]
        manifest_path = first_item['manifest_path']
        with open(manifest_path, 'r', encoding='utf-8') as handle:
            manifest = json.load(handle)
        assert manifest['source_id'] == 'rss_news_minimal'

        snapshot = get_snapshot()
        assert snapshot['inspectah_ingest_items_total']['count'] >= result.items_ingested
        assert snapshot['inspectah_explore_queries_total']['count'] >= 1.0


if __name__ == '__main__':
    unittest.main()
