from __future__ import annotations

from copy import deepcopy
import sys
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.formatting import format_source_item_to_draft
from content_engine.health import build_draft_health_report
from content_engine.models import AiAssistanceRecord, DraftReviewRecord
from content_engine.storage import append_draft_records, append_draft_review_records
from source_engine.models import SourceItem


def _build_source_item(item_id: str, title: str) -> SourceItem:
    return SourceItem(
        item_id=item_id,
        source_id="src_test",
        source_name="Test Source",
        source_family="food_editorial",
        run_id="run-1",
        source_url=f"https://example.com/{item_id}",
        canonical_url=f"https://example.com/{item_id}",
        discovered_at="2026-04-03T00:00:00+00:00",
        fetched_at="2026-04-03T00:00:00+00:00",
        raw_title=title,
        raw_summary="A short summary about why the kitchen pattern matters.",
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


class DraftHealthTests(unittest.TestCase):
    def test_build_draft_health_report_aggregates_latest_snapshots_and_reviews(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft_path = root / "draft_records.jsonl"
            review_path = root / "draft_reviews.jsonl"

            approved_base = format_source_item_to_draft(
                _build_source_item("item-approved", "Why This Kitchen Trick Works"),
                created_at="2026-04-03T12:00:00+00:00",
            )
            approved_base.quality_gate_status = "pass"
            approved_base.quality_flags = []
            approved_base.derivative_risk_level = "low"
            approved_base.derivative_risk_notes = "Clean enough for approval."
            approved_latest = deepcopy(approved_base)
            approved_latest.approval_state = "approved"
            approved_latest.workflow_state = "reviewed"
            approved_latest.updated_at = "2026-04-03T12:05:00+00:00"
            approved_latest.headline_variants = [
                "The Real Reason This Kitchen Trick Works",
                "What Actually Explains This Kitchen Trick",
            ]
            approved_latest.ai_assistance_log = [
                AiAssistanceRecord(
                    skill_name="generate_headline_variants",
                    target_field="headline_variants",
                    model_label="test-provider",
                    created_at="2026-04-03T12:04:00+00:00",
                )
            ]

            blocked_draft = format_source_item_to_draft(
                _build_source_item("item-blocked", "Why This Cooking Question Matters"),
                created_at="2026-04-03T12:10:00+00:00",
            )
            blocked_draft.quality_gate_status = "blocked"
            blocked_draft.quality_flags = ["derivative_risk_high"]
            blocked_draft.derivative_risk_level = "high"
            blocked_draft.updated_at = "2026-04-03T12:15:00+00:00"

            append_draft_records([approved_base, approved_latest, blocked_draft], path=draft_path)
            append_draft_review_records(
                [
                    DraftReviewRecord(
                        review_id="review-1",
                        draft_id=approved_latest.draft_id,
                        source_item_id=approved_latest.source_item_id,
                        reviewer_label="solo_operator",
                        reviewed_at="2026-04-03T12:06:00+00:00",
                        review_outcome="approved",
                        previous_approval_state="pending_review",
                        updated_approval_state="approved",
                        updated_workflow_state="reviewed",
                        quality_gate_status="pass",
                        derivative_risk_level="low",
                        review_notes=("ready_for_queue",),
                    )
                ],
                path=review_path,
            )

            summary, rows = build_draft_health_report(
                draft_records_path=draft_path,
                draft_reviews_path=review_path,
            )

            self.assertEqual(summary.total_drafts, 2)
            self.assertEqual(summary.quality_gate_counts["pass"], 1)
            self.assertEqual(summary.quality_gate_counts["blocked"], 1)
            self.assertEqual(summary.approval_state_counts["approved"], 1)
            self.assertEqual(summary.routing_action_counts["proceed"], 1)
            self.assertEqual(summary.routing_action_counts["reject_for_v1"], 1)
            self.assertEqual(summary.ai_enriched_drafts, 1)
            self.assertEqual(summary.drafts_with_headline_variants, 1)

            row_by_id = {row.draft_id: row for row in rows}
            self.assertEqual(
                row_by_id[approved_latest.draft_id].operator_signal,
                "approved_ready_for_phase_3",
            )
            self.assertEqual(row_by_id[approved_latest.draft_id].review_count, 1)
            self.assertEqual(row_by_id[blocked_draft.draft_id].operator_signal, "blocked_quality")
            self.assertEqual(row_by_id[approved_latest.draft_id].routing_action, "proceed")
            self.assertEqual(row_by_id[blocked_draft.draft_id].routing_action, "reject_for_v1")
            self.assertIn(("derivative_risk_high", 1), summary.top_quality_flags)
            self.assertIn(("blocked_quality_gate", 1), summary.top_routing_reasons)

    def test_build_draft_health_report_flags_pending_review_states(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft_path = root / "draft_records.jsonl"

            ready_draft = format_source_item_to_draft(
                _build_source_item("item-ready", "Why This Ingredient Works"),
                created_at="2026-04-03T12:20:00+00:00",
            )
            ready_draft.quality_gate_status = "pass"
            ready_draft.quality_flags = []
            ready_draft.derivative_risk_level = "low"
            ready_draft.derivative_risk_notes = "Ready for review."

            flagged_draft = format_source_item_to_draft(
                _build_source_item("item-flagged", "The Secret Reason This Ingredient Works"),
                created_at="2026-04-03T12:25:00+00:00",
            )
            flagged_draft.quality_gate_status = "review_flag"
            flagged_draft.quality_flags = ["anchor_title_mismatch"]

            append_draft_records([ready_draft, flagged_draft], path=draft_path)
            summary, rows = build_draft_health_report(draft_records_path=draft_path)

            self.assertEqual(summary.operator_signal_counts["ready_for_review"], 1)
            self.assertEqual(summary.operator_signal_counts["review_flag_pending"], 1)
            self.assertEqual(summary.routing_action_counts["review_only"], 1)
            self.assertEqual(summary.routing_action_counts["proceed"], 1)
            row_by_id = {row.draft_id: row for row in rows}
            self.assertEqual(row_by_id[ready_draft.draft_id].operator_signal, "ready_for_review")
            self.assertEqual(row_by_id[flagged_draft.draft_id].operator_signal, "review_flag_pending")
            self.assertEqual(row_by_id[ready_draft.draft_id].routing_action, "proceed")
            self.assertEqual(row_by_id[flagged_draft.draft_id].routing_action, "review_only")
            self.assertIn("anchor_title_mismatch", row_by_id[flagged_draft.draft_id].routing_reasons)


if __name__ == "__main__":
    unittest.main()
