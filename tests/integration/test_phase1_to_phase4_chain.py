from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from content_engine.formatting import format_source_item_to_draft
from content_engine.review import record_draft_review
from distribution_engine.facebook import prepare_social_package_record
from distribution_engine.facebook_publish_updates import record_facebook_publish_update
from distribution_engine.health import build_distribution_health_report
from distribution_engine.publish_updates import record_blog_publish_update
from distribution_engine.review import record_social_package_review
from distribution_engine.workflow import prepare_distribution_linkage_records
from distribution_engine.wordpress import prepare_blog_publish_record
from source_engine.models import SourceItem
from tracking_engine.audit import build_tracking_audit_report, record_tracking_normalization_run
from tracking_engine.chain_history import build_publish_chain_history_report
from tracking_engine.reporting import build_publish_exception_report


def _write_jsonl(path: Path, records: list[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            payload = record.to_dict() if hasattr(record, "to_dict") else record
            handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-int-chain-1",
        source_id="src_integration",
        source_name="Integration Source",
        source_family="editorial_food",
        run_id="run-int-1",
        source_url="https://example.com/sourdough",
        canonical_url="https://example.com/sourdough",
        discovered_at="2026-04-03T09:00:00+00:00",
        fetched_at="2026-04-03T09:00:00+00:00",
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
            "For everyday readers, the useful takeaway is simple: sourdough tastes different because time, fermentation, and microbial activity all shape the final loaf. "
            "Once those factors are understood, the flavor difference stops feeling mysterious and starts feeling predictable."
        ),
        author_name="Editor",
        published_at="2026-04-02T10:00:00+00:00",
        topical_label="food_fact",
        freshness_label="evergreen",
        normalization_status="normalized",
        dedupe_status="unique",
        quality_flags=[],
        template_suggestion="food_fact_article",
    )


