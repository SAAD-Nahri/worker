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
from distribution_engine.models import FacebookPublishRecord
from distribution_engine.workflow import (
    prepare_blog_facebook_mapping_record,
    prepare_blog_queue_item_record,
    prepare_facebook_queue_item_record,
)
from distribution_engine.wordpress import prepare_blog_publish_record
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-workflow-123456",
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


def _build_approved_draft():
    item = _build_source_item()
    draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")
    approved_draft, _ = record_draft_review(
        draft,
        review_outcome="approved",
        review_notes=["ready_for_phase_3"],
        reviewed_at="2026-04-03T12:05:00+00:00",
    )
    return approved_draft


class DistributionWorkflowTests(unittest.TestCase):
    def test_prepare_blog_queue_item_record_starts_ready_for_wordpress(self) -> None:
        approved_draft = _build_approved_draft()
        blog_record = prepare_blog_publish_record(
            approved_draft,
            allow_non_pass_quality=True,
            created_at="2026-04-03T12:10:00+00:00",
        )

        queue_record = prepare_blog_queue_item_record(blog_record, created_at="2026-04-03T12:20:00+00:00")

        self.assertEqual(queue_record.queue_type, "blog_publish")
        self.assertEqual(queue_record.queue_state, "ready_for_wordpress")
        self.assertEqual(queue_record.approval_state, "pending_review")

    def test_prepare_blog_queue_item_record_marks_ready_for_blog_schedule(self) -> None:
        approved_draft = _build_approved_draft()
        blog_record = prepare_blog_publish_record(
            approved_draft,
            publish_intent="schedule",
            allow_non_pass_quality=True,
            created_at="2026-04-03T12:10:00+00:00",
        )
        blog_record.wordpress_status = "draft_created"
        blog_record.wordpress_post_id = "wp-123"

        queue_record = prepare_blog_queue_item_record(blog_record, created_at="2026-04-03T12:20:00+00:00")

        self.assertEqual(queue_record.queue_state, "ready_for_blog_schedule")
        self.assertEqual(queue_record.approval_state, "pending_review")

    def test_prepare_facebook_queue_item_record_without_package_marks_pending(self) -> None:
        approved_draft = _build_approved_draft()
        blog_record = prepare_blog_publish_record(
            approved_draft,
            allow_non_pass_quality=True,
            created_at="2026-04-03T12:10:00+00:00",
        )

        queue_record = prepare_facebook_queue_item_record(blog_record, created_at="2026-04-03T12:20:00+00:00")

        self.assertEqual(queue_record.queue_type, "facebook_publish")
        self.assertEqual(queue_record.queue_state, "social_packaging_pending")
        self.assertEqual(queue_record.approval_state, "pending_review")

    def test_prepare_facebook_queue_item_record_with_approved_linked_package_is_queue_ready(self) -> None:
        approved_draft = _build_approved_draft()
        blog_record = prepare_blog_publish_record(
            approved_draft,
            allow_non_pass_quality=True,
            created_at="2026-04-03T12:10:00+00:00",
        )
        blog_record.wordpress_status = "draft_created"
        blog_record.wordpress_post_id = "wp-123"
        blog_record.wordpress_post_url = "https://example.com/why-this-kitchen-trick-works"
        social_record = prepare_social_package_record(
            approved_draft,
            blog_publish_record=blog_record,
            created_at="2026-04-03T12:15:00+00:00",
        )
        social_record.approval_state = "approved"

        queue_record = prepare_facebook_queue_item_record(
            blog_record,
            social_package_record=social_record,
            created_at="2026-04-03T12:20:00+00:00",
        )

        self.assertEqual(queue_record.queue_state, "approved_for_queue")
        self.assertEqual(queue_record.approval_state, "approved")

    def test_prepare_blog_facebook_mapping_record_preserves_selected_outputs(self) -> None:
        approved_draft = _build_approved_draft()
        blog_record = prepare_blog_publish_record(
            approved_draft,
            allow_non_pass_quality=True,
            created_at="2026-04-03T12:10:00+00:00",
        )
        blog_record.wordpress_status = "draft_created"
        blog_record.wordpress_post_url = "https://example.com/why-this-kitchen-trick-works"
        social_record = prepare_social_package_record(
            approved_draft,
            blog_publish_record=blog_record,
            created_at="2026-04-03T12:15:00+00:00",
        )

        mapping = prepare_blog_facebook_mapping_record(
            blog_record,
            social_package_record=social_record,
            created_at="2026-04-03T12:20:00+00:00",
        )

        self.assertEqual(mapping.mapping_status, "packaged_social_pending")
        self.assertEqual(mapping.selected_blog_title, blog_record.wordpress_title)
        self.assertEqual(mapping.selected_hook_text, social_record.hook_text)
        self.assertEqual(mapping.blog_url, blog_record.wordpress_post_url)

    def test_prepare_blog_facebook_mapping_record_rejects_unlinked_social_package(self) -> None:
        approved_draft = _build_approved_draft()
        blog_record = prepare_blog_publish_record(
            approved_draft,
            allow_non_pass_quality=True,
            created_at="2026-04-03T12:10:00+00:00",
        )
        social_record = prepare_social_package_record(
            approved_draft,
            blog_publish_record=blog_record,
            created_at="2026-04-03T12:15:00+00:00",
        )
        social_record.blog_publish_id = None

        with self.assertRaisesRegex(ValueError, "same blog_publish_id"):
            prepare_blog_facebook_mapping_record(blog_record, social_package_record=social_record)

    def test_prepare_facebook_queue_item_record_marks_scheduled_publish_state(self) -> None:
        approved_draft = _build_approved_draft()
        blog_record = prepare_blog_publish_record(
            approved_draft,
            allow_non_pass_quality=True,
            created_at="2026-04-03T12:10:00+00:00",
        )
        blog_record.wordpress_status = "published"
        blog_record.wordpress_post_id = "wp-123"
        blog_record.wordpress_post_url = "https://example.com/why-this-kitchen-trick-works"
        social_record = prepare_social_package_record(
            approved_draft,
            blog_publish_record=blog_record,
            created_at="2026-04-03T12:15:00+00:00",
        )
        social_record.approval_state = "approved"
        facebook_publish_record = FacebookPublishRecord(
            facebook_publish_id="fbpub-1",
            social_package_id=social_record.social_package_id,
            draft_id=approved_draft.draft_id,
            blog_publish_id=blog_record.blog_publish_id,
            destination_type="facebook_page",
            publish_status="scheduled",
            facebook_post_id="fb-post-123",
            scheduled_for_facebook="2026-04-03T15:00:00+00:00",
            created_at="2026-04-03T13:00:00+00:00",
            updated_at="2026-04-03T13:00:00+00:00",
            last_publish_attempt_at="2026-04-03T13:00:00+00:00",
            last_publish_result="facebook_scheduled",
        )

        queue_record = prepare_facebook_queue_item_record(
            blog_record,
            social_package_record=social_record,
            facebook_publish_record=facebook_publish_record,
            created_at="2026-04-03T13:05:00+00:00",
        )

        self.assertEqual(queue_record.queue_state, "scheduled_facebook")
        self.assertEqual(queue_record.approval_state, "approved")
        self.assertEqual(queue_record.scheduled_for, "2026-04-03T15:00:00+00:00")

    def test_prepare_blog_facebook_mapping_record_marks_social_published(self) -> None:
        approved_draft = _build_approved_draft()
        blog_record = prepare_blog_publish_record(
            approved_draft,
            allow_non_pass_quality=True,
            created_at="2026-04-03T12:10:00+00:00",
        )
        blog_record.wordpress_status = "published"
        blog_record.wordpress_post_id = "wp-123"
        blog_record.wordpress_post_url = "https://example.com/why-this-kitchen-trick-works"
        social_record = prepare_social_package_record(
            approved_draft,
            blog_publish_record=blog_record,
            created_at="2026-04-03T12:15:00+00:00",
        )
        social_record.approval_state = "approved"
        facebook_publish_record = FacebookPublishRecord(
            facebook_publish_id="fbpub-1",
            social_package_id=social_record.social_package_id,
            draft_id=approved_draft.draft_id,
            blog_publish_id=blog_record.blog_publish_id,
            destination_type="facebook_page",
            publish_status="published",
            facebook_post_id="fb-post-123",
            scheduled_for_facebook="2026-04-03T15:00:00+00:00",
            published_at_facebook="2026-04-03T15:01:00+00:00",
            created_at="2026-04-03T13:00:00+00:00",
            updated_at="2026-04-03T15:01:00+00:00",
            last_publish_attempt_at="2026-04-03T15:01:00+00:00",
            last_publish_result="facebook_published",
        )

        mapping = prepare_blog_facebook_mapping_record(
            blog_record,
            social_package_record=social_record,
            facebook_publish_record=facebook_publish_record,
            created_at="2026-04-03T15:02:00+00:00",
        )

        self.assertEqual(mapping.mapping_status, "social_published")
        self.assertEqual(mapping.facebook_publish_id, "fbpub-1")


if __name__ == "__main__":
    unittest.main()
