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
from distribution_engine.facebook_transport import FacebookGraphTransportError
from distribution_engine.facebook_transport_cli import main
from distribution_engine.storage import (
    append_blog_publish_records,
    append_social_package_records,
    load_latest_facebook_publish_for_social_package,
    load_latest_mapping_for_blog_publish,
    load_latest_queue_item_for_blog_publish,
    read_facebook_publish_records,
)
from distribution_engine.wordpress import prepare_blog_publish_record
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-facebook-transport-cli-123456",
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
                "page_id": "123456789",
                "page_access_token": "page-token-123",
                "api_version": "v24.0",
                "timeout_seconds": 15,
            }
        ),
        encoding="utf-8",
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
    return blog_record, social_record


class FacebookTransportCliTests(unittest.TestCase):
    def test_facebook_transport_cli_dry_run_does_not_mutate_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "facebook_graph_config.json"
            blog_path = root / "blog_publish_records.jsonl"
            social_path = root / "social_package_records.jsonl"
            _write_config(config_path)

            blog_record, social_record = _build_social_inputs()
            append_blog_publish_records([blog_record], path=blog_path)
            append_social_package_records([social_record], path=social_path)

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--social-package-id",
                        social_record.social_package_id,
                        "--action",
                        "published",
                        "--config-path",
                        str(config_path),
                        "--social-package-records-path",
                        str(social_path),
                        "--blog-publish-records-path",
                        str(blog_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            records = read_facebook_publish_records(path=root / "facebook_publish_records.jsonl")
            self.assertEqual(len(records), 0)
            self.assertEqual(payload["execution_mode"], "dry_run")
            self.assertEqual(payload["request"]["form_fields"]["link"], blog_record.wordpress_post_url)

    def test_facebook_transport_cli_execute_published_appends_success_and_refreshes_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "facebook_graph_config.json"
            blog_path = root / "blog_publish_records.jsonl"
            social_path = root / "social_package_records.jsonl"
            facebook_path = root / "facebook_publish_records.jsonl"
            queue_path = root / "queue_item_records.jsonl"
            mapping_path = root / "blog_facebook_mapping_records.jsonl"
            _write_config(config_path)

            blog_record, social_record = _build_social_inputs()
            append_blog_publish_records([blog_record], path=blog_path)
            append_social_package_records([social_record], path=social_path)

            def _executor(*_args):
                return {"id": "pagepost-123", "_response_status_code": 200}

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--social-package-id",
                        social_record.social_package_id,
                        "--action",
                        "published",
                        "--config-path",
                        str(config_path),
                        "--execute",
                        "--social-package-records-path",
                        str(social_path),
                        "--blog-publish-records-path",
                        str(blog_path),
                        "--facebook-publish-records-path",
                        str(facebook_path),
                        "--queue-item-records-path",
                        str(queue_path),
                        "--mapping-records-path",
                        str(mapping_path),
                    ],
                    request_executor=_executor,
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            latest_publish = load_latest_facebook_publish_for_social_package(
                social_record.social_package_id,
                path=facebook_path,
            )
            latest_queue = load_latest_queue_item_for_blog_publish(
                blog_record.blog_publish_id,
                queue_type="facebook_publish",
                path=queue_path,
            )
            latest_mapping = load_latest_mapping_for_blog_publish(blog_record.blog_publish_id, path=mapping_path)
            self.assertEqual(payload["transport_outcome"], "success")
            self.assertEqual(latest_publish.publish_status, "published")
            self.assertEqual(latest_publish.facebook_post_id, "pagepost-123")
            self.assertEqual(latest_queue.queue_state, "published_facebook")
            self.assertEqual(latest_mapping.mapping_status, "social_published")

    def test_facebook_transport_cli_execute_schedule_appends_success(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "facebook_graph_config.json"
            blog_path = root / "blog_publish_records.jsonl"
            social_path = root / "social_package_records.jsonl"
            facebook_path = root / "facebook_publish_records.jsonl"
            queue_path = root / "queue_item_records.jsonl"
            mapping_path = root / "blog_facebook_mapping_records.jsonl"
            _write_config(config_path)

            blog_record, social_record = _build_social_inputs()
            blog_record.wordpress_status = "scheduled"
            blog_record.scheduled_for_blog = "2026-04-04T12:00:00+00:00"
            append_blog_publish_records([blog_record], path=blog_path)
            append_social_package_records([social_record], path=social_path)

            def _executor(*_args):
                return {"id": "pagepost-999", "_response_status_code": 200}

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--social-package-id",
                        social_record.social_package_id,
                        "--action",
                        "scheduled",
                        "--scheduled-for-facebook",
                        "2026-04-04T13:00:00+00:00",
                        "--schedule-mode",
                        "manual",
                        "--config-path",
                        str(config_path),
                        "--execute",
                        "--social-package-records-path",
                        str(social_path),
                        "--blog-publish-records-path",
                        str(blog_path),
                        "--facebook-publish-records-path",
                        str(facebook_path),
                        "--queue-item-records-path",
                        str(queue_path),
                        "--mapping-records-path",
                        str(mapping_path),
                    ],
                    request_executor=_executor,
                )

            self.assertEqual(exit_code, 0)
            latest_publish = load_latest_facebook_publish_for_social_package(
                social_record.social_package_id,
                path=facebook_path,
            )
            latest_queue = load_latest_queue_item_for_blog_publish(
                blog_record.blog_publish_id,
                queue_type="facebook_publish",
                path=queue_path,
            )
            self.assertEqual(latest_publish.publish_status, "scheduled")
            self.assertEqual(latest_publish.schedule_mode, "manual")
            self.assertEqual(latest_queue.queue_state, "scheduled_facebook")

    def test_facebook_transport_cli_execute_records_failed_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "facebook_graph_config.json"
            blog_path = root / "blog_publish_records.jsonl"
            social_path = root / "social_package_records.jsonl"
            facebook_path = root / "facebook_publish_records.jsonl"
            queue_path = root / "queue_item_records.jsonl"
            mapping_path = root / "blog_facebook_mapping_records.jsonl"
            _write_config(config_path)

            blog_record, social_record = _build_social_inputs()
            append_blog_publish_records([blog_record], path=blog_path)
            append_social_package_records([social_record], path=social_path)

            def _executor(*_args):
                raise FacebookGraphTransportError("page token expired")

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--social-package-id",
                        social_record.social_package_id,
                        "--action",
                        "published",
                        "--config-path",
                        str(config_path),
                        "--execute",
                        "--social-package-records-path",
                        str(social_path),
                        "--blog-publish-records-path",
                        str(blog_path),
                        "--facebook-publish-records-path",
                        str(facebook_path),
                        "--queue-item-records-path",
                        str(queue_path),
                        "--mapping-records-path",
                        str(mapping_path),
                    ],
                    request_executor=_executor,
                )

            self.assertEqual(exit_code, 1)
            payload = json.loads(buffer.getvalue().strip())
            latest_publish = load_latest_facebook_publish_for_social_package(
                social_record.social_package_id,
                path=facebook_path,
            )
            latest_queue = load_latest_queue_item_for_blog_publish(
                blog_record.blog_publish_id,
                queue_type="facebook_publish",
                path=queue_path,
            )
            self.assertEqual(payload["transport_outcome"], "failed")
            self.assertEqual(latest_publish.publish_status, "failed")
            self.assertEqual(latest_publish.last_error, "page token expired")
            self.assertEqual(latest_queue.queue_state, "facebook_publish_failed")


if __name__ == "__main__":
    unittest.main()
