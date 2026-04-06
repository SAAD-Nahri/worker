from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from content_engine.models import DraftRecord, DraftSection
from distribution_engine.models import BlogFacebookMappingRecord, BlogPublishRecord, QueueItemRecord
from source_engine.models import SourceItem
from tracking_engine.chain_history_cli import main


def _write_jsonl(path: Path, records: list[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


class PublishChainHistoryCliTests(unittest.TestCase):
    def test_chain_history_cli_outputs_json_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source_path = base / "source_items.jsonl"
            draft_path = base / "draft_records.jsonl"
            blog_publish_path = base / "blog_publish_records.jsonl"
            queue_path = base / "queue_item_records.jsonl"
            mapping_path = base / "mapping_records.jsonl"

            _write_jsonl(
                source_path,
                [
                    SourceItem(
                        item_id="item-1",
                        source_id="src-1",
                        source_name="Food Source",
                        source_family="editorial_food",
                        run_id="run-1",
                        source_url="https://example.com/story",
                        canonical_url="https://example.com/story",
                        discovered_at="2026-04-03T09:00:00Z",
                        fetched_at="2026-04-03T09:00:00Z",
                        raw_title="Why Sourdough Bread Tastes Different",
                        raw_summary="Summary",
                        raw_body_text="Body",
                        author_name="Editor",
                        published_at="2026-04-02T10:00:00Z",
                        topical_label="food_fact",
                        freshness_label="evergreen",
                        normalization_status="normalized",
                        dedupe_status="unique",
                        template_suggestion="blog_food_fact_v1",
                    )
                ],
            )
            _write_jsonl(
                draft_path,
                [
                    DraftRecord(
                        draft_id="draft-1",
                        workflow_state="reviewed",
                        approval_state="approved",
                        language="en",
                        source_item_id="item-1",
                        source_id="src-1",
                        source_url="https://example.com/story",
                        source_domain="example.com",
                        source_title="Why Sourdough Bread Tastes Different",
                        source_published_at="2026-04-02T10:00:00Z",
                        template_id="blog_food_fact_v1",
                        template_family="food_fact_article",
                        template_version="v1",
                        category="Food Facts",
                        tag_candidates=["bread"],
                        headline_selected="Why Sourdough Bread Tastes Different",
                        sections=[DraftSection(section_key="direct_answer", section_label="Direct Answer", position=1, body_blocks=["Fermentation matters."])],
                        quality_gate_status="pass",
                        derivative_risk_level="low",
                        created_at="2026-04-03T09:05:00Z",
                        updated_at="2026-04-03T09:10:00Z",
                    )
                ],
            )
            _write_jsonl(
                blog_publish_path,
                [
                    BlogPublishRecord(
                        blog_publish_id="blog-1",
                        draft_id="draft-1",
                        source_item_id="item-1",
                        template_id="blog_food_fact_v1",
                        wordpress_title="Why Sourdough Bread Tastes Different",
                        wordpress_slug="why-sourdough-bread-tastes-different",
                        wordpress_excerpt="Excerpt",
                        wordpress_body_html="<p>Body</p>",
                        wordpress_category="Food Facts",
                        wordpress_tags=["bread"],
                        canonical_source_url="https://example.com/story",
                        wordpress_status="draft_created",
                        wordpress_post_id="101",
                        created_at="2026-04-03T09:20:00Z",
                        updated_at="2026-04-03T09:25:00Z",
                    )
                ],
            )
            _write_jsonl(
                queue_path,
                [
                    QueueItemRecord(
                        queue_item_id="blogq-1",
                        queue_type="blog_publish",
                        draft_id="draft-1",
                        blog_publish_id="blog-1",
                        social_package_id=None,
                        queue_state="wordpress_draft_created",
                        approval_state="approved",
                        created_at="2026-04-03T09:20:00Z",
                        updated_at="2026-04-03T09:25:00Z",
                        last_transition_at="2026-04-03T09:25:00Z",
                    ),
                    QueueItemRecord(
                        queue_item_id="fbq-1",
                        queue_type="facebook_publish",
                        draft_id="draft-1",
                        blog_publish_id="blog-1",
                        social_package_id=None,
                        queue_state="social_packaging_pending",
                        approval_state="pending_review",
                        created_at="2026-04-03T09:20:00Z",
                        updated_at="2026-04-03T09:25:00Z",
                        last_transition_at="2026-04-03T09:25:00Z",
                    ),
                ],
            )
            _write_jsonl(
                mapping_path,
                [
                    BlogFacebookMappingRecord(
                        mapping_id="map-1",
                        source_item_id="item-1",
                        draft_id="draft-1",
                        blog_publish_id="blog-1",
                        social_package_id=None,
                        facebook_publish_id=None,
                        selected_blog_title="Why Sourdough Bread Tastes Different",
                        blog_url=None,
                        mapping_status="blog_only",
                        created_at="2026-04-03T09:25:00Z",
                        updated_at="2026-04-03T09:25:00Z",
                    )
                ],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "--source-items-path",
                        str(source_path),
                        "--draft-records-path",
                        str(draft_path),
                        "--blog-publish-records-path",
                        str(blog_publish_path),
                        "--queue-item-records-path",
                        str(queue_path),
                        "--mapping-records-path",
                        str(mapping_path),
                        "--json",
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["summary"]["total_chains"], 1)
            self.assertEqual(payload["snapshots"][0]["chain_id"], "blog-1")
            self.assertEqual(payload["snapshots"][0]["chain_status"], "social_packaging_pending")

    def test_chain_history_cli_outputs_exception_view_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source_path = base / "source_items.jsonl"
            draft_path = base / "draft_records.jsonl"
            blog_publish_path = base / "blog_publish_records.jsonl"
            queue_path = base / "queue_item_records.jsonl"
            mapping_path = base / "mapping_records.jsonl"

            _write_jsonl(
                source_path,
                [
                    SourceItem(
                        item_id="item-1",
                        source_id="src-1",
                        source_name="Food Source",
                        source_family="editorial_food",
                        run_id="run-1",
                        source_url="https://example.com/story",
                        canonical_url="https://example.com/story",
                        discovered_at="2026-04-03T09:00:00Z",
                        fetched_at="2026-04-03T09:00:00Z",
                        raw_title="Why Sourdough Bread Tastes Different",
                        raw_summary="Summary",
                        raw_body_text="Body",
                        author_name="Editor",
                        published_at="2026-04-02T10:00:00Z",
                        topical_label="food_fact",
                        freshness_label="evergreen",
                        normalization_status="normalized",
                        dedupe_status="unique",
                        template_suggestion="blog_food_fact_v1",
                    )
                ],
            )
            _write_jsonl(
                draft_path,
                [
                    DraftRecord(
                        draft_id="draft-1",
                        workflow_state="reviewed",
                        approval_state="approved",
                        language="en",
                        source_item_id="item-1",
                        source_id="src-1",
                        source_url="https://example.com/story",
                        source_domain="example.com",
                        source_title="Why Sourdough Bread Tastes Different",
                        source_published_at="2026-04-02T10:00:00Z",
                        template_id="blog_food_fact_v1",
                        template_family="food_fact_article",
                        template_version="v1",
                        category="Food Facts",
                        tag_candidates=["bread"],
                        headline_selected="Why Sourdough Bread Tastes Different",
                        sections=[DraftSection(section_key="direct_answer", section_label="Direct Answer", position=1, body_blocks=["Fermentation matters."])],
                        quality_gate_status="pass",
                        derivative_risk_level="low",
                        created_at="2026-04-03T09:05:00Z",
                        updated_at="2026-04-03T09:10:00Z",
                    )
                ],
            )
            _write_jsonl(
                blog_publish_path,
                [
                    BlogPublishRecord(
                        blog_publish_id="blog-1",
                        draft_id="draft-1",
                        source_item_id="item-1",
                        template_id="blog_food_fact_v1",
                        wordpress_title="Why Sourdough Bread Tastes Different",
                        wordpress_slug="why-sourdough-bread-tastes-different",
                        wordpress_excerpt="Excerpt",
                        wordpress_body_html="<p>Body</p>",
                        wordpress_category="Food Facts",
                        wordpress_tags=["bread"],
                        canonical_source_url="https://example.com/story",
                        wordpress_status="failed",
                        last_error="transport_error",
                        created_at="2026-04-03T09:20:00Z",
                        updated_at="2026-04-03T09:25:00Z",
                    )
                ],
            )
            _write_jsonl(
                queue_path,
                [
                    QueueItemRecord(
                        queue_item_id="blogq-1",
                        queue_type="blog_publish",
                        draft_id="draft-1",
                        blog_publish_id="blog-1",
                        social_package_id=None,
                        queue_state="blog_publish_failed",
                        approval_state="approved",
                        last_error="transport_error",
                        created_at="2026-04-03T09:20:00Z",
                        updated_at="2026-04-03T09:25:00Z",
                        last_transition_at="2026-04-03T09:25:00Z",
                    ),
                    QueueItemRecord(
                        queue_item_id="fbq-1",
                        queue_type="facebook_publish",
                        draft_id="draft-1",
                        blog_publish_id="blog-1",
                        social_package_id=None,
                        queue_state="social_packaging_pending",
                        approval_state="pending_review",
                        created_at="2026-04-03T09:20:00Z",
                        updated_at="2026-04-03T09:25:00Z",
                        last_transition_at="2026-04-03T09:25:00Z",
                    ),
                ],
            )
            _write_jsonl(
                mapping_path,
                [
                    BlogFacebookMappingRecord(
                        mapping_id="map-1",
                        source_item_id="item-1",
                        draft_id="draft-1",
                        blog_publish_id="blog-1",
                        social_package_id=None,
                        facebook_publish_id=None,
                        selected_blog_title="Why Sourdough Bread Tastes Different",
                        blog_url=None,
                        mapping_status="blog_only",
                        created_at="2026-04-03T09:25:00Z",
                        updated_at="2026-04-03T09:25:00Z",
                    )
                ],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "--source-items-path",
                        str(source_path),
                        "--draft-records-path",
                        str(draft_path),
                        "--blog-publish-records-path",
                        str(blog_publish_path),
                        "--queue-item-records-path",
                        str(queue_path),
                        "--mapping-records-path",
                        str(mapping_path),
                        "--view",
                        "exceptions",
                        "--json",
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["summary"]["total_exception_chains"], 1)
            self.assertEqual(payload["rows"][0]["chain_status"], "blog_publish_failed")
            self.assertIn("blog_publish_failed", payload["rows"][0]["exception_reasons"])

    def test_chain_history_cli_can_record_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source_path = base / "source_items.jsonl"
            draft_path = base / "draft_records.jsonl"
            blog_publish_path = base / "blog_publish_records.jsonl"
            queue_path = base / "queue_item_records.jsonl"
            mapping_path = base / "mapping_records.jsonl"
            audit_path = base / "tracking_audit_records.jsonl"

            _write_jsonl(
                source_path,
                [
                    SourceItem(
                        item_id="item-1",
                        source_id="src-1",
                        source_name="Food Source",
                        source_family="editorial_food",
                        run_id="run-1",
                        source_url="https://example.com/story",
                        canonical_url="https://example.com/story",
                        discovered_at="2026-04-03T09:00:00Z",
                        fetched_at="2026-04-03T09:00:00Z",
                        raw_title="Why Sourdough Bread Tastes Different",
                        raw_summary="Summary",
                        raw_body_text="Body",
                        author_name="Editor",
                        published_at="2026-04-02T10:00:00Z",
                        topical_label="food_fact",
                        freshness_label="evergreen",
                        normalization_status="normalized",
                        dedupe_status="unique",
                        template_suggestion="blog_food_fact_v1",
                    )
                ],
            )
            _write_jsonl(
                draft_path,
                [
                    DraftRecord(
                        draft_id="draft-1",
                        workflow_state="reviewed",
                        approval_state="approved",
                        language="en",
                        source_item_id="item-1",
                        source_id="src-1",
                        source_url="https://example.com/story",
                        source_domain="example.com",
                        source_title="Why Sourdough Bread Tastes Different",
                        source_published_at="2026-04-02T10:00:00Z",
                        template_id="blog_food_fact_v1",
                        template_family="food_fact_article",
                        template_version="v1",
                        category="Food Facts",
                        tag_candidates=["bread"],
                        headline_selected="Why Sourdough Bread Tastes Different",
                        sections=[DraftSection(section_key="direct_answer", section_label="Direct Answer", position=1, body_blocks=["Fermentation matters."])],
                        quality_gate_status="pass",
                        derivative_risk_level="low",
                        created_at="2026-04-03T09:05:00Z",
                        updated_at="2026-04-03T09:10:00Z",
                    )
                ],
            )
            _write_jsonl(
                blog_publish_path,
                [
                    BlogPublishRecord(
                        blog_publish_id="blog-1",
                        draft_id="draft-1",
                        source_item_id="item-1",
                        template_id="blog_food_fact_v1",
                        wordpress_title="Why Sourdough Bread Tastes Different",
                        wordpress_slug="why-sourdough-bread-tastes-different",
                        wordpress_excerpt="Excerpt",
                        wordpress_body_html="<p>Body</p>",
                        wordpress_category="Food Facts",
                        wordpress_tags=["bread"],
                        canonical_source_url="https://example.com/story",
                        wordpress_status="draft_created",
                        wordpress_post_id="101",
                        created_at="2026-04-03T09:20:00Z",
                        updated_at="2026-04-03T09:25:00Z",
                    )
                ],
            )
            _write_jsonl(
                queue_path,
                [
                    QueueItemRecord(
                        queue_item_id="blogq-1",
                        queue_type="blog_publish",
                        draft_id="draft-1",
                        blog_publish_id="blog-1",
                        social_package_id=None,
                        queue_state="wordpress_draft_created",
                        approval_state="approved",
                        created_at="2026-04-03T09:20:00Z",
                        updated_at="2026-04-03T09:25:00Z",
                        last_transition_at="2026-04-03T09:25:00Z",
                    ),
                    QueueItemRecord(
                        queue_item_id="fbq-1",
                        queue_type="facebook_publish",
                        draft_id="draft-1",
                        blog_publish_id="blog-1",
                        social_package_id=None,
                        queue_state="social_packaging_pending",
                        approval_state="pending_review",
                        created_at="2026-04-03T09:20:00Z",
                        updated_at="2026-04-03T09:25:00Z",
                        last_transition_at="2026-04-03T09:25:00Z",
                    ),
                ],
            )
            _write_jsonl(
                mapping_path,
                [
                    BlogFacebookMappingRecord(
                        mapping_id="map-1",
                        source_item_id="item-1",
                        draft_id="draft-1",
                        blog_publish_id="blog-1",
                        social_package_id=None,
                        facebook_publish_id=None,
                        selected_blog_title="Why Sourdough Bread Tastes Different",
                        blog_url=None,
                        mapping_status="blog_only",
                        created_at="2026-04-03T09:25:00Z",
                        updated_at="2026-04-03T09:25:00Z",
                    )
                ],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "--source-items-path",
                        str(source_path),
                        "--draft-records-path",
                        str(draft_path),
                        "--blog-publish-records-path",
                        str(blog_publish_path),
                        "--queue-item-records-path",
                        str(queue_path),
                        "--mapping-records-path",
                        str(mapping_path),
                        "--record-audit",
                        "--audit-records-path",
                        str(audit_path),
                        "--json",
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertIn("audit_record", payload)
            self.assertEqual(payload["audit_record"]["event_type"], "normalization_run")


if __name__ == "__main__":
    unittest.main()
