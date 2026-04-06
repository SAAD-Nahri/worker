from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.drafts import create_draft_skeleton
from content_engine.quality import evaluate_draft_quality
from content_engine.templates import get_blog_template_contract
from source_engine.models import SourceItem


def _build_source_item(raw_body_text: str, template_suggestion: str = "food_fact_article") -> SourceItem:
    return SourceItem(
        item_id="item-quality-123456",
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
        raw_body_text=raw_body_text,
        author_name=None,
        published_at="2026-04-01T00:00:00+00:00",
        topical_label="food_explainer",
        freshness_label="fresh",
        normalization_status="normalized",
        dedupe_status="unique",
        quality_flags=[],
        template_suggestion=template_suggestion,
    )


class DraftQualityTests(unittest.TestCase):
    def test_evaluate_draft_quality_blocks_high_derivative_risk(self) -> None:
        source_text = (
            "This kitchen behavior surprises a lot of people because heat, moisture, and structure all work together. "
            "When the balance shifts, the result changes quickly in the pan. "
            "Understanding that pattern helps cooks get more reliable outcomes at home. "
            "The same explanation shows up again when the method is described step by step for everyday cooking."
        )
        item = _build_source_item(source_text)
        draft = create_draft_skeleton(item, created_at="2026-04-03T12:00:00+00:00")
        draft.intro_text = "This kitchen behavior surprises a lot of people because heat, moisture, and structure all work together."
        draft.sections = [
            replace(
                draft.sections[0],
                body_blocks=[
                    "When the balance shifts, the result changes quickly in the pan. Understanding that pattern helps cooks get more reliable outcomes at home."
                ],
            ),
            replace(
                draft.sections[1],
                body_blocks=[
                    "The same explanation shows up again when the method is described step by step for everyday cooking. That repeated structure should keep the derivative risk high."
                ],
            ),
            replace(
                draft.sections[2],
                bullet_points=[
                    "Heat, moisture, and structure all work together.",
                    "The balance shifts quickly in the pan.",
                    "Reliable outcomes come from understanding the pattern.",
                ],
            ),
            replace(
                draft.sections[3],
                body_blocks=[
                    "This version still follows the source too closely and does not create enough distance from the original phrasing."
                ],
            ),
        ]

        result = evaluate_draft_quality(draft, item)

        self.assertEqual(result.quality_gate_status, "blocked")
        self.assertEqual(result.derivative_risk_level, "high")
        self.assertIn("derivative_risk_high", result.quality_flags)

    def test_evaluate_draft_quality_review_flags_clicky_title_and_medium_overlap(self) -> None:
        source_text = (
            "Black beans work well in soups, bowls, and practical weeknight meals. "
            "They are dependable pantry ingredients that help stretch simple cooking across several meals."
        )
        item = _build_source_item(source_text, template_suggestion="food_benefit_article")
        draft = create_draft_skeleton(
            item,
            template_contract=get_blog_template_contract("blog_food_benefit_v1"),
            created_at="2026-04-03T12:00:00+00:00",
        )
        draft.headline_selected = "The Secret Reason Black Beans Work So Well"
        draft.intro_text = (
            "Black beans are practical pantry ingredients that make weeknight meals easier to plan. "
            "They also help keep pantry cooking flexible across the week."
        )
        draft.sections = [
            replace(
                draft.sections[0],
                body_blocks=[
                    "They are easy to work into soups and bowls when dinner needs to stay simple. They are dependable pantry ingredients that help stretch simple cooking when a meal plan needs more range."
                ],
            ),
            replace(
                draft.sections[1],
                bullet_points=[
                    "They fit soups and bowls easily.",
                    "They help stretch pantry meals.",
                    "They stay practical on busy nights.",
                    "They give simple meal plans more flexibility.",
                ],
            ),
            replace(
                draft.sections[2],
                body_blocks=[
                    "Their usefulness is practical rather than magical or extreme. The ingredient still works best as one dependable part of a broader meal routine."
                ],
            ),
            replace(
                draft.sections[3],
                body_blocks=[
                    "That makes them helpful, even if the wording is still a little close to the source. The structure is usable, but the tone and overlap should still trigger review."
                ],
            ),
        ]

        result = evaluate_draft_quality(draft, item)

        self.assertEqual(result.quality_gate_status, "review_flag")
        self.assertEqual(result.derivative_risk_level, "medium")
        self.assertIn("title_clicky", result.quality_flags)

    def test_evaluate_draft_quality_passes_low_risk_complete_draft(self) -> None:
        source_text = (
            "Cooks often notice better pan results once they understand that moisture and temperature affect texture together. "
            "A simple explanation can make the pattern easier to repeat in everyday cooking. "
            "That kind of kitchen knowledge is more useful when it is short, clear, and practical."
        )
        item = _build_source_item(source_text)
        draft = create_draft_skeleton(item, created_at="2026-04-03T12:00:00+00:00")
        draft.headline_selected = "Why Small Kitchen Patterns Often Lead To Better Results"
        draft.intro_text = (
            "Good kitchen habits usually come from understanding a simple pattern early, not from memorizing dozens of separate tricks or disconnected tips. A short explanation often makes the next cooking decision feel much easier and much more repeatable at home."
        )
        draft.sections = [
            replace(
                draft.sections[0],
                body_blocks=[
                    "The short answer is that better results usually come from noticing a few repeatable conditions before the food even finishes cooking. That framing moves the article away from isolated tricks and toward a clearer kitchen pattern.",
                    "It also helps readers understand why the result feels more stable once the same signals are watched consistently from one attempt to the next.",
                ],
            ),
            replace(
                draft.sections[1],
                body_blocks=[
                    "That matters because surface dryness, pan temperature, and ingredient thickness all shape the final texture in small but predictable ways. Seen together, those details explain the pattern without turning the draft into a copy of the source.",
                    "The explanation stays useful because it connects the pattern to decisions people actually make at the stove instead of repeating the original article's structure. That added context keeps the section comfortably within the contract and helps the reader understand why the pattern stays stable over time.",
                ],
            ),
            replace(
                draft.sections[2],
                bullet_points=[
                    "Notice how moisture changes browning speed before the pan ever looks finished or fully settled.",
                    "Use steady heat instead of chasing fast color that can hide the real pattern underneath.",
                    "Read small texture clues as usable feedback instead of treating them as random kitchen noise.",
                    "Keep the method consistent long enough to learn the pattern and repeat it with confidence later.",
                ],
            ),
            replace(
                draft.sections[3],
                body_blocks=[
                    "Once the pattern is clear, it becomes much easier to repeat the result with confidence in later meals. That gives the reader a practical takeaway instead of another vague food fact.",
                ],
            ),
        ]

        result = evaluate_draft_quality(draft, item)

        self.assertEqual(result.quality_gate_status, "pass")
        self.assertEqual(result.derivative_risk_level, "low")
        self.assertEqual(result.quality_flags, ())

    def test_evaluate_draft_quality_blocks_missing_required_fields(self) -> None:
        item = _build_source_item(
            "A long enough source body that should not matter because the draft itself is incomplete and missing key lineage fields."
        )
        draft = create_draft_skeleton(item, created_at="2026-04-03T12:00:00+00:00")
        draft.source_url = ""
        draft.headline_selected = ""

        result = evaluate_draft_quality(draft, item)

        self.assertEqual(result.quality_gate_status, "blocked")
        self.assertIn("missing_source_url", result.quality_flags)
        self.assertIn("missing_headline", result.quality_flags)

    def test_evaluate_draft_quality_review_flags_semantic_profile_risks(self) -> None:
        source_text = (
            "A short food explanation can still be structurally complete while pointing at the wrong terms. "
            "That is exactly the kind of draft this semantic profile is meant to catch before queueing."
        )
        item = _build_source_item(source_text)
        draft = create_draft_skeleton(item, created_at="2026-04-03T12:00:00+00:00")
        draft.headline_selected = "Why A Simple Food Explanation Still Needs Good Anchors"
        draft.intro_text = (
            "Good content quality starts with the right subject and the right supporting details. "
            "When those anchors drift, the draft can look finished while still sounding wrong. "
            "That is why semantic gates need to sit beside structural ones instead of waiting for operator cleanup."
        )
        draft.sections = [
            replace(
                draft.sections[0],
                body_blocks=[
                    "The direct answer should stay focused on the real food point instead of filler phrasing that only sounds specific. "
                    "A draft that misses the subject early rarely recovers later, even when every section is technically present."
                ],
            ),
            replace(
                draft.sections[1],
                body_blocks=[
                    "That is why deterministic quality checks matter. They help catch weak semantic framing before manual review time is wasted. "
                    "The goal is to spend human attention on meaningful polish, not on rescuing drafts with broken anchors."
                ],
            ),
            replace(
                draft.sections[2],
                bullet_points=[
                    "Keep the subject anchor clear.",
                    "Use body-supported support terms.",
                    "Review recipe-heavy context separately.",
                    "Do not trust fragment-like phrasing.",
                ],
            ),
            replace(
                draft.sections[3],
                body_blocks=[
                    "A content system gets stronger when semantic quality is part of the gate instead of a manual surprise. "
                    "That keeps the queue cleaner and makes later distribution work more trustworthy."
                ],
            ),
        ]

        result = evaluate_draft_quality(
            draft,
            item,
            semantic_profile={
                "low_signal_topic_term_count": 2,
                "body_supported_topic_term_count": 1,
                "recipe_like_paragraph_ratio": 0.52,
                "noise_like_paragraph_ratio": 0.0,
            },
        )

        self.assertEqual(result.quality_gate_status, "review_flag")
        self.assertIn("semantic_term_noise", result.quality_flags)
        self.assertIn("source_context_recipe_heavy", result.quality_flags)
        self.assertIn("anchor_title_mismatch", result.quality_flags)

    def test_evaluate_draft_quality_review_flags_slot_guidance_issues(self) -> None:
        source_text = (
            "A clean food fact draft still needs the right section pacing, enough support detail, and a fast answer early in the article. "
            "Without those constraints, a technically complete draft can still feel weak and under-explained."
        )
        item = _build_source_item(source_text)
        draft = create_draft_skeleton(item, created_at="2026-04-03T12:00:00+00:00")
        draft.headline_selected = "Why Section-Level Template Rules Matter For Food Facts"
        draft.intro_text = (
            "This introduction is intentionally much longer than the template wants because it keeps adding filler context about structure, workflow, pacing, review behavior, deterministic formatting, editorial cleanup, acceptance criteria, and quality reports before it ever gets to the answer section that readers actually need to see early in the piece. It also adds another sentence about process discipline, draft governance, contract enforcement, and operator time so the answer lands later than it should in an answer-first article. A third sentence keeps pushing the answer back by talking about reviewer effort, implementation polish, operational clarity, acceptance packs, documentation quality, and residual-risk bookkeeping instead of getting to the actual food fact. A fourth sentence adds even more process talk about template audits, rollout safety, and revision tracking so the answer clearly starts too late for the contract."
        )
        draft.sections = [
            replace(
                draft.sections[0],
                body_blocks=[
                    "The direct answer is present, but it shows up late because the introduction already used most of the early article space. That makes the structure less answer-first than the contract expects."
                ],
            ),
            replace(
                draft.sections[1],
                body_blocks=[
                    "The explanation section is still usable because it names the structural issue clearly and stays away from source copying. It focuses on why a template needs stronger contract enforcement instead of acting like loose prose guidance is enough."
                ],
            ),
            replace(
                draft.sections[2],
                bullet_points=[
                    "Only one supporting point is present here, so the section should trigger a bullet-count review flag."
                ],
            ),
            replace(
                draft.sections[3],
                body_blocks=[
                    "The recap stays short and clear so the draft remains reviewable even though several slot-level template checks should fire."
                ],
            ),
        ]

        result = evaluate_draft_quality(draft, item)

        self.assertEqual(result.quality_gate_status, "review_flag")
        self.assertIn("intro_length_outside_target", result.quality_flags)
        self.assertIn("direct_answer_position_too_late", result.quality_flags)
        self.assertIn("supporting_points_bullet_count_outside_target", result.quality_flags)


if __name__ == "__main__":
    unittest.main()
