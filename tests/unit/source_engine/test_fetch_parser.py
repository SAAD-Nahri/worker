from __future__ import annotations

import gzip
import sys
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from source_engine.fetch.http import read_response_payload
from source_engine.fetch.rss_fetcher import _parse_rss, fetch_feed_entries
from source_engine.models import SourceRecord


class FetchParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rss_source = SourceRecord(
            source_id="src_test",
            source_name="Test Source",
            domain="example.com",
            source_family="food_editorial",
            source_type="rss_plus_fetch",
            primary_topic_fit="test fit",
            active=True,
            priority_level="tier_1",
            rss_feed_url="https://example.com/feed",
            fetch_method="rss_discovery_plus_article_fetch",
            body_extraction_required=True,
            freshness_pattern="daily",
            quality_notes="ok",
            risk_notes="low",
            created_at="2026-04-02T00:00:00Z",
            updated_at="2026-04-02T00:00:00Z",
        )

    def test_parse_rss_items(self) -> None:
        payload = """
        <rss version="2.0">
          <channel>
            <item>
              <title>Why This Kitchen Trick Works</title>
              <link>https://example.com/article</link>
              <description><![CDATA[<p>Helpful text</p>]]></description>
              <pubDate>Thu, 02 Apr 2026 10:00:00 +0000</pubDate>
            </item>
          </channel>
        </rss>
        """
        root = ET.fromstring(payload)
        entries = list(_parse_rss(root))
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].title, "Why This Kitchen Trick Works")
        self.assertEqual(entries[0].summary, "Helpful text")

    def test_read_response_payload_decompresses_gzip(self) -> None:
        payload = gzip.compress(b"<rss></rss>")
        response = FakeResponse(payload, {"Content-Encoding": "gzip"})
        self.assertEqual(read_response_payload(response), b"<rss></rss>")

    def test_fetch_feed_entries_manual_seed_returns_manual_only(self) -> None:
        source = SourceRecord(
            source_id="src_manual",
            source_name="Manual Source",
            domain="example.com",
            source_family="food_editorial",
            source_type="manual_seed",
            primary_topic_fit="test fit",
            active=True,
            priority_level="tier_1",
            rss_feed_url=None,
            fetch_method="manual_review_only",
            body_extraction_required=False,
            freshness_pattern="irregular",
            quality_notes="ok",
            risk_notes="low",
            created_at="2026-04-02T00:00:00Z",
            updated_at="2026-04-02T00:00:00Z",
        )
        result, entries = fetch_feed_entries(source)
        self.assertEqual(result.status, "manual_only")
        self.assertEqual(result.fallback_action, "manual_seed_review")
        self.assertEqual(entries, [])

    def test_fetch_feed_entries_missing_rss_marks_source_degraded(self) -> None:
        source = SourceRecord(
            source_id="src_missing",
            source_name="Missing Feed Source",
            domain="example.com",
            source_family="food_editorial",
            source_type="rss_plus_fetch",
            primary_topic_fit="test fit",
            active=True,
            priority_level="tier_1",
            rss_feed_url=None,
            fetch_method="rss_discovery_plus_article_fetch",
            body_extraction_required=True,
            freshness_pattern="daily",
            quality_notes="ok",
            risk_notes="low",
            created_at="2026-04-02T00:00:00Z",
            updated_at="2026-04-02T00:00:00Z",
        )
        result, entries = fetch_feed_entries(source)
        self.assertEqual(result.status, "degraded")
        self.assertEqual(result.fallback_action, "manual_source_review")
        self.assertEqual(entries, [])


class FakeResponse:
    def __init__(self, payload: bytes, headers: dict[str, str]) -> None:
        self._payload = payload
        self._headers = headers

    def read(self, size: int | None = None) -> bytes:
        return self._payload

    def getheader(self, name: str) -> str | None:
        return self._headers.get(name)


if __name__ == "__main__":
    unittest.main()
