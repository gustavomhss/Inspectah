import json
import shutil
import unittest

from fastapi.testclient import TestClient

from inspectah.api import build_app
from inspectah.config import DB_PATH, EVIDENCE_DIR
from inspectah.explore.api import get_item_detail, query_items
from inspectah.explore.rate_limit import configure_rate_limit, reset_rate_limit_state
from inspectah.models import init_db, reset_db
from inspectah.watchers import run_once_for_source


class ExploreApiTestCase(unittest.TestCase):
    def setUp(self):
        reset_db()
        evidence_root = EVIDENCE_DIR / 'rss_news_minimal'
        if evidence_root.exists():
            shutil.rmtree(evidence_root)
        init_db()
        fixture = 'tests/fixtures/rss_sample.xml'
        created = run_once_for_source('rss_news_minimal', use_fixture=True, fixture_path=fixture)
        self.assertEqual(created, 2)
        configure_rate_limit(per_minute=5, burst=3)
        reset_rate_limit_state()
        app = build_app()
        self.client = TestClient(app)
        self.identity_headers = {'X-Client-Id': 'integration-suite'}

    def tearDown(self):
        reset_db()
        reset_rate_limit_state()

    def test_list_items_default(self):
        response = query_items()
        self.assertEqual(len(response['items']), 2)
        item = response['items'][0]
        self.assertIn('title', item)
        self.assertIn('url', item)
        self.assertIn('collected_at', item)

    def test_time_filter(self):
        response = query_items(collected_from='2999-01-01T00:00:00+00:00')
        self.assertEqual(len(response['items']), 0)

    def test_text_search(self):
        response = query_items(q='First')
        titles = [item['title'] for item in response['items']]
        self.assertEqual(titles, ['First Item'])

    def test_get_item_detail(self):
        item_id = query_items()['items'][0]['item_id']
        detail = get_item_detail(item_id)
        self.assertIn('manifest_path', detail)
        manifest_path = detail['manifest_path']
        with open(manifest_path, 'r', encoding='utf-8') as fh:
            manifest = json.load(fh)
        self.assertEqual(manifest['source_id'], 'rss_news_minimal')

    def test_explore_payload_includes_fields(self):
        response = self.client.get('/explore/items', headers=self.identity_headers)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('items', payload)
        self.assertGreater(len(payload['items']), 0)
        first_item = payload['items'][0]
        self.assertIn('fields', first_item)
        self.assertIsInstance(first_item['fields'], dict)
        self.assertIn('title', first_item['fields'])

    def test_rate_limit_headers_and_429(self):
        for _ in range(3):
            response = self.client.get('/explore/items', headers=self.identity_headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers.get('X-RateLimit-Limit'), '5')
            self.assertIn('X-RateLimit-Remaining', response.headers)
            self.assertIn('X-RateLimit-Reset', response.headers)
            self.assertEqual(response.headers.get('X-RateLimit-Policy'), '5/min burst 3')
        throttled = self.client.get('/explore/items', headers=self.identity_headers)
        self.assertEqual(throttled.status_code, 429)
        data = throttled.json()
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'RATE_LIMITED')
        self.assertIn('retry_after', data['error'])
        self.assertEqual(throttled.headers.get('X-RateLimit-Limit'), '5')
        self.assertEqual(throttled.headers.get('X-RateLimit-Policy'), '5/min burst 3')

    def test_sources_endpoint_returns_metadata(self):
        response = self.client.get('/explore/sources', headers=self.identity_headers)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('sources', payload)
        self.assertGreater(len(payload['sources']), 0)
        sample = payload['sources'][0]
        self.assertIn('id', sample)
        self.assertIn('name', sample)


if __name__ == '__main__':
    unittest.main()
