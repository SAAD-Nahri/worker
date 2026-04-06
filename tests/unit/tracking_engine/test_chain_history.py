from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from content_engine.models import DraftRecord, DraftReviewRecord, DraftSection
from distribution_engine.models import (
    BlogFacebookMappingRecord,
    BlogPublishRecord,
    FacebookPublishRecord,
    QueueItemRecord,
    SocialPackageRecord,
    SocialPackageReviewRecord,
)
from source_engine.models import SourceItem
from tracking_engine.chain_history import build_publish_chain_history_report


def _write_jsonl(path: Path, records: list[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            payload = record.to_dict() if hasattr(record, "to_dict") else record
            handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _make_source_item(item_id: str = "item-1") -> SourceItem:
    return SourceItem(
        item_id=item_id,
        source_id="src-1",
        source_name="Food Source",
        source_family="editorial_food",
        run_id="run-1",
        source_url="https://example.com/story",
        canonical_url="https://example.com/story",
        discovered_at="2026-04-03T09:00:00Z",
        fetched_at="2026-04-03T09:00:00Z",
        raw_title="Why Sourdough Bread Tastes Different",
        raw_summary="A short summary.",
        raw_body_text="A long enough body for the draft.",
        author_name="Editor",
        published_at="2026-04-02T10:00:00Z",
        topical_label="food_fact",
        freshness_label="evergreen",
        normalization_status="normalized",
        dedupe_status="unique",
        template_suggestion="blog_food_fact_v1",
    )


def _make_draft_record(draft_id: str = "draft-1", source_item_id: str = "item-1") -> DraftRecord:
    return DraftRecord(
        draft_id=draft_id,
        workflow_state="reviewed",
        approval_state="approved",
        language="en",
        source_item_id=source_item_id,
        source_id="src-1",
        source_url="https://example.com/story",
        source_domain="example.com",
        source_title="Why Sourdough Bread Tastes Different",
        source_published_at="2026-04-02T10:00:00Z",
        template_id="blog_food_fact_v1",
        template_family="food_fact_article",
        template_version="v1",
        category="Food Facts",
        tag_candidates=["bread", "sourdough"],
        headline_selected="Why Sourdough Bread Tastes Different",
        headline_variants=["What Makes Sourdough Bread Taste Different", "Why Sourdough Has a Distinct Flavor"],
        intro_text="Sourdough stands out because fermentation changes flavor and texture.",
        sections=[
            DraftSection(section_key="direct_answer", section_label="Direct Answer", position=1, body_blocks=["Fermentation changes the bread."], bullet_points=[]),
        ],
        excerpt="A short excerpt.",
        quality_gate_status="pass",
        derivative_risk_level="low",
        derivative_risk_notes="",
        created_at="2026-04-03T09:05:00Z",
        updated_at="2026-04-03T09:10:00Z",
    )


def _make_draft_review_record(draft_id: str = "draft-1", source_item_id: str = "item-1") -> DraftReviewRecord:
    return DraftReviewRecord(
        review_id="review-1",
        draft_id=draft_id,
        source_item_id=source_item_id,
        reviewer_label="operator",
        reviewed_at="2026-04-03T09:12:00Z",
        review_outcome="approved",
        previous_approval_state="pending_review",
        updated_approval_state="approved",
        updated_workflow_state="reviewed",
        quality_gate_status="pass",
        derivative_risk_level="low",
        review_notes=("looks good",),
    )


def _make_blog_publish_record(blog_publish_id: str = "blog-1", draft_id: str = "draft-1", source_item_id: str = "item-1") -> BlogPublishRecord:
    return BlogPublishRecord(
        blog_publish_id=blog_publish_id,
        draft_id=draft_id,
        source_item_id=source_item_id,
        template_id="blog_food_fact_v1",
        wordpress_title="Why Sourdough Bread Tastes Different",
        wordpress_slug="why-sourdough-bread-tastes-different",
        wordpress_excerpt="A short excerpt.",
        wordpress_body_html="<p>Sourdough stands out because fermentation changes flavor and texture.</p>",
        wordpress_category="Food Facts",
        wordpress_tags=["bread", "sourdough"],
        publish_intent="draft",
        canonical_source_url="https://example.com/story",
        wordpress_post_id="101",
        wordpress_post_url="https://blog.example.com/sourdough",
        wordpress_status="published",
        published_at_blog="2026-04-03T10:00:00Z",
        last_publish_attempt_at="2026-04-03T10:00:00Z",
        last_publish_result="published",
        created_at="2026-04-03T09:20:00Z",
        updated_at="2026-04-03T10:00:00Z",
    )


def _make_social_package_record(
    social_package_id: str = "social-1",
    draft_id: str = "draft-1",
    blog_publish_id: str | None = "blog-1",
) -> SocialPackageRecord:
    return SocialPackageRecord(
        social_package_id=social_package_id,
        draft_id=draft_id,
        blog_publish_id=blog_publish_id,
        package_template_id="fb_curiosity_hook_v1",
        comment_template_id="fb_comment_read_more_prompt_v1",
        hook_text="Sourdough tastes different for a reason.",
        caption_text="Fermentation changes more than texture. It also changes flavor in ways people notice right away.",
        comment_cta_text="Read more at the blog link.",
        approval_state="approved",
        selected_variant_label="primary",
        blog_url="https://blog.example.com/sourdough",
        created_at="2026-04-03T10:05:00Z",
        updated_at="2026-04-03T10:06:00Z",
    )


def _make_social_review_record(
    social_package_id: str = "social-1",
    draft_id: str = "draft-1",
    blog_publish_id: str | None = "blog-1",
) -> SocialPackageReviewRecord:
    return SocialPackageReviewRecord(
        review_id="social-review-1",
        social_package_id=social_package_id,
        draft_id=draft_id,
        blog_publish_id=blog_publish_id,
        reviewer_label="operator",
        reviewed_at="2026-04-03T10:07:00Z",
        review_outcome="approved",
        previous_approval_state="pending_review",
        updated_approval_state="approved",
        review_notes=("hook matches blog",),
    )


def _make_facebook_publish_record(
    facebook_publish_id: str = "fbpub-1",
    social_package_id: str = "social-1",
    draft_id: str = "draft-1",
    blog_publish_id: str = "blog-1",
) -> FacebookPublishRecord:
    return FacebookPublishRecord(
        facebook_publish_id=facebook_publish_id,
        social_package_id=social_package_id,
        draft_id=draft_id,
        blog_publish_id=blog_publish_id,
        publish_status="published",
        facebook_post_id="555",
        published_at_facebook="2026-04-03T10:15:00Z",
        last_publish_attempt_at="2026-04-03T10:15:00Z",
        last_publish_result="published",
        created_at="2026-04-03T10:10:00Z",
        updated_at="2026-04-03T10:15:00Z",
    )


def _make_blog_queue(blog_publish_id: str = "blog-1", draft_id: str = "draft-1") -> QueueItemRecord:
    return QueueItemRecord(
        queue_item_id="blogq-1",
        queue_type="blog_publish",
        draft_id=draft_id,
        blog_publish_id=blog_publish_id,
        social_package_id=None,
        queue_state="published_blog",
        approval_state="approved",
        created_at="2026-04-03T09:20:00Z",
        updated_at="2026-04-03T10:00:00Z",
        last_transition_at="2026-04-03T10:00:00Z",
    )


def _make_facebook_queue(
    blog_publish_id: str = "blog-1",
    draft_id: str = "draft-1",
    social_package_id: str | None = "social-1",
    queue_state: str = "published_facebook",
    approval_state: str = "approved",
) -> QueueItemRecord:
    return QueueItemRecord(
        queue_item_id="fbq-1",
        queue_type="facebook_publish",
        draft_id=draft_id,
        blog_publish_id=blog_publish_id,
        social_package_id=social_package_id,
        queue_state=queue_state,
        approval_state=approval_state,
        created_at="2026-04-03T10:05:00Z",
        updated_at="2026-04-03T10:15:00Z",
        last_transition_at="2026-04-03T10:15:00Z",
    )


def _make_mapping_record(
    blog_publish_id: str = "blog-1",
    draft_id: str = "draft-1",
    source_item_id: str = "item-1",
    social_package_id: str | None = "social-1",
    facebook_publish_id: str | None = "fbpub-1",
    mapping_status: str = "social_published",
) -> BlogFacebookMappingRecord:
    return BlogFacebookMappingRecord(
        mapping_id="map-1",
        source_item_id=source_item_id,
        draft_id=draft_id,
        blog_publish_id=blog_publish_id,
        social_package_id=social_package_id,
        facebook_publish_id=facebook_publish_id,
        selected_blog_title="Why Sourdough Bread Tastes Different",
        selected_hook_text="" if social_package_id is None else "Sourdough tastes different for a reason.",
        selected_caption_text="" if social_package_id is None else "Fermentation changes more than texture.",
        selected_comment_cta_text="" if social_package_id is None else "Read more at the blog link.",
        blog_url="https://blog.example.com/sourdough",
        mapping_status=mapping_status,
        created_at="2026-04-03T10:06:00Z",
        updated_at="2026-04-03T10:15:00Z",
    )


class PublishChainHistoryTests(unittest.TestCase):
    def test_build_publish_chain_history_report_preserves_complete_chain_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source_path = base / "source_items.jsonl"
            draft_path = base / "draft_records.jsonl"
            draft_review_path = base / "draft_reviews.jsonl"
            blog_publish_path = base / "blog_publish_records.jsonl"
            social_package_path = base / "social_package_records.jsonl"
            social_review_path = base / "social_package_reviews.jsonl"
            facebook_publish_path = base / "facebook_publish_records.jsonl"
            queue_path = base / "queue_item_records.jsonl"
            mapping_path = base / "mapping_records.jsonl"

            _write_jsonl(source_path, [_make_source_item()])
            _write_jsonl(draft_path, [_make_draft_record()])
            _write_jsonl(draft_review_path, [_make_draft_review_record()])
            _write_jsonl(blog_publish_path, [_make_blog_publish_record()])
            _write_jsonl(social_package_path, [_make_social_package_record()])
            _write_jsonl(social_review_path, [_make_social_review_record()])
            _write_jsonl(facebook_publish_path, [_make_facebook_publish_record()])
            _write_jsonl(queue_path, [_make_blog_queue(), _make_facebook_queue()])
            _write_jsonl(mapping_path, [_make_mapping_record()])

            summary, snapshots = build_publish_chain_history_report(
                source_items_path=source_path,
                draft_records_path=draft_path,
                draft_reviews_path=draft_review_path,
                blog_publish_records_path=blog_publish_path,
                social_package_records_path=social_package_path,
                social_package_reviews_path=social_review_path,
                facebook_publish_records_path=facebook_publish_path,
                queue_item_records_path=queue_path,
                mapping_records_path=mapping_path,
            )

            self.assertEqual(summary.total_chains, 1)
            self.assertEqual(summary.chains_with_social_package, 1)
            self.assertEqual(summary.chains_with_facebook_publish, 1)
            self.assertEqual(summary.chain_status_counts["published_facebook"], 1)
            snapshot = snapshots[0]
            self.assertEqual(snapshot.chain_id, "blog-1")
            self.assertEqual(snapshot.snapshot_version, "v1")
            self.assertTrue(snapshot.snapshot_generated_at.endswith("Z"))
            self.assertEqual(snapshot.source_name, "Food Source")
            self.assertEqual(snapshot.source_published_at, "2026-04-02T10:00:00Z")
            self.assertEqual(snapshot.source_dedupe_status, "unique")
            self.assertEqual(snapshot.template_family, "food_fact_article")
            self.assertEqual(snapshot.draft_language, "en")
            self.assertEqual(snapshot.tag_candidates, ("bread", "sourdough"))
            self.assertEqual(snapshot.selected_blog_title, "Why Sourdough Bread Tastes Different")
            self.assertEqual(snapshot.publish_intent, "draft")
            self.assertEqual(snapshot.wordpress_slug, "why-sourdough-bread-tastes-different")
            self.assertEqual(snapshot.wordpress_category, "Food Facts")
            self.assertEqual(snapshot.wordpress_tags, ("bread", "sourdough"))
            self.assertEqual(snapshot.published_at_blog, "2026-04-03T10:00:00Z")
            self.assertEqual(snapshot.selected_hook_text, "Sourdough tastes different for a reason.")
            self.assertEqual(snapshot.package_template_id, "fb_curiosity_hook_v1")
            self.assertEqual(snapshot.comment_template_id, "fb_comment_read_more_prompt_v1")
            self.assertEqual(snapshot.target_destination, "facebook_page")
            self.assertEqual(snapshot.blog_url_used_in_package, "https://blog.example.com/sourdough")
            self.assertEqual(snapshot.facebook_publish_status, "published")
            self.assertEqual(snapshot.published_at_facebook, "2026-04-03T10:15:00Z")
            self.assertEqual(snapshot.chain_status, "published_facebook")
            self.assertEqual(snapshot.draft_review_count, 1)
            self.assertEqual(snapshot.social_review_count, 1)
            self.assertTrue(snapshot.has_confirmed_blog_url)
            self.assertFalse(snapshot.consistency_issues)

    def test_build_publish_chain_history_report_keeps_blog_only_chain_visible(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source_path = base / "source_items.jsonl"
            draft_path = base / "draft_records.jsonl"
            blog_publish_path = base / "blog_publish_records.jsonl"
            queue_path = base / "queue_item_records.jsonl"
            mapping_path = base / "mapping_records.jsonl"

            _write_jsonl(source_path, [_make_source_item()])
            _write_jsonl(draft_path, [_make_draft_record()])
            _write_jsonl(blog_publish_path, [_make_blog_publish_record()])
            _write_jsonl(
                queue_path,
                [
                    QueueItemRecord(
                        queue_item_id="blogq-1",
                        queue_type="blog_publish",
                        draft_id="draft-1",
                        blog_publish_id="blog-1",
                        social_package_id=None,
                        queue_state="wordpress_draft_created",
                        approval_state="approved",
                        created_at="2026-04-03T09:20:00Z",
                        updated_at="2026-04-03T09:30:00Z",
                        last_transition_at="2026-04-03T09:30:00Z",
                    ),
                    QueueItemRecord(
                        queue_item_id="fbq-1",
                        queue_type="facebook_publish",
                        draft_id="draft-1",
                        blog_publish_id="blog-1",
                        social_package_id=None,
                        queue_state="social_packaging_pending",
                        approval_state="pending_review",
                        created_at="2026-04-03T09:20:00Z",
                        updated_at="2026-04-03T09:30:00Z",
                        last_transition_at="2026-04-03T09:30:00Z",
                    ),
                ],
            )
            _write_jsonl(
                mapping_path,
                [
                    _make_mapping_record(
                        social_package_id=None,
                        facebook_publish_id=None,
                        mapping_status="blog_only",
                    )
                ],
            )

            summary, snapshots = build_publish_chain_history_report(
                source_items_path=source_path,
                draft_records_path=draft_path,
                blog_publish_records_path=blog_publish_path,
                queue_item_records_path=queue_path,
                mapping_records_path=mapping_path,
            )

            self.assertEqual(summary.total_chains, 1)
            self.assertEqual(summary.chains_with_social_package, 0)
            self.assertEqual(summary.chains_with_facebook_publish, 0)
            self.assertEqual(summary.chain_status_counts["social_packaging_pending"], 1)
            snapshot = snapshots[0]
            self.assertIsNone(snapshot.social_package_id)
            self.assertEqual(snapshot.mapping_status, "blog_only")
            self.assertEqual(snapshot.chain_status, "social_packaging_pending")
            self.assertEqual(snapshot.selected_hook_text, "")
            self.assertEqual(snapshot.selected_caption_text, "")
            self.assertEqual(snapshot.selected_comment_cta_text, "")


if __name__ == "__main__":
    unittest.main()
