from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.formatting import format_source_item_to_draft
from content_engine.review import record_draft_review
from distribution_engine.facebook import prepare_social_package_record
from distribution_engine.storage import (
    append_blog_publish_records,
    append_social_package_records,
    load_latest_blog_publish_record,
    load_latest_mapping_for_blog_publish,
    load_latest_queue_item_for_blog_publish,
    read_blog_publish_records,
)
from distribution_engine.wordpress import prepare_blog_publish_record
from distribution_engine.wordpress_transport import WordPressRestTransportError
from distribution_engine.wordpress_post_state_cli import main
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-wordpress-post-state-cli-123456",
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


def _write_config(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "base_url": "https://wordpress.example.com",
                "username": "operator",
                "application_password": "app pass 1234",
                "category_id_by_name": {"food-facts": 7},
                "tag_id_by_name": {"kitchen": 11, "food-facts": 13},
                "timeout_seconds": 12,
            }
        ),
        encoding="utf-8",
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
    return approved_draft, prepare_blog_publish_record(
        approved_draft,
        allow_non_pass_quality=True,
        created_at="2026-04-03T12:10:00+00:00",
    )


class WordPressPostStateCliTests(unittest.TestCase):
    def test_wordpress_post_state_cli_dry_run_does_not_mutate_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "wordpress_config.json"
            blog_path = root / "blog_publish_records.jsonl"
            _write_config(config_path)

            _, blog_record = _build_blog_publish_record()
            blog_record.wordpress_post_id = "345"
            blog_record.wordpress_status = "draft_created"
            append_blog_publish_records([blog_record], path=blog_path)

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--blog-publish-id",
                        blog_record.blog_publish_id,
                        "--config-path",
                        str(config_path),
                        "--blog-publish-records-path",
                        str(blog_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            records = read_blog_publish_records(path=blog_path)
            self.assertEqual(len(records), 1)
            self.assertEqual(payload["execution_mode"], "dry_run")
            self.assertEqual(payload["request"]["wordpress_post_id"], "345")
            self.assertFalse(payload["reconciled"])

    def test_wordpress_post_state_cli_execute_without_reconcile_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "wordpress_config.json"
            blog_path = root / "blog_publish_records.jsonl"
            _write_config(config_path)

            _, blog_record = _build_blog_publish_record()
            blog_record.wordpress_post_id = "345"
            blog_record.wordpress_status = "draft_created"
            append_blog_publish_records([blog_record], path=blog_path)

            def _executor(*_args):
                return {
                    "id": 345,
                    "status": "draft",
                    "link": "https://wordpress.example.com/why-this-kitchen-trick-works/",
                    "_response_status_code": 200,
                }

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--blog-publish-id",
                        blog_record.blog_publish_id,
                        "--config-path",
                        str(config_path),
                        "--execute",
                        "--blog-publish-records-path",
                        str(blog_path),
                    ],
                    request_executor=_executor,
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            records = read_blog_publish_records(path=blog_path)
            self.assertEqual(len(records), 1)
            self.assertEqual(payload["execution_result"]["remote_status"], "draft")
            self.assertFalse(payload["reconciled"])

    def test_wordpress_post_state_cli_reconciles_published_state_and_refreshes_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "wordpress_config.json"
            blog_path = root / "blog_publish_records.jsonl"
            social_path = root / "social_package_records.jsonl"
            queue_path = root / "queue_item_records.jsonl"
            mapping_path = root / "blog_facebook_mapping_records.jsonl"
            _write_config(config_path)

            approved_draft, blog_record = _build_blog_publish_record()
            blog_record.wordpress_post_id = "345"
            blog_record.wordpress_status = "draft_created"
            blog_record.wordpress_post_url = "https://wordpress.example.com/why-this-kitchen-trick-works/"
            append_blog_publish_records([blog_record], path=blog_path)

            social_record = prepare_social_package_record(
                approved_draft,
                blog_publish_record=blog_record,
                created_at="2026-04-03T12:15:00+00:00",
            )
            social_record.approval_state = "approved"
            append_social_package_records([social_record], path=social_path)

            def _executor(*_args):
                return {
                    "id": 345,
                    "status": "publish",
                    "link": "https://wordpress.example.com/why-this-kitchen-trick-works/",
                    "date_gmt": "2026-04-04T20:30:00",
                    "_response_status_code": 200,
                }

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--blog-publish-id",
                        blog_record.blog_publish_id,
                        "--config-path",
                        str(config_path),
                        "--execute",
                        "--reconcile-local-state",
                        "--blog-publish-records-path",
                        str(blog_path),
                        "--social-package-records-path",
                        str(social_path),
                        "--queue-item-records-path",
                        str(queue_path),
                        "--mapping-records-path",
                        str(mapping_path),
                    ],
                    request_executor=_executor,
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            latest_blog = load_latest_blog_publish_record(blog_record.blog_publish_id, path=blog_path)
            latest_blog_queue = load_latest_queue_item_for_blog_publish(
                blog_record.blog_publish_id,
                queue_type="blog_publish",
                path=queue_path,
            )
            latest_facebook_queue = load_latest_queue_item_for_blog_publish(
                blog_record.blog_publish_id,
                queue_type="facebook_publish",
                path=queue_path,
            )
            latest_mapping = load_latest_mapping_for_blog_publish(blog_record.blog_publish_id, path=mapping_path)

            self.assertTrue(payload["reconciled"])
            self.assertEqual(payload["reconciled_action"], "published")
            self.assertEqual(latest_blog.wordpress_status, "published")
            self.assertEqual(latest_blog.published_at_blog, "2026-04-04T20:30:00+00:00")
            self.assertEqual(latest_blog_queue.queue_state, "published_blog")
            self.assertEqual(latest_facebook_queue.queue_state, "approved_for_queue")
            self.assertEqual(latest_mapping.mapping_status, "packaged_social_pending")
            self.assertEqual(
                latest_mapping.blog_url,
                "https://wordpress.example.com/why-this-kitchen-trick-works/",
            )

    def test_wordpress_post_state_cli_execute_returns_structured_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "wordpress_config.json"
            blog_path = root / "blog_publish_records.jsonl"
            _write_config(config_path)

            _, blog_record = _build_blog_publish_record()
            blog_record.wordpress_post_id = "345"
            blog_record.wordpress_status = "draft_created"
            append_blog_publish_records([blog_record], path=blog_path)

            def _executor(*_args):
                raise WordPressRestTransportError("dns lookup failed", retryable=True)

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--blog-publish-id",
                        blog_record.blog_publish_id,
                        "--config-path",
                        str(config_path),
                        "--execute",
                        "--blog-publish-records-path",
                        str(blog_path),
                    ],
                    request_executor=_executor,
                )

            self.assertEqual(exit_code, 1)
            payload = json.loads(buffer.getvalue().strip())
            self.assertEqual(payload["transport_outcome"], "failed")
            self.assertEqual(payload["requested_wordpress_post_id"], "345")
            self.assertFalse(payload["reconciled"])


if __name__ == "__main__":
    unittest.main()
