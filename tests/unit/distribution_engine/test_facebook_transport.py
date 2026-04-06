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
from distribution_engine.facebook_publish_updates import record_facebook_publish_update
from distribution_engine.facebook_transport import (
    FacebookGraphConfig,
    FacebookGraphTransportError,
    build_facebook_graph_validation_request,
    build_facebook_graph_request_for_config,
    execute_facebook_graph_validation_request,
    execute_facebook_graph_request,
    sync_facebook_graph_post,
    validate_facebook_graph_transport,
)
from distribution_engine.transport_retry import TransportRetryPolicy
from distribution_engine.wordpress import prepare_blog_publish_record
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-facebook-transport-123456",
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


def _build_config() -> FacebookGraphConfig:
    return FacebookGraphConfig(
        page_id="123456789",
        page_access_token="page-token-123",
        api_version="v24.0",
        timeout_seconds=15,
    )


def _build_social_inputs():
    item = _build_source_item()
    draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")
    approved_draft, _ = record_draft_review(
        draft,
        review_outcome="approved",
        review_notes=["ready_for_phase_3"],
        reviewed_at="2026-04-03T12:05:00+00:00",
    )
    blog_record = prepare_blog_publish_record(
        approved_draft,
        allow_non_pass_quality=True,
        created_at="2026-04-03T12:10:00+00:00",
    )
    blog_record.wordpress_status = "published"
    blog_record.wordpress_post_id = "wp-123"
    blog_record.wordpress_post_url = "https://wordpress.example.com/why-this-kitchen-trick-works/"
    blog_record.published_at_blog = "2026-04-03T13:00:00+00:00"
    social_record = prepare_social_package_record(
        approved_draft,
        blog_publish_record=blog_record,
        created_at="2026-04-03T13:10:00+00:00",
    )
    social_record.approval_state = "approved"
    return approved_draft, blog_record, social_record