class Phase1ToPhase4ChainSmokeTests(unittest.TestCase):
    def test_full_chain_connects_from_source_to_tracking_and_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            source_path = base / "source_items.jsonl"
            draft_path = base / "draft_records.jsonl"
            draft_review_path = base / "draft_reviews.jsonl"
            blog_publish_path = base / "blog_publish_records.jsonl"
            social_package_path = base / "social_package_records.jsonl"
            social_review_path = base / "social_package_reviews.jsonl"
            facebook_publish_path = base / "facebook_publish_records.jsonl"
            queue_path = base / "queue_item_records.jsonl"
            mapping_path = base / "blog_facebook_mapping_records.jsonl"
            audit_path = base / "tracking_audit_records.jsonl"

            source_item = _build_source_item()
            draft = format_source_item_to_draft(source_item, created_at="2026-04-03T09:10:00+00:00")
            self.assertEqual(draft.quality_gate_status, "pass")

            approved_draft, draft_review = record_draft_review(
                draft,
                review_outcome="approved",
                review_notes=["ready_for_distribution"],
                reviewer_label="integration_smoke",
                reviewed_at="2026-04-03T09:15:00+00:00",
            )

            blog_prepared = prepare_blog_publish_record(
                approved_draft,
                publish_intent="draft",
                created_at="2026-04-03T09:20:00+00:00",
            )
            blog_published = record_blog_publish_update(
                blog_prepared,
                update_action="published",
                attempted_at="2026-04-03T09:30:00+00:00",
                wordpress_post_id="wp-101",
                wordpress_post_url="https://blog.example.com/why-sourdough-bread-tastes-different",
                published_at_blog="2026-04-03T09:30:00+00:00",
            )

            social_package = prepare_social_package_record(
                approved_draft,
                blog_publish_record=blog_published,
                created_at="2026-04-03T09:35:00+00:00",
            )
            approved_social_package, social_review = record_social_package_review(
                social_package,
                review_outcome="approved",
                review_notes=["hook_matches_blog"],
                reviewer_label="integration_smoke",
                reviewed_at="2026-04-03T09:37:00+00:00",
            )

            facebook_publish = record_facebook_publish_update(
                approved_social_package,
                blog_published,
                update_action="published",
                attempted_at="2026-04-03T09:45:00+00:00",
                facebook_post_id="fb-post-555",
                published_at_facebook="2026-04-03T09:45:00+00:00",
            )

            blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
                blog_published,
                social_package_record=approved_social_package,
                facebook_publish_record=facebook_publish,
                created_at="2026-04-03T09:46:00+00:00",
            )

            _write_jsonl(source_path, [source_item])
            _write_jsonl(draft_path, [approved_draft])
            _write_jsonl(draft_review_path, [draft_review])
            _write_jsonl(blog_publish_path, [blog_published])
            _write_jsonl(social_package_path, [approved_social_package])
            _write_jsonl(social_review_path, [social_review])
            _write_jsonl(facebook_publish_path, [facebook_publish])
            _write_jsonl(queue_path, [blog_queue, facebook_queue])
            _write_jsonl(mapping_path, [mapping])

            distribution_summary, distribution_rows = build_distribution_health_report(
                blog_publish_records_path=blog_publish_path,
                social_package_records_path=social_package_path,
                social_package_reviews_path=social_review_path,
                facebook_publish_records_path=facebook_publish_path,
                queue_item_records_path=queue_path,
                mapping_records_path=mapping_path,
            )

            self.assertEqual(distribution_summary.total_blog_publish_chains, 1)
            self.assertEqual(distribution_summary.operator_signal_counts["published_facebook"], 1)
            self.assertEqual(distribution_summary.rows_with_consistency_issues, 0)
            distribution_row = distribution_rows[0]
            self.assertEqual(distribution_row.blog_queue_state, "published_blog")
            self.assertEqual(distribution_row.facebook_queue_state, "published_facebook")
            self.assertEqual(distribution_row.mapping_status, "social_published")
            self.assertTrue(distribution_row.has_confirmed_blog_url)
            self.assertTrue(distribution_row.has_facebook_post_id)

            history_summary, snapshots = build_publish_chain_history_report(
                source_items_path=source_path,
                draft_records_path=draft_path,
                draft_reviews_path=draft_review_path,
                blog_publish_records_path=blog_publish_path,
                social_package_records_path=social_package_path,
                social_package_reviews_path=social_review_path,
                facebook_publish_records_path=facebook_publish_path,
                queue_item_records_path=queue_path,
                mapping_records_path=mapping_path,
                snapshot_generated_at="2026-04-03T09:50:00Z",
            )

            self.assertEqual(history_summary.total_chains, 1)
            self.assertEqual(history_summary.chains_with_social_package, 1)
            self.assertEqual(history_summary.chains_with_facebook_publish, 1)
            self.assertEqual(history_summary.chain_status_counts["published_facebook"], 1)
            snapshot = snapshots[0]
            self.assertEqual(snapshot.source_item_id, source_item.item_id)
            self.assertEqual(snapshot.blog_publish_id, blog_published.blog_publish_id)
            self.assertEqual(snapshot.social_package_id, approved_social_package.social_package_id)
            self.assertEqual(snapshot.facebook_publish_id, facebook_publish.facebook_publish_id)
            self.assertEqual(snapshot.selected_blog_title, blog_published.wordpress_title)
            self.assertEqual(snapshot.selected_hook_text, approved_social_package.hook_text)
            self.assertEqual(snapshot.selected_caption_text, approved_social_package.caption_text)
            self.assertEqual(snapshot.selected_comment_cta_text, approved_social_package.comment_cta_text)
            self.assertEqual(snapshot.chain_status, "published_facebook")
            self.assertFalse(snapshot.consistency_issues)
            self.assertFalse(snapshot.schedule_alerts)

            exception_summary, exception_rows = build_publish_exception_report(snapshots)
            self.assertEqual(exception_summary.total_exception_chains, 0)
            self.assertEqual(exception_rows, [])

            audit_record = record_tracking_normalization_run(
                actor_label="integration_smoke",
                view_name="all",
                history_summary=history_summary,
                exception_summary=exception_summary,
                audit_records_path=audit_path,
                event_timestamp="2026-04-03T09:55:00Z",
            )
            audit_summary, audit_records = build_tracking_audit_report(audit_path)

            self.assertEqual(audit_summary.total_events, 1)
            self.assertEqual(audit_summary.normalization_run_count, 1)
            self.assertEqual(audit_records[0].event_id, audit_record.event_id)
            self.assertEqual(audit_records[0].event_status, "success")
            self.assertEqual(audit_records[0].total_chains, 1)


if __name__ == "__main__":
    unittest.main()
