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

from ai_layer.openai_provider import OpenAiProviderConfig
from content_engine.formatting import format_source_item_to_draft
from content_engine.review import record_draft_review
from content_engine.storage import append_draft_records
from distribution_engine.review import record_social_package_review
from distribution_engine.facebook import prepare_social_package_record
from operator_api.services import OperatorApiPaths, apply_social_package_variant_selection
from distribution_engine.social_refinement import refine_social_package_with_openai
from distribution_engine.social_refinement_cli import main
from distribution_engine.storage import (
    append_blog_publish_records,
    append_social_package_records,
    append_social_package_review_records,
    load_latest_social_package_record,
    read_social_package_records,
)
from distribution_engine.wordpress import prepare_blog_publish_record
from source_engine.models import SourceItem


def _build_source_item() -> SourceItem:
    return SourceItem(
        item_id="item-social-refinement-1",
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
            "This food question comes up often because the visible result looks simple, but ingredient behavior and kitchen context usually explain more than people expect. The practical answer becomes clearer once the basic cause is stated early.\n\n"
            "The short answer is that texture, moisture, timing, and ingredient structure often explain the result better than random luck. When those factors line up, the pattern looks surprising but still follows a repeatable explanation.\n\n"
            "That context helps people understand what they are seeing instead of treating the result like a mystery. The stronger explanation usually comes from a few clear signals, not from an overloaded list of trivia.\n\n"
            "Once the pattern is clear, the topic becomes easier to remember and easier to explain in a short mobile-friendly post."
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


def _build_approved_draft_and_package():
    item = _build_source_item()
    draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")
    approved_draft, _ = record_draft_review(
        draft,
        review_outcome="approved",
        review_notes=["ready_for_phase_3"],
        reviewed_at="2026-04-03T12:05:00+00:00",
    )
    blog_record = prepare_blog_publish_record(
        approved_draft,
        created_at="2026-04-03T12:10:00+00:00",
        allow_non_pass_quality=True,
    )
    blog_record.wordpress_status = "draft_created"
    blog_record.wordpress_post_url = "https://example.com/why-this-kitchen-trick-works"
    package = prepare_social_package_record(
        approved_draft,
        blog_publish_record=blog_record,
        created_at="2026-04-03T12:15:00+00:00",
    )
    return approved_draft, blog_record, package


class SocialRefinementTests(unittest.TestCase):
    def test_refine_social_package_with_openai_adds_variants_and_ai_log_without_changing_selection(self) -> None:
        approved_draft, blog_record, package = _build_approved_draft_and_package()
        current_label = package.selected_variant_label
        current_hook = package.hook_text

        def response_creator(request, config):
            return json.dumps(
                {
                    "variants": [
                        {
                            "hook_text": "What makes this kitchen trick work so consistently?",
                            "caption_text": "The short answer comes down to heat, moisture, and structure working together in a way most people do not notice at first.",
                            "comment_cta_text": "Full post here if you want the full explanation.",
                        },
                        {
                            "hook_text": "Why this simple kitchen pattern is easier to repeat than it looks",
                            "caption_text": "The blog version turns the short answer into a quick explanation you can scan fast and remember the next time you cook.",
                            "comment_cta_text": "Full post here if you want the practical breakdown.",
                        },
                    ]
                }
            )

        result = refine_social_package_with_openai(
            package,
            approved_draft,
            config=OpenAiProviderConfig(api_key="sk-test"),
            blog_publish_record=blog_record,
            response_creator=response_creator,
        )

        self.assertEqual(result.added_variant_labels, ("openai_refined_1_v1", "openai_refined_2_v1"))
        self.assertIsNone(result.fallback_reason)
        self.assertEqual(result.updated_package.selected_variant_label, current_label)
        self.assertEqual(result.updated_package.approval_state, package.approval_state)
        self.assertEqual(result.updated_package.hook_text, current_hook)
        self.assertEqual(len(result.updated_package.ai_assistance_log), 1)
        self.assertEqual(result.updated_package.ai_assistance_log[0].model_label, "gpt-5.4-mini")
        self.assertEqual(len(result.updated_package.variant_options), len(package.variant_options) + 2)

    def test_refine_social_package_with_openai_returns_fallback_when_only_duplicates_are_generated(self) -> None:
        approved_draft, blog_record, package = _build_approved_draft_and_package()

        def response_creator(request, config):
            return json.dumps(
                {
                    "variants": [
                        {
                            "hook_text": package.hook_text,
                            "caption_text": package.caption_text,
                            "comment_cta_text": package.comment_cta_text,
                        }
                    ]
                }
            )

        result = refine_social_package_with_openai(
            package,
            approved_draft,
            config=OpenAiProviderConfig(api_key="sk-test"),
            blog_publish_record=blog_record,
            response_creator=response_creator,
        )

        self.assertEqual(result.updated_package, package)
        self.assertEqual(result.added_variant_labels, ())
        self.assertIn("duplicate", result.fallback_reason)

    def test_social_refinement_cli_reports_missing_config_without_mutating_records(self) -> None:
        approved_draft, blog_record, package = _build_approved_draft_and_package()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft_path = root / "draft_records.jsonl"
            blog_path = root / "blog_publish_records.jsonl"
            social_path = root / "social_package_records.jsonl"
            missing_config_path = root / "openai_provider_config.local.json"

            append_draft_records([approved_draft], path=draft_path)
            append_blog_publish_records([blog_record], path=blog_path)
            append_social_package_records([package], path=social_path)

            buffer = io.StringIO()
            with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False):
                with redirect_stdout(buffer):
                    exit_code = main(
                        [
                            "--social-package-id",
                            package.social_package_id,
                            "--provider",
                            "openai",
                            "--openai-config-path",
                            str(missing_config_path),
                            "--draft-records-path",
                            str(draft_path),
                            "--blog-publish-records-path",
                            str(blog_path),
                            "--social-package-records-path",
                            str(social_path),
                        ]
                    )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            self.assertEqual(payload["provider_requested"], "openai")
            self.assertIsNone(payload["provider"])
            self.assertIn("OpenAI provider requires OPENAI_API_KEY", payload["fallback_reason"])
            self.assertEqual(len(read_social_package_records(social_path)), 1)
            latest_package = load_latest_social_package_record(package.social_package_id, path=social_path)
            self.assertEqual(len(latest_package.ai_assistance_log), 0)

    def test_selecting_openai_variant_reopens_social_review(self) -> None:
        approved_draft, blog_record, package = _build_approved_draft_and_package()

        def response_creator(request, config):
            return json.dumps(
                {
                    "variants": [
                        {
                            "hook_text": "Why this kitchen answer stays easier to repeat than people expect",
                            "caption_text": "The linked article explains the repeatable cause without stretching the claim past what the draft and source already support.",
                            "comment_cta_text": "Read the full breakdown here.",
                        }
                    ]
                }
            )

        result = refine_social_package_with_openai(
            package,
            approved_draft,
            config=OpenAiProviderConfig(api_key="sk-test"),
            blog_publish_record=blog_record,
            response_creator=response_creator,
        )
        approved_package, review_record = record_social_package_review(
            result.updated_package,
            review_outcome="approved",
            review_notes=["ready_for_queue"],
            reviewed_at="2026-04-03T12:20:00+00:00",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft_path = root / "draft_records.jsonl"
            blog_path = root / "blog_publish_records.jsonl"
            social_path = root / "social_package_records.jsonl"
            social_review_path = root / "social_package_reviews.jsonl"

            append_draft_records([approved_draft], path=draft_path)
            append_blog_publish_records([blog_record], path=blog_path)
            append_social_package_records([package, result.updated_package, approved_package], path=social_path)
            append_social_package_review_records([review_record], path=social_review_path)

            payload = apply_social_package_variant_selection(
                approved_package.social_package_id,
                variant_label="openai_refined_1_v1",
                paths=OperatorApiPaths(
                    draft_records_path=draft_path,
                    blog_publish_records_path=blog_path,
                    social_package_records_path=social_path,
                    social_package_reviews_path=social_review_path,
                ),
            )

        selected_package = payload["social_package"]
        self.assertEqual(selected_package["selected_variant_label"], "openai_refined_1_v1")
        self.assertEqual(selected_package["approval_state"], "pending_review")
        self.assertEqual(selected_package["ai_assistance_log"][0]["skill_name"], "refine_social_package_variants")


if __name__ == "__main__":
    unittest.main()
