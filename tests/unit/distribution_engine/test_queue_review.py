from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from distribution_engine.models import QueueItemRecord
from distribution_engine.queue_review import record_queue_review


class QueueReviewTests(unittest.TestCase):
    def test_record_queue_review_approves_ready_queue(self) -> None:
        queue_item = QueueItemRecord(
            queue_item_id="blogq-test-1",
            queue_type="blog_publish",
            draft_id="draft-1",
            blog_publish_id="blog-1",
            social_package_id=None,
            queue_state="ready_for_blog_schedule",
            approval_state="pending_review",
            scheduled_for=None,
            last_transition_at="2026-04-04T10:00:00+00:00",
            created_at="2026-04-04T10:00:00+00:00",
            updated_at="2026-04-04T10:00:00+00:00",
        )

        review_record = record_queue_review(
            queue_item,
            review_outcome="approved",
            review_notes=["slot_clear_for_manual_schedule"],
            reviewer_label="queue_tester",
            reviewed_at="2026-04-04T10:10:00+00:00",
        )

        self.assertEqual(review_record.review_outcome, "approved")
        self.assertEqual(review_record.updated_queue_review_state, "approved")
        self.assertEqual(review_record.queue_state_at_review, "ready_for_blog_schedule")

    def test_record_queue_review_requires_actionable_note_for_hold(self) -> None:
        queue_item = QueueItemRecord(
            queue_item_id="blogq-test-2",
            queue_type="blog_publish",
            draft_id="draft-2",
            blog_publish_id="blog-2",
            social_package_id=None,
            queue_state="ready_for_wordpress",
            approval_state="pending_review",
            scheduled_for=None,
            last_transition_at="2026-04-04T10:00:00+00:00",
            created_at="2026-04-04T10:00:00+00:00",
            updated_at="2026-04-04T10:00:00+00:00",
        )

        with self.assertRaises(ValueError):
            record_queue_review(queue_item, review_outcome="hold", review_notes=[])

    def test_record_queue_review_marks_removed_with_actionable_note(self) -> None:
        queue_item = QueueItemRecord(
            queue_item_id="blogq-test-3",
            queue_type="blog_publish",
            draft_id="draft-3",
            blog_publish_id="blog-3",
            social_package_id=None,
            queue_state="ready_for_blog_schedule",
            approval_state="approved",
            scheduled_for=None,
            last_transition_at="2026-04-04T10:00:00+00:00",
            created_at="2026-04-04T10:00:00+00:00",
            updated_at="2026-04-04T10:00:00+00:00",
        )

        review_record = record_queue_review(
            queue_item,
            review_outcome="removed",
            review_notes=["removed_from_current_batch_due_to_topic_overlap"],
            reviewer_label="queue_tester",
            reviewed_at="2026-04-04T10:15:00+00:00",
        )

        self.assertEqual(review_record.review_outcome, "removed")
        self.assertEqual(review_record.updated_queue_review_state, "removed")
        self.assertEqual(
            review_record.review_notes,
            ("removed_from_current_batch_due_to_topic_overlap",),
        )


if __name__ == "__main__":
    unittest.main()
