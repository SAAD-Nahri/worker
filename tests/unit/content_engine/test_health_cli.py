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
from content_engine.health_cli import main
from content_engine.storage import append_draft_records
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-health-cli",
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


class DraftHealthCliTests(unittest.TestCase):
    def test_health_cli_outputs_json_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft_path = root / "draft_records.jsonl"
            draft = format_source_item_to_draft(
                _build_source_item(),
                created_at="2026-04-03T12:00:00+00:00",
            )
            draft.quality_gate_status = "pass"
            draft.quality_flags = []
            draft.derivative_risk_level = "low"
            draft.derivative_risk_notes = "Ready for review."
            append_draft_records([draft], path=draft_path)

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(["--draft-records-path", str(draft_path), "--json"])

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue())
            self.assertEqual(payload["summary"]["total_drafts"], 1)
            self.assertEqual(payload["rows"][0]["draft_id"], draft.draft_id)
            self.assertEqual(payload["rows"][0]["operator_signal"], "ready_for_review")
            self.assertEqual(payload["rows"][0]["routing_action"], "proceed")
            self.assertEqual(payload["summary"]["routing_action_counts"]["proceed"], 1)

    def test_health_cli_outputs_routing_information_in_text_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft_path = root / "draft_records.jsonl"
            draft = format_source_item_to_draft(
                _build_source_item(),
                created_at="2026-04-03T12:00:00+00:00",
            )
            draft.source_title = "10 Italian Street Foods You Need To Try"
            draft.quality_gate_status = "review_flag"
            draft.quality_flags = ["semantic_term_noise"]
            draft.derivative_risk_level = "low"
            draft.derivative_risk_notes = "Needs reroute."
            append_draft_records([draft], path=draft_path)

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(["--draft-records-path", str(draft_path)])

            output = buffer.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("Routing: proceed=0 review_only=0 hold_for_reroute=1 reject_for_v1=0", output)
            self.assertIn("hold_for_reroute", output)
            self.assertIn("routing_reasons: roundup_or_listicle_title", output)


if __name__ == "__main__":
    unittest.main()
