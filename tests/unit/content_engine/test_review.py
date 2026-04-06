from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.drafts import create_draft_skeleton
from content_engine.review import record_draft_review
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-review-123456",
        source_id="src_test",
        source_name="Test Source",
        source_family="food_editorial",
        run_id="run-1",
        source_url="https://example.com/story",
        canonical_url="https://example.com/story",
        discovered_at="2026-04-03T00:00:00+00:00",
        fetched_at="2026-04-03T00:00:00+00:00",
        raw_title="Why This Kitchen Trick Works",
        raw_summary="Short summary",
        raw_body_text="Useful body text for a source item that is long enough to matter in review tests.",
        author_name=None,
        published_at="2026-04-01T00:00:00+00:00",
        topical_label="food_explainer",
        freshness_label="fresh",
        normalization_status="normalized",
        dedupe_status="unique",
        quality_flags=[],
        template_suggestion="food_fact_article",
    )


class DraftReviewTests(unittest.TestCase):
    def test_record_draft_review_approves_pass_draft(self) -> None:
        draft = create_draft_skeleton(_build_source_item(), created_at="2026-04-03T12:00:00+00:00")
        draft.quality_gate_status = "pass"
        draft.derivative_risk_level = "low"

        updated_draft, review_record = record_draft_review(
            draft,
            review_outcome="approved",
            review_notes=["ready_for_queue"],
            reviewer_label="operator_one",
            reviewed_at="2026-04-03T13:00:00+00:00",
        )

        self.assertEqual(updated_draft.approval_state, "approved")
        self.assertEqual(updated_draft.workflow_state, "reviewed")
        self.assertIn("ready_for_queue", updated_draft.review_notes)
        self.assertEqual(review_record.review_outcome, "approved")
        self.assertEqual(review_record.updated_workflow_state, "reviewed")

    def test_record_draft_review_rejects_vague_notes_for_needs_edits(self) -> None:
        draft = create_draft_skeleton(_build_source_item(), created_at="2026-04-03T12:00:00+00:00")
        draft.quality_gate_status = "review_flag"
        draft.derivative_risk_level = "medium"

        with self.assertRaises(ValueError):
            record_draft_review(
                draft,
                review_outcome="needs_edits",
                review_notes=["rewrite"],
            )

    def test_record_draft_review_rejects_approval_of_blocked_draft(self) -> None:
        draft = create_draft_skeleton(_build_source_item(), created_at="2026-04-03T12:00:00+00:00")
        draft.quality_gate_status = "blocked"

        with self.assertRaises(ValueError):
            record_draft_review(draft, review_outcome="approved")

    def test_record_draft_review_requires_actionable_notes_for_rejected(self) -> None:
        draft = create_draft_skeleton(_build_source_item(), created_at="2026-04-03T12:00:00+00:00")
        draft.quality_gate_status = "review_flag"

        with self.assertRaises(ValueError):
            record_draft_review(draft, review_outcome="rejected", review_notes=[])


if __name__ == "__main__":
    unittest.main()
