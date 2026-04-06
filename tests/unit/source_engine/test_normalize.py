from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from source_engine.models import FetchEntry, SourceRecord
from source_engine.normalize import normalize_source_item, normalize_url


class NormalizeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = SourceRecord(
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

    def test_normalize_url_strips_tracking_params(self) -> None:
        url = "https://Example.com/article/?utm_source=abc&fbclid=123&id=9"
        self.assertEqual(normalize_url(url), "https://example.com/article?id=9")

    def test_normalize_source_item_sets_flags_and_template(self) -> None:
        entry = FetchEntry(
            title="Why This Kitchen Trick Works",
            link="https://example.com/article?utm_source=abc",
            summary="<p>Useful summary</p>",
            content="",
            author_name="Tester",
            published_at="Thu, 02 Apr 2026 10:00:00 +0000",
        )
        item = normalize_source_item(self.source, entry, "2026-04-02T12:00:00+00:00")
        self.assertEqual(item.canonical_url, "https://example.com/article")
        self.assertEqual(item.template_suggestion, "curiosity_article")
        self.assertIn("article_body_not_fetched", item.quality_flags)
        self.assertEqual(item.body_extraction_status, "pending")
        self.assertGreater(item.body_word_count or 0, 0)


if __name__ == "__main__":
    unittest.main()
