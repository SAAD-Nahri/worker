from __future__ import annotations

import io
import json
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.formatting import format_source_item_to_draft
from content_engine.micro_skill_cli import main
from content_engine.storage import append_draft_records, load_latest_draft_record
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-cli-123456",
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
    return SourceItem(
        **{
            **item.to_dict(),
            "item_id": "item-cli-curiosity-123456",
            "raw_title": "How To Give Your Costco Croissant Container A Second Life",
            "raw_summary": "A quick food-storage summary about why the container is worth keeping around.",
            "template_suggestion": "curiosity_article",
        }
    )


class MicroSkillCliTests(unittest.TestCase):
    def test_micro_skill_cli_appends_updated_draft_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft_path = root / "draft_records.jsonl"
            source_path = root / "source_items.jsonl"
            item = _build_source_item()
            source_path.write_text(json.dumps(item.to_dict()) + "\n", encoding="utf-8")
            draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")
            append_draft_records([draft], path=draft_path)

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--draft-id",
                        draft.draft_id,
                        "--skill",
                        "generate_headline_variants",
                        "--skill",
                        "generate_excerpt",
                        "--draft-records-path",
                        str(draft_path),
                        "--source-items-path",
                        str(source_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            self.assertEqual(payload["provider"], "heuristic-v1")
            self.assertEqual(payload["skills"], ["generate_headline_variants", "generate_excerpt"])
            latest = load_latest_draft_record(draft.draft_id, path=draft_path)
            self.assertGreaterEqual(len(latest.headline_variants), 2)
            self.assertGreaterEqual(len(latest.excerpt.split()), 20)

    def test_micro_skill_cli_rejects_intro_generation_for_template_without_intro_slot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft_path = root / "draft_records.jsonl"
            source_path = root / "source_items.jsonl"
            item = _build_curiosity_source_item()
            source_path.write_text(json.dumps(item.to_dict()) + "\n", encoding="utf-8")
            draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")
            append_draft_records([draft], path=draft_path)

            with self.assertRaises(SystemExit):
                main(
                    [
                        "--draft-id",
                        draft.draft_id,
                        "--skill",
                        "generate_short_intro",
                        "--draft-records-path",
                        str(draft_path),
                        "--source-items-path",
                        str(source_path),
                    ]
                )

    def test_micro_skill_cli_openai_provider_falls_back_to_heuristic_when_config_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft_path = root / "draft_records.jsonl"
            source_path = root / "source_items.jsonl"
            missing_config_path = root / "openai_provider_config.local.json"
            item = _build_source_item()
            source_path.write_text(json.dumps(item.to_dict()) + "\n", encoding="utf-8")
            draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")
            append_draft_records([draft], path=draft_path)

            buffer = io.StringIO()
            with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False):
                with redirect_stdout(buffer):
                    exit_code = main(
                        [
                            "--draft-id",
                            draft.draft_id,
                            "--skill",
                            "generate_headline_variants",
                            "--provider",
                            "openai",
                            "--openai-config-path",
                            str(missing_config_path),
                            "--draft-records-path",
                            str(draft_path),
                            "--source-items-path",
                            str(source_path),
                        ]
                    )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            self.assertEqual(payload["provider_requested"], "openai")
            self.assertEqual(payload["provider"], "heuristic-v1")
            self.assertIn("OPENAI_API_KEY", payload["fallback_reason"])
            latest = load_latest_draft_record(draft.draft_id, path=draft_path)
            self.assertGreaterEqual(len(latest.headline_variants), 2)
            self.assertEqual(len(latest.ai_assistance_log), 0)


if __name__ == "__main__":
    unittest.main()
