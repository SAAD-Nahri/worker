from __future__ import annotations

import sys
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from distribution_engine.models import BlogPublishRecord, FacebookPublishRecord, SocialPackageRecord
from distribution_engine.schedule_report import build_distribution_schedule_report
from distribution_engine.storage import (
    append_blog_facebook_mapping_records,
    append_blog_publish_records,
    append_facebook_publish_records,
    append_queue_item_records,
    append_social_package_records,
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
        last_publish_attempt_at=updated_at,
        last_publish_result=wordpress_status,
        created_at=updated_at,
        updated_at=updated_at,
    )


def _build_social_package_record(
    social_package_id: str,
    *,
    draft_id: str,
    blog_publish_id: str,
    approval_state: str = "approved",
    updated_at: str = "2026-04-03T12:10:00+00:00",
) -> SocialPackageRecord:
    return SocialPackageRecord(
        social_package_id=social_package_id,
        draft_id=draft_id,
        blog_publish_id=blog_publish_id,
        package_template_id="fb_curiosity_hook_v1",
        comment_template_id="fb_comment_link_line_v1",
        hook_text="Why this food fact matters",
        caption_text="A short caption aligned to the blog draft.",
        comment_cta_text="Read more in the blog post.",
        target_destination="facebook_page",
        approval_state=approval_state,
        blog_url="https://blog.example.com/post",
        selected_variant_label="primary",
        created_at=updated_at,
        updated_at=updated_at,
    )


def _build_facebook_publish_record(
    facebook_publish_id: str,
    *,
    social_package_id: str,
    draft_id: str,
    blog_publish_id: str,
    scheduled_for_facebook: str,
    updated_at: str = "2026-04-03T12:20:00+00:00",
) -> FacebookPublishRecord:
    return FacebookPublishRecord(
        facebook_publish_id=facebook_publish_id,
        social_package_id=social_package_id,
        draft_id=draft_id,
        blog_publish_id=blog_publish_id,
        publish_status="scheduled",
        schedule_mode="manual",
        scheduled_for_facebook=scheduled_for_facebook,
        last_publish_attempt_at=updated_at,
        last_publish_result="scheduled",
        created_at=updated_at,
        updated_at=updated_at,
    )


class DistributionScheduleReportTests(unittest.TestCase):
    def test_build_distribution_schedule_report_surfaces_schedule_states_and_alerts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            blog_path = root / "blog_publish_records.jsonl"
            social_path = root / "social_package_records.jsonl"
            facebook_path = root / "facebook_publish_records.jsonl"
            queue_path = root / "queue_item_records.jsonl"
            mapping_path = root / "blog_facebook_mapping_records.jsonl"

            shared_blog_slot = "2026-04-04T10:00:00+00:00"
            shared_facebook_slot = "2026-04-04T11:00:00+00:00"

            scheduled_blog_a = _build_blog_publish_record(
                "blog-schedule-a",
                draft_id="draft-a",
                source_item_id="source-a",
                title="Why Butter Changes Flavor",
                wordpress_status="scheduled",
                publish_intent="schedule",
                wordpress_post_id="wp-1",
                wordpress_post_url="https://blog.example.com/butter",
                schedule_mode="manual",
                scheduled_for_blog=shared_blog_slot,
                updated_at="2026-04-03T12:30:00+00:00",
            )
            scheduled_blog_b = _build_blog_publish_record(
                "blog-schedule-b",
                draft_id="draft-b",
                source_item_id="source-b",
                title="Why Salt Changes Texture",
                wordpress_status="scheduled",
                publish_intent="schedule",
                wordpress_post_id="wp-2",
                wordpress_post_url="https://blog.example.com/salt",
                schedule_mode="manual",
                scheduled_for_blog=shared_blog_slot,
                updated_at="2026-04-03T12:31:00+00:00",
            )
            ready_blog = _build_blog_publish_record(
                "blog-ready-c",
                draft_id="draft-c",
                source_item_id="source-c",
                title="Why Steam Changes Cooking",
                wordpress_status="draft_created",
                publish_intent="schedule",
                wordpress_post_id="wp-3",
                updated_at="2026-04-03T12:32:00+00:00",
            )
            awaiting_blog = _build_blog_publish_record(
                "blog-awaiting-d",
                draft_id="draft-d",
                source_item_id="source-d",
                title="Why Citrus Tastes Brighter",
                wordpress_status="scheduled",
                publish_intent="schedule",
                wordpress_post_id="wp-4",
                wordpress_post_url="https://blog.example.com/citrus",
                schedule_mode="manual",
                scheduled_for_blog="2026-04-04T14:00:00+00:00",
                updated_at="2026-04-03T12:33:00+00:00",
            )
            append_blog_publish_records([scheduled_blog_a, scheduled_blog_b, ready_blog, awaiting_blog], path=blog_path)

            social_a = _build_social_package_record("social-a", draft_id="draft-a", blog_publish_id="blog-schedule-a")
            social_b = _build_social_package_record("social-b", draft_id="draft-b", blog_publish_id="blog-schedule-b")
            social_d = _build_social_package_record("social-d", draft_id="draft-d", blog_publish_id="blog-awaiting-d")
            append_social_package_records([social_a, social_b, social_d], path=social_path)

            facebook_a = _build_facebook_publish_record(
                "fb-a",
                social_package_id="social-a",
                draft_id="draft-a",
                blog_publish_id="blog-schedule-a",
                scheduled_for_facebook=shared_facebook_slot,
                updated_at="2026-04-03T12:40:00+00:00",
            )
            append_facebook_publish_records([facebook_a], path=facebook_path)

            queue_records = []
            mappings = []
            for blog_publish, social_package, facebook_publish, created_at in (
                (scheduled_blog_a, social_a, facebook_a, "2026-04-03T12:40:00+00:00"),
                (scheduled_blog_b, social_b, None, "2026-04-03T12:41:00+00:00"),
                (ready_blog, None, None, "2026-04-03T12:42:00+00:00"),
                (awaiting_blog, social_d, None, "2026-04-03T12:43:00+00:00"),
            ):
                blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
                    blog_publish,
                    social_package_record=social_package,
                    facebook_publish_record=facebook_publish,
                    created_at=created_at,
                )
                queue_records.extend([blog_queue, facebook_queue])
                mappings.append(mapping)
            append_queue_item_records(queue_records, path=queue_path)
            append_blog_facebook_mapping_records(mappings, path=mapping_path)

            summary, rows = build_distribution_schedule_report(
                blog_publish_records_path=blog_path,
                social_package_records_path=social_path,
                facebook_publish_records_path=facebook_path,
                queue_item_records_path=queue_path,
                mapping_records_path=mapping_path,
            )

            self.assertEqual(summary.total_rows, 4)
            self.assertEqual(summary.rows_with_schedule_alerts, 2)
            self.assertEqual(summary.schedule_alert_counts["blog_schedule_collision"], 2)
            self.assertEqual(summary.ready_for_blog_schedule, 1)
            self.assertEqual(summary.ready_for_facebook_schedule, 1)
            self.assertEqual(summary.awaiting_facebook_schedule, 0)
            self.assertEqual(summary.scheduled_pairs, 0)

            row_by_id = {row.blog_publish_id: row for row in rows}
            self.assertEqual(row_by_id["blog-ready-c"].scheduling_signal, "ready_for_blog_schedule")
            self.assertEqual(row_by_id["blog-schedule-b"].scheduling_signal, "collision_review")
            self.assertEqual(row_by_id["blog-awaiting-d"].scheduling_signal, "ready_for_facebook_schedule")


if __name__ == "__main__":
    unittest.main()
