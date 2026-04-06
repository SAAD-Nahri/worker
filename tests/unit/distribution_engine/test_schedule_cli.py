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

from distribution_engine.models import BlogPublishRecord
from distribution_engine.schedule_cli import main
from distribution_engine.storage import append_blog_facebook_mapping_records, append_blog_publish_records, append_queue_item_records
from distribution_engine.workflow import prepare_distribution_linkage_records


def _build_blog_publish_record(blog_publish_id: str) -> BlogPublishRecord:
    return BlogPublishRecord(
        blog_publish_id=blog_publish_id,
        draft_id="draft-schedule-cli",
        source_item_id="source-schedule-cli",
        template_id="blog_food_fact_v1",
        wordpress_title="Why Onion Flavor Changes",
        wordpress_slug="why-onion-flavor-changes",
        wordpress_excerpt="An excerpt about onion flavor changes.",
        wordpress_body_html="<p>Why onion flavor changes.</p>",
        wordpress_category="Food Facts",
        wordpress_tags=["Ingredient Basics"],
        publish_intent="schedule",
        canonical_source_url="https://example.com/onion",
        wordpress_post_id="wp-301",
        wordpress_post_url="https://blog.example.com/onion",
        wordpress_status="draft_created",
        last_publish_attempt_at="2026-04-03T12:20:00+00:00",
        last_publish_result="draft_created",
        created_at="2026-04-03T12:20:00+00:00",
        updated_at="2026-04-03T12:20:00+00:00",
    )


class DistributionScheduleCliTests(unittest.TestCase):
    def test_distribution_schedule_cli_outputs_json_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            blog_path = root / "blog_publish_records.jsonl"
            queue_path = root / "queue_item_records.jsonl"
            mapping_path = root / "blog_facebook_mapping_records.jsonl"

            blog_publish = _build_blog_publish_record("blog-schedule-cli-json")
            blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
                blog_publish,
                created_at="2026-04-03T12:22:00+00:00",
            )
            append_blog_publish_records([blog_publish], path=blog_path)
            append_queue_item_records([blog_queue, facebook_queue], path=queue_path)
            append_blog_facebook_mapping_records([mapping], path=mapping_path)

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--blog-publish-records-path",
                        str(blog_path),
                        "--queue-item-records-path",
                        str(queue_path),
                        "--mapping-records-path",
                        str(mapping_path),
                        "--json",
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue())
            self.assertEqual(payload["summary"]["total_rows"], 1)
            self.assertEqual(payload["rows"][0]["scheduling_signal"], "ready_for_blog_schedule")

    def test_distribution_schedule_cli_outputs_text_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            blog_path = root / "blog_publish_records.jsonl"
            queue_path = root / "queue_item_records.jsonl"
            mapping_path = root / "blog_facebook_mapping_records.jsonl"

            blog_publish = _build_blog_publish_record("blog-schedule-cli-text")
            blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
                blog_publish,
                created_at="2026-04-03T12:22:00+00:00",
            )
            append_blog_publish_records([blog_publish], path=blog_path)
            append_queue_item_records([blog_queue, facebook_queue], path=queue_path)
            append_blog_facebook_mapping_records([mapping], path=mapping_path)

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--blog-publish-records-path",
                        str(blog_path),
                        "--queue-item-records-path",
                        str(queue_path),
                        "--mapping-records-path",
                        str(mapping_path),
                    ]
                )

            output = buffer.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("Distribution schedule summary", output)
            self.assertIn("ready_for_blog_schedule=1", output)
            self.assertIn("blog-schedule-cli-text", output)


if __name__ == "__main__":
    unittest.main()
