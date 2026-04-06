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
from distribution_engine.facebook import prepare_social_package_record, select_facebook_package_template_id
from distribution_engine.wordpress import prepare_blog_publish_record
from source_engine.models import SourceItem


def _build_source_item(
    item_id: str,
    raw_title: str,
    raw_summary: str,
    template_suggestion: str,
) -> SourceItem:
    return SourceItem(
        item_id=item_id,
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
            "This food question comes up often because the visible result looks simple, but ingredient behavior and kitchen context usually explain more than people expect. The practical answer becomes clearer once the basic cause is stated early.\n\n"
            "The short answer is that texture, moisture, timing, and ingredient structure often explain the result better than random luck. When those factors line up, the pattern looks surprising but still follows a repeatable explanation.\n\n"
            "That context helps people understand what they are seeing instead of treating the result like a mystery. The stronger explanation usually comes from a few clear signals, not from an overloaded list of trivia.\n\n"
            "Once the pattern is clear, the topic becomes easier to remember and easier to explain in a short mobile-friendly post."
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


def _build_approved_draft(
    item_id: str = "item-social-1",
    raw_title: str = "Why This Kitchen Trick Works",
    raw_summary: str = "A short summary about why the trick works.",
    template_suggestion: str = "food_fact_article",
):
    item = _build_source_item(
        item_id=item_id,
        raw_title=raw_title,
        raw_summary=raw_summary,
        template_suggestion=template_suggestion,
    )
    draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")
    approved_draft, _ = record_draft_review(
        draft,
        review_outcome="approved",
        review_notes=["ready_for_phase_3"],
        reviewed_at="2026-04-03T12:05:00+00:00",
    )
    return approved_draft


class FacebookPackagingTests(unittest.TestCase):
    def test_select_facebook_package_template_by_template_family(self) -> None:
        curiosity = _build_approved_draft(
            item_id="item-curiosity-1",
            raw_title="Why Do Onions Make You Cry",
            raw_summary="A short summary about why onions trigger tears.",
            template_suggestion="curiosity_article",
        )
        benefit = _build_approved_draft(
            item_id="item-benefit-1",
            raw_title="Why Beans Deserve A Place In More Weeknight Meals",
            raw_summary="A moderate, practical summary about why beans are useful.",
            template_suggestion="food_benefit_article",
        )
        fact = _build_approved_draft()

        self.assertEqual(select_facebook_package_template_id(curiosity), "fb_curiosity_hook_v1")
        self.assertEqual(select_facebook_package_template_id(benefit), "fb_soft_cta_post_v1")
        self.assertEqual(select_facebook_package_template_id(fact), "fb_short_caption_v1")

    def test_prepare_social_package_record_uses_confirmed_blog_url_only(self) -> None:
        approved_draft = _build_approved_draft()
        blog_record = prepare_blog_publish_record(
            approved_draft,
            created_at="2026-04-03T12:10:00+00:00",
            allow_non_pass_quality=True,
        )
        blog_record.wordpress_post_url = "https://example.com/why-this-kitchen-trick-works"

        package_without_confirmed_url = prepare_social_package_record(
            approved_draft,
            blog_publish_record=blog_record,
            created_at="2026-04-03T12:15:00+00:00",
        )

        self.assertIsNone(package_without_confirmed_url.blog_url)
        self.assertIn("drop the full post", package_without_confirmed_url.comment_cta_text.lower())

        blog_record.wordpress_status = "draft_created"
        package_with_confirmed_url = prepare_social_package_record(
            approved_draft,
            blog_publish_record=blog_record,
            created_at="2026-04-03T12:16:00+00:00",
        )

        self.assertEqual(package_with_confirmed_url.blog_url, blog_record.wordpress_post_url)
        self.assertIn("full post here", package_with_confirmed_url.comment_cta_text.lower())

    def test_prepare_social_package_record_requires_reviewed_approved_draft(self) -> None:
        approved_draft = _build_approved_draft()
        approved_draft.workflow_state = "drafted"

        with self.assertRaisesRegex(ValueError, "reviewed approved draft"):
            prepare_social_package_record(approved_draft)

    def test_prepare_social_package_record_rejects_mismatched_blog_publish_record(self) -> None:
        approved_draft = _build_approved_draft()
        other_draft = _build_approved_draft(item_id="item-social-2", raw_title="What Makes Whipped Cream Hold")
        mismatched_blog_record = prepare_blog_publish_record(
            other_draft,
            created_at="2026-04-03T12:20:00+00:00",
            allow_non_pass_quality=True,
        )

        with self.assertRaisesRegex(ValueError, "does not match the approved draft"):
            prepare_social_package_record(approved_draft, blog_publish_record=mismatched_blog_record)


if __name__ == "__main__":
    unittest.main()
