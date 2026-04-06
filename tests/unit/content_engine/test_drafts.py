from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.drafts import create_draft_skeleton
from source_engine.models import SourceItem


def _build_source_item(
    template_suggestion: str = "food_fact_article",
    canonical_url: str = "https://example.com/story",
) -> SourceItem:
    return SourceItem(
        item_id="item-1234567890ab",
        source_id="src_test",
        source_name="Test Source",
        source_family="food_editorial",
        run_id="run-1",
        source_url="https://example.com/story?utm_source=test",
        canonical_url=canonical_url,
        discovered_at="2026-04-03T00:00:00+00:00",
        fetched_at="2026-04-03T00:00:00+00:00",
        raw_title="Why This Kitchen Trick Works",
        raw_summary="Short summary",
        raw_body_text="Useful body text for a source item.",
        author_name=None,
        published_at="2026-04-01T00:00:00+00:00",
        topical_label="food_explainer",
        freshness_label="fresh",
        normalization_status="normalized",
        dedupe_status="unique",
        quality_flags=[],
        template_suggestion=template_suggestion,
    )


class DraftSkeletonTests(unittest.TestCase):
    def test_create_draft_skeleton_preserves_source_lineage(self) -> None:
        item = _build_source_item()

        draft = create_draft_skeleton(item, created_at="2026-04-03T12:00:00+00:00")

        self.assertEqual(draft.source_item_id, item.item_id)
        self.assertEqual(draft.source_id, item.source_id)
        self.assertEqual(draft.source_url, "https://example.com/story")
        self.assertEqual(draft.source_domain, "example.com")
        self.assertEqual(draft.source_title, item.raw_title)
        self.assertEqual(draft.template_id, "blog_food_fact_v1")
        self.assertEqual(draft.category, "food-facts")

    def test_create_draft_skeleton_builds_expected_body_sections(self) -> None:
        item = _build_source_item(template_suggestion="food_benefit_article")

        draft = create_draft_skeleton(item, created_at="2026-04-03T12:00:00+00:00")

        self.assertEqual(
            [section.section_key for section in draft.sections],
            ["why_this_food_matters", "practical_points", "caution_or_limit", "conclusion"],
        )
        self.assertEqual(draft.quality_gate_status, "blocked")
        self.assertIn("draft_not_formatted", draft.quality_flags)
        self.assertEqual(draft.derivative_risk_level, "high")

    def test_create_draft_skeleton_uses_curiosity_template_defaults(self) -> None:
        item = _build_source_item(template_suggestion="curiosity_article")

        draft = create_draft_skeleton(item, created_at="2026-04-03T12:00:00+00:00")

        self.assertEqual(draft.template_id, "blog_curiosity_food_v1")
        self.assertEqual(draft.category, "food-questions")
        self.assertEqual(draft.headline_selected, item.raw_title)


if __name__ == "__main__":
    unittest.main()
