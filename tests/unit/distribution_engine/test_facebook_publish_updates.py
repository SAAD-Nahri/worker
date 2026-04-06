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
from distribution_engine.facebook import prepare_social_package_record
from distribution_engine.facebook_publish_updates import record_facebook_publish_update
from distribution_engine.wordpress import prepare_blog_publish_record
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-facebook-update-123456",
        source_id="src_test",
        source_name="Test Source",
        source_family="food_editorial",
        run_id="run-1",
        source_url="https://example.com/story",
        canonical_url="https://example.com/story",
        discovered_at="2026-04-03T00:00:00+00:00",
        fetched_at="2026-04-03T00:00:00+00:00",
        raw_title="Why This Kitchen Trick Works",
        raw_summary="A short summary about why the trick works.",
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
        template_suggestion="food_fact_article",
    )


def _build_linked_social_package():
    item = _build_source_item()
    draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")
    approved_draft, _ = record_draft_review(
        draft,
        review_outcome="approved",
        review_notes=["ready_for_phase_3"],
        reviewed_at="2026-04-03T12:05:00+00:00",
    )
    blog_record = prepare_blog_publish_record(
        approved_draft,
        allow_non_pass_quality=True,
        created_at="2026-04-03T12:10:00+00:00",
    )
    blog_record.wordpress_status = "published"
    blog_record.wordpress_post_id = "wp-123"
    blog_record.wordpress_post_url = "https://example.com/why-this-kitchen-trick-works"
    blog_record.published_at_blog = "2026-04-03T12:20:00+00:00"
    social_record = prepare_social_package_record(
        approved_draft,
        blog_publish_record=blog_record,
        created_at="2026-04-03T12:25:00+00:00",
    )
    social_record.approval_state = "approved"
    return social_record, blog_record


class FacebookPublishUpdateTests(unittest.TestCase):
    def test_record_facebook_publish_update_marks_scheduled(self) -> None:
        social_record, blog_record = _build_linked_social_package()

        publish_record = record_facebook_publish_update(
            social_record,
            blog_record,
            update_action="scheduled",
            facebook_post_id="fb-post-123",
            schedule_mode="manual",
            schedule_approved_by="solo_operator",
            scheduled_for_facebook="2026-04-03T15:00:00+00:00",
            attempted_at="2026-04-03T13:00:00+00:00",
        )

        self.assertEqual(publish_record.publish_status, "scheduled")
        self.assertEqual(publish_record.facebook_post_id, "fb-post-123")
        self.assertEqual(publish_record.schedule_mode, "manual")
        self.assertEqual(publish_record.scheduled_for_facebook, "2026-04-03T15:00:00+00:00")
        self.assertEqual(publish_record.last_publish_result, "facebook_scheduled")

    def test_record_facebook_publish_update_marks_published(self) -> None:
        social_record, blog_record = _build_linked_social_package()
        scheduled_record = record_facebook_publish_update(
            social_record,
            blog_record,
            update_action="scheduled",
            facebook_post_id="fb-post-123",
            schedule_mode="manual",
            scheduled_for_facebook="2026-04-03T15:00:00+00:00",
            attempted_at="2026-04-03T13:00:00+00:00",
        )

        published_record = record_facebook_publish_update(
            social_record,
            blog_record,
            update_action="published",
            existing_publish_record=scheduled_record,
            facebook_post_id="fb-post-123",
            published_at_facebook="2026-04-03T15:01:00+00:00",
            attempted_at="2026-04-03T15:01:00+00:00",
        )

        self.assertEqual(published_record.facebook_publish_id, scheduled_record.facebook_publish_id)
        self.assertEqual(published_record.publish_status, "published")
        self.assertEqual(published_record.published_at_facebook, "2026-04-03T15:01:00+00:00")

    def test_record_facebook_publish_update_rejects_published_before_blog_is_live(self) -> None:
        social_record, blog_record = _build_linked_social_package()
        blog_record.wordpress_status = "draft_created"

        with self.assertRaisesRegex(ValueError, "linked blog publish record to already be published"):
            record_facebook_publish_update(
                social_record,
                blog_record,
                update_action="published",
                facebook_post_id="fb-post-123",
                published_at_facebook="2026-04-03T15:01:00+00:00",
            )

    def test_record_facebook_publish_update_requires_confirmed_blog_url(self) -> None:
        social_record, blog_record = _build_linked_social_package()
        blog_record.wordpress_status = "prepared_local"
        blog_record.wordpress_post_url = None

        with self.assertRaisesRegex(ValueError, "confirmed blog URL"):
            record_facebook_publish_update(
                social_record,
                blog_record,
                update_action="scheduled",
                facebook_post_id="fb-post-123",
                scheduled_for_facebook="2026-04-03T15:00:00+00:00",
            )

    def test_record_facebook_publish_update_rejects_facebook_schedule_before_blog_schedule(self) -> None:
        social_record, blog_record = _build_linked_social_package()
        blog_record.wordpress_status = "scheduled"
        blog_record.scheduled_for_blog = "2026-04-03T15:00:00+00:00"

        with self.assertRaisesRegex(ValueError, "cannot be earlier"):
            record_facebook_publish_update(
                social_record,
                blog_record,
                update_action="scheduled",
                facebook_post_id="fb-post-123",
                schedule_mode="manual",
                scheduled_for_facebook="2026-04-03T14:30:00+00:00",
            )

    def test_record_facebook_publish_update_requires_error_for_failed(self) -> None:
        social_record, blog_record = _build_linked_social_package()

        with self.assertRaisesRegex(ValueError, "requires error_message"):
            record_facebook_publish_update(
                social_record,
                blog_record,
                update_action="failed",
            )


if __name__ == "__main__":
    unittest.main()
