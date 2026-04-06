from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from tracking_engine.models import PublishChainSnapshot
from tracking_engine.reporting import (
    build_publish_exception_report,
    build_source_template_activity_summary,
    build_variant_usage_summary,
)


def _make_snapshot(
    *,
    chain_id: str,
    source_id: str = "src-1",
    source_family: str = "editorial_food",
    template_id: str = "blog_food_fact_v1",
    template_family: str = "food_fact_article",
    category: str = "Food Facts",
    wordpress_status: str = "published",
    facebook_publish_status: str | None = "published",
    chain_status: str = "published_facebook",
    social_package_id: str | None = "social-1",
    facebook_publish_id: str | None = "fbpub-1",
    selected_variant_label: str | None = "primary",
    package_template_id: str | None = "fb_curiosity_hook_v1",
    comment_template_id: str | None = "fb_comment_read_more_prompt_v1",
    selected_hook_text: str = "Hook text",
    selected_caption_text: str = "Caption text",
    selected_comment_cta_text: str = "Read more",
    consistency_issues: tuple[str, ...] = (),
    schedule_alerts: tuple[str, ...] = (),
) -> PublishChainSnapshot:
    return PublishChainSnapshot(
        chain_id=f"blog-{chain_id}",
        snapshot_generated_at="2026-04-03T12:00:00Z",
        snapshot_version="v1",
        source_item_id=f"item-{chain_id}",
        source_id=source_id,
        source_name="Food Source",
        source_family=source_family,
        source_title="Why Sourdough Bread Tastes Different",
        source_url="https://example.com/story",
        canonical_url="https://example.com/story",
        source_published_at="2026-04-02T10:00:00Z",
        source_dedupe_status="unique",
        draft_id=f"draft-{chain_id}",
        template_id=template_id,
        template_family=template_family,
        draft_language="en",
        draft_workflow_state="reviewed",
        draft_approval_state="approved",
        quality_gate_status="pass",
        derivative_risk_level="low",
        category=category,
        tag_candidates=("bread", "sourdough"),
        selected_blog_title="Why Sourdough Bread Tastes Different",
        headline_selected="Why Sourdough Bread Tastes Different",
        headline_variants_count=2,
        blog_publish_id=f"blog-{chain_id}",
        publish_intent="draft",
        wordpress_status=wordpress_status,
        wordpress_slug="why-sourdough-bread-tastes-different",
        wordpress_category=category,
        wordpress_tags=("bread", "sourdough"),
        wordpress_post_id="101",
        wordpress_post_url="https://blog.example.com/story",
        published_at_blog="2026-04-03T10:00:00Z",
        last_blog_publish_result=wordpress_status,
        last_blog_publish_error=None,
        social_package_id=social_package_id,
        package_template_id=package_template_id,
        comment_template_id=comment_template_id,
        target_destination="facebook_page" if social_package_id else None,
        social_approval_state="approved" if social_package_id else None,
        selected_variant_label=selected_variant_label,
        blog_url_used_in_package="https://blog.example.com/story" if social_package_id else None,
        social_packaging_notes=None,
        selected_hook_text=selected_hook_text if social_package_id else "",
        selected_caption_text=selected_caption_text if social_package_id else "",
        selected_comment_cta_text=selected_comment_cta_text if social_package_id else "",
        facebook_publish_id=facebook_publish_id,
        facebook_destination_type="facebook_page" if facebook_publish_id else None,
        facebook_publish_status=facebook_publish_status,
        published_at_facebook="2026-04-03T10:15:00Z" if facebook_publish_id else None,
        last_facebook_publish_result=facebook_publish_status if facebook_publish_id else None,
        last_facebook_publish_error=None,
        blog_queue_state="published_blog",
        facebook_queue_state="published_facebook" if facebook_publish_id else "social_packaging_pending",
        mapping_status="social_published" if facebook_publish_id else "blog_only",
        draft_review_count=1,
        latest_draft_review_outcome="approved",
        social_review_count=1 if social_package_id else 0,
        latest_social_review_outcome="approved" if social_package_id else None,
        has_confirmed_blog_url=True,
        has_facebook_publish_record=facebook_publish_id is not None,
        chain_status=chain_status,
        consistency_issues=consistency_issues,
        schedule_alerts=schedule_alerts,
        latest_activity_at="2026-04-03T10:15:00Z",
    )


