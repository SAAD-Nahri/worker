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

from cli.replay_phase2_gold_set import main
from content_engine.gold_set import build_gold_set_summary, evaluate_gold_set_cases, load_gold_set_cases
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="gold-set-clean",
        source_id="src_test",
        source_name="Test Source",
        source_family="curiosity_editorial",
        run_id="run-1",
        source_url="https://example.com/story",
        canonical_url="https://example.com/story",
        discovered_at="2026-04-03T00:00:00+00:00",
        fetched_at="2026-04-03T00:00:00+00:00",
        raw_title="How To Give Your Costco Croissant Container A Second Life",
        raw_summary="A quick story about reusing a bakery container in a practical way.",
        raw_body_text=(
            "If you frequently buy croissants from Costco, you have probably ended up with a few empty plastic clamshell containers. "
            "The story is less about the bakery itself and more about giving the container a simple second life.\n\n"
            "The useful part is that the container is sturdy enough for light home organization, leftovers, or simple food storage. "
            "That makes the idea practical, cheap, and easy to understand.\n\n"
            "It also connects to environmental sustainability in a small but clear way. "
            "The article works because the reuse angle is specific instead of vague.\n\n"
            "Readers do not need a huge amount of prose to understand the point, but they do need enough context to see why the reuse idea is worth clicking. "
            "That extra context keeps the piece above the minimum eligibility threshold while staying squarely inside the curiosity-template path."
        ),
        author_name=None,
        published_at="2026-04-01T00:00:00+00:00",
        topical_label="food_curiosity",
        freshness_label="fresh",
        normalization_status="normalized",
        dedupe_status="unique",
        quality_flags=[],
        template_suggestion="curiosity_article",
    )


class GoldSetTests(unittest.TestCase):
    def test_evaluate_gold_set_cases_reports_clean_and_error_cases(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_items_path = root / "source_items.jsonl"
            manifest_path = root / "gold_set.json"

            clean_item = _build_source_item()
            source_items_path.write_text(json.dumps(clean_item.to_dict()) + "\n", encoding="utf-8")

            manifest = {
                "version": "test_gold_set",
                "cases": [
                    {
                        "case_id": "clean_fit",
                        "source_item_id": clean_item.item_id,
                        "expected_template_id": "blog_curiosity_food_v1",
                        "expected_subject_anchor": "costco croissant container",
                        "expected_intro_terms": [
                            "costco croissant container",
                            "bakery container",
                        ],
                        "forbidden_intro_terms": ["commission"],
                        "expected_quality_gate_status": "pass",
                        "expected_required_flags": [],
                        "expected_routing_action": "proceed",
                        "reason": "clean curiosity fit",
                    },
                    {
                        "case_id": "thin_reject",
                        "source_item": {
                            "item_id": "thin-control",
                            "source_id": "src_test",
                            "source_name": "Test Source",
                            "source_family": "food_editorial",
                            "run_id": "run-1",
                            "source_url": "https://example.com/thin",
                            "canonical_url": "https://example.com/thin",
                            "discovered_at": "2026-04-03T00:00:00+00:00",
                            "fetched_at": "2026-04-03T00:00:00+00:00",
                            "raw_title": "Tiny Example",
                            "raw_summary": "Too short to support a draft.",
                            "raw_body_text": "Too short.",
                            "author_name": None,
                            "published_at": "2026-04-03T00:00:00+00:00",
                            "topical_label": "food_explainer",
                            "freshness_label": "fresh",
                            "normalization_status": "normalized",
                            "dedupe_status": "unique",
                            "quality_flags": [],
                            "template_suggestion": "food_fact_article",
                        },
                        "expected_format_result": "error",
                        "expected_routing_action": "reject_for_v1",
                        "expected_error_fragment": "not eligible",
                        "reason": "blocked control",
                    },
                ],
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            cases = load_gold_set_cases(path=manifest_path)
            results = evaluate_gold_set_cases(cases, source_items_path=source_items_path)
            summary = build_gold_set_summary(results)

            self.assertEqual(len(results), 2)
            self.assertTrue(summary["all_passed"])
            self.assertEqual(summary["passed"], 2)

    def test_replay_phase2_gold_set_cli_returns_zero_for_all_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_items_path = root / "source_items.jsonl"
            manifest_path = root / "gold_set.json"

            clean_item = _build_source_item()
            source_items_path.write_text(json.dumps(clean_item.to_dict()) + "\n", encoding="utf-8")

            manifest = {
                "version": "test_gold_set",
                "cases": [
                    {
                        "case_id": "clean_fit",
                        "source_item_id": clean_item.item_id,
                        "expected_template_id": "blog_curiosity_food_v1",
                        "expected_subject_anchor": "costco croissant container",
                        "expected_intro_terms": [
                            "costco croissant container",
                            "bakery container",
                        ],
                        "forbidden_intro_terms": ["commission"],
                        "expected_quality_gate_status": "pass",
                        "expected_required_flags": [],
                        "expected_routing_action": "proceed",
                        "reason": "clean curiosity fit",
                    }
                ],
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--manifest-path",
                        str(manifest_path),
                        "--source-items-path",
                        str(source_items_path),
                        "--json",
                    ]
                )

            payload = json.loads(buffer.getvalue().strip())
            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["all_passed"])
            self.assertEqual(payload["passed"], 1)


if __name__ == "__main__":
    unittest.main()
