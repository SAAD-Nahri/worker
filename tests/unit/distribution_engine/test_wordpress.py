from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.formatting import format_source_item_to_draft
from content_engine.review import record_draft_review
from distribution_engine.wordpress import (
    build_wordpress_slug,
    prepare_blog_publish_record,
    render_draft_to_wordpress_html,
)
from source_engine.models import SourceItem


def _build_source_item(
    raw_title: str = "Why This Kitchen Trick Works",
    raw_summary: str = "A short summary about why the trick works.",
    template_suggestion: str = "food_fact_article",
) -> SourceItem:
    return SourceItem(
        item_id="item-phase3-123456",
        source_id="src_test",
        source_name="Test Source",
        source_family="food_editorial",
        run_id="run-1",
        source_url="https://example.com/story",
        canonical_url="https://example.com/story",
        discovered_at="2026-04-03T00:00:00+00:00",
        fetched_at="2026-04-03T00:00:00+00:00",
        raw_title=raw_title,
        raw_summary=raw_summary,
        raw_body_text=(
            "This kitchen behavior surprises a lot of people because the visible result looks simple while the underlying food science is doing several things at once. Heat changes texture, moisture changes timing, and ingredient structure affects how quickly a food reacts in the pan.\n\n"
            "The main reason the trick works is that heat, moisture, and ingredient structure all interact in predictable ways over a short period of time. When one part of that balance changes, cooks often see very different results even when they think they followed the same steps.\n\n"
            "When home cooks understand that relationship, they can get more consistent results and avoid common mistakes that feel random but actually follow a pattern. This makes the kitchen process less frustrating and turns a confusing habit into something practical and repeatable.\n\n"
            "That is why simple food facts often lead to better cooking habits. They give people a quick explanation, a useful takeaway, and a reason to keep using the method with more confidence the next time they cook."
        ),
        author_name=None,
        published_at="2026-04-01T00:00:00+00:00",
        topical_label="food_explainer",
        freshness_label="fresh",
        normalization_status="normalized",
        dedupe_status="unique",
        quality_flags=[],
        template_suggestion=template_suggestion,
    )


def _build_approved_draft() -> object:
    item = _build_source_item()
    draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")
    draft.related_read_bridge = "If this food explanation surprised you, the full archive uses the same answer-first structure."
    approved_draft, _ = record_draft_review(
        draft,
        review_outcome="approved",
        review_notes=["ready_for_queue"],
        reviewed_at="2026-04-03T12:05:00+00:00",
    )
    return approved_draft


class WordPressPublishingTests(unittest.TestCase):
    def test_render_draft_to_wordpress_html_preserves_structure(self) -> None:
        approved_draft = _build_approved_draft()

        html_output = render_draft_to_wordpress_html(approved_draft)

        self.assertIn("<p>", html_output)
        self.assertIn("<h2>The Short Answer</h2>", html_output)
        self.assertIn("<h2>Why It Happens</h2>", html_output)
        self.assertIn("<ul>", html_output)
        self.assertIn("If this food explanation surprised you", html_output)

    def test_prepare_blog_publish_record_requires_approved_draft(self) -> None:
        item = _build_source_item()
        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")

        with self.assertRaisesRegex(ValueError, "approved draft"):
            prepare_blog_publish_record(draft)

    def test_prepare_blog_publish_record_requires_pass_quality_without_override(self) -> None:
        approved_draft = _build_approved_draft()
        approved_draft.quality_gate_status = "review_flag"

        with self.assertRaisesRegex(ValueError, "pass-quality draft"):
            prepare_blog_publish_record(approved_draft)

    def test_prepare_blog_publish_record_allows_explicit_quality_override(self) -> None:
        approved_draft = _build_approved_draft()
        approved_draft.quality_gate_status = "review_flag"

        record = prepare_blog_publish_record(
            approved_draft,
            publish_intent="schedule",
            allow_non_pass_quality=True,
            created_at="2026-04-03T12:10:00+00:00",
        )

        self.assertEqual(record.publish_intent, "schedule")
        self.assertEqual(record.wordpress_status, "prepared_local")
        self.assertEqual(record.last_publish_result, "payload_prepared")
        self.assertEqual(record.created_at, "2026-04-03T12:10:00+00:00")

    def test_prepare_blog_publish_record_builds_expected_payload(self) -> None:
        approved_draft = _build_approved_draft()

        record = prepare_blog_publish_record(
            approved_draft,
            publish_intent="draft",
            created_at="2026-04-03T12:10:00+00:00",
        )

        self.assertEqual(record.draft_id, approved_draft.draft_id)
        self.assertEqual(record.source_item_id, approved_draft.source_item_id)
        self.assertEqual(record.wordpress_title, approved_draft.headline_selected)
        self.assertEqual(record.wordpress_excerpt, approved_draft.excerpt)
        self.assertEqual(record.wordpress_category, approved_draft.category)
        self.assertEqual(record.wordpress_tags, approved_draft.tag_candidates)
        self.assertEqual(record.wordpress_slug, "why-this-kitchen-trick-works")
        self.assertIn("<h2>The Short Answer</h2>", record.wordpress_body_html)

    def test_build_wordpress_slug_normalizes_unicode_and_punctuation(self) -> None:
        slug = build_wordpress_slug("The Only 2 Foods Jacques Pépin Thinks Twice About Eating!")

        self.assertEqual(slug, "the-only-2-foods-jacques-pepin-thinks-twice-about-eating")


if __name__ == "__main__":
    unittest.main()