class FacebookTransportTests(unittest.TestCase):
    def test_build_facebook_graph_validation_request_targets_page_identity(self) -> None:
        request = build_facebook_graph_validation_request(_build_config())

        self.assertEqual(request.method, "GET")
        self.assertEqual(
            request.url,
            "https://graph.facebook.com/v24.0/123456789?fields=id,name",
        )
        self.assertEqual(request.timeout_seconds, 15)

    def test_build_facebook_graph_request_for_publish_uses_feed_endpoint(self) -> None:
        _, blog_record, social_record = _build_social_inputs()

        request = build_facebook_graph_request_for_config(
            social_record,
            blog_record,
            action="published",
            config=_build_config(),
        )

        self.assertEqual(request.url, "https://graph.facebook.com/v24.0/123456789/feed")
        self.assertEqual(request.form_fields["link"], blog_record.wordpress_post_url)
        self.assertIn(social_record.hook_text, request.form_fields["message"])
        self.assertIn(social_record.caption_text, request.form_fields["message"])
        self.assertEqual(request.deferred_comment_cta_text, social_record.comment_cta_text)

    def test_build_facebook_graph_request_for_schedule_includes_schedule_fields(self) -> None:
        _, blog_record, social_record = _build_social_inputs()
        blog_record.wordpress_status = "scheduled"
        blog_record.scheduled_for_blog = "2026-04-04T12:00:00+00:00"

        request = build_facebook_graph_request_for_config(
            social_record,
            blog_record,
            action="scheduled",
            config=_build_config(),
            scheduled_for_facebook="2026-04-04T13:00:00+00:00",
        )

        self.assertEqual(request.form_fields["published"], "false")
        self.assertEqual(request.form_fields["scheduled_publish_time"], "1775307600")
        self.assertEqual(request.scheduled_for_facebook, "2026-04-04T13:00:00+00:00")

    def test_build_facebook_graph_request_rejects_publish_before_blog_is_published(self) -> None:
        _, blog_record, social_record = _build_social_inputs()
        blog_record.wordpress_status = "draft_created"

        with self.assertRaisesRegex(ValueError, "linked blog post to already be published"):
            build_facebook_graph_request_for_config(
                social_record,
                blog_record,
                action="published",
                config=_build_config(),
            )

    def test_sync_facebook_graph_post_dry_run_returns_preview_only(self) -> None:
        _, blog_record, social_record = _build_social_inputs()

        result = sync_facebook_graph_post(
            social_record,
            blog_record,
            _build_config(),
            action="published",
            execute=False,
        )

        self.assertEqual(result.execution_mode, "dry_run")
        self.assertIsNone(result.updated_facebook_publish_record)

    def test_sync_facebook_graph_post_execute_marks_published(self) -> None:
        _, blog_record, social_record = _build_social_inputs()

        def _executor(*_args):
            return {"id": "pagepost-123", "_response_status_code": 200}

        result = sync_facebook_graph_post(
            social_record,
            blog_record,
            _build_config(),
            action="published",
            execute=True,
            request_executor=_executor,
        )

        self.assertEqual(result.updated_facebook_publish_record.publish_status, "published")
        self.assertEqual(result.updated_facebook_publish_record.facebook_post_id, "pagepost-123")
        self.assertEqual(result.execution_result.response_status_code, 200)

    def test_sync_facebook_graph_post_execute_marks_scheduled(self) -> None:
        _, blog_record, social_record = _build_social_inputs()
        blog_record.wordpress_status = "scheduled"
        blog_record.scheduled_for_blog = "2026-04-04T12:00:00+00:00"

        def _executor(*_args):
            return {"id": "pagepost-999", "_response_status_code": 200}

        result = sync_facebook_graph_post(
            social_record,
            blog_record,
            _build_config(),
            action="scheduled",
            scheduled_for_facebook="2026-04-04T13:00:00+00:00",
            execute=True,
            schedule_mode="manual",
            request_executor=_executor,
        )

        self.assertEqual(result.updated_facebook_publish_record.publish_status, "scheduled")
        self.assertEqual(result.updated_facebook_publish_record.schedule_mode, "manual")
        self.assertEqual(result.updated_facebook_publish_record.facebook_post_id, "pagepost-999")

    def test_sync_facebook_graph_post_retries_retryable_failure_and_succeeds(self) -> None:
        _, blog_record, social_record = _build_social_inputs()
        attempts = {"count": 0}

        def _executor(*_args):
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise FacebookGraphTransportError("Facebook Graph transport request failed: timed out")
            return {"id": "pagepost-123", "_response_status_code": 200}

        result = sync_facebook_graph_post(
            social_record,
            blog_record,
            _build_config(),
            action="published",
            execute=True,
            retry_policy=TransportRetryPolicy(max_attempts=2, initial_delay_seconds=0.0),
            request_executor=_executor,
        )

        self.assertEqual(attempts["count"], 2)
        self.assertEqual(result.execution_result.attempt_count, 2)
        self.assertEqual(result.updated_facebook_publish_record.publish_status, "published")

    def test_sync_facebook_graph_post_rejects_existing_scheduled_publish_record(self) -> None:
        _, blog_record, social_record = _build_social_inputs()
        existing = record_facebook_publish_update(
            social_record,
            blog_record,
            update_action="published",
            facebook_post_id="pagepost-123",
            published_at_facebook="2026-04-03T14:00:00+00:00",
        )

        with self.assertRaisesRegex(ValueError, "already scheduled or published"):
            sync_facebook_graph_post(
                social_record,
                blog_record,
                _build_config(),
                action="published",
                execute=False,
                existing_publish_record=existing,
            )

    def test_execute_facebook_graph_request_requires_post_id(self) -> None:
        _, blog_record, social_record = _build_social_inputs()
        request = build_facebook_graph_request_for_config(
            social_record,
            blog_record,
            action="published",
            config=_build_config(),
        )

        def _executor(*_args):
            return {"success": True}

        with self.assertRaisesRegex(FacebookGraphTransportError, "did not include a post id"):
            execute_facebook_graph_request(request, _build_config(), request_executor=_executor)

    def test_execute_facebook_graph_validation_request_requires_page_id(self) -> None:
        request = build_facebook_graph_validation_request(_build_config())

        def _executor(*_args):
            return {"name": "Food Facts Page"}

        with self.assertRaisesRegex(FacebookGraphTransportError, "did not include a page id"):
            execute_facebook_graph_validation_request(request, _build_config(), request_executor=_executor)

    def test_validate_facebook_graph_transport_execute_returns_page_identity(self) -> None:
        def _executor(*_args):
            return {
                "id": "123456789",
                "name": "Food Facts Page",
                "_response_status_code": 200,
            }

        result = validate_facebook_graph_transport(
            _build_config(),
            execute=True,
            request_executor=_executor,
        )

        self.assertEqual(result.execution_mode, "execute")
        self.assertEqual(result.execution_result.validated_page_id, "123456789")
        self.assertEqual(result.execution_result.validated_page_name, "Food Facts Page")


if __name__ == "__main__":
    unittest.main()
