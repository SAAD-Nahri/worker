from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.formatting import evaluate_draft_against_source, format_source_item_to_draft
from content_engine.micro_skills import HeuristicMicroSkillProvider, apply_micro_skills
from content_engine.review import record_draft_review
from source_engine.models import SourceItem


def _build_source_item(
    raw_title: str = "Why This Kitchen Trick Works",
    raw_summary: str = "A short summary about why the trick works.",
    template_suggestion: str = "food_fact_article",
) -> SourceItem:
    return SourceItem(
        item_id="item-micro-123456",
        source_id="src_test",
        source_name="Test Source",
        source_family="food_editorial",
        run_id="run-1",
        source_url="https://example.com/story",
        canonical_url="https://example.com/story",
        discovered_at="2026-04-03T00:00:00+00:00",
        fetched_at="2026-04-03T00:00:00+00:00",
        raw_title=raw_title,
        raw_summary=raw_summary,
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
        template_suggestion=template_suggestion,
    )


class StubAiProvider:
    provider_label = "gpt-test"
    records_ai_usage = True

    def generate_headline_variants(self, draft, source_item, desired_count):
        return [
            "The Real Reason This Kitchen Trick Works",
            "What Actually Explains This Kitchen Trick",
            "Why This Simple Kitchen Trick Matters",
        ]

    def generate_short_intro(self, draft, source_item, min_words, max_words):
        return (
            "This version keeps the kitchen explanation short, honest, and answer-first so the reader sees the pattern quickly without wading through a long setup first."
        )

    def generate_excerpt(self, draft, source_item, min_words, max_words):
        return "A short mobile-friendly summary that keeps the main kitchen point visible without turning the excerpt into a second article."


class WeakProvider:
    provider_label = "weak-provider"
    records_ai_usage = True

    def generate_headline_variants(self, draft, source_item, desired_count):
        return [draft.headline_selected]

    def generate_short_intro(self, draft, source_item, min_words, max_words):
        return "Too short."

    def generate_excerpt(self, draft, source_item, min_words, max_words):
        return "Tiny."


class NoisyHeadlineProvider:
    provider_label = "noisy-provider"
    records_ai_usage = True

    def generate_headline_variants(self, draft, source_item, desired_count):
        return [
            "You Won't Believe This Kitchen Trick",
            "Why To Give Your Costco Croissant Container A Second Life Matters In The Kitchen",
            "What To Know About Your Costco Croissant Container",
        ]

    def generate_short_intro(self, draft, source_item, min_words, max_words):
        return draft.intro_text

    def generate_excerpt(self, draft, source_item, min_words, max_words):
        return draft.excerpt


class LongIntroProvider:
    provider_label = "long-intro-provider"
    records_ai_usage = True

    def generate_headline_variants(self, draft, source_item, desired_count):
        return []

    def generate_short_intro(self, draft, source_item, min_words, max_words):
        return (
            "This rewritten introduction is intentionally much longer than the food-fact template wants because it keeps adding setup about process, kitchen patterns, explanation quality, reader expectations, scanning behavior, and workflow discipline before the draft reaches the direct answer. "
            "It is still readable, but it spends too much space on framing and pushes the answer later than the accepted contract allows for an answer-first explainer."
        )

    def generate_excerpt(self, draft, source_item, min_words, max_words):
        return draft.excerpt


class ClaimReviewIntroProvider:
    provider_label = "claim-review-provider"
    records_ai_usage = True

    def generate_headline_variants(self, draft, source_item, desired_count):
        return []

    def generate_short_intro(self, draft, source_item, min_words, max_words):
        return (
            "This updated introduction keeps the explanation mobile-friendly, but it also calls the method the best shortcut for home cooks who want a cleaner answer before reading the rest of the article."
        )

    def generate_excerpt(self, draft, source_item, min_words, max_words):
        return draft.excerpt


