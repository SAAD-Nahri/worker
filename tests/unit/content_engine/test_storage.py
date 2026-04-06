from __future__ import annotations

import sys
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.drafts import create_draft_skeleton
from content_engine.models import DraftReviewRecord
from content_engine.storage import (
    append_draft_records,
    append_draft_review_records,
    load_latest_draft_record,
    read_jsonl_records,
)
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-1234567890ab",
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
        raw_body_text="Useful body text for a source item.",
        author_name=None,
        published_at="2026-04-01T00:00:00+00:00",
        topical_label="food_explainer",
        freshness_label="fresh",
        normalization_status="normalized",
        dedupe_status="unique",
        quality_flags=[],
        template_suggestion="food_fact_article",
    )


class DraftStorageTests(unittest.TestCase):
    def test_append_draft_records_writes_jsonl_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "draft_records.jsonl"
            draft = create_draft_skeleton(_build_source_item(), created_at="2026-04-03T12:00:00+00:00")

            append_draft_records([draft], path=path)
            payload = read_jsonl_records(path)

            self.assertEqual(len(payload), 1)
            self.assertEqual(payload[0]["draft_id"], draft.draft_id)
            self.assertEqual(payload[0]["template_id"], "blog_food_fact_v1")
            self.assertEqual(payload[0]["source_item_id"], "item-1234567890ab")

    def test_load_latest_draft_record_returns_most_recent_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "draft_records.jsonl"
            draft = create_draft_skeleton(_build_source_item(), created_at="2026-04-03T12:00:00+00:00")
            newer = create_draft_skeleton(_build_source_item(), created_at="2026-04-03T12:05:00+00:00")
            newer.draft_id = draft.draft_id
            newer.updated_at = "2026-04-03T12:05:00+00:00"
            newer.approval_state = "approved"

            append_draft_records([draft, newer], path=path)
            latest = load_latest_draft_record(draft.draft_id, path=path)

            self.assertEqual(latest.updated_at, "2026-04-03T12:05:00+00:00")
            self.assertEqual(latest.approval_state, "approved")

    def test_append_draft_review_records_writes_jsonl_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "draft_reviews.jsonl"
            review = DraftReviewRecord(
                review_id="review-1",
                draft_id="draft-1",
                source_item_id="item-1",
                reviewer_label="solo_operator",
                reviewed_at="2026-04-03T12:00:00+00:00",
                review_outcome="approved",
                previous_approval_state="pending_review",
                updated_approval_state="approved",
                updated_workflow_state="reviewed",
                quality_gate_status="pass",
                derivative_risk_level="low",
                review_notes=("title_fix resolved",),
            )

            append_draft_review_records([review], path=path)
            payload = read_jsonl_records(path)

            self.assertEqual(len(payload), 1)
            self.assertEqual(payload[0]["review_id"], "review-1")
            self.assertEqual(payload[0]["review_outcome"], "approved")


if __name__ == "__main__":
    unittest.main()
