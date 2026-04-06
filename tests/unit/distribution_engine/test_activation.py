from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.formatting import format_source_item_to_draft
from content_engine.storage import append_draft_records
from distribution_engine.activation import build_system_activation_readiness_report
from distribution_engine.models import BlogPublishRecord, FacebookPublishRecord, SocialPackageRecord
from distribution_engine.storage import (
    append_blog_facebook_mapping_records,
    append_blog_publish_records,
    append_facebook_publish_records,
    append_queue_item_records,
    append_social_package_records,
)
from distribution_engine.workflow import prepare_distribution_linkage_records
from source_engine.models import SourceItem
from tracking_engine.audit import record_transport_validation_audit


def _build_source_item(item_id: str, title: str) -> SourceItem:
    return SourceItem(
        item_id=item_id,
        source_id="src_test",
        source_name="Test Source",
        source_family="food_editorial",
        run_id="run-1",
        source_url=f"https://example.com/{item_id}",
        canonical_url=f"https://example.com/{item_id}",
        discovered_at="2026-04-03T00:00:00+00:00",
        fetched_at="2026-04-03T00:00:00+00:00",
        raw_title=title,
        raw_summary="A short summary about a simple food question.",
        raw_body_text=(
            "This kitchen behavior surprises a lot of people because the visible result looks simple while the underlying food science is doing several things at once. Heat changes texture, moisture changes timing, and ingredient structure affects how quickly a food reacts in the pan.\n\n"
            "The main reason the trick works is that heat, moisture, and ingredient structure all interact in predictable ways over a short period of time. When one part of that balance changes, cooks often see very different results even when they think they followed the same steps.\n\n"
            "When home cooks understand that relationship, they can get more consistent results and avoid common mistakes that feel random but actually follow a pattern. This makes the kitchen process less frustrating and turns a confusing habit into something practical and repeatable.\n\n"
            "That is why simple food facts often lead to better cooking habits. They give people a quick explanation, a useful takeaway, and a reason to keep using the method with more confidence the next time they cook."
        ),
        author_name=None,
        published_at="2026-04-01T00:00:00+00:00",
        topical_label="food_curiosity",
        freshness_label="fresh",
        normalization_status="normalized",
        dedupe_status="unique",
        quality_flags=[],
        template_suggestion="curiosity_article",
    )


def _build_approved_draft(*, draft_id: str, item_id: str, title: str):
    draft = format_source_item_to_draft(
        _build_source_item(item_id, title),
        created_at="2026-04-03T12:00:00+00:00",
    )
    draft.draft_id = draft_id
    draft.quality_gate_status = "pass"
    draft.quality_flags = []
    draft.derivative_risk_level = "low"
    draft.derivative_risk_notes = "Clean enough for activation."
    draft.approval_state = "approved"
    draft.workflow_state = "reviewed"
    draft.updated_at = "2026-04-03T12:10:00+00:00"
    return draft


def _build_blog_publish_record(
    *,
    blog_publish_id: str,
    draft_id: str,
    source_item_id: str,
    title: str,
    wordpress_status: str = "prepared_local",
) -> BlogPublishRecord:
    return BlogPublishRecord(
        blog_publish_id=blog_publish_id,
        draft_id=draft_id,
        source_item_id=source_item_id,
        template_id="blog_curiosity_food_v1",
        wordpress_title=title,
        wordpress_slug=title.lower().replace(" ", "-"),
        wordpress_excerpt=f"Excerpt for {title}",
        wordpress_body_html=f"<p>{title}</p>",
        wordpress_category="food-questions",
        wordpress_tags=["food-storage"],
        publish_intent="draft",
        canonical_source_url=f"https://example.com/{source_item_id}",
        wordpress_post_id=None,
        wordpress_post_url=None,
        wordpress_status=wordpress_status,
        schedule_mode=None,
        scheduled_for_blog=None,
        published_at_blog=None,
        last_publish_attempt_at="2026-04-03T12:20:00+00:00",
        last_publish_result="payload_prepared",
        last_error=None,
        created_at="2026-04-03T12:20:00+00:00",
        updated_at="2026-04-03T12:20:00+00:00",
    )


def _build_social_package_record(*, social_package_id: str, draft_id: str, blog_publish_id: str) -> SocialPackageRecord:
    return SocialPackageRecord(
        social_package_id=social_package_id,
        draft_id=draft_id,
        blog_publish_id=blog_publish_id,
        package_template_id="fb_curiosity_hook_v1",
        comment_template_id="fb_comment_curiosity_reinforcement_v1",
        hook_text="How To Give Your Costco Croissant Container A Second Life?",
        caption_text="A short caption that keeps the main point visible.",
        comment_cta_text="If you want the short answer and the full explanation, I can drop the post here.",
        target_destination="facebook_page",
        approval_state="approved",
        blog_url=None,
        selected_variant_label="deterministic_primary_v1",
        packaging_notes="technical canary",
        created_at="2026-04-03T12:21:00+00:00",
        updated_at="2026-04-03T12:21:00+00:00",
    )


