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

from content_engine.formatting import format_source_item_to_draft
from content_engine.review import record_draft_review
from content_engine.storage import append_draft_records, read_draft_review_records
from distribution_engine.facebook import prepare_social_package_record
from distribution_engine.models import QueueItemRecord
from distribution_engine.storage import (
    append_blog_publish_records,
    append_queue_item_records,
    append_social_package_records,
    read_queue_review_records,
    read_social_package_review_records,
)
from distribution_engine.workflow import prepare_distribution_linkage_records
from distribution_engine.wordpress import prepare_blog_publish_record
from operator_api.app import build_app
from operator_api.config import OperatorApiConfig, load_operator_api_config
from operator_api.services import OperatorApiPaths
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-operator-api-1",
        source_id="src_operator_api",
        source_name="Operator API Source",
        source_family="editorial_food",
        run_id="run-operator-api-1",
        source_url="https://example.com/sourdough",
        canonical_url="https://example.com/sourdough",
        discovered_at="2026-04-04T09:00:00+00:00",
        fetched_at="2026-04-04T09:00:00+00:00",
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
        author_name="Editor",
        published_at="2026-04-03T10:00:00+00:00",
        topical_label="food_fact",
        freshness_label="evergreen",
        normalization_status="normalized",
        dedupe_status="unique",
        quality_flags=[],
        template_suggestion="food_fact_article",
    )


class OperatorApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        base = Path(self.temp_dir.name)
        self.paths = OperatorApiPaths(
            draft_records_path=base / "draft_records.jsonl",
            draft_reviews_path=base / "draft_reviews.jsonl",
            blog_publish_records_path=base / "blog_publish_records.jsonl",
            social_package_records_path=base / "social_package_records.jsonl",
            social_package_reviews_path=base / "social_package_reviews.jsonl",
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

    def test_draft_inbox_and_detail_and_review_endpoint(self) -> None:
        inbox = self.client.get("/drafts/inbox", headers=self.headers)
        self.assertEqual(inbox.status_code, 200)
        payload = inbox.json()
        self.assertEqual(payload["summary"]["total_drafts"], 2)
        detail = self.client.get(f"/drafts/{self.pending_draft_id}", headers=self.headers)
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["draft"]["draft_id"], self.pending_draft_id)

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
        self.assertEqual(len(latest_reviews), 2)
        self.assertEqual(latest_reviews[-1].review_outcome, "approved")

    def test_dashboard_summary_includes_recent_activity_and_current_alerts(self) -> None:
        response = self.client.get("/dashboard/summary", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("recent_activity", payload)
        self.assertIn("current_alerts", payload)
        self.assertGreaterEqual(len(payload["recent_activity"]), 1)
        self.assertEqual(payload["recent_activity"][0]["activity_type"], "draft_review")
        self.assertEqual(payload["recent_activity"][0]["review_outcome"], "approved")
        self.assertEqual(payload["recent_activity"][0]["detail_target_type"], "draft")
        self.assertEqual(payload["recent_activity"][0]["detail_target_id"], self.approved_draft_id)
        self.assertIn("message", payload["current_alerts"][0])
        self.assertTrue(
            any(
                alert.get("queue_item_id") == self.failed_blog_queue_id
                for alert in payload["current_alerts"]
            )
        )

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
        self.assertEqual(len(social_reviews), 1)
        self.assertEqual(social_reviews[0].review_outcome, "approved")

        queue_inbox = self.client.get("/queue/inbox", headers=self.headers)
        self.assertEqual(queue_inbox.status_code, 200)
        facebook_rows = [
            row for row in queue_inbox.json()["rows"] if row["queue_type"] == "facebook_publish"
        ]
        self.assertEqual(facebook_rows[0]["queue_state"], "approved_for_queue")

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
        self.assertEqual(schedule_payload["linked_blog_publish"]["scheduled_for_blog"], "2026-04-05T09:00:00+00:00")

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
        self.assertGreaterEqual(payload["record_counts"]["draft_rows"], 1)
        self.assertTrue(payload["review_surfaces"]["draft_review_available"])
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
        source_item = _build_source_item()

        pending_draft = format_source_item_to_draft(
            source_item,
            created_at="2026-04-04T10:00:00+00:00",
        )
        self.pending_draft_id = pending_draft.draft_id
        append_draft_records([pending_draft], path=self.paths.draft_records_path)

        approved_seed_draft = format_source_item_to_draft(
            source_item,
            created_at="2026-04-04T10:05:00+00:00",
        )
        approved_draft, approved_review = record_draft_review(
            approved_seed_draft,
            review_outcome="approved",
            review_notes=["ready_for_distribution"],
            reviewer_label="seed_operator",
            reviewed_at="2026-04-04T10:07:00+00:00",
        )
        append_draft_records([approved_draft], path=self.paths.draft_records_path)
        self.approved_draft_id = approved_draft.draft_id
        from content_engine.storage import append_draft_review_records

        append_draft_review_records([approved_review], path=self.paths.draft_reviews_path)

        blog_record = prepare_blog_publish_record(
            approved_draft,
            publish_intent="schedule",
            created_at="2026-04-04T10:10:00+00:00",
        )
        blog_record.wordpress_status = "draft_created"
        blog_record.wordpress_post_id = "wp-operator-1"
        blog_record.wordpress_post_url = "https://example.com/why-sourdough-bread-tastes-different"
        append_blog_publish_records([blog_record], path=self.paths.blog_publish_records_path)

        social_package = prepare_social_package_record(
            approved_draft,
            blog_publish_record=blog_record,
            created_at="2026-04-04T10:12:00+00:00",
        )
        append_social_package_records([social_package], path=self.paths.social_package_records_path)

        blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
            blog_record,
            social_package_record=social_package,
            facebook_publish_record=None,
            created_at="2026-04-04T10:13:00+00:00",
        )
        append_queue_item_records([blog_queue, facebook_queue], path=self.paths.queue_item_records_path)
        from distribution_engine.storage import append_blog_facebook_mapping_records

        append_blog_facebook_mapping_records([mapping], path=self.paths.mapping_records_path)

        failed_blog_record = prepare_blog_publish_record(
            approved_draft,
            publish_intent="draft",
            created_at="2026-04-04T10:20:00+00:00",
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
        self.social_package_id = social_package.social_package_id
        self.facebook_queue_id = facebook_queue.queue_item_id
        self.failed_blog_queue_id = failed_blog_queue.queue_item_id


if __name__ == "__main__":
    unittest.main()
