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

from distribution_engine.health_cli import main
from distribution_engine.models import BlogPublishRecord, SocialPackageRecord
from distribution_engine.storage import (
    append_blog_facebook_mapping_records,
    append_blog_publish_records,
    append_queue_item_records,
    append_social_package_records,
)
from distribution_engine.workflow import prepare_distribution_linkage_records


def _build_blog_publish_record(blog_publish_id: str) -> BlogPublishRecord:
    return BlogPublishRecord(
        blog_publish_id=blog_publish_id,
        draft_id="draft-health-cli",
        source_item_id="source-health-cli",
        template_id="blog_food_fact_v1",
        wordpress_title="Why Onion Flavor Changes",
        wordpress_slug="why-onion-flavor-changes",
        wordpress_excerpt="An excerpt about onion flavor changes.",
        wordpress_body_html="<p>Why onion flavor changes.</p>",
        wordpress_category="Food Facts",
        wordpress_tags=["Ingredient Basics"],
        publish_intent="draft",
        canonical_source_url="https://example.com/onion",
        wordpress_post_id="wp-301",
        wordpress_post_url="https://blog.example.com/onion",
        wordpress_status="published",
        published_at_blog="2026-04-03T12:20:00+00:00",
        last_publish_attempt_at="2026-04-03T12:20:00+00:00",
        last_publish_result="published",
        created_at="2026-04-03T12:20:00+00:00",
        updated_at="2026-04-03T12:20:00+00:00",
    )


def _build_social_package_record(blog_publish_id: str) -> SocialPackageRecord:
    return SocialPackageRecord(
        social_package_id="social-health-cli",
        draft_id="draft-health-cli",
        blog_publish_id=blog_publish_id,
        package_template_id="fb_curiosity_hook_v1",
        comment_template_id="fb_comment_link_line_v1",
        hook_text="Why onions taste different when cooked",
        caption_text="A short caption aligned to the blog.",
        comment_cta_text="Read the full explanation on the blog.",
        target_destination="facebook_page",
        approval_state="approved",
        blog_url="https://blog.example.com/onion",
        selected_variant_label="primary",
        created_at="2026-04-03T12:21:00+00:00",
        updated_at="2026-04-03T12:21:00+00:00",
    )


class DistributionHealthCliTests(unittest.TestCase):
    def test_distribution_health_cli_outputs_json_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            blog_path = root / "blog_publish_records.jsonl"
            social_path = root / "social_package_records.jsonl"
            queue_path = root / "queue_item_records.jsonl"
            mapping_path = root / "blog_facebook_mapping_records.jsonl"

            blog_publish = _build_blog_publish_record("blog-health-cli")
            social_package = _build_social_package_record(blog_publish.blog_publish_id)
            blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
                blog_publish,
                social_package_record=social_package,
                created_at="2026-04-03T12:22:00+00:00",
            )
            append_blog_publish_records([blog_publish], path=blog_path)
            append_social_package_records([social_package], path=social_path)
            append_queue_item_records([blog_queue, facebook_queue], path=queue_path)
            append_blog_facebook_mapping_records([mapping], path=mapping_path)

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--blog-publish-records-path",
                        str(blog_path),
                        "--social-package-records-path",
                        str(social_path),
                        "--queue-item-records-path",
                        str(queue_path),
                        "--mapping-records-path",
                        str(mapping_path),
                        "--json",
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue())
            self.assertEqual(payload["summary"]["total_blog_publish_chains"], 1)
            self.assertEqual(payload["summary"]["rows_with_consistency_issues"], 0)
            self.assertEqual(payload["summary"]["rows_with_schedule_alerts"], 0)
            self.assertEqual(payload["rows"][0]["blog_publish_id"], blog_publish.blog_publish_id)
            self.assertEqual(payload["rows"][0]["operator_signal"], "ready_for_facebook_publish")

    def test_distribution_health_cli_outputs_text_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            blog_path = root / "blog_publish_records.jsonl"
            queue_path = root / "queue_item_records.jsonl"
            mapping_path = root / "blog_facebook_mapping_records.jsonl"

            blog_publish = _build_blog_publish_record("blog-health-cli-text")
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
            self.assertIn("Distribution health summary", output)
            self.assertIn("Coverage: social_packages=0/1 remote_wordpress_post=1/1 confirmed_blog_url=1/1 facebook_post_ids=0/1", output)
            self.assertIn("Operator alerts: consistency_issue_rows=0 schedule_alert_rows=0", output)
            self.assertIn("social_packaging_pending", output)


if __name__ == "__main__":
    unittest.main()
