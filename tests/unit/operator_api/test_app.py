from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.models import AiAssistanceRecord
from content_engine.formatting import format_source_item_to_draft
from content_engine.review import record_draft_review
from content_engine.storage import append_draft_records, read_draft_review_records
from distribution_engine.facebook import prepare_social_package_record
from distribution_engine.review import record_social_package_review
from distribution_engine.models import QueueItemRecord
from distribution_engine.storage import (
    append_blog_facebook_mapping_records,
    append_blog_publish_records,
    append_queue_item_records,
    append_social_package_records,
    append_social_package_review_records,
    read_queue_review_records,
    read_social_package_review_records,
)
from distribution_engine.workflow import prepare_distribution_linkage_records
from distribution_engine.wordpress import prepare_blog_publish_record
from media_engine.assets import prepare_asset_record
from media_engine.briefs import prepare_media_brief_record
from media_engine.review import record_asset_review
from media_engine.storage import (
    append_asset_records,
    append_asset_review_records,
    append_media_brief_records,
    read_asset_review_records,
)
from operator_api.app import build_app
from operator_api.config import OperatorApiConfig, load_operator_api_config
from operator_api.services import OperatorApiPaths
from source_engine.models import SourceItem
from source_engine.storage import append_source_items


def _build_source_item(
    *,
    item_id: str,
    source_url: str,
    raw_title: str,
    raw_summary: str,
    raw_body_text: str,
    template_suggestion: str,
    topical_label: str,
) -> SourceItem:
    return SourceItem(
        item_id=item_id,
        source_id=f"src_{item_id}",
        source_name=f"Source {item_id}",
        source_family="editorial_food",
        run_id=f"run_{item_id}",
        source_url=source_url,
        canonical_url=source_url,
        discovered_at="2026-04-04T09:00:00+00:00",
        fetched_at="2026-04-04T09:00:00+00:00",
        raw_title=raw_title,
        raw_summary=raw_summary,
        raw_body_text=raw_body_text,
        author_name="Editor",
        published_at="2026-04-03T10:00:00+00:00",
        topical_label=topical_label,
        freshness_label="evergreen",
        normalization_status="normalized",
        dedupe_status="unique",
        quality_flags=[],
        template_suggestion=template_suggestion,
    )


def _attach_headline_variants(draft, *variants: str):
    draft.headline_variants = [draft.headline_selected, *variants]
    return draft


class OperatorApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        base = Path(self.temp_dir.name)
        self.paths = OperatorApiPaths(
            draft_records_path=base / "draft_records.jsonl",
            draft_reviews_path=base / "draft_reviews.jsonl",
            source_items_path=base / "source_items.jsonl",
            blog_publish_records_path=base / "blog_publish_records.jsonl",
            social_package_records_path=base / "social_package_records.jsonl",
            social_package_reviews_path=base / "social_package_reviews.jsonl",
            media_brief_records_path=base / "media_brief_records.jsonl",
            asset_records_path=base / "asset_records.jsonl",
            asset_review_records_path=base / "asset_review_records.jsonl",
            facebook_publish_records_path=base / "facebook_publish_records.jsonl",
            queue_item_records_path=base / "queue_item_records.jsonl",
            queue_review_records_path=base / "queue_review_records.jsonl",
            mapping_records_path=base / "blog_facebook_mapping_records.jsonl",
        )
        self.secret = "operator-secret"
        app = build_app(
            config=OperatorApiConfig(
                bind_host="127.0.0.1",
                bind_port=8765,
                shared_secret=self.secret,
                enable_docs=True,
            ),
            paths=self.paths,
        )
        self.client = TestClient(app)
        self.headers = {"X-Content-Ops-Shared-Secret": self.secret}
        self._seed_chain()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_dashboard_requires_shared_secret(self) -> None:
        response = self.client.get("/dashboard/summary")
        self.assertEqual(response.status_code, 401)

        response = self.client.get(
            "/dashboard/summary",
            headers={"X-Content-Ops-Shared-Secret": "wrong"},
        )
        self.assertEqual(response.status_code, 403)

    def test_healthz_endpoint_is_public_and_reports_ok(self) -> None:
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "service": "content_ops_operator_api",
            },
        )

    def test_draft_inbox_filters_work(self) -> None:
        response = self.client.get(
            "/drafts/inbox",
            headers=self.headers,
            params={"search": "olive"},
        )
        self.assertEqual(response.status_code, 200)
        rows = response.json()["rows"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["draft_id"], self.approved_draft_id)

        response = self.client.get(
            "/drafts/inbox",
            headers=self.headers,
            params={"approval_state": "needs_edits"},
        )
        self.assertEqual(response.status_code, 200)
        rows = response.json()["rows"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["draft_id"], self.needs_edits_draft_id)

        response = self.client.get(
            "/drafts/inbox",
            headers=self.headers,
            params={"operator_signal": "ready_for_review"},
        )
        self.assertEqual(response.status_code, 200)
        rows = response.json()["rows"]
        self.assertEqual([row["draft_id"] for row in rows], [self.pending_draft_id])

        response = self.client.get(
            "/drafts/inbox",
            headers=self.headers,
            params={"source_domain": "health.example"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["rows"][0]["draft_id"], self.approved_benefit_draft_id)

        response = self.client.get(
            "/drafts/inbox",
            headers=self.headers,
            params={"template_id": "blog_curiosity_food_v1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["rows"][0]["draft_id"], self.approved_draft_id)

        response = self.client.get(
            "/drafts/inbox",
            headers=self.headers,
            params={"category": "food-benefits-light"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["rows"][0]["draft_id"], self.approved_benefit_draft_id)

    def test_draft_inbox_detail_review_and_variant_selection_endpoint(self) -> None:
        inbox = self.client.get("/drafts/inbox", headers=self.headers)
        self.assertEqual(inbox.status_code, 200)
        payload = inbox.json()
        self.assertEqual(payload["summary"]["total_drafts"], 4)

        detail = self.client.get(f"/drafts/{self.pending_draft_id}", headers=self.headers)
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["draft"]["draft_id"], self.pending_draft_id)
        self.assertEqual(detail.json()["draft"]["ai_assistance_log"], [])

        variant_response = self.client.post(
            f"/drafts/{self.approved_draft_id}/select-headline-variant",
            headers=self.headers,
            json={"headline_variant": self.approved_draft_alt_headline},
        )
        self.assertEqual(variant_response.status_code, 200)
        variant_payload = variant_response.json()["draft"]
        self.assertEqual(variant_payload["headline_selected"], self.approved_draft_alt_headline)
        self.assertEqual(variant_payload["approval_state"], "pending_review")
        self.assertEqual(variant_payload["workflow_state"], "drafted")

        review_response = self.client.post(
            f"/drafts/{self.pending_draft_id}/review",
            headers=self.headers,
            json={
                "review_outcome": "approved",
                "review_notes": ["ready_for_distribution"],
                "reviewer_label": "api_reviewer",
            },
        )
        self.assertEqual(review_response.status_code, 200)
        latest_reviews = read_draft_review_records(self.paths.draft_reviews_path)
        self.assertEqual(len(latest_reviews), 4)
        self.assertEqual(latest_reviews[-1].review_outcome, "approved")

    def test_dashboard_summary_includes_recent_activity_alerts_and_priority_sections(self) -> None:
        response = self.client.get("/dashboard/summary", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("recent_activity", payload)
        self.assertIn("current_alerts", payload)
        self.assertIn("priority_drafts", payload)
        self.assertIn("priority_social_packages", payload)
        self.assertIn("priority_media_assets", payload)
        self.assertIn("priority_queue_items", payload)
        self.assertGreaterEqual(len(payload["recent_activity"]), 1)
        self.assertEqual(payload["recent_activity"][0]["activity_type"], "social_review")
        self.assertGreaterEqual(len(payload["priority_drafts"]), 1)
        self.assertEqual(payload["priority_drafts"][0]["detail_target_id"], self.pending_draft_id)
        self.assertEqual(payload["priority_social_packages"][0]["detail_target_id"], self.social_package_id)
        self.assertEqual(payload["priority_media_assets"][0]["detail_target_id"], self.pending_asset_id)
        self.assertEqual(payload["priority_queue_items"][0]["detail_target_id"], self.blog_queue_id)
        self.assertTrue(
            any(
                alert.get("queue_item_id") == self.failed_blog_queue_id
                for alert in payload["current_alerts"]
            )
        )

    def test_media_asset_inbox_detail_and_review_endpoint(self) -> None:
        response = self.client.get(
            "/media-assets/inbox",
            headers=self.headers,
            params={"approval_state": "pending_review"},
        )
        self.assertEqual(response.status_code, 200)
        rows = response.json()["rows"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["asset_record_id"], self.pending_asset_id)
        self.assertFalse(rows[0]["asset_complete"])

        detail = self.client.get(
            f"/media-assets/{self.pending_asset_id}",
            headers=self.headers,
        )
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["asset_record"]["media_brief_id"], self.pending_media_brief_id)
        self.assertEqual(detail.json()["linked_media_brief"]["draft_id"], self.approved_draft_id)

        review_response = self.client.post(
            f"/media-assets/{self.pending_asset_id}/review",
            headers=self.headers,
            json={
                "review_outcome": "approved",
                "review_notes": ["rights_checked_and_alt_text_confirmed"],
                "reviewer_label": "api_media_reviewer",
            },
        )
        self.assertEqual(review_response.status_code, 200)
        self.assertEqual(review_response.json()["asset_record"]["approval_state"], "approved")
        self.assertTrue(review_response.json()["asset_readiness"]["asset_complete"])

        asset_reviews = read_asset_review_records(self.paths.asset_review_records_path)
        self.assertEqual(len(asset_reviews), 2)
        self.assertEqual(asset_reviews[-1].review_outcome, "approved")

    def test_social_package_inbox_filters_work(self) -> None:
        response = self.client.get(
            "/social-packages/inbox",
            headers=self.headers,
            params={"approval_state": "approved"},
        )
        self.assertEqual(response.status_code, 200)
        rows = response.json()["rows"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["social_package_id"], self.approved_social_package_id)

        response = self.client.get(
            "/social-packages/inbox",
            headers=self.headers,
            params={"linkage_state": "approved_for_queue"},
        )
        self.assertEqual(response.status_code, 200)
        rows = response.json()["rows"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["social_package_id"], self.approved_social_package_id)

        response = self.client.get(
            "/social-packages/inbox",
            headers=self.headers,
            params={"search": "chickpeas"},
        )
        self.assertEqual(response.status_code, 200)
        rows = response.json()["rows"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["social_package_id"], self.approved_social_package_id)

    def test_social_package_review_endpoint_refreshes_queue_state(self) -> None:
        response = self.client.post(
            f"/social-packages/{self.social_package_id}/review",
            headers=self.headers,
            json={
                "review_outcome": "approved",
                "review_notes": ["hook_matches_blog"],
                "reviewer_label": "api_social_reviewer",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["social_package"]["approval_state"], "approved")

        social_reviews = read_social_package_review_records(self.paths.social_package_reviews_path)
        self.assertEqual(len(social_reviews), 2)
        self.assertEqual(social_reviews[-1].review_outcome, "approved")

        queue_inbox = self.client.get("/queue/inbox", headers=self.headers)
        self.assertEqual(queue_inbox.status_code, 200)
        facebook_rows = [
            row
            for row in queue_inbox.json()["rows"]
            if row["queue_type"] == "facebook_publish" and row["blog_publish_id"] == self.blog_publish_id
        ]
        self.assertEqual(facebook_rows[0]["queue_state"], "approved_for_queue")

    def test_social_variant_selection_reopens_review_and_updates_text(self) -> None:
        approve_response = self.client.post(
            f"/social-packages/{self.social_package_id}/review",
            headers=self.headers,
            json={
                "review_outcome": "approved",
                "review_notes": ["clean_package"],
                "reviewer_label": "api_social_reviewer",
            },
        )
        self.assertEqual(approve_response.status_code, 200)

        detail_before = self.client.get(
            f"/social-packages/{self.social_package_id}",
            headers=self.headers,
        )
        self.assertEqual(detail_before.status_code, 200)
        package_before = detail_before.json()["social_package"]
        current_label = package_before["selected_variant_label"]
        self.assertEqual(package_before["ai_assistance_log"][0]["model_label"], "gpt-5.4-mini")
        self.assertEqual(
            detail_before.json()["linked_draft"]["ai_assistance_log"][0]["skill_name"],
            "generate_headline_variants",
        )

        response = self.client.post(
            f"/social-packages/{self.social_package_id}/select-variant",
            headers=self.headers,
            json={"variant_label": "openai_refined_1_v1"},
        )
        self.assertEqual(response.status_code, 200)
        package = response.json()["social_package"]
        self.assertEqual(package["selected_variant_label"], "openai_refined_1_v1")
        self.assertEqual(package["approval_state"], "pending_review")
        self.assertNotEqual(package["selected_variant_label"], current_label)
        self.assertNotEqual(package["hook_text"], package_before["hook_text"])

    def test_detail_payloads_include_draft_and_social_ai_provenance(self) -> None:
        draft_detail = self.client.get(f"/drafts/{self.approved_draft_id}", headers=self.headers)
        self.assertEqual(draft_detail.status_code, 200)
        self.assertEqual(
            draft_detail.json()["draft"]["ai_assistance_log"][0]["target_field"],
            "headline_variants",
        )
        self.assertEqual(
            draft_detail.json()["downstream"]["asset_record_id"],
            self.pending_asset_id,
        )

        social_detail = self.client.get(
            f"/social-packages/{self.social_package_id}",
            headers=self.headers,
        )
        self.assertEqual(social_detail.status_code, 200)
        self.assertEqual(
            social_detail.json()["social_package"]["ai_assistance_log"][0]["skill_name"],
            "refine_social_package_variants",
        )
        self.assertEqual(
            social_detail.json()["linked_draft"]["ai_assistance_log"][0]["model_label"],
            "gpt-5.4-mini",
        )
        self.assertEqual(
            social_detail.json()["linked_asset"]["asset_record_id"],
            self.pending_asset_id,
        )
        self.assertFalse(social_detail.json()["asset_readiness"]["asset_complete"])

    def test_queue_inbox_filters_work(self) -> None:
        response = self.client.get(
            "/queue/inbox",
            headers=self.headers,
            params={"queue_type": "facebook_publish"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {row["queue_item_id"] for row in response.json()["rows"]},
            {self.facebook_queue_id, self.approved_facebook_queue_id},
        )

        response = self.client.get(
            "/queue/inbox",
            headers=self.headers,
            params={"queue_state": "blog_publish_failed"},
        )
        self.assertEqual(response.status_code, 200)
        rows = response.json()["rows"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["queue_item_id"], self.failed_blog_queue_id)

        response = self.client.get(
            f"/queue/{self.blog_queue_id}",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["allowed_actions"]["schedule"])
        self.assertEqual(response.json()["linked_asset"]["asset_record_id"], self.pending_asset_id)

        approve_response = self.client.post(
            f"/queue/{self.blog_queue_id}/approve",
            headers=self.headers,
            json={
                "review_outcome": "approved",
                "review_notes": ["queue_slot_accepted"],
                "reviewer_label": "queue_operator",
            },
        )
        self.assertEqual(approve_response.status_code, 200)

        response = self.client.get(
            "/queue/inbox",
            headers=self.headers,
            params={"queue_review_state": "approved"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["rows"][0]["queue_item_id"], self.blog_queue_id)

        response = self.client.get(
            "/queue/inbox",
            headers=self.headers,
            params={"schedule_allowed": "true"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["rows"][0]["queue_item_id"], self.blog_queue_id)

        response = self.client.get(
            "/queue/inbox",
            headers=self.headers,
            params={"blocked_only": "true"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            all(
                row["approve_block_reason"] or row["schedule_block_reason"]
                for row in response.json()["rows"]
            )
        )

    def test_queue_approve_and_schedule_endpoint(self) -> None:
        queue_detail_before = self.client.get(
            f"/queue/{self.blog_queue_id}",
            headers=self.headers,
        )
        self.assertEqual(queue_detail_before.status_code, 200)
        self.assertFalse(queue_detail_before.json()["allowed_actions"]["schedule"])
        self.assertEqual(
            queue_detail_before.json()["allowed_actions"]["schedule_block_reason"],
            "Queue scheduling requires an approved queue review first.",
        )

        approve_response = self.client.post(
            f"/queue/{self.blog_queue_id}/approve",
            headers=self.headers,
            json={
                "review_outcome": "approved",
                "review_notes": ["queue_slot_accepted"],
                "reviewer_label": "queue_operator",
            },
        )
        self.assertEqual(approve_response.status_code, 200)
        approve_payload = approve_response.json()
        self.assertEqual(approve_payload["queue_review_state"], "approved")

        queue_inbox_after_approve = self.client.get("/queue/inbox", headers=self.headers)
        self.assertEqual(queue_inbox_after_approve.status_code, 200)
        blog_rows = [
            row
            for row in queue_inbox_after_approve.json()["rows"]
            if row["queue_item_id"] == self.blog_queue_id
        ]
        self.assertEqual(len(blog_rows), 1)
        self.assertTrue(blog_rows[0]["schedule_allowed"])
        self.assertIsNone(blog_rows[0]["schedule_block_reason"])

        schedule_response = self.client.post(
            f"/queue/{self.blog_queue_id}/schedule",
            headers=self.headers,
            json={
                "scheduled_for": "2026-04-05T09:00:00+00:00",
                "reviewer_label": "queue_operator",
                "schedule_mode": "manual",
            },
        )
        self.assertEqual(schedule_response.status_code, 200)
        schedule_payload = schedule_response.json()
        self.assertEqual(schedule_payload["queue_item"]["queue_state"], "scheduled_blog")
        self.assertEqual(schedule_payload["linked_blog_publish"]["schedule_mode"], "manual")
        self.assertEqual(
            schedule_payload["linked_blog_publish"]["scheduled_for_blog"],
            "2026-04-05T09:00:00+00:00",
        )

        queue_reviews = read_queue_review_records(self.paths.queue_review_records_path)
        self.assertEqual(len(queue_reviews), 1)
        self.assertEqual(queue_reviews[0].review_outcome, "approved")

    def test_queue_schedule_endpoint_rejects_schedule_before_approval(self) -> None:
        response = self.client.post(
            f"/queue/{self.blog_queue_id}/schedule",
            headers=self.headers,
            json={
                "scheduled_for": "2026-04-05T09:00:00+00:00",
                "reviewer_label": "queue_operator",
                "schedule_mode": "manual",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"],
            "Queue scheduling requires an approved queue review first.",
        )

    def test_queue_detail_blocks_approve_for_failed_queue_item(self) -> None:
        detail = self.client.get(f"/queue/{self.failed_blog_queue_id}", headers=self.headers)
        self.assertEqual(detail.status_code, 200)
        payload = detail.json()
        self.assertFalse(payload["allowed_actions"]["approve"])
        self.assertEqual(
            payload["allowed_actions"]["approve_block_reason"],
            "Failed queue items cannot be approved for queue until the failure is resolved.",
        )

        inbox = self.client.get("/queue/inbox", headers=self.headers)
        self.assertEqual(inbox.status_code, 200)
        failed_rows = [
            row for row in inbox.json()["rows"] if row["queue_item_id"] == self.failed_blog_queue_id
        ]
        self.assertEqual(len(failed_rows), 1)
        self.assertFalse(failed_rows[0]["approve_allowed"])
        self.assertEqual(
            failed_rows[0]["approve_block_reason"],
            "Failed queue items cannot be approved for queue until the failure is resolved.",
        )

    def test_queue_remove_endpoint_records_removed_state(self) -> None:
        response = self.client.post(
            f"/queue/{self.blog_queue_id}/approve",
            headers=self.headers,
            json={
                "review_outcome": "removed",
                "review_notes": ["removed_from_current_batch_due_to_schedule_conflict"],
                "reviewer_label": "queue_operator",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["queue_review_state"], "removed")
        self.assertFalse(payload["allowed_actions"]["schedule"])
        self.assertEqual(
            payload["allowed_actions"]["schedule_block_reason"],
            "Queue scheduling requires an approved queue review first.",
        )

        queue_reviews = read_queue_review_records(self.paths.queue_review_records_path)
        self.assertEqual(len(queue_reviews), 1)
        self.assertEqual(queue_reviews[0].review_outcome, "removed")

    def test_combined_health_endpoint_returns_activation_and_fast_lane_placeholders(self) -> None:
        response = self.client.get("/health/combined", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("draft_health", payload)
        self.assertIn("distribution_health", payload)
        self.assertEqual(payload["fast_lane"]["status"], "disabled")

    def test_operator_validation_endpoint_returns_backend_readiness_snapshot(self) -> None:
        response = self.client.get("/validation/operator-baseline", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ready_for_live_plugin_validation")
        self.assertTrue(payload["endpoint_checks"]["dashboard_summary"]["ok"])
        self.assertTrue(payload["endpoint_checks"]["media_assets_inbox"]["ok"])
        self.assertGreaterEqual(payload["record_counts"]["draft_rows"], 1)
        self.assertGreaterEqual(payload["record_counts"]["media_asset_rows"], 1)
        self.assertTrue(payload["review_surfaces"]["draft_review_available"])
        self.assertTrue(payload["review_surfaces"]["media_review_available"])
        self.assertIn("activation_signal", payload["workflow_snapshot"])
        self.assertEqual(payload["workflow_snapshot"]["fast_lane_status"], "disabled")

    def test_load_operator_api_config_accepts_enable_docs_from_environment(self) -> None:
        import os

        original_enable_docs = os.environ.get("CONTENT_OPS_OPERATOR_API_ENABLE_DOCS")
        original_shared_secret = os.environ.get("CONTENT_OPS_OPERATOR_API_SHARED_SECRET")
        os.environ["CONTENT_OPS_OPERATOR_API_ENABLE_DOCS"] = "true"
        os.environ["CONTENT_OPS_OPERATOR_API_SHARED_SECRET"] = "env-secret"
        try:
            config = load_operator_api_config(path=self.paths.draft_records_path.parent / "missing.json")
        finally:
            if original_enable_docs is None:
                os.environ.pop("CONTENT_OPS_OPERATOR_API_ENABLE_DOCS", None)
            else:
                os.environ["CONTENT_OPS_OPERATOR_API_ENABLE_DOCS"] = original_enable_docs
            if original_shared_secret is None:
                os.environ.pop("CONTENT_OPS_OPERATOR_API_SHARED_SECRET", None)
            else:
                os.environ["CONTENT_OPS_OPERATOR_API_SHARED_SECRET"] = original_shared_secret

        self.assertTrue(config.enable_docs)

    def _seed_chain(self) -> None:
        source_fact = _build_source_item(
            item_id="item-operator-api-1",
            source_url="https://example.com/sourdough",
            raw_title="Why Sourdough Bread Tastes Different",
            raw_summary="A short explanation of why sourdough has a more complex flavor than standard yeast bread.",
            raw_body_text=(
                "Sourdough bread tastes different because fermentation changes far more than the loaf's rise. "
                "Wild yeast and lactic acid bacteria keep working through a longer fermentation window, which gives the dough "
                "more time to develop tangy acids and deeper aroma compounds.\n\n"
                "That longer fermentation is the main reason the flavor feels more complex. Instead of tasting only yeasty or neutral, "
                "sourdough can carry mild sour notes, toasted depth, and a fuller aroma because the microbes keep transforming sugars while the dough rests.\n\n"
                "Commercial yeast bread usually ferments faster, so it can still taste good but often stays cleaner and simpler. "
                "Sourdough's slower process gives bakers more flavor development, more texture variation, and a stronger sense that the loaf has character beyond basic bread structure.\n\n"
                "For everyday readers, the useful takeaway is simple: sourdough tastes different because time, fermentation, and microbial activity all shape the final loaf."
            ),
            template_suggestion="food_fact_article",
            topical_label="food_fact",
        )
        source_curiosity = _build_source_item(
            item_id="item-operator-api-2",
            source_url="https://olive.test/cloudy-oil",
            raw_title="Why Olive Oil Looks Cloudy in the Cold",
            raw_summary="A quick explanation of why chilled olive oil turns cloudy and thick.",
            raw_body_text=(
                "Olive oil can look cloudy in the cold because some of its natural waxes and fatty compounds start to solidify at lower temperatures. "
                "That change is visual first, which is why the bottle suddenly looks hazy instead of clear.\n\n"
                "The cloudiness does not automatically mean the oil has gone bad. In many cases it simply means the bottle was stored in a cool kitchen, pantry, or refrigerator long enough for the oil to react to the lower temperature.\n\n"
                "Once the bottle warms back up, the oil usually clears again. For readers, the useful point is that temperature affects the look of olive oil more than people expect, and the cloudy appearance is often temporary rather than a sign of spoilage."
            ),
            template_suggestion="curiosity_article",
            topical_label="food_question",
        )
        source_benefit = _build_source_item(
            item_id="item-operator-api-3",
            source_url="https://health.example/chickpeas",
            raw_title="Why Chickpeas Can Be a Helpful Pantry Staple",
            raw_summary="A short explainer on why chickpeas are useful for quick meals and pantry planning.",
            raw_body_text=(
                "Chickpeas can be a helpful pantry staple because they work across soups, salads, spreads, and fast skillet meals without needing much planning. "
                "That kind of flexibility matters on busy weeks when convenience often decides what actually gets cooked.\n\n"
                "They are also easy to pair with vegetables, grains, and simple seasonings, which makes them practical for readers who want more meal options without buying a completely different ingredient list every time.\n\n"
                "The key benefit angle is not hype. It is that chickpeas are adaptable, easy to keep on hand, and useful in everyday cooking when people want something reliable.\n\n"
                "That reliability is what gives them pantry value. A can or a jar of chickpeas can turn into lunch, dinner, or a simple side without much extra work, and that helps readers who want practical ingredients instead of impressive-but-unused purchases.\n\n"
                "For this kind of article, the honest takeaway is that chickpeas matter because they reduce friction in everyday cooking. They are easy to store, easy to pair, and useful when a reader wants a dependable ingredient that fits real weeknight habits."
            ),
            template_suggestion="food_benefit_article",
            topical_label="food_benefit",
        )
        source_needs_edits = _build_source_item(
            item_id="item-operator-api-4",
            source_url="https://pantry.example/garlic-storage",
            raw_title="What Happens When Garlic Sits Out Too Long",
            raw_summary="A quick explainer about how storage conditions affect garlic quality over time.",
            raw_body_text=(
                "Garlic can lose quality faster when it sits in warm, bright conditions for too long because moisture balance and sprouting both change what the cloves feel like and how they cook. "
                "That is why storage advice matters even for common pantry ingredients.\n\n"
                "The point is not that garlic becomes unusable overnight. It is that heat, humidity, and time can all reduce quality and make the cloves harder to use well in everyday cooking.\n\n"
                "Readers usually care about the practical signal: softer cloves, early sprouting, or a sharper smell can all suggest the bulb is past its best condition. That does not mean every clove needs to be thrown away immediately, but it does mean storage habits affect cooking quality more than people assume.\n\n"
                "That is the useful pantry lesson in this case. Garlic lasts better when storage conditions are steady, dry, and cool, and the article should help the operator review flow catch whether the draft makes that takeaway clear enough."
            ),
            template_suggestion="food_fact_article",
            topical_label="food_fact",
        )
        append_source_items(
            [source_fact, source_curiosity, source_benefit, source_needs_edits],
            path=self.paths.source_items_path,
        )

        pending_draft = _attach_headline_variants(
            format_source_item_to_draft(
                source_fact,
                created_at="2026-04-04T10:00:00+00:00",
            ),
            "What Makes Sourdough Bread Taste Different?",
            "Why Sourdough Has a More Complex Flavor",
        )
        self.pending_draft_id = pending_draft.draft_id
        append_draft_records([pending_draft], path=self.paths.draft_records_path)

        approved_seed_draft = _attach_headline_variants(
            format_source_item_to_draft(
                source_curiosity,
                created_at="2026-04-04T10:05:00+00:00",
            ),
            "What Makes Olive Oil Turn Cloudy in the Cold?",
            "Why Olive Oil Turns Hazy in the Refrigerator",
        )
        self.approved_draft_alt_headline = "What Makes Olive Oil Turn Cloudy in the Cold?"
        approved_draft, approved_review = record_draft_review(
            approved_seed_draft,
            review_outcome="approved",
            review_notes=["ready_for_distribution"],
            reviewer_label="seed_operator",
            reviewed_at="2026-04-04T10:07:00+00:00",
        )
        approved_draft.ai_assistance_log.append(
            AiAssistanceRecord(
                skill_name="generate_headline_variants",
                target_field="headline_variants",
                model_label="gpt-5.4-mini",
                created_at="2026-04-04T10:06:00+00:00",
            )
        )
        append_draft_records([approved_draft], path=self.paths.draft_records_path)
        self.approved_draft_id = approved_draft.draft_id
        from content_engine.storage import append_draft_review_records

        append_draft_review_records([approved_review], path=self.paths.draft_reviews_path)

        approved_benefit_seed = _attach_headline_variants(
            format_source_item_to_draft(
                source_benefit,
                created_at="2026-04-04T10:08:00+00:00",
            ),
            "Why Chickpeas Work So Well as a Pantry Staple",
            "What Makes Chickpeas So Useful in the Pantry",
        )
        approved_benefit_draft, approved_benefit_review = record_draft_review(
            approved_benefit_seed,
            review_outcome="approved",
            review_notes=["ready_for_distribution"],
            reviewer_label="seed_operator",
            reviewed_at="2026-04-04T10:09:00+00:00",
        )
        append_draft_records([approved_benefit_draft], path=self.paths.draft_records_path)
        append_draft_review_records([approved_benefit_review], path=self.paths.draft_reviews_path)
        self.approved_benefit_draft_id = approved_benefit_draft.draft_id

        needs_edits_seed = _attach_headline_variants(
            format_source_item_to_draft(
                source_needs_edits,
                created_at="2026-04-04T10:10:00+00:00",
            ),
            "Why Garlic Quality Changes Faster at Room Temperature",
            "What Happens When Garlic Stays Out Too Long",
        )
        needs_edits_draft, needs_edits_review = record_draft_review(
            needs_edits_seed,
            review_outcome="needs_edits",
            review_notes=["tighten storage guidance and clarify the practical takeaway"],
            reviewer_label="seed_operator",
            reviewed_at="2026-04-04T10:11:00+00:00",
        )
        append_draft_records([needs_edits_draft], path=self.paths.draft_records_path)
        append_draft_review_records([needs_edits_review], path=self.paths.draft_reviews_path)
        self.needs_edits_draft_id = needs_edits_draft.draft_id

        blog_record = prepare_blog_publish_record(
            approved_draft,
            publish_intent="schedule",
            created_at="2026-04-04T10:12:00+00:00",
            allow_non_pass_quality=True,
        )
        blog_record.wordpress_status = "draft_created"
        blog_record.wordpress_post_id = "wp-operator-1"
        blog_record.wordpress_post_url = "https://example.com/why-olive-oil-looks-cloudy-in-the-cold"
        append_blog_publish_records([blog_record], path=self.paths.blog_publish_records_path)

        social_package = prepare_social_package_record(
            approved_draft,
            blog_publish_record=blog_record,
            created_at="2026-04-04T10:13:00+00:00",
        )
        social_package.variant_options.append(
            {
                "label": "openai_refined_1_v1",
                "hook_text": "Why this kitchen answer is easier to repeat than it looks",
                "caption_text": "The linked article explains the practical cause in a clearer way without stretching the claim beyond the approved draft.",
                "comment_cta_text": "Read the full breakdown here.",
            }
        )
        social_package.ai_assistance_log.append(
            AiAssistanceRecord(
                skill_name="refine_social_package_variants",
                target_field="variant_options",
                model_label="gpt-5.4-mini",
                created_at="2026-04-04T10:13:30+00:00",
            )
        )
        append_social_package_records([social_package], path=self.paths.social_package_records_path)

        pending_media_brief = prepare_media_brief_record(
            approved_draft,
            blog_publish_record=blog_record,
            social_package_record=social_package,
            created_at="2026-04-04T10:13:10+00:00",
        )
        append_media_brief_records([pending_media_brief], path=self.paths.media_brief_records_path)
        pending_asset = prepare_asset_record(
            pending_media_brief,
            asset_source_kind="licensed",
            provenance_reference="licensed_stock_asset:olive-cloudy-01",
            asset_url_or_path="https://cdn.example.com/assets/olive-cloudy-01.jpg",
            alt_text="Cloudy olive oil in a glass bottle stored in a cold kitchen setting.",
            caption_support_text="Use as the shared visual for the olive-oil explainer.",
            created_at="2026-04-04T10:13:20+00:00",
        )
        append_asset_records([pending_asset], path=self.paths.asset_records_path)

        blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
            blog_record,
            social_package_record=social_package,
            facebook_publish_record=None,
            created_at="2026-04-04T10:14:00+00:00",
        )
        append_queue_item_records([blog_queue, facebook_queue], path=self.paths.queue_item_records_path)
        append_blog_facebook_mapping_records([mapping], path=self.paths.mapping_records_path)

        approved_blog_record = prepare_blog_publish_record(
            approved_benefit_draft,
            publish_intent="draft",
            created_at="2026-04-04T10:15:00+00:00",
            allow_non_pass_quality=True,
        )
        approved_blog_record.wordpress_status = "published"
        approved_blog_record.wordpress_post_id = "wp-operator-2"
        approved_blog_record.wordpress_post_url = "https://example.com/why-chickpeas-can-be-a-helpful-pantry-staple"
        approved_blog_record.published_at_blog = "2026-04-04T10:16:00+00:00"
        append_blog_publish_records([approved_blog_record], path=self.paths.blog_publish_records_path)

        approved_social_seed = prepare_social_package_record(
            approved_benefit_draft,
            blog_publish_record=approved_blog_record,
            created_at="2026-04-04T10:17:00+00:00",
        )
        approved_social_package, approved_social_review = record_social_package_review(
            approved_social_seed,
            review_outcome="approved",
            review_notes=["ready_for_queue"],
            reviewer_label="seed_social_operator",
            reviewed_at="2026-04-04T10:18:00+00:00",
        )
        append_social_package_records(
            [approved_social_seed, approved_social_package],
            path=self.paths.social_package_records_path,
        )
        append_social_package_review_records(
            [approved_social_review],
            path=self.paths.social_package_reviews_path,
        )

        approved_media_brief = prepare_media_brief_record(
            approved_benefit_draft,
            blog_publish_record=approved_blog_record,
            social_package_record=approved_social_package,
            created_at="2026-04-04T10:17:10+00:00",
        )
        append_media_brief_records([approved_media_brief], path=self.paths.media_brief_records_path)
        approved_asset_seed = prepare_asset_record(
            approved_media_brief,
            asset_source_kind="owned",
            provenance_reference="owned_photo_library:chickpeas-bowl-01",
            asset_url_or_path="C:/assets/chickpeas-bowl-01.jpg",
            alt_text="Bowl of cooked chickpeas on a kitchen counter with simple meal ingredients.",
            caption_support_text="Approved pantry staple supporting visual.",
            created_at="2026-04-04T10:17:20+00:00",
        )
        approved_asset, approved_asset_review = record_asset_review(
            approved_asset_seed,
            review_outcome="approved",
            review_notes=["rights_checked_and_usage_confirmed"],
            reviewer_label="seed_media_operator",
            reviewed_at="2026-04-04T10:17:30+00:00",
        )
        append_asset_records(
            [approved_asset_seed, approved_asset],
            path=self.paths.asset_records_path,
        )
        append_asset_review_records(
            [approved_asset_review],
            path=self.paths.asset_review_records_path,
        )

        approved_blog_queue, approved_facebook_queue, approved_mapping = prepare_distribution_linkage_records(
            approved_blog_record,
            social_package_record=approved_social_package,
            facebook_publish_record=None,
            created_at="2026-04-04T10:19:00+00:00",
        )
        append_queue_item_records(
            [approved_blog_queue, approved_facebook_queue],
            path=self.paths.queue_item_records_path,
        )
        append_blog_facebook_mapping_records([approved_mapping], path=self.paths.mapping_records_path)

        failed_blog_record = prepare_blog_publish_record(
            approved_draft,
            publish_intent="draft",
            created_at="2026-04-04T10:20:00+00:00",
            allow_non_pass_quality=True,
        )
        failed_blog_record.wordpress_status = "failed"
        failed_blog_record.last_error = "draft_sync_failed"
        append_blog_publish_records([failed_blog_record], path=self.paths.blog_publish_records_path)

        failed_blog_queue = QueueItemRecord(
            queue_item_id="blogq-failed-operator-1",
            queue_type="blog_publish",
            draft_id=approved_draft.draft_id,
            blog_publish_id=failed_blog_record.blog_publish_id,
            social_package_id=None,
            queue_state="blog_publish_failed",
            approval_state="pending_review",
            scheduled_for=None,
            last_transition_at="2026-04-04T10:21:00+00:00",
            last_error="draft_sync_failed",
            created_at="2026-04-04T10:21:00+00:00",
            updated_at="2026-04-04T10:21:00+00:00",
        )
        append_queue_item_records([failed_blog_queue], path=self.paths.queue_item_records_path)

        self.blog_publish_id = blog_record.blog_publish_id
        self.blog_queue_id = blog_queue.queue_item_id
        self.pending_media_brief_id = pending_media_brief.media_brief_id
        self.pending_asset_id = pending_asset.asset_record_id
        self.social_package_id = social_package.social_package_id
        self.facebook_queue_id = facebook_queue.queue_item_id
        self.approved_social_package_id = approved_social_package.social_package_id
        self.approved_media_brief_id = approved_media_brief.media_brief_id
        self.approved_asset_id = approved_asset.asset_record_id
        self.approved_facebook_queue_id = approved_facebook_queue.queue_item_id
        self.failed_blog_queue_id = failed_blog_queue.queue_item_id


if __name__ == "__main__":
    unittest.main()
