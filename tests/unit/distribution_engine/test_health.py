from __future__ import annotations

import sys
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from distribution_engine.health import build_distribution_health_report
from distribution_engine.models import (
    BlogPublishRecord,
    FacebookPublishRecord,
    SocialPackageRecord,
    SocialPackageReviewRecord,
)
from distribution_engine.review import record_social_package_review
from distribution_engine.storage import (
    append_blog_facebook_mapping_records,
    append_blog_publish_records,
    append_facebook_publish_records,
    append_queue_item_records,
    append_social_package_records,
    append_social_package_review_records,
)
from distribution_engine.workflow import prepare_distribution_linkage_records


def _build_blog_publish_record(
    blog_publish_id: str,
    *,
    draft_id: str,
    source_item_id: str,
    title: str,
    wordpress_status: str,
    publish_intent: str = "draft",
    wordpress_post_id: str | None = None,
    wordpress_post_url: str | None = None,
    schedule_mode: str | None = None,
    scheduled_for_blog: str | None = None,
    published_at_blog: str | None = None,
    last_error: str | None = None,
    updated_at: str = "2026-04-03T12:00:00+00:00",
) -> BlogPublishRecord:
    return BlogPublishRecord(
        blog_publish_id=blog_publish_id,
        draft_id=draft_id,
        source_item_id=source_item_id,
        template_id="blog_food_fact_v1",
        wordpress_title=title,
        wordpress_slug=title.lower().replace(" ", "-"),
        wordpress_excerpt=f"Excerpt for {title}",
        wordpress_body_html=f"<p>{title}</p>",
        wordpress_category="Food Facts",
        wordpress_tags=["Kitchen Science"],
        publish_intent=publish_intent,
        canonical_source_url=f"https://example.com/{source_item_id}",
        wordpress_post_id=wordpress_post_id,
        wordpress_post_url=wordpress_post_url,
        wordpress_status=wordpress_status,
        schedule_mode=schedule_mode,
        scheduled_for_blog=scheduled_for_blog,
        published_at_blog=published_at_blog,
        last_publish_attempt_at=updated_at,
        last_publish_result=wordpress_status,
        last_error=last_error,
        created_at=updated_at,
        updated_at=updated_at,
    )


def _build_social_package_record(
    social_package_id: str,
    *,
    draft_id: str,
    blog_publish_id: str,
    approval_state: str,
    updated_at: str = "2026-04-03T12:10:00+00:00",
) -> SocialPackageRecord:
    return SocialPackageRecord(
        social_package_id=social_package_id,
        draft_id=draft_id,
        blog_publish_id=blog_publish_id,
        package_template_id="fb_curiosity_hook_v1",
        comment_template_id="fb_comment_link_line_v1",
        hook_text="Why this food trick works",
        caption_text="A short caption that stays aligned with the blog draft.",
        comment_cta_text="Read more in the blog post.",
        target_destination="facebook_page",
        approval_state=approval_state,
        blog_url="https://blog.example.com/post",
        selected_variant_label="primary",
        packaging_notes=None,
        created_at=updated_at,
        updated_at=updated_at,
    )


def _build_facebook_publish_record(
    facebook_publish_id: str,
    *,
    social_package_id: str,
    draft_id: str,
    blog_publish_id: str,
    publish_status: str,
    facebook_post_id: str | None = None,
    schedule_mode: str | None = None,
    scheduled_for_facebook: str | None = None,
    published_at_facebook: str | None = None,
    last_error: str | None = None,
    updated_at: str = "2026-04-03T12:20:00+00:00",
) -> FacebookPublishRecord:
    return FacebookPublishRecord(
        facebook_publish_id=facebook_publish_id,
        social_package_id=social_package_id,
        draft_id=draft_id,
        blog_publish_id=blog_publish_id,
        destination_type="facebook_page",
        publish_status=publish_status,
        facebook_post_id=facebook_post_id,
        schedule_mode=schedule_mode,
        scheduled_for_facebook=scheduled_for_facebook,
        published_at_facebook=published_at_facebook,
        last_publish_attempt_at=updated_at,
        last_publish_result=publish_status,
        last_error=last_error,
        created_at=updated_at,
        updated_at=updated_at,
    )


