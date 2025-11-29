import shutil
import unittest

from inspectah.config import EVIDENCE_DIR
from inspectah.metrics import get_snapshot, reset_metrics
from inspectah.models import init_db, reset_db
from inspectah.watchers import run_once_for_source
from inspectah.explore.api import query_items


class MetricsIntegrationTestCase(unittest.TestCase):
    def setUp(self):
        reset_db()
        if EVIDENCE_DIR.exists():
            shutil.rmtree(EVIDENCE_DIR)
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        init_db()
        reset_metrics()

    def test_metrics_snapshot_after_watcher_and_explore(self):
        fixture = 'tests/fixtures/rss_sample.xml'
        created = run_once_for_source('rss_news_minimal', use_fixture=True, fixture_path=fixture)
        self.assertGreaterEqual(created, 1)
        query_items()
        snapshot = get_snapshot()
        run_metrics = snapshot['inspectah_run_latency_ms']
        explore_metrics = snapshot['inspectah_explore_query_latency_ms']
        self.assertGreaterEqual(run_metrics['count'], 1)
        self.assertGreaterEqual(explore_metrics['count'], 1)
        self.assertGreaterEqual(run_metrics['min'], 0.0)
        self.assertGreaterEqual(explore_metrics['min'], 0.0)


if __name__ == '__main__':
    unittest.main()
