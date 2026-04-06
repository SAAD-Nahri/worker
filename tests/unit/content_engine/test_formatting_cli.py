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

from content_engine.formatting_cli import main
from content_engine.storage import load_latest_draft_record
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-format-cli",
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


def _build_curiosity_source_item() -> SourceItem:
    item = _build_source_item()
    item.item_id = "item-format-cli-curiosity"
    item.raw_title = "Why Do Some Cheeses Taste Sharper As They Age?"
    item.raw_summary = "A short food curiosity about aging, texture, and flavor development."
    item.raw_body_text = (
        "Cheese tastes sharper with age because moisture, enzymes, and time change the texture and flavor in ways that become easier to notice over months of storage. "
        "As the cheese loses water, the flavor feels more concentrated and the structure becomes firmer.\n\n"
        "That process matters because people often describe sharpness as if it were only about heat or intensity, when it is really about how flavor compounds develop and stand out over time. "
        "The same cheese can feel much more assertive later because the balance inside it keeps changing.\n\n"
        "A familiar example is cheddar, which can move from mild and creamy to crumbly and much more pronounced as it ages. "
        "That makes the question easier to understand because the sharper taste is tied to an ordinary process, not a mysterious ingredient.\n\n"
        "The useful answer is that aging changes both flavor concentration and texture. "
        "Once that is clear, the headline question stops sounding mysterious and starts feeling like a practical food explanation."
    )
    item.topical_label = "food_history"
    item.source_family = "curiosity_editorial"
    item.template_suggestion = "curiosity_article"
    return item


class FormattingCliTests(unittest.TestCase):
    def test_formatting_cli_creates_and_persists_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft_path = root / "draft_records.jsonl"
            source_path = root / "source_items.jsonl"
            item = _build_source_item()
            source_path.write_text(json.dumps(item.to_dict()) + "\n", encoding="utf-8")

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--source-item-id",
                        item.item_id,
                        "--draft-records-path",
                        str(draft_path),
                        "--source-items-path",
                        str(source_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            self.assertEqual(payload["source_item_id"], item.item_id)
            self.assertEqual(payload["template_id"], "blog_food_fact_v1")
            self.assertEqual(payload["routing_action"], "proceed")
            self.assertEqual(payload["routing_reasons"], [])
            latest = load_latest_draft_record(payload["draft_id"], path=draft_path)
            self.assertEqual(latest.source_item_id, item.item_id)
            self.assertEqual(latest.template_id, "blog_food_fact_v1")
            self.assertTrue(latest.category)

    def test_formatting_cli_honors_explicit_template_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft_path = root / "draft_records.jsonl"
            source_path = root / "source_items.jsonl"
            item = _build_curiosity_source_item()
            source_path.write_text(json.dumps(item.to_dict()) + "\n", encoding="utf-8")

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--source-item-id",
                        item.item_id,
                        "--template-id",
                        "blog_curiosity_food_v1",
                        "--draft-records-path",
                        str(draft_path),
                        "--source-items-path",
                        str(source_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            latest = load_latest_draft_record(payload["draft_id"], path=draft_path)
            self.assertEqual(latest.template_id, "blog_curiosity_food_v1")

    def test_formatting_cli_rejects_mismatched_template_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft_path = root / "draft_records.jsonl"
            source_path = root / "source_items.jsonl"
            item = _build_source_item()
            source_path.write_text(json.dumps(item.to_dict()) + "\n", encoding="utf-8")

            with self.assertRaises(SystemExit):
                main(
                    [
                        "--source-item-id",
                        item.item_id,
                        "--template-id",
                        "blog_curiosity_food_v1",
                        "--draft-records-path",
                        str(draft_path),
                        "--source-items-path",
                        str(source_path),
                    ]
                )


if __name__ == "__main__":
    unittest.main()
