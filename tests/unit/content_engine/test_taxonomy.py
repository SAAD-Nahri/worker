from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.taxonomy import assign_category_and_tags
from content_engine.templates import get_blog_template_contract
from source_engine.models import SourceItem


def _build_source_item(
    raw_title: str,
    raw_body_text: str,
    template_suggestion: str = "food_fact_article",
    topical_label: str = "food_explainer",
    source_family: str = "food_editorial",
) -> SourceItem:
    return SourceItem(
        item_id="item-taxonomy-123456",
        source_id="src_test",
        source_name="Test Source",
        source_family=source_family,
        run_id="run-1",
        source_url="https://example.com/story",
        canonical_url="https://example.com/story",
        discovered_at="2026-04-03T00:00:00+00:00",
        fetched_at="2026-04-03T00:00:00+00:00",
        raw_title=raw_title,
        raw_summary="Short summary",
        raw_body_text=raw_body_text,
        author_name=None,
        published_at="2026-04-01T00:00:00+00:00",
        topical_label=topical_label,
        freshness_label="fresh",
        normalization_status="normalized",
        dedupe_status="unique",
        quality_flags=[],
        template_suggestion=template_suggestion,
    )


class TaxonomyTests(unittest.TestCase):
    def test_assign_category_and_tags_uses_template_default_for_food_fact(self) -> None:
        item = _build_source_item(
            raw_title="Why This Kitchen Trick Works",
            raw_body_text=(
                "Heat, moisture, and ingredient structure all affect the result in the pan. "
                "That pattern matters because small shifts change the timing and texture quickly."
            ),
        )

        category, tags = assign_category_and_tags(
            item,
            get_blog_template_contract("blog_food_fact_v1"),
            ["ingredient structure", "heat", "moisture"],
        )

        self.assertEqual(category, "food-facts")
        self.assertIn("practical-cooking", tags)
        self.assertIn("food-science", tags)
        self.assertIn("question-angle", tags)

    def test_assign_category_and_tags_overrides_for_ingredient_guides(self) -> None:
        item = _build_source_item(
            raw_title="How Yogurt Changes In The Fridge",
            raw_body_text=(
                "Yogurt changes in the fridge because storage time and temperature affect texture. "
                "Understanding that pattern makes the ingredient easier to use."
            ),
            topical_label="ingredient_explainer",
            source_family="ingredient_reference",
        )

        category, tags = assign_category_and_tags(
            item,
            get_blog_template_contract("blog_food_fact_v1"),
            ["yogurt", "storage", "temperature"],
        )

        self.assertEqual(category, "ingredient-guides")
        self.assertIn("ingredient-basics", tags)
        self.assertIn("food-storage", tags)

    def test_assign_category_and_tags_overrides_for_food_history(self) -> None:
        item = _build_source_item(
            raw_title="What Is The Oldest Soup Tradition Still Served Today?",
            raw_body_text=(
                "The origin of a soup tradition can stay visible for centuries when it remains tied to regional culture and everyday cooking. "
                "That history survives because the dish keeps both meaning and usefulness."
            ),
            template_suggestion="curiosity_article",
            topical_label="food_history",
            source_family="curiosity_editorial",
        )

        category, tags = assign_category_and_tags(
            item,
            get_blog_template_contract("blog_curiosity_food_v1"),
            ["oldest soup", "regional culture", "origin"],
        )

        self.assertEqual(category, "food-history-culture")
        self.assertIn("food-history", tags)
        self.assertIn("food-origins", tags)
        self.assertIn("food-culture", tags)


if __name__ == "__main__":
    unittest.main()