class MicroSkillTests(unittest.TestCase):
    def test_apply_micro_skills_with_heuristic_provider_keeps_system_working_without_ai(self) -> None:
        item = _build_source_item()
        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")

        enriched = apply_micro_skills(
            draft,
            item,
            requested_skills=["generate_headline_variants", "generate_excerpt"],
            provider=HeuristicMicroSkillProvider(),
            created_at="2026-04-03T12:05:00+00:00",
        )

        self.assertGreaterEqual(len(enriched.headline_variants), 2)
        self.assertGreaterEqual(len(enriched.excerpt.split()), 20)
        self.assertEqual(len(enriched.ai_assistance_log), 0)
        self.assertEqual(enriched.updated_at, "2026-04-03T12:05:00+00:00")

    def test_apply_micro_skills_logs_ai_usage_with_stub_provider(self) -> None:
        item = _build_source_item()
        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")

        enriched = apply_micro_skills(
            draft,
            item,
            requested_skills=[
                "generate_headline_variants",
                "generate_short_intro",
                "generate_excerpt",
            ],
            provider=StubAiProvider(),
            created_at="2026-04-03T12:10:00+00:00",
        )

        self.assertEqual(len(enriched.headline_variants), 3)
        self.assertEqual(enriched.headline_variants[0], "The Real Reason This Kitchen Trick Works")
        self.assertGreaterEqual(len(enriched.intro_text.split()), 20)
        self.assertGreaterEqual(len(enriched.excerpt.split()), 20)
        self.assertEqual(len(enriched.ai_assistance_log), 3)
        self.assertEqual(enriched.ai_assistance_log[0].model_label, "gpt-test")

    def test_apply_micro_skills_falls_back_when_provider_output_is_weak(self) -> None:
        item = _build_source_item()
        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")

        enriched = apply_micro_skills(
            draft,
            item,
            requested_skills=[
                "generate_headline_variants",
                "generate_short_intro",
                "generate_excerpt",
            ],
            provider=WeakProvider(),
            created_at="2026-04-03T12:15:00+00:00",
        )

        self.assertGreaterEqual(len(enriched.headline_variants), 2)
        self.assertGreaterEqual(len(enriched.intro_text.split()), 35)
        self.assertLessEqual(len(enriched.intro_text.split()), 70)
        self.assertGreaterEqual(len(enriched.excerpt.split()), 20)
        self.assertEqual(len(enriched.ai_assistance_log), 3)

    def test_heuristic_headline_variants_respect_how_to_second_life_title_shape(self) -> None:
        item = _build_source_item(
            raw_title="How To Give Your Costco Croissant Container A Second Life",
            raw_summary="A quick food-storage summary about why the container is worth keeping around.",
            template_suggestion="curiosity_article",
        )
        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")

        enriched = apply_micro_skills(
            draft,
            item,
            requested_skills=["generate_headline_variants"],
            provider=HeuristicMicroSkillProvider(),
            created_at="2026-04-03T12:20:00+00:00",
        )

        self.assertEqual(
            enriched.headline_variants,
            [
                "Why Your Costco Croissant Container Is Worth Saving",
                "A Better Second Use For Your Costco Croissant Container",
                "How Your Costco Croissant Container Can Be Reused",
            ],
        )

    def test_apply_micro_skills_rejects_intro_generation_for_templates_without_intro_slot(self) -> None:
        item = _build_source_item(
            raw_title="How To Give Your Costco Croissant Container A Second Life",
            raw_summary="A quick food-storage summary about why the container is worth keeping around.",
            template_suggestion="curiosity_article",
        )
        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")

        with self.assertRaisesRegex(ValueError, "has no intro slot"):
            apply_micro_skills(
                draft,
                item,
                requested_skills=["generate_short_intro"],
                provider=HeuristicMicroSkillProvider(),
                created_at="2026-04-03T12:22:00+00:00",
            )

    def test_apply_micro_skills_filters_clicky_or_awkward_headline_variants(self) -> None:
        item = _build_source_item(
            raw_title="How To Give Your Costco Croissant Container A Second Life",
            raw_summary="A quick food-storage summary about why the container is worth keeping around.",
            template_suggestion="curiosity_article",
        )
        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")

        enriched = apply_micro_skills(
            draft,
            item,
            requested_skills=["generate_headline_variants"],
            provider=NoisyHeadlineProvider(),
            created_at="2026-04-03T12:25:00+00:00",
        )

        self.assertEqual(
            enriched.headline_variants,
            [
                "Why Your Costco Croissant Container Is Worth Saving",
                "A Better Second Use For Your Costco Croissant Container",
                "How Your Costco Croissant Container Can Be Reused",
            ],
        )

    def test_apply_micro_skills_resets_review_state_after_intro_change(self) -> None:
        item = _build_source_item()
        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")
        approved_draft, _ = record_draft_review(
            draft,
            review_outcome="approved",
            review_notes=["ready_for_queue"],
            reviewed_at="2026-04-03T12:05:00+00:00",
        )

        enriched = apply_micro_skills(
            approved_draft,
            item,
            requested_skills=["generate_short_intro"],
            provider=LongIntroProvider(),
            created_at="2026-04-03T12:10:00+00:00",
        )
        expected_quality = evaluate_draft_against_source(enriched, item)

        self.assertEqual(enriched.approval_state, "pending_review")
        self.assertEqual(enriched.workflow_state, "drafted")
        self.assertEqual(enriched.quality_gate_status, expected_quality.quality_gate_status)
        self.assertEqual(tuple(enriched.quality_flags), expected_quality.quality_flags)
        self.assertEqual(len(enriched.ai_assistance_log), 1)

    def test_apply_micro_skills_re_evaluates_quality_after_intro_change(self) -> None:
        item = _build_source_item()
        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")
        approved_draft, _ = record_draft_review(
            draft,
            review_outcome="approved",
            review_notes=["ready_for_queue"],
            reviewed_at="2026-04-03T12:05:00+00:00",
        )

        enriched = apply_micro_skills(
            approved_draft,
            item,
            requested_skills=["generate_short_intro"],
            provider=ClaimReviewIntroProvider(),
            created_at="2026-04-03T12:10:00+00:00",
        )

        self.assertEqual(enriched.approval_state, "pending_review")
        self.assertEqual(enriched.workflow_state, "drafted")
        self.assertEqual(enriched.quality_gate_status, "review_flag")
        self.assertIn("claim_tone_review", enriched.quality_flags)
        self.assertEqual(len(enriched.ai_assistance_log), 1)

    def test_apply_micro_skills_keeps_review_state_for_non_content_skills(self) -> None:
        item = _build_source_item()
        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")
        approved_draft, _ = record_draft_review(
            draft,
            review_outcome="approved",
            review_notes=["ready_for_queue"],
            reviewed_at="2026-04-03T12:05:00+00:00",
        )

        enriched = apply_micro_skills(
            approved_draft,
            item,
            requested_skills=["generate_headline_variants", "generate_excerpt"],
            provider=HeuristicMicroSkillProvider(),
            created_at="2026-04-03T12:10:00+00:00",
        )

        self.assertEqual(enriched.approval_state, "approved")
        self.assertEqual(enriched.workflow_state, "reviewed")
        self.assertEqual(enriched.quality_gate_status, "pass")

    def test_heuristic_headline_variants_handle_list_style_avoidance_titles(self) -> None:
        item = _build_source_item(
            raw_title="The Only 2 Foods Jacques Pépin Thinks Twice About Eating",
            raw_summary="A short summary about two foods Jacques Pépin still avoids.",
        )
        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")

        enriched = apply_micro_skills(
            draft,
            item,
            requested_skills=["generate_headline_variants"],
            provider=HeuristicMicroSkillProvider(),
            created_at="2026-04-03T12:30:00+00:00",
        )

        self.assertEqual(
            enriched.headline_variants,
            [
                "Which Foods Jacques Pépin Avoids",
                "Why Jacques Pépin Still Skips Certain Foods",
                "A Clearer Look At The Foods Jacques Pépin Avoids",
            ],
        )


if __name__ == "__main__":
    unittest.main()