class DistributionHealthTests(unittest.TestCase):
    def test_build_distribution_health_report_aggregates_latest_distribution_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            blog_path = root / "blog_publish_records.jsonl"
            social_path = root / "social_package_records.jsonl"
            review_path = root / "social_package_reviews.jsonl"
            facebook_path = root / "facebook_publish_records.jsonl"
            queue_path = root / "queue_item_records.jsonl"
            mapping_path = root / "blog_facebook_mapping_records.jsonl"

            published_blog = _build_blog_publish_record(
                "blog-published-1",
                draft_id="draft-1",
                source_item_id="source-1",
                title="Why Butter Changes Flavor",
                wordpress_status="published",
                publish_intent="draft",
                wordpress_post_id="wp-101",
                wordpress_post_url="https://blog.example.com/butter",
                published_at_blog="2026-04-03T12:12:00+00:00",
                updated_at="2026-04-03T12:12:00+00:00",
            )
            pending_old = _build_blog_publish_record(
                "blog-pending-1",
                draft_id="draft-2",
                source_item_id="source-2",
                title="Why Salt Changes Texture",
                wordpress_status="prepared_local",
                updated_at="2026-04-03T12:00:00+00:00",
            )
            pending_latest = _build_blog_publish_record(
                "blog-pending-1",
                draft_id="draft-2",
                source_item_id="source-2",
                title="Why Salt Changes Texture",
                wordpress_status="draft_created",
                wordpress_post_id="wp-102",
                publish_intent="draft",
                updated_at="2026-04-03T12:14:00+00:00",
            )
            failed_blog = _build_blog_publish_record(
                "blog-failed-1",
                draft_id="draft-3",
                source_item_id="source-3",
                title="Why Steam Changes Cooking",
                wordpress_status="published",
                wordpress_post_id="wp-103",
                wordpress_post_url="https://blog.example.com/steam",
                published_at_blog="2026-04-03T12:11:00+00:00",
                updated_at="2026-04-03T12:11:00+00:00",
            )

            append_blog_publish_records(
                [published_blog, pending_old, pending_latest, failed_blog],
                path=blog_path,
            )

            approved_social = _build_social_package_record(
                "social-approved-1",
                draft_id="draft-1",
                blog_publish_id="blog-published-1",
                approval_state="approved",
                updated_at="2026-04-03T12:13:00+00:00",
            )
            pending_social = _build_social_package_record(
                "social-pending-1",
                draft_id="draft-3",
                blog_publish_id="blog-failed-1",
                approval_state="pending_review",
                updated_at="2026-04-03T12:15:00+00:00",
            )
            append_social_package_records([approved_social, pending_social], path=social_path)

            approved_social_latest, rejected_review = record_social_package_review(
                approved_social,
                review_outcome="needs_edits",
                review_notes=["tighten hook"],
                reviewer_label="solo_operator",
                reviewed_at="2026-04-03T12:13:30+00:00",
            )
            approved_social_final, approved_review = record_social_package_review(
                approved_social_latest,
                review_outcome="approved",
                review_notes=["hook_matches_blog"],
                reviewer_label="solo_operator",
                reviewed_at="2026-04-03T12:14:00+00:00",
            )
            append_social_package_records([approved_social_latest, approved_social_final], path=social_path)
            append_social_package_review_records(
                [rejected_review, approved_review],
                path=review_path,
            )

            published_facebook = _build_facebook_publish_record(
                "fb-publish-1",
                social_package_id=approved_social_final.social_package_id,
                draft_id="draft-1",
                blog_publish_id="blog-published-1",
                publish_status="published",
                facebook_post_id="fb-1001",
                published_at_facebook="2026-04-03T12:16:00+00:00",
                updated_at="2026-04-03T12:16:00+00:00",
            )
            failed_facebook = _build_facebook_publish_record(
                "fb-publish-2",
                social_package_id=pending_social.social_package_id,
                draft_id="draft-3",
                blog_publish_id="blog-failed-1",
                publish_status="failed",
                last_error="facebook_api_timeout",
                updated_at="2026-04-03T12:17:00+00:00",
            )
            append_facebook_publish_records([published_facebook, failed_facebook], path=facebook_path)

            row1_blog_queue, row1_fb_queue, row1_mapping = prepare_distribution_linkage_records(
                published_blog,
                social_package_record=approved_social_final,
                facebook_publish_record=published_facebook,
                created_at="2026-04-03T12:16:00+00:00",
            )
            row2_blog_queue, row2_fb_queue, row2_mapping = prepare_distribution_linkage_records(
                pending_latest,
                created_at="2026-04-03T12:14:30+00:00",
            )
            row3_blog_queue, row3_fb_queue, row3_mapping = prepare_distribution_linkage_records(
                failed_blog,
                social_package_record=pending_social,
                facebook_publish_record=failed_facebook,
                created_at="2026-04-03T12:17:00+00:00",
            )
            append_queue_item_records(
                [row1_blog_queue, row1_fb_queue, row2_blog_queue, row2_fb_queue, row3_blog_queue, row3_fb_queue],
                path=queue_path,
            )
            append_blog_facebook_mapping_records([row1_mapping, row2_mapping, row3_mapping], path=mapping_path)

            summary, rows = build_distribution_health_report(
                blog_publish_records_path=blog_path,
                social_package_records_path=social_path,
                social_package_reviews_path=review_path,
                facebook_publish_records_path=facebook_path,
                queue_item_records_path=queue_path,
                mapping_records_path=mapping_path,
            )

            self.assertEqual(summary.total_blog_publish_chains, 3)
            self.assertEqual(summary.wordpress_status_counts["published"], 2)
            self.assertEqual(summary.wordpress_status_counts["draft_created"], 1)
            self.assertEqual(summary.social_approval_counts["approved"], 1)
            self.assertEqual(summary.social_approval_counts["pending_review"], 1)
            self.assertEqual(summary.social_approval_counts["none"], 1)
            self.assertEqual(summary.facebook_publish_status_counts["published"], 1)
            self.assertEqual(summary.facebook_publish_status_counts["failed"], 1)
            self.assertEqual(summary.facebook_publish_status_counts["none"], 1)
            self.assertEqual(summary.blog_chains_with_social_package, 2)
            self.assertEqual(summary.blog_chains_with_remote_wordpress_post, 3)
            self.assertEqual(summary.blog_chains_with_confirmed_blog_url, 2)
            self.assertEqual(summary.blog_chains_with_facebook_post_id, 1)
            self.assertEqual(summary.rows_with_consistency_issues, 0)
            self.assertEqual(summary.rows_with_schedule_alerts, 0)
            self.assertIn(("facebook_api_timeout", 1), summary.top_errors)

            row_by_id = {row.blog_publish_id: row for row in rows}
            self.assertEqual(row_by_id["blog-published-1"].operator_signal, "published_facebook")
            self.assertEqual(row_by_id["blog-published-1"].social_review_count, 2)
            self.assertEqual(row_by_id["blog-published-1"].latest_social_review_outcome, "approved")
            self.assertEqual(row_by_id["blog-published-1"].consistency_issues, ())
            self.assertEqual(row_by_id["blog-pending-1"].operator_signal, "social_packaging_pending")
            self.assertEqual(row_by_id["blog-pending-1"].wordpress_status, "draft_created")
            self.assertEqual(row_by_id["blog-failed-1"].operator_signal, "facebook_publish_failed")
            self.assertEqual(row_by_id["blog-failed-1"].last_facebook_error, "facebook_api_timeout")
            self.assertEqual(row_by_id["blog-failed-1"].consistency_issues, ())

    def test_build_distribution_health_report_flags_missing_workflow_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            blog_path = root / "blog_publish_records.jsonl"

            orphan_blog = _build_blog_publish_record(
                "blog-orphan-1",
                draft_id="draft-orphan",
                source_item_id="source-orphan",
                title="Why Citrus Smells Stronger",
                wordpress_status="prepared_local",
                updated_at="2026-04-03T12:18:00+00:00",
            )
            append_blog_publish_records([orphan_blog], path=blog_path)

            summary, rows = build_distribution_health_report(blog_publish_records_path=blog_path)

            self.assertEqual(summary.total_blog_publish_chains, 1)
            self.assertEqual(summary.operator_signal_counts["state_incomplete"], 1)
            self.assertEqual(summary.rows_with_consistency_issues, 1)
            self.assertEqual(summary.consistency_issue_counts["missing_workflow_state"], 1)
            self.assertEqual(rows[0].operator_signal, "state_incomplete")
            self.assertEqual(rows[0].blog_queue_state, None)
            self.assertEqual(rows[0].facebook_queue_state, None)
            self.assertEqual(rows[0].mapping_status, None)
            self.assertEqual(rows[0].consistency_issues, ("missing_workflow_state",))

    def test_build_distribution_health_report_detects_schedule_collisions_and_schedule_order_issues(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            blog_path = root / "blog_publish_records.jsonl"
            social_path = root / "social_package_records.jsonl"
            facebook_path = root / "facebook_publish_records.jsonl"
            queue_path = root / "queue_item_records.jsonl"
            mapping_path = root / "blog_facebook_mapping_records.jsonl"

            shared_blog_schedule = "2026-04-04T10:00:00+00:00"
            shared_facebook_schedule = "2026-04-04T11:00:00+00:00"

            scheduled_blog_a = _build_blog_publish_record(
                "blog-scheduled-a",
                draft_id="draft-scheduled-a",
                source_item_id="source-scheduled-a",
                title="Why Garlic Smells Stronger",
                wordpress_status="scheduled",
                publish_intent="schedule",
                wordpress_post_id="wp-401",
                wordpress_post_url="https://blog.example.com/garlic",
                schedule_mode="manual",
                scheduled_for_blog=shared_blog_schedule,
                updated_at="2026-04-03T13:00:00+00:00",
            )
            scheduled_blog_b = _build_blog_publish_record(
                "blog-scheduled-b",
                draft_id="draft-scheduled-b",
                source_item_id="source-scheduled-b",
                title="Why Tomato Flavor Changes",
                wordpress_status="scheduled",
                publish_intent="schedule",
                wordpress_post_id="wp-402",
                wordpress_post_url="https://blog.example.com/tomato",
                schedule_mode="manual",
                scheduled_for_blog=shared_blog_schedule,
                updated_at="2026-04-03T13:01:00+00:00",
            )
            scheduled_blog_c = _build_blog_publish_record(
                "blog-scheduled-c",
                draft_id="draft-scheduled-c",
                source_item_id="source-scheduled-c",
                title="Why Pepper Feels Hot",
                wordpress_status="scheduled",
                publish_intent="schedule",
                wordpress_post_id="wp-403",
                wordpress_post_url="https://blog.example.com/pepper",
                schedule_mode="manual",
                scheduled_for_blog="2026-04-04T12:00:00+00:00",
                updated_at="2026-04-03T13:02:00+00:00",
            )
            append_blog_publish_records(
                [scheduled_blog_a, scheduled_blog_b, scheduled_blog_c],
                path=blog_path,
            )

            social_a = _build_social_package_record(
                "social-scheduled-a",
                draft_id="draft-scheduled-a",
                blog_publish_id="blog-scheduled-a",
                approval_state="approved",
                updated_at="2026-04-03T13:03:00+00:00",
            )
            social_b = _build_social_package_record(
                "social-scheduled-b",
                draft_id="draft-scheduled-b",
                blog_publish_id="blog-scheduled-b",
                approval_state="approved",
                updated_at="2026-04-03T13:03:30+00:00",
            )
            social_c = _build_social_package_record(
                "social-scheduled-c",
                draft_id="draft-scheduled-c",
                blog_publish_id="blog-scheduled-c",
                approval_state="approved",
                updated_at="2026-04-03T13:04:00+00:00",
            )
            append_social_package_records([social_a, social_b, social_c], path=social_path)

            facebook_a = _build_facebook_publish_record(
                "fb-scheduled-a",
                social_package_id=social_a.social_package_id,
                draft_id="draft-scheduled-a",
                blog_publish_id="blog-scheduled-a",
                publish_status="scheduled",
                schedule_mode="manual",
                scheduled_for_facebook=shared_facebook_schedule,
                updated_at="2026-04-03T13:05:00+00:00",
            )
            facebook_b = _build_facebook_publish_record(
                "fb-scheduled-b",
                social_package_id=social_b.social_package_id,
                draft_id="draft-scheduled-b",
                blog_publish_id="blog-scheduled-b",
                publish_status="scheduled",
                schedule_mode="manual",
                scheduled_for_facebook=shared_facebook_schedule,
                updated_at="2026-04-03T13:05:30+00:00",
            )
            facebook_c = _build_facebook_publish_record(
                "fb-scheduled-c",
                social_package_id=social_c.social_package_id,
                draft_id="draft-scheduled-c",
                blog_publish_id="blog-scheduled-c",
                publish_status="scheduled",
                schedule_mode="manual",
                scheduled_for_facebook="2026-04-04T11:30:00+00:00",
                updated_at="2026-04-03T13:06:00+00:00",
            )
            append_facebook_publish_records([facebook_a, facebook_b, facebook_c], path=facebook_path)

            rows_to_append = []
            mappings_to_append = []
            for blog_publish, social_package, facebook_publish, created_at in (
                (scheduled_blog_a, social_a, facebook_a, "2026-04-03T13:05:00+00:00"),
                (scheduled_blog_b, social_b, facebook_b, "2026-04-03T13:05:30+00:00"),
                (scheduled_blog_c, social_c, facebook_c, "2026-04-03T13:06:00+00:00"),
            ):
                blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
                    blog_publish,
                    social_package_record=social_package,
                    facebook_publish_record=facebook_publish,
                    created_at=created_at,
                )
                rows_to_append.extend([blog_queue, facebook_queue])
                mappings_to_append.append(mapping)
            append_queue_item_records(rows_to_append, path=queue_path)
            append_blog_facebook_mapping_records(mappings_to_append, path=mapping_path)

            summary, rows = build_distribution_health_report(
                blog_publish_records_path=blog_path,
                social_package_records_path=social_path,
                facebook_publish_records_path=facebook_path,
                queue_item_records_path=queue_path,
                mapping_records_path=mapping_path,
            )

            self.assertEqual(summary.total_blog_publish_chains, 3)
            self.assertEqual(summary.rows_with_schedule_alerts, 2)
            self.assertEqual(summary.schedule_alert_counts["blog_schedule_collision"], 2)
            self.assertEqual(summary.schedule_alert_counts["facebook_schedule_collision"], 2)
            self.assertEqual(summary.rows_with_consistency_issues, 1)
            self.assertEqual(summary.consistency_issue_counts["facebook_schedule_before_blog"], 1)

            row_by_id = {row.blog_publish_id: row for row in rows}
            self.assertEqual(
                row_by_id["blog-scheduled-a"].schedule_alerts,
                ("blog_schedule_collision", "facebook_schedule_collision"),
            )
            self.assertEqual(
                row_by_id["blog-scheduled-b"].schedule_alerts,
                ("blog_schedule_collision", "facebook_schedule_collision"),
            )
            self.assertEqual(
                row_by_id["blog-scheduled-c"].consistency_issues,
                ("facebook_schedule_before_blog",),
            )


if __name__ == "__main__":
    unittest.main()
