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
from distribution_engine.wordpress import prepare_blog_publish_record
from distribution_engine.wordpress_transport import (
    WordPressRestConfig,
    WordPressRestTransportError,
    build_wordpress_rest_post_state_request,
    build_wordpress_rest_validation_request,
    build_wordpress_rest_request,
    execute_wordpress_rest_post_state_request,
    execute_wordpress_rest_validation_request,
    execute_wordpress_rest_request,
    inspect_wordpress_rest_post_state,
    sync_wordpress_rest_draft,
    validate_wordpress_rest_transport,
)
from distribution_engine.transport_retry import TransportRetryPolicy
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-wordpress-transport-123456",
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


def _build_config() -> WordPressRestConfig:
    return WordPressRestConfig(
        base_url="https://wordpress.example.com",
        username="operator",
        application_password="app pass 1234",
        category_id_by_name={"food-facts": 7},
        tag_id_by_name={"Kitchen": 11, "food-facts": 13},
        timeout_seconds=12,
    )


class WordPressTransportTests(unittest.TestCase):
    def test_build_wordpress_rest_validation_request_targets_users_me_endpoint(self) -> None:
        request = build_wordpress_rest_validation_request(_build_config())

        self.assertEqual(request.method, "GET")
        self.assertEqual(
            request.url,
            "https://wordpress.example.com/wp-json/wp/v2/users/me?context=edit",
        )
        self.assertEqual(request.timeout_seconds, 12)

    def test_build_wordpress_rest_post_state_request_targets_post_endpoint(self) -> None:
        request = build_wordpress_rest_post_state_request("345", _build_config())

        self.assertEqual(request.method, "GET")
        self.assertEqual(request.wordpress_post_id, "345")
        self.assertEqual(
            request.url,
            "https://wordpress.example.com/wp-json/wp/v2/posts/345?context=edit",
        )
        self.assertEqual(request.timeout_seconds, 12)

    def test_build_wordpress_rest_request_maps_taxonomy_and_skips_unknown_tags(self) -> None:
        blog_record = _build_blog_publish_record()
        blog_record.wordpress_tags = ["kitchen", "pantry", "food-facts"]

        request = build_wordpress_rest_request(blog_record, _build_config())

        self.assertEqual(request.operation, "create_draft")
        self.assertEqual(request.url, "https://wordpress.example.com/wp-json/wp/v2/posts")
        self.assertEqual(request.payload["status"], "draft")
        self.assertEqual(request.payload["categories"], [7])
        self.assertEqual(request.payload["tags"], [11, 13])
        self.assertEqual(request.skipped_tag_names, ("pantry",))
        self.assertIn("<h2>The Short Answer</h2>", request.payload["content"])

    def test_build_wordpress_rest_request_uses_update_operation_for_existing_post(self) -> None:
        blog_record = _build_blog_publish_record()
        blog_record.wordpress_status = "draft_created"
        blog_record.wordpress_post_id = "wp-123"

        request = build_wordpress_rest_request(blog_record, _build_config())

        self.assertEqual(request.operation, "update_draft")
        self.assertEqual(
            request.url,
            "https://wordpress.example.com/wp-json/wp/v2/posts/wp-123",
        )
        self.assertEqual(request.existing_wordpress_post_id, "wp-123")

    def test_build_wordpress_rest_request_rejects_scheduled_records(self) -> None:
        blog_record = _build_blog_publish_record()
        blog_record.wordpress_status = "scheduled"
        blog_record.wordpress_post_id = "wp-123"

        with self.assertRaisesRegex(ValueError, "draft sync only supports prepared or remote-draft records"):
            build_wordpress_rest_request(blog_record, _build_config())

    def test_sync_wordpress_rest_draft_dry_run_returns_preview_only(self) -> None:
        blog_record = _build_blog_publish_record()

        result = sync_wordpress_rest_draft(blog_record, _build_config(), execute=False)

        self.assertEqual(result.execution_mode, "dry_run")
        self.assertIsNone(result.updated_blog_publish_record)
        self.assertEqual(result.request.operation, "create_draft")

    def test_sync_wordpress_rest_draft_execute_marks_draft_created(self) -> None:
        blog_record = _build_blog_publish_record()

        def _executor(*_args):
            return {
                "id": 345,
                "link": "https://wordpress.example.com/why-this-kitchen-trick-works/",
                "status": "draft",
                "_response_status_code": 201,
            }

        result = sync_wordpress_rest_draft(
            blog_record,
            _build_config(),
            execute=True,
            request_executor=_executor,
        )

        self.assertEqual(result.execution_mode, "execute")
        self.assertEqual(result.updated_blog_publish_record.wordpress_status, "draft_created")
        self.assertEqual(result.updated_blog_publish_record.wordpress_post_id, "345")
        self.assertEqual(
            result.updated_blog_publish_record.wordpress_post_url,
            "https://wordpress.example.com/why-this-kitchen-trick-works/",
        )

    def test_sync_wordpress_rest_draft_execute_marks_draft_updated(self) -> None:
        blog_record = _build_blog_publish_record()
        blog_record.wordpress_status = "draft_created"
        blog_record.wordpress_post_id = "345"
        blog_record.wordpress_post_url = "https://wordpress.example.com/why-this-kitchen-trick-works/"

        def _executor(*_args):
            return {
                "id": 345,
                "link": "https://wordpress.example.com/why-this-kitchen-trick-works/",
                "status": "draft",
                "_response_status_code": 200,
            }

        result = sync_wordpress_rest_draft(
            blog_record,
            _build_config(),
            execute=True,
            request_executor=_executor,
        )

        self.assertEqual(result.request.operation, "update_draft")
        self.assertEqual(result.updated_blog_publish_record.wordpress_status, "draft_updated")
        self.assertEqual(result.execution_result.response_status_code, 200)

    def test_sync_wordpress_rest_draft_retries_retryable_failure_and_succeeds(self) -> None:
        blog_record = _build_blog_publish_record()
        attempts = {"count": 0}

        def _executor(*_args):
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise WordPressRestTransportError("WordPress REST draft sync request failed: timed out")
            return {
                "id": 345,
                "link": "https://wordpress.example.com/why-this-kitchen-trick-works/",
                "status": "draft",
                "_response_status_code": 201,
            }

        result = sync_wordpress_rest_draft(
            blog_record,
            _build_config(),
            execute=True,
            retry_policy=TransportRetryPolicy(max_attempts=2, initial_delay_seconds=0.0),
            request_executor=_executor,
        )

        self.assertEqual(attempts["count"], 2)
        self.assertEqual(result.execution_result.attempt_count, 2)
        self.assertEqual(result.updated_blog_publish_record.wordpress_status, "draft_created")

    def test_execute_wordpress_rest_request_rejects_non_draft_remote_status(self) -> None:
        blog_record = _build_blog_publish_record()
        request = build_wordpress_rest_request(blog_record, _build_config())

        def _executor(*_args):
            return {"id": 345, "status": "publish"}

        with self.assertRaisesRegex(WordPressRestTransportError, "unsupported remote status 'publish'"):
            execute_wordpress_rest_request(request, _build_config(), request_executor=_executor)

    def test_execute_wordpress_rest_validation_request_requires_user_id(self) -> None:
        request = build_wordpress_rest_validation_request(_build_config())

        def _executor(*_args):
            return {"name": "Operator"}

        with self.assertRaisesRegex(WordPressRestTransportError, "did not include a user id"):
            execute_wordpress_rest_validation_request(request, _build_config(), request_executor=_executor)

    def test_validate_wordpress_rest_transport_execute_returns_validated_user(self) -> None:
        def _executor(*_args):
            return {
                "id": 44,
                "slug": "operator",
                "name": "Solo Operator",
                "_response_status_code": 200,
            }

        result = validate_wordpress_rest_transport(
            _build_config(),
            execute=True,
            request_executor=_executor,
        )

        self.assertEqual(result.execution_mode, "execute")
        self.assertEqual(result.execution_result.validated_user_id, "44")
        self.assertEqual(result.execution_result.validated_user_slug, "operator")
        self.assertEqual(result.execution_result.validated_user_name, "Solo Operator")

    def test_execute_wordpress_rest_post_state_request_parses_remote_fields(self) -> None:
        request = build_wordpress_rest_post_state_request("345", _build_config())

        def _executor(*_args):
            return {
                "id": 345,
                "status": "future",
                "link": "https://wordpress.example.com/why-this-kitchen-trick-works/",
                "slug": "why-this-kitchen-trick-works",
                "title": {"rendered": "Why This Kitchen Trick Works"},
                "date_gmt": "2026-04-04T09:30:00",
                "modified_gmt": "2026-04-04T09:35:00",
                "_response_status_code": 200,
            }

        result = execute_wordpress_rest_post_state_request(
            request,
            _build_config(),
            request_executor=_executor,
        )

        self.assertEqual(result.wordpress_post_id, "345")
        self.assertEqual(result.remote_status, "future")
        self.assertEqual(result.remote_slug, "why-this-kitchen-trick-works")
        self.assertEqual(result.remote_title, "Why This Kitchen Trick Works")
        self.assertEqual(result.remote_published_at, "2026-04-04T09:30:00+00:00")
        self.assertEqual(result.remote_modified_at, "2026-04-04T09:35:00+00:00")
        self.assertEqual(result.response_status_code, 200)

    def test_inspect_wordpress_rest_post_state_dry_run_returns_preview(self) -> None:
        result = inspect_wordpress_rest_post_state("345", _build_config(), execute=False)

        self.assertEqual(result.execution_mode, "dry_run")
        self.assertEqual(result.request.wordpress_post_id, "345")
        self.assertIsNone(result.execution_result)


if __name__ == "__main__":
    unittest.main()
