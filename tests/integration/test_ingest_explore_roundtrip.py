from __future__ import annotations
import shutil
import unittest

from inspectah.config import EVIDENCE_DIR
from inspectah.ingest.pipeline import run_ingest_pipeline
from inspectah.models import init_db, reset_db
from inspectah.explore.api import query_items
from inspectah.metrics import get_snapshot, reset_metrics


class IngestExploreRoundtripTestCase(unittest.TestCase):
    def setUp(self):
        reset_db()
        if EVIDENCE_DIR.exists():
            shutil.rmtree(EVIDENCE_DIR)
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        init_db()
        reset_metrics()

    def tearDown(self):
        reset_db()

    def test_ingest_fixture_and_query(self):
        fixture = 'tests/fixtures/rss_sample.xml'
        result = run_ingest_pipeline('rss_news_minimal', use_fixture=True, fixture_path=fixture)
        self.assertGreaterEqual(result.items_ingested, 1)

        response = query_items()
        self.assertGreaterEqual(len(response['items']), 1)
        item = response['items'][0]
        self.assertIn('fields', item)
        snapshot = get_snapshot()
        self.assertGreaterEqual(snapshot['inspectah_ingest_items_total']['count'], 1)
        self.assertGreaterEqual(snapshot['inspectah_explore_queries_total']['count'], 1)


if __name__ == '__main__':
    unittest.main()
