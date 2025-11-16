import json
import tempfile
from pathlib import Path

from inspectah.evidence import builder


SAMPLE_ITEM = {
    'source_id': 'rss_fixture',
    'item_id': 'rss-1',
    'run_id': 'run-123',
    'watcher_type': 'rss',
    'fetched_at': '2025-03-10T10:00:00Z',
    'request_url': 'fixtures/s5/rss_feed.xml',
}


def test_builder_creates_bundle_with_manifest():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = builder.build_bundle(
            SAMPLE_ITEM,
            raw_content=b'conteudo',
            text_content='texto',
            base_dir=tmpdir,
        )
        bundle_path = Path(result['bundle_path'])
        assert bundle_path.exists()
        manifest = json.loads((bundle_path / 'manifest.json').read_text())
        assert 'raw.bin' in manifest['files']
        assert 'text.txt' in manifest['files']
        meta = json.loads((bundle_path / 'meta.json').read_text())
        assert meta['source_id'] == SAMPLE_ITEM['source_id']


def test_builder_is_write_once():
    with tempfile.TemporaryDirectory() as tmpdir:
        builder.build_bundle(SAMPLE_ITEM, raw_content=b'1', text_content='a', base_dir=tmpdir)
        try:
            builder.build_bundle(SAMPLE_ITEM, raw_content=b'2', text_content='b', base_dir=tmpdir)
        except FileExistsError:
            return
        raise AssertionError('Esperava FileExistsError ao recriar bundle')
