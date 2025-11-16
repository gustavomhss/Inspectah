import tempfile
import unittest
from pathlib import Path

from inspectah.registry.loader import FieldConfig, SourceConfig, load_fields, load_sources


class RegistryLoaderTestCase(unittest.TestCase):
    def test_load_sources_rss_news_minimal(self):
        sources = load_sources()
        self.assertIn("rss_news_minimal", sources)
        cfg = sources["rss_news_minimal"]
        self.assertIsInstance(cfg, SourceConfig)
        self.assertEqual(cfg.name, "RSS News Minimal")
        self.assertEqual(cfg.type, "rss")
        self.assertEqual(cfg.schedule_minutes, 5)
        self.assertTrue(cfg.enabled)

    def test_load_fields_rss_news_minimal(self):
        fields = load_fields()
        self.assertIn("rss_news_minimal", fields)
        cfg = fields["rss_news_minimal"]
        self.assertIsInstance(cfg, FieldConfig)
        self.assertEqual({f.name for f in cfg.definitions}, {"title", "url", "published_at", "source_name"})
        url_field = next(f for f in cfg.definitions if f.name == "url")
        self.assertEqual(url_field.transforms, ["normalize_url"])

    def test_load_sources_invalid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "bad.yaml").write_text("name: missing_keys\n")
            with self.assertRaises(ValueError):
                load_sources(directory=Path(tmpdir))

    def test_load_fields_invalid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "bad.yaml").write_text("source_id: x\nfields:\n  - {}\n")
            with self.assertRaises(ValueError):
                load_fields(directory=Path(tmpdir))


if __name__ == "__main__":
    unittest.main()
