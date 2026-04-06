from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.formatting import format_source_item_to_draft
from content_engine.review import record_draft_review
from distribution_engine.facebook import prepare_social_package_record
from distribution_engine.facebook_publish_cli import main
from distribution_engine.storage import (
    append_blog_publish_records,
    append_social_package_records,
    load_latest_facebook_publish_for_social_package,
    load_latest_mapping_for_blog_publish,
    load_latest_queue_item_for_blog_publish,
)
from distribution_engine.wordpress import prepare_blog_publish_record
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-facebook-publish-cli-123456",
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


class FacebookPublishCliTests(unittest.TestCase):
    def test_facebook_publish_cli_records_scheduled_publish_and_refreshes_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            blog_path = root / "blog_publish_records.jsonl"
            social_path = root / "social_package_records.jsonl"
            facebook_publish_path = root / "facebook_publish_records.jsonl"
            queue_path = root / "queue_item_records.jsonl"
            mapping_path = root / "blog_facebook_mapping_records.jsonl"

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
            blog_record.wordpress_post_url = "https://example.com/why-this-kitchen-trick-works"
            blog_record.published_at_blog = "2026-04-03T12:20:00+00:00"
            append_blog_publish_records([blog_record], path=blog_path)
            social_record = prepare_social_package_record(
                approved_draft,
                blog_publish_record=blog_record,
                created_at="2026-04-03T12:25:00+00:00",
            )
            social_record.approval_state = "approved"
            append_social_package_records([social_record], path=social_path)

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--social-package-id",
                        social_record.social_package_id,
                        "--action",
                        "scheduled",
                        "--facebook-post-id",
                        "fb-post-123",
                        "--schedule-mode",
                        "manual",
                        "--scheduled-for-facebook",
                        "2026-04-03T15:00:00+00:00",
                        "--social-package-records-path",
                        str(social_path),
                        "--blog-publish-records-path",
                        str(blog_path),
                        "--facebook-publish-records-path",
                        str(facebook_publish_path),
                        "--queue-item-records-path",
                        str(queue_path),
                        "--mapping-records-path",
                        str(mapping_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            latest_publish = load_latest_facebook_publish_for_social_package(
                social_record.social_package_id,
                path=facebook_publish_path,
            )
            latest_queue = load_latest_queue_item_for_blog_publish(
                blog_record.blog_publish_id,
                queue_type="facebook_publish",
                path=queue_path,
            )
            latest_mapping = load_latest_mapping_for_blog_publish(blog_record.blog_publish_id, path=mapping_path)
            self.assertEqual(payload["publish_status"], "scheduled")
            self.assertEqual(payload["schedule_mode"], "manual")
            self.assertEqual(latest_publish.facebook_post_id, "fb-post-123")
            self.assertEqual(latest_queue.queue_state, "scheduled_facebook")
            self.assertEqual(latest_mapping.mapping_status, "social_queued")

    def test_facebook_publish_cli_requires_error_for_failed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            blog_path = root / "blog_publish_records.jsonl"
            social_path = root / "social_package_records.jsonl"

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
            blog_record.wordpress_post_url = "https://example.com/why-this-kitchen-trick-works"
            blog_record.published_at_blog = "2026-04-03T12:20:00+00:00"
            append_blog_publish_records([blog_record], path=blog_path)
            social_record = prepare_social_package_record(
                approved_draft,
                blog_publish_record=blog_record,
                created_at="2026-04-03T12:25:00+00:00",
            )
            social_record.approval_state = "approved"
            append_social_package_records([social_record], path=social_path)

            with self.assertRaises(SystemExit):
                main(
                    [
                        "--social-package-id",
                        social_record.social_package_id,
                        "--action",
                        "failed",
                        "--social-package-records-path",
                        str(social_path),
                        "--blog-publish-records-path",
                        str(blog_path),
                    ]
                )


if __name__ == "__main__":
    unittest.main()
