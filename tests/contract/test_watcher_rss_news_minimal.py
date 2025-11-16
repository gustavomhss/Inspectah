import json
import shutil
import unittest
from pathlib import Path

from inspectah.config import EVIDENCE_DIR
from inspectah.models import fetch_items_by_source, get_connection, init_db, reset_db
from inspectah.watchers import run_once_for_source


class WatcherContractTestCase(unittest.TestCase):
    def setUp(self):
        reset_db()
        target = EVIDENCE_DIR / 'rss_news_minimal'
        if target.exists():
            shutil.rmtree(target)
        init_db()

    def test_watcher_fixture_and_dedup(self):
        fixture = Path('tests/fixtures/rss_sample.xml')
        first_run = run_once_for_source('rss_news_minimal', use_fixture=True, fixture_path=str(fixture))
        self.assertEqual(first_run, 2)
        with get_connection() as conn:
            items = fetch_items_by_source(conn, 'rss_news_minimal')
        self.assertEqual(len(items), 2)
        for entry in items:
            manifest_path = Path(entry['manifest_path'])
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text())
            for key in ['item_id', 'source_id', 'canonical_url', 'collected_at', 'content_hash', 'evidence_sha256', 'raw_path', 'text_path']:
                self.assertIn(key, manifest)
            self.assertTrue(Path(manifest['raw_path']).exists())
            self.assertTrue(Path(manifest['text_path']).exists())
        second_run = run_once_for_source('rss_news_minimal', use_fixture=True, fixture_path=str(fixture))
        self.assertEqual(second_run, 0)
        with get_connection() as conn:
            self.assertEqual(len(fetch_items_by_source(conn, 'rss_news_minimal')), 2)


if __name__ == '__main__':
    unittest.main()
