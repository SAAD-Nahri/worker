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
from distribution_engine.publish_updates import record_blog_publish_update
from distribution_engine.wordpress import prepare_blog_publish_record
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-blog-update-123456",
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


def _build_blog_publish_record():
    item = _build_source_item()
    draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")
    approved_draft, _ = record_draft_review(
        draft,
        review_outcome="approved",
        review_notes=["ready_for_phase_3"],
        reviewed_at="2026-04-03T12:05:00+00:00",
    )
    return prepare_blog_publish_record(
        approved_draft,
        allow_non_pass_quality=True,
        created_at="2026-04-03T12:10:00+00:00",
    )


class BlogPublishUpdateTests(unittest.TestCase):
    def test_record_blog_publish_update_marks_draft_created(self) -> None:
        blog_record = _build_blog_publish_record()

        updated = record_blog_publish_update(
            blog_record,
            update_action="draft_created",
            wordpress_post_id="wp-123",
            wordpress_post_url="https://example.com/why-this-kitchen-trick-works",
            attempted_at="2026-04-03T12:20:00+00:00",
        )

        self.assertEqual(updated.wordpress_status, "draft_created")
        self.assertEqual(updated.last_publish_result, "wordpress_draft_created")
        self.assertEqual(updated.wordpress_post_id, "wp-123")

    def test_record_blog_publish_update_marks_scheduled(self) -> None:
        blog_record = _build_blog_publish_record()
        blog_record.wordpress_status = "draft_created"
        blog_record.wordpress_post_id = "wp-123"

        updated = record_blog_publish_update(
            blog_record,
            update_action="scheduled",
            wordpress_post_id="wp-123",
            wordpress_post_url="https://example.com/why-this-kitchen-trick-works",
            schedule_mode="manual",
            schedule_approved_by="solo_operator",
            scheduled_for_blog="2026-04-04T12:00:00+00:00",
            attempted_at="2026-04-03T12:20:00+00:00",
        )

        self.assertEqual(updated.wordpress_status, "scheduled")
        self.assertEqual(updated.publish_intent, "schedule")
        self.assertEqual(updated.schedule_mode, "manual")
        self.assertEqual(updated.schedule_applied_by, "solo_operator")
        self.assertEqual(updated.scheduled_for_blog, "2026-04-04T12:00:00+00:00")

    def test_record_blog_publish_update_rejects_auto_schedule_without_schedule_intent(self) -> None:
        blog_record = _build_blog_publish_record()
        blog_record.wordpress_status = "draft_created"
        blog_record.wordpress_post_id = "wp-123"

        with self.assertRaisesRegex(ValueError, "publish_intent='schedule'"):
            record_blog_publish_update(
                blog_record,
                update_action="scheduled",
                wordpress_post_id="wp-123",
                schedule_mode="auto",
                scheduled_for_blog="2026-04-04T12:00:00+00:00",
            )

    def test_record_blog_publish_update_requires_error_for_failed(self) -> None:
        blog_record = _build_blog_publish_record()

        with self.assertRaisesRegex(ValueError, "requires error_message"):
            record_blog_publish_update(blog_record, update_action="failed")


if __name__ == "__main__":
    unittest.main()
