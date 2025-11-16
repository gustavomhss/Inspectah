import unittest
from datetime import datetime, timezone

from inspectah.fields.designer import normalize_url, parse_rfc822_date


class TransformsTestCase(unittest.TestCase):
    def test_parse_rfc822_date_variants(self):
        cases = [
            ("Tue, 03 Jun 2003 09:39:21 GMT", datetime(2003, 6, 3, 9, 39, 21, tzinfo=timezone.utc)),
            ("Fri, 21 Nov 1997 09:55:06 -0600", datetime(1997, 11, 21, 15, 55, 6, tzinfo=timezone.utc)),
        ]
        for raw, expected in cases:
            self.assertEqual(parse_rfc822_date(raw), expected)

    def test_parse_rfc822_date_invalid(self):
        with self.assertRaises(ValueError):
            parse_rfc822_date("not-a-date")

    def test_normalize_url(self):
        cases = [
            (" https://Example.com/News/ ", "https://example.com/News"),
            ("http://example.com", "http://example.com/"),
        ]
        for raw, expected in cases:
            self.assertEqual(normalize_url(raw), expected)

    def test_normalize_url_invalid(self):
        with self.assertRaises(ValueError):
            normalize_url(" " )


if __name__ == "__main__":
    unittest.main()
