from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from source_engine.dedupe import check_duplicate, update_dedupe_index
from source_engine.models import SourceItem


def build_item(item_id: str, title: str, canonical_url: str) -> SourceItem:
    return SourceItem(
        item_id=item_id,
        source_id="src_test",
        source_name="Test Source",
        source_family="food_editorial",
        run_id=None,
        source_url=canonical_url,
        canonical_url=canonical_url,
        discovered_at="2026-04-02T00:00:00+00:00",
        fetched_at="2026-04-02T00:00:00+00:00",
        raw_title=title,
        raw_summary="summary",
        raw_body_text="body",
        author_name=None,
        published_at=None,
        topical_label="food_explainer",
        freshness_label="fresh",
        normalization_status="normalized",
        dedupe_status="pending",
    )


class DedupeTests(unittest.TestCase):
    def test_exact_duplicate_by_canonical_url(self) -> None:
        index = {"canonical_urls": {}, "normalized_titles": {}, "title_tokens": {}}
        first = build_item("1", "Why This Kitchen Trick Works", "https://example.com/article")
        index = update_dedupe_index(first, index)
        duplicate = build_item("2", "Different Title", "https://example.com/article")
        result = check_duplicate(duplicate, index)
        self.assertEqual(result.status, "exact_duplicate")

    def test_near_duplicate_by_normalized_title(self) -> None:
        index = {"canonical_urls": {}, "normalized_titles": {}, "title_tokens": {}}
        first = build_item("1", "Why This Kitchen Trick Works", "https://example.com/article")
        index = update_dedupe_index(first, index)
        duplicate = build_item("2", "Why This Kitchen Trick Works!", "https://example.com/article-2")
        result = check_duplicate(duplicate, index)
        self.assertEqual(result.status, "near_duplicate")


if __name__ == "__main__":
    unittest.main()
