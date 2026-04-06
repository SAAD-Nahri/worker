from __future__ import annotations

import sys
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from distribution_engine.models import (
    BlogFacebookMappingRecord,
    BlogPublishRecord,
    FacebookPublishRecord,
    QueueItemRecord,
    SocialPackageRecord,
    SocialPackageReviewRecord,
)
from distribution_engine.storage import (
    append_blog_publish_records,
    append_blog_facebook_mapping_records,
    append_facebook_publish_records,
    append_queue_item_records,
    append_social_package_records,
    append_social_package_review_records,
    load_latest_mapping_record,
    load_latest_blog_publish_record,
    load_latest_facebook_publish_for_social_package,
    load_latest_facebook_publish_record,
    load_latest_queue_item_record,
    load_latest_social_package_for_draft,
    load_latest_social_package_record,
    read_facebook_publish_records,
    read_social_package_review_records,
)


class BlogPublishStorageTests(unittest.TestCase):
    def test_append_and_load_latest_blog_publish_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "blog_publish_records.jsonl"
            first = BlogPublishRecord(
                blog_publish_id="blog-1",
                draft_id="draft-1",
                source_item_id="source-1",
                template_id="blog_food_fact_v1",
                wordpress_title="First Title",
                wordpress_slug="first-title",
                wordpress_excerpt="First excerpt",
                wordpress_body_html="<p>First</p>",
                wordpress_category="food-facts",
                wordpress_tags=["kitchen", "food-facts"],
                canonical_source_url="https://example.com/first",
                created_at="2026-04-03T12:00:00+00:00",
                updated_at="2026-04-03T12:00:00+00:00",
                last_publish_attempt_at="2026-04-03T12:00:00+00:00",
                last_publish_result="payload_prepared",
            )
            second = BlogPublishRecord(
                blog_publish_id="blog-1",
                draft_id="draft-1",
                source_item_id="source-1",
                template_id="blog_food_fact_v1",
                wordpress_title="Updated Title",
                wordpress_slug="updated-title",
                wordpress_excerpt="Updated excerpt",
                wordpress_body_html="<p>Updated</p>",
                wordpress_category="food-facts",
                wordpress_tags=["kitchen"],
                canonical_source_url="https://example.com/first",
                wordpress_status="draft_created",
                created_at="2026-04-03T12:05:00+00:00",
                updated_at="2026-04-03T12:05:00+00:00",
                last_publish_attempt_at="2026-04-03T12:05:00+00:00",
                last_publish_result="wordpress_draft_created",
            )

            append_blog_publish_records([first, second], path=path)

            latest = load_latest_blog_publish_record("blog-1", path=path)
            self.assertEqual(latest.wordpress_title, "Updated Title")
            self.assertEqual(latest.wordpress_status, "draft_created")

    def test_append_and_load_latest_social_package_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "social_package_records.jsonl"
            first = SocialPackageRecord(
                social_package_id="social-1",
                draft_id="draft-1",
                blog_publish_id="blog-1",
                package_template_id="fb_short_caption_v1",
                comment_template_id="fb_comment_link_line_v1",
                hook_text="Why this kitchen trick matters",
                caption_text="The full post gives the clean explanation in one quick read.",
                comment_cta_text="I'll drop the full post in the comments if you want the explanation.",
                created_at="2026-04-03T12:00:00+00:00",
                updated_at="2026-04-03T12:00:00+00:00",
            )
            second = SocialPackageRecord(
                social_package_id="social-1",
                draft_id="draft-1",
                blog_publish_id="blog-1",
                package_template_id="fb_short_caption_v1",
                comment_template_id="fb_comment_link_line_v1",
                hook_text="Why this kitchen trick matters",
                caption_text="The blog post breaks the answer down in one clean read.",
                comment_cta_text="Full post here if you want the full explanation.",
                approval_state="approved",
                blog_url="https://example.com/why-this-kitchen-trick-works",
                created_at="2026-04-03T12:05:00+00:00",
                updated_at="2026-04-03T12:05:00+00:00",
            )

            append_social_package_records([first, second], path=path)

            latest_by_id = load_latest_social_package_record("social-1", path=path)
            latest_by_draft = load_latest_social_package_for_draft("draft-1", path=path)
            self.assertEqual(latest_by_id.approval_state, "approved")
            self.assertEqual(latest_by_draft.comment_cta_text, "Full post here if you want the full explanation.")

    def test_append_and_load_latest_queue_and_mapping_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            queue_path = root / "queue_item_records.jsonl"
            mapping_path = root / "blog_facebook_mapping_records.jsonl"
            blog_queue = QueueItemRecord(
                queue_item_id="queue-blog-1",
                queue_type="blog_publish",
                draft_id="draft-1",
                blog_publish_id="blog-1",
                social_package_id=None,
                queue_state="ready_for_wordpress",
                approval_state="pending_review",
                last_transition_at="2026-04-03T12:00:00+00:00",
                created_at="2026-04-03T12:00:00+00:00",
                updated_at="2026-04-03T12:00:00+00:00",
            )
            blog_queue_updated = QueueItemRecord(
                queue_item_id="queue-blog-1",
                queue_type="blog_publish",
                draft_id="draft-1",
                blog_publish_id="blog-1",
                social_package_id=None,
                queue_state="wordpress_draft_created",
                approval_state="pending_review",
                last_transition_at="2026-04-03T12:05:00+00:00",
                created_at="2026-04-03T12:05:00+00:00",
                updated_at="2026-04-03T12:05:00+00:00",
            )
            mapping = BlogFacebookMappingRecord(
                mapping_id="map-1",
                source_item_id="source-1",
                draft_id="draft-1",
                blog_publish_id="blog-1",
                social_package_id=None,
                facebook_publish_id=None,
                selected_blog_title="Why This Kitchen Trick Works",
                mapping_status="blog_only",
                created_at="2026-04-03T12:00:00+00:00",
                updated_at="2026-04-03T12:00:00+00:00",
            )
            mapping_updated = BlogFacebookMappingRecord(
                mapping_id="map-1",
                source_item_id="source-1",
                draft_id="draft-1",
                blog_publish_id="blog-1",
                social_package_id="social-1",
                facebook_publish_id=None,
                selected_blog_title="Why This Kitchen Trick Works",
                selected_hook_text="Why this kitchen trick matters",
                selected_caption_text="The full post gives the clean explanation in one quick read.",
                selected_comment_cta_text="Full post here if you want the full explanation.",
                blog_url="https://example.com/why-this-kitchen-trick-works",
                mapping_status="packaged_social_pending",
                created_at="2026-04-03T12:05:00+00:00",
                updated_at="2026-04-03T12:05:00+00:00",
            )

            append_queue_item_records([blog_queue, blog_queue_updated], path=queue_path)
            append_blog_facebook_mapping_records([mapping, mapping_updated], path=mapping_path)

            latest_queue = load_latest_queue_item_record("queue-blog-1", path=queue_path)
            latest_mapping = load_latest_mapping_record("map-1", path=mapping_path)
            self.assertEqual(latest_queue.queue_state, "wordpress_draft_created")
            self.assertEqual(latest_mapping.mapping_status, "packaged_social_pending")

    def test_append_and_read_social_package_review_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "social_package_reviews.jsonl"
            review = SocialPackageReviewRecord(
                review_id="review-1",
                social_package_id="social-1",
                draft_id="draft-1",
                blog_publish_id="blog-1",
                reviewer_label="solo_operator",
                reviewed_at="2026-04-03T12:30:00+00:00",
                review_outcome="approved",
                previous_approval_state="pending_review",
                updated_approval_state="approved",
                review_notes=("hook_matches_blog",),
            )

            append_social_package_review_records([review], path=path)

            records = read_social_package_review_records(path=path)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].review_id, "review-1")

    def test_append_and_read_facebook_publish_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "facebook_publish_records.jsonl"
            first = FacebookPublishRecord(
                facebook_publish_id="fbpub-1",
                social_package_id="social-1",
                draft_id="draft-1",
                blog_publish_id="blog-1",
                destination_type="facebook_page",
                publish_status="scheduled",
                facebook_post_id="fb-post-123",
                scheduled_for_facebook="2026-04-03T14:00:00+00:00",
                created_at="2026-04-03T13:00:00+00:00",
                updated_at="2026-04-03T13:00:00+00:00",
                last_publish_attempt_at="2026-04-03T13:00:00+00:00",
                last_publish_result="facebook_scheduled",
            )
            second = FacebookPublishRecord(
                facebook_publish_id="fbpub-1",
                social_package_id="social-1",
                draft_id="draft-1",
                blog_publish_id="blog-1",
                destination_type="facebook_page",
                publish_status="published",
                facebook_post_id="fb-post-123",
                scheduled_for_facebook="2026-04-03T14:00:00+00:00",
                published_at_facebook="2026-04-03T14:01:00+00:00",
                created_at="2026-04-03T13:00:00+00:00",
                updated_at="2026-04-03T14:01:00+00:00",
                last_publish_attempt_at="2026-04-03T14:01:00+00:00",
                last_publish_result="facebook_published",
            )

            append_facebook_publish_records([first, second], path=path)

            records = read_facebook_publish_records(path=path)
            latest_by_id = load_latest_facebook_publish_record("fbpub-1", path=path)
            latest_by_social = load_latest_facebook_publish_for_social_package("social-1", path=path)
            self.assertEqual(len(records), 2)
            self.assertEqual(latest_by_id.publish_status, "published")
            self.assertEqual(latest_by_social.published_at_facebook, "2026-04-03T14:01:00+00:00")


if __name__ == "__main__":
    unittest.main()
