from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from source_engine.source_status import SourceReviewSnapshot, recommend_source_status


class SourceStatusTests(unittest.TestCase):
    def test_recommend_downgraded_after_review_window_without_strong_candidates(self) -> None:
        snapshot = SourceReviewSnapshot(
            current_status="active_secondary",
            reviewed_items=4,
            strong_candidates=0,
            weak_or_repetitive_items=2,
        )
        result = recommend_source_status(snapshot)
        self.assertEqual(result.next_status, "downgraded")

    def test_recommend_paused_for_mostly_weak_items(self) -> None:
        snapshot = SourceReviewSnapshot(
            current_status="active_selective",
            reviewed_items=4,
            strong_candidates=0,
            weak_or_repetitive_items=4,
        )
        result = recommend_source_status(snapshot)
        self.assertEqual(result.next_status, "paused")

    def test_watchlist_can_be_promoted_after_strong_candidate(self) -> None:
        snapshot = SourceReviewSnapshot(
            current_status="watchlist",
            reviewed_items=1,
            strong_candidates=1,
            weak_or_repetitive_items=0,
        )
        result = recommend_source_status(snapshot)
        self.assertEqual(result.next_status, "active_selective")


if __name__ == "__main__":
    unittest.main()
