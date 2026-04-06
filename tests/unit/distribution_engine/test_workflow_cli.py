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
from content_engine.storage import append_draft_records
from distribution_engine.facebook import prepare_social_package_record
from distribution_engine.storage import (
    append_blog_publish_records,
    append_social_package_records,
    load_latest_mapping_record,
    load_latest_queue_item_for_blog_publish,
)
from distribution_engine.workflow_cli import main
from distribution_engine.wordpress import prepare_blog_publish_record
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-linkage-cli-123456",
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


class DistributionWorkflowCliTests(unittest.TestCase):
    def test_workflow_cli_creates_queue_and_mapping_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft_path = root / "draft_records.jsonl"
            blog_path = root / "blog_publish_records.jsonl"
            social_path = root / "social_package_records.jsonl"
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
            append_draft_records([approved_draft], path=draft_path)
            blog_record = prepare_blog_publish_record(
                approved_draft,
                allow_non_pass_quality=True,
                created_at="2026-04-03T12:10:00+00:00",
            )
            blog_record.wordpress_status = "draft_created"
            blog_record.wordpress_post_id = "wp-123"
            blog_record.wordpress_post_url = "https://example.com/why-this-kitchen-trick-works"
            append_blog_publish_records([blog_record], path=blog_path)
            social_record = prepare_social_package_record(
                approved_draft,
                blog_publish_record=blog_record,
                created_at="2026-04-03T12:15:00+00:00",
            )
            append_social_package_records([social_record], path=social_path)

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--blog-publish-id",
                        blog_record.blog_publish_id,
                        "--social-package-id",
                        social_record.social_package_id,
                        "--blog-publish-records-path",
                        str(blog_path),
                        "--social-package-records-path",
                        str(social_path),
                        "--queue-item-records-path",
                        str(queue_path),
                        "--mapping-records-path",
                        str(mapping_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            self.assertEqual(payload["mapping_status"], "packaged_social_pending")
            latest_blog_queue = load_latest_queue_item_for_blog_publish(
                blog_record.blog_publish_id,
                queue_type="blog_publish",
                path=queue_path,
            )
            latest_mapping = load_latest_mapping_record(payload["mapping_id"], path=mapping_path)
            self.assertEqual(latest_blog_queue.queue_state, "wordpress_draft_created")
            self.assertEqual(latest_mapping.social_package_id, social_record.social_package_id)

    def test_workflow_cli_rejects_duplicate_initial_linkage_without_allow_refresh(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            blog_path = root / "blog_publish_records.jsonl"
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
            append_blog_publish_records([blog_record], path=blog_path)

            with redirect_stdout(io.StringIO()):
                main(
                    [
                        "--blog-publish-id",
                        blog_record.blog_publish_id,
                        "--blog-publish-records-path",
                        str(blog_path),
                        "--queue-item-records-path",
                        str(queue_path),
                        "--mapping-records-path",
                        str(mapping_path),
                    ]
                )

            with self.assertRaises(SystemExit):
                main(
                    [
                        "--blog-publish-id",
                        blog_record.blog_publish_id,
                        "--blog-publish-records-path",
                        str(blog_path),
                        "--queue-item-records-path",
                        str(queue_path),
                        "--mapping-records-path",
                        str(mapping_path),
                    ]
                )


if __name__ == "__main__":
    unittest.main()
