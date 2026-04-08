from __future__ import annotations

import json
import sys
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_layer.openai_provider import OpenAiProviderConfig, load_openai_provider_config
from content_engine.formatting import format_source_item_to_draft
from content_engine.micro_skills import OpenAiMicroSkillProvider, apply_micro_skills
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-openai-provider-1",
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


class OpenAiProviderTests(unittest.TestCase):
    def test_load_openai_provider_config_prefers_env_api_key_over_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "openai_provider_config.local.json"
            config_path.write_text(
                json.dumps(
                    {
                        "api_key": "sk-file",
                        "model": "gpt-file-model",
                        "timeout_seconds": 45,
                    }
                ),
                encoding="utf-8",
            )

            config = load_openai_provider_config(
                config_path,
                environ={"OPENAI_API_KEY": "sk-env"},
            )

        self.assertEqual(config.api_key, "sk-env")
        self.assertEqual(config.model, "gpt-file-model")
        self.assertEqual(config.timeout_seconds, 45)

    def test_load_openai_provider_config_uses_file_when_env_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "openai_provider_config.local.json"
            config_path.write_text(
                json.dumps(
                    {
                        "api_key": "sk-file-only",
                        "model": "gpt-file-only",
                        "timeout_seconds": 31,
                    }
                ),
                encoding="utf-8",
            )

            config = load_openai_provider_config(
                config_path,
                environ={"OPENAI_API_KEY": ""},
            )

        self.assertEqual(config.api_key, "sk-file-only")
        self.assertEqual(config.model, "gpt-file-only")
        self.assertEqual(config.timeout_seconds, 31)

    def test_load_openai_provider_config_rejects_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "openai_provider_config.local.json"
            config_path.write_text("{bad-json", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "not valid JSON"):
                load_openai_provider_config(config_path, environ={"OPENAI_API_KEY": ""})

    def test_load_openai_provider_config_rejects_non_integer_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "openai_provider_config.local.json"
            config_path.write_text(
                json.dumps(
                    {
                        "api_key": "sk-file",
                        "model": "gpt-file-model",
                        "timeout_seconds": "thirty",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "timeout_seconds must be an integer"):
                load_openai_provider_config(config_path, environ={"OPENAI_API_KEY": ""})

    def test_load_openai_provider_config_missing_secret_is_explicit_and_secret_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "openai_provider_config.local.json"

            with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY") as context:
                load_openai_provider_config(config_path, environ={"OPENAI_API_KEY": ""})

        self.assertNotIn("sk-", str(context.exception))

    def test_openai_provider_routes_requests_to_prompt_contracts(self) -> None:
        item = _build_source_item()
        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")
        captured_tasks: list[str] = []

        def response_creator(request, config):
            captured_tasks.append(request.task_name)
            if request.task_name == "generate_headline_variants":
                return json.dumps(
                    {
                        "headline_variants": [
                            "The Real Reason This Kitchen Trick Works",
                            "What Actually Explains This Kitchen Trick",
                            "Why This Kitchen Shortcut Holds Up",
                        ]
                    }
                )
            if request.task_name == "generate_short_intro":
                return json.dumps(
                    {
                        "intro_text": "This intro keeps the answer clear, practical, and easy to scan so the reader sees the kitchen pattern quickly, understands the useful cause, and gets a grounded explanation before the rest of the article expands the point."
                    }
                )
            if request.task_name == "generate_excerpt":
                return json.dumps(
                    {
                        "excerpt_text": "A short mobile-friendly summary that keeps the main kitchen point visible without turning the excerpt into a second article or a promotional tease."
                    }
                )
            raise AssertionError(f"Unexpected task: {request.task_name}")

        provider = OpenAiMicroSkillProvider(
            OpenAiProviderConfig(api_key="sk-test"),
            response_creator=response_creator,
        )
        fallback_events: list[str] = []

        enriched = apply_micro_skills(
            draft,
            item,
            requested_skills=[
                "generate_headline_variants",
                "generate_short_intro",
                "generate_excerpt",
            ],
            provider=provider,
            created_at="2026-04-03T12:10:00+00:00",
            fallback_events=fallback_events,
        )

        self.assertEqual(
            captured_tasks,
            [
                "generate_headline_variants",
                "generate_short_intro",
                "generate_excerpt",
            ],
        )
        self.assertEqual(fallback_events, [])
        self.assertEqual(len(enriched.ai_assistance_log), 3)
        self.assertTrue(all(entry.model_label == "gpt-5.4-mini" for entry in enriched.ai_assistance_log))

    def test_openai_provider_falls_back_cleanly_when_output_is_weak(self) -> None:
        item = _build_source_item()
        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")

        def response_creator(request, config):
            if request.task_name == "generate_headline_variants":
                return json.dumps({"headline_variants": ["You Won't Believe This Kitchen Trick"]})
            if request.task_name == "generate_short_intro":
                return json.dumps({"intro_text": "Too short."})
            if request.task_name == "generate_excerpt":
                return json.dumps({"excerpt_text": "Tiny."})
            raise AssertionError(f"Unexpected task: {request.task_name}")

        provider = OpenAiMicroSkillProvider(
            OpenAiProviderConfig(api_key="sk-test"),
            response_creator=response_creator,
        )
        fallback_events: list[str] = []

        enriched = apply_micro_skills(
            draft,
            item,
            requested_skills=[
                "generate_headline_variants",
                "generate_short_intro",
                "generate_excerpt",
            ],
            provider=provider,
            created_at="2026-04-03T12:15:00+00:00",
            fallback_events=fallback_events,
        )

        self.assertGreaterEqual(len(enriched.headline_variants), 2)
        self.assertGreaterEqual(len(enriched.excerpt.split()), 20)
        self.assertEqual(len(enriched.ai_assistance_log), 0)
        self.assertEqual(len(fallback_events), 3)
        self.assertTrue(all("fell back" in reason for reason in fallback_events))


if __name__ == "__main__":
    unittest.main()
