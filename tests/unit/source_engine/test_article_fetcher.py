from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from source_engine.fetch.article_fetcher import apply_article_body_result, extract_article_text, fetch_article_body
from source_engine.models import ArticleBodyResult, SourceItem, SourceRecord


class ArticleFetcherTests(unittest.TestCase):
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

    def test_fetch_article_body_blocks_external_domain(self) -> None:
        result = fetch_article_body(self.source, "https://outside.example.org/article")
        self.assertEqual(result.status, "blocked_external_domain")

    def test_extract_article_text_prefers_article_body_and_filters_boilerplate(self) -> None:
        html = """
        <html>
          <body>
            <article>
              <p>This is the first real paragraph with enough words to look like article content for extraction tests.</p>
              <p>Subscribe to our newsletter for updates.</p>
              <p>This is the second substantial paragraph and it should remain in the final extracted body text.</p>
              <p>Mikey says: this long reader comment should not remain in the extracted body because it is page discussion, not article copy.</p>
              <p>Your email address will not be published. Required fields are marked.</p>
              <script>var ignored = true;</script>
            </article>
          </body>
        </html>
        """
        text = extract_article_text(html)
        self.assertIn("first real paragraph", text)
        self.assertIn("second substantial paragraph", text)
        self.assertNotIn("newsletter", text.lower())
        self.assertNotIn("mikey says", text.lower())
        self.assertNotIn("your email address will not be published", text.lower())
        self.assertNotIn("ignored", text.lower())

    def test_apply_article_body_result_replaces_feed_body_on_success(self) -> None:
        item = SourceItem(
            item_id="1",
            source_id="src_test",
            source_name="Test Source",
            source_family="food_editorial",
            run_id=None,
            source_url="https://example.com/article",
            canonical_url="https://example.com/article",
            discovered_at="2026-04-02T00:00:00+00:00",
            fetched_at="2026-04-02T00:00:00+00:00",
            raw_title="Test Article",
            raw_summary="summary",
            raw_body_text="feed summary only",
            author_name=None,
            published_at=None,
            topical_label="food_explainer",
            freshness_label="fresh",
            normalization_status="normalized",
            dedupe_status="unique",
            body_extraction_status="pending",
            body_word_count=3,
            quality_flags=["article_body_not_fetched"],
        )
        result = ArticleBodyResult(
            url="https://example.com/article",
            status="fetched",
            body_text="This is a much richer article body with enough words to replace the feed text cleanly.",
            word_count=15,
        )
        apply_article_body_result(item, result)
        self.assertEqual(item.body_extraction_status, "fetched")
        self.assertEqual(item.raw_body_text, result.body_text)
        self.assertNotIn("article_body_not_fetched", item.quality_flags)


if __name__ == "__main__":
    unittest.main()