class SystemActivationReadinessTests(unittest.TestCase):
    def test_report_detects_placeholder_credentials_and_approved_candidate(self) -> None:
        root = ROOT / "tests" / "_tmp_activation_case_placeholder"
        shutil.rmtree(root, ignore_errors=True)
        root.mkdir(parents=True, exist_ok=True)
        try:
            wordpress_config = root / "wordpress_rest_config.local.json"
            facebook_config = root / "facebook_graph_config.local.json"
            draft_path = root / "draft_records.jsonl"
            blog_path = root / "blog_publish_records.jsonl"
            social_path = root / "social_package_records.jsonl"
            review_path = root / "social_package_reviews.jsonl"
            facebook_publish_path = root / "facebook_publish_records.jsonl"
            queue_path = root / "queue_item_records.jsonl"
            mapping_path = root / "blog_facebook_mapping_records.jsonl"
            audit_path = root / "tracking_audit_records.jsonl"

            wordpress_config.write_text(
                json.dumps(
                    {
                        "base_url": "https://example.com",
                        "username": "wordpress_username",
                        "application_password": "xxxx xxxx xxxx xxxx xxxx xxxx",
                        "category_id_by_name": {"food-questions": 14},
                        "tag_id_by_name": {"food-storage": 201},
                    }
                ),
                encoding="utf-8",
            )
            facebook_config.write_text(
                json.dumps(
                    {
                        "page_id": "123456789012345",
                        "page_access_token": "EAAB_PLACEHOLDER_REPLACE_LOCALLY",
                    }
                ),
                encoding="utf-8",
            )
            append_draft_records(
                [
                    _build_approved_draft(
                        draft_id="draft-approved-1",
                        item_id="item-1",
                        title="How To Give Your Costco Croissant Container A Second Life",
                    )
                ],
                path=draft_path,
            )

            summary, config_statuses, candidate_rows, canary_rows = build_system_activation_readiness_report(
                wordpress_config_path=wordpress_config,
                facebook_config_path=facebook_config,
                draft_records_path=draft_path,
                blog_publish_records_path=blog_path,
                social_package_records_path=social_path,
                social_package_reviews_path=review_path,
                facebook_publish_records_path=facebook_publish_path,
                queue_item_records_path=queue_path,
                mapping_records_path=mapping_path,
                audit_records_path=audit_path,
            )

            self.assertEqual(summary.readiness_signal, "awaiting_real_credentials")
            self.assertIn("wordpress_config_not_ready", summary.blocking_reasons)
            self.assertIn("facebook_config_not_ready", summary.blocking_reasons)
            self.assertIn("local_canary_chain_missing", summary.blocking_reasons)
            self.assertEqual(summary.approved_pass_draft_count, 1)
            self.assertEqual(summary.local_canary_chain_count, 0)
            self.assertEqual(len(candidate_rows), 1)
            self.assertEqual(len(canary_rows), 0)

            config_by_name = {status.config_name: status for status in config_statuses}
            self.assertFalse(config_by_name["wordpress"].ready_for_execute)
            self.assertTrue(config_by_name["wordpress"].placeholder_detected)
            self.assertFalse(config_by_name["facebook"].ready_for_execute)
            self.assertTrue(config_by_name["facebook"].placeholder_detected)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_report_detects_ready_configs_successful_validations_and_local_only_canary(self) -> None:
        root = ROOT / "tests" / "_tmp_activation_case_ready"
        shutil.rmtree(root, ignore_errors=True)
        root.mkdir(parents=True, exist_ok=True)
        try:
            wordpress_config = root / "wordpress_rest_config.local.json"
            facebook_config = root / "facebook_graph_config.local.json"
            draft_path = root / "draft_records.jsonl"
            blog_path = root / "blog_publish_records.jsonl"
            social_path = root / "social_package_records.jsonl"
            queue_path = root / "queue_item_records.jsonl"
            mapping_path = root / "blog_facebook_mapping_records.jsonl"
            audit_path = root / "tracking_audit_records.jsonl"

            wordpress_config.write_text(
                json.dumps(
                    {
                        "base_url": "https://blog.example.com",
                        "username": "operator_admin",
                        "application_password": "abcd efgh ijkl mnop qrst uvwx",
                        "category_id_by_name": {"food-questions": 14},
                        "tag_id_by_name": {"food-storage": 201},
                    }
                ),
                encoding="utf-8",
            )
            facebook_config.write_text(
                json.dumps(
                    {
                        "page_id": "999888777666555",
                        "page_access_token": "EAAB-real-token-for-local-testing",
                    }
                ),
                encoding="utf-8",
            )

            approved_draft = _build_approved_draft(
                draft_id="draft-approved-2",
                item_id="item-2",
                title="How To Give Your Costco Croissant Container A Second Life",
            )
            append_draft_records([approved_draft], path=draft_path)

            blog_publish = _build_blog_publish_record(
                blog_publish_id="blog-canary-1",
                draft_id=approved_draft.draft_id,
                source_item_id=approved_draft.source_item_id,
                title=approved_draft.headline_selected,
            )
            social_package = _build_social_package_record(
                social_package_id="social-canary-1",
                draft_id=approved_draft.draft_id,
                blog_publish_id=blog_publish.blog_publish_id,
            )
            append_blog_publish_records([blog_publish], path=blog_path)
            append_social_package_records([social_package], path=social_path)
            blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
                blog_publish,
                social_package_record=social_package,
                created_at="2026-04-03T12:25:00+00:00",
            )
            append_queue_item_records([blog_queue, facebook_queue], path=queue_path)
            append_blog_facebook_mapping_records([mapping], path=mapping_path)

            record_transport_validation_audit(
                actor_label="operator",
                entity_type="wordpress_transport",
                entity_id="https://blog.example.com",
                event_status="success",
                event_summary="WordPress transport validation succeeded.",
                execution_mode="execute",
                config_path=str(wordpress_config),
                validated_identity_id="1",
                validated_identity_name="operator_admin",
                audit_records_path=audit_path,
                event_timestamp="2026-04-03T12:30:00Z",
            )
            record_transport_validation_audit(
                actor_label="operator",
                entity_type="facebook_transport",
                entity_id="999888777666555",
                event_status="success",
                event_summary="Facebook transport validation succeeded.",
                execution_mode="execute",
                config_path=str(facebook_config),
                validated_identity_id="999888777666555",
                validated_identity_name="Test Page",
                audit_records_path=audit_path,
                event_timestamp="2026-04-03T12:31:00Z",
            )

            summary, config_statuses, candidate_rows, canary_rows = build_system_activation_readiness_report(
                wordpress_config_path=wordpress_config,
                facebook_config_path=facebook_config,
                draft_records_path=draft_path,
                blog_publish_records_path=blog_path,
                social_package_records_path=social_path,
                queue_item_records_path=queue_path,
                mapping_records_path=mapping_path,
                audit_records_path=audit_path,
            )

            self.assertEqual(summary.readiness_signal, "awaiting_live_canary_execution")
            self.assertGreaterEqual(summary.successful_wordpress_validations, 1)
            self.assertGreaterEqual(summary.successful_facebook_validations, 1)
            self.assertEqual(summary.local_canary_chain_count, 1)
            self.assertIn("live_canary_execution_missing", summary.blocking_reasons)
            self.assertEqual(len(candidate_rows), 1)
            self.assertEqual(len(canary_rows), 1)
            self.assertTrue(all(status.ready_for_execute for status in config_statuses))
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_report_detects_live_canary_retry_required_after_failed_facebook_publish(self) -> None:
        root = ROOT / "tests" / "_tmp_activation_case_retry_required"
        shutil.rmtree(root, ignore_errors=True)
        root.mkdir(parents=True, exist_ok=True)
        try:
            wordpress_config = root / "wordpress_rest_config.local.json"
            facebook_config = root / "facebook_graph_config.local.json"
            draft_path = root / "draft_records.jsonl"
            blog_path = root / "blog_publish_records.jsonl"
            social_path = root / "social_package_records.jsonl"
            queue_path = root / "queue_item_records.jsonl"
            mapping_path = root / "blog_facebook_mapping_records.jsonl"
            facebook_publish_path = root / "facebook_publish_records.jsonl"
            audit_path = root / "tracking_audit_records.jsonl"

            wordpress_config.write_text(
                json.dumps(
                    {
                        "base_url": "https://blog.example.com",
                        "username": "operator_admin",
                        "application_password": "abcd efgh ijkl mnop qrst uvwx",
                        "category_id_by_name": {"food-questions": 14},
                        "tag_id_by_name": {"food-storage": 201},
                    }
                ),
                encoding="utf-8",
            )
            facebook_config.write_text(
                json.dumps(
                    {
                        "page_id": "999888777666555",
                        "page_access_token": "EAAB-real-token-for-local-testing",
                    }
                ),
                encoding="utf-8",
            )

            approved_draft = _build_approved_draft(
                draft_id="draft-approved-3",
                item_id="item-3",
                title="How To Give Your Costco Croissant Container A Second Life",
            )
            append_draft_records([approved_draft], path=draft_path)

            blog_publish = _build_blog_publish_record(
                blog_publish_id="blog-canary-2",
                draft_id=approved_draft.draft_id,
                source_item_id=approved_draft.source_item_id,
                title=approved_draft.headline_selected,
                wordpress_status="published",
            )
            blog_publish.wordpress_post_id = "25"
            blog_publish.wordpress_post_url = "https://blog.example.com/post-25"
            blog_publish.published_at_blog = "2026-04-03T12:40:00+00:00"
            blog_publish.last_publish_result = "wordpress_published"
            social_package = _build_social_package_record(
                social_package_id="social-canary-2",
                draft_id=approved_draft.draft_id,
                blog_publish_id=blog_publish.blog_publish_id,
            )
            append_blog_publish_records([blog_publish], path=blog_path)
            append_social_package_records([social_package], path=social_path)
            append_facebook_publish_records(
                [
                    FacebookPublishRecord(
                        facebook_publish_id="fbpub-canary-2",
                        social_package_id=social_package.social_package_id,
                        draft_id=approved_draft.draft_id,
                        blog_publish_id=blog_publish.blog_publish_id,
                        destination_type="facebook_page",
                        publish_status="failed",
                        last_publish_attempt_at="2026-04-03T12:45:00+00:00",
                        last_publish_result="facebook_publish_failed",
                        last_error="Facebook token expired.",
                        created_at="2026-04-03T12:45:00+00:00",
                        updated_at="2026-04-03T12:45:00+00:00",
                    )
                ],
                path=facebook_publish_path,
            )
            blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
                blog_publish,
                social_package_record=social_package,
                facebook_publish_record=FacebookPublishRecord(
                    facebook_publish_id="fbpub-canary-2",
                    social_package_id=social_package.social_package_id,
                    draft_id=approved_draft.draft_id,
                    blog_publish_id=blog_publish.blog_publish_id,
                    destination_type="facebook_page",
                    publish_status="failed",
                    last_publish_attempt_at="2026-04-03T12:45:00+00:00",
                    last_publish_result="facebook_publish_failed",
                    last_error="Facebook token expired.",
                    created_at="2026-04-03T12:45:00+00:00",
                    updated_at="2026-04-03T12:45:00+00:00",
                ),
                created_at="2026-04-03T12:46:00+00:00",
            )
            append_queue_item_records([blog_queue, facebook_queue], path=queue_path)
            append_blog_facebook_mapping_records([mapping], path=mapping_path)

            record_transport_validation_audit(
                actor_label="operator",
                entity_type="wordpress_transport",
                entity_id="https://blog.example.com",
                event_status="success",
                event_summary="WordPress transport validation succeeded.",
                execution_mode="execute",
                config_path=str(wordpress_config),
                validated_identity_id="1",
                validated_identity_name="operator_admin",
                audit_records_path=audit_path,
                event_timestamp="2026-04-03T12:30:00Z",
            )
            record_transport_validation_audit(
                actor_label="operator",
                entity_type="facebook_transport",
                entity_id="999888777666555",
                event_status="success",
                event_summary="Facebook transport validation succeeded.",
                execution_mode="execute",
                config_path=str(facebook_config),
                validated_identity_id="999888777666555",
                validated_identity_name="Test Page",
                audit_records_path=audit_path,
                event_timestamp="2026-04-03T12:31:00Z",
            )

            summary, _config_statuses, _candidate_rows, canary_rows = build_system_activation_readiness_report(
                wordpress_config_path=wordpress_config,
                facebook_config_path=facebook_config,
                draft_records_path=draft_path,
                blog_publish_records_path=blog_path,
                social_package_records_path=social_path,
                facebook_publish_records_path=facebook_publish_path,
                queue_item_records_path=queue_path,
                mapping_records_path=mapping_path,
                audit_records_path=audit_path,
            )

            self.assertEqual(summary.readiness_signal, "canary_retry_required")
            self.assertIn("live_canary_retry_required", summary.blocking_reasons)
            self.assertNotIn("live_canary_execution_missing", summary.blocking_reasons)
            self.assertEqual(summary.local_canary_chain_count, 1)
            self.assertEqual(len(canary_rows), 1)
            self.assertEqual(canary_rows[0].facebook_publish_status, "failed")
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