class TrackingReportingTests(unittest.TestCase):
    def test_publish_exception_report_includes_failed_and_partial_chains(self) -> None:
        snapshots = [
            _make_snapshot(chain_id="good"),
            _make_snapshot(
                chain_id="failed",
                wordpress_status="failed",
                facebook_publish_status=None,
                social_package_id=None,
                facebook_publish_id=None,
                selected_variant_label=None,
                package_template_id=None,
                comment_template_id=None,
                chain_status="blog_publish_failed",
                consistency_issues=("missing_workflow_state",),
            ),
            _make_snapshot(
                chain_id="partial",
                facebook_publish_status=None,
                facebook_publish_id=None,
                chain_status="social_packaging_pending",
                schedule_alerts=("facebook_schedule_collision",),
            ),
        ]

        summary, rows = build_publish_exception_report(snapshots)

        self.assertEqual(summary.total_exception_chains, 2)
        self.assertEqual(summary.failed_chain_count, 1)
        self.assertEqual(summary.partial_chain_count, 1)
        self.assertEqual(summary.consistency_issue_chains, 1)
        self.assertEqual(summary.schedule_alert_chains, 1)
        self.assertEqual(summary.exception_reason_counts["blog_publish_failed"], 1)
        self.assertEqual(summary.exception_reason_counts["facebook_publish_pending"], 1)
        self.assertEqual(rows[0].chain_id, "blog-failed")

    def test_variant_usage_summary_groups_selected_values(self) -> None:
        snapshots = [
            _make_snapshot(chain_id="one"),
            _make_snapshot(chain_id="two"),
            _make_snapshot(
                chain_id="three",
                package_template_id="fb_short_caption_v1",
                comment_template_id="fb_comment_link_line_v1",
                selected_variant_label="backup",
                selected_hook_text="Different hook",
                selected_caption_text="Different caption",
                selected_comment_cta_text="Another CTA",
            ),
        ]

        summary = build_variant_usage_summary(snapshots)

        self.assertEqual(summary.total_chains, 3)
        self.assertEqual(summary.chains_with_headline_variants, 3)
        self.assertEqual(summary.selected_variant_label_counts["primary"], 2)
        self.assertEqual(summary.selected_variant_label_counts["backup"], 1)
        self.assertEqual(
            summary.hook_counts_by_package_template["fb_curiosity_hook_v1"]["Hook text"],
            2,
        )
        self.assertEqual(
            summary.comment_cta_counts_by_comment_template["fb_comment_link_line_v1"]["Another CTA"],
            1,
        )

    def test_source_template_activity_summary_counts_mix(self) -> None:
        snapshots = [
            _make_snapshot(chain_id="one", source_id="src-1", source_family="editorial_food"),
            _make_snapshot(chain_id="two", source_id="src-2", source_family="food_news"),
            _make_snapshot(
                chain_id="three",
                source_id="src-2",
                source_family="food_news",
                template_id="blog_curiosity_article_v1",
                template_family="curiosity_article",
                category="Food Curiosity",
            ),
        ]

        summary = build_source_template_activity_summary(snapshots)

        self.assertEqual(summary.total_chains, 3)
        self.assertEqual(summary.counts_by_source_id["src-2"], 2)
        self.assertEqual(summary.counts_by_source_family["food_news"], 2)
        self.assertEqual(summary.counts_by_template_family["curiosity_article"], 1)
        self.assertEqual(summary.counts_by_category["Food Curiosity"], 1)


if __name__ == "__main__":
    unittest.main()
