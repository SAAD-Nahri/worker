from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.templates import (
    get_blog_template_contract,
    list_blog_template_contracts,
    select_blog_template_contract,
)
from source_engine.models import SourceItem


def _build_source_item(template_suggestion: str = "food_fact_article") -> SourceItem:
    return SourceItem(
        item_id="item-1234567890ab",
        source_id="src_test",
        source_name="Test Source",
        source_family="food_editorial",
        run_id="run-1",
        source_url="https://example.com/story",
        canonical_url="https://example.com/story",
        discovered_at="2026-04-03T00:00:00+00:00",
        fetched_at="2026-04-03T00:00:00+00:00",
        raw_title="Why This Kitchen Trick Works",
        raw_summary="Short summary",
        raw_body_text="Useful body text for a source item.",
        author_name=None,
        published_at="2026-04-01T00:00:00+00:00",
        topical_label="food_explainer",
        freshness_label="fresh",
        normalization_status="normalized",
        dedupe_status="unique",
        quality_flags=[],
        template_suggestion=template_suggestion,
    )


class TemplateContractTests(unittest.TestCase):
    def test_list_blog_template_contracts_returns_all_v1_contracts(self) -> None:
        contracts = list_blog_template_contracts()

        self.assertEqual(len(contracts), 3)
        self.assertEqual({contract.template_id for contract in contracts}, {
            "blog_food_fact_v1",
            "blog_food_benefit_v1",
            "blog_curiosity_food_v1",
        })

    def test_get_blog_template_contract_returns_expected_contract(self) -> None:
        contract = get_blog_template_contract("blog_food_fact_v1")

        self.assertEqual(contract.template_family, "food_fact_article")
        self.assertEqual(contract.default_category, "food-facts")
        self.assertEqual(contract.body_section_keys, ("direct_answer", "why_it_happens", "supporting_points", "recap"))
        self.assertIsNotNone(contract.get_slot_guidance("intro"))
        self.assertEqual(contract.get_slot_guidance("supporting_points").min_bullet_count, 2)
        self.assertEqual(contract.get_slot_guidance("direct_answer").max_words_before_slot, 120)

    def test_select_blog_template_contract_uses_source_template_suggestion(self) -> None:
        contract = select_blog_template_contract(_build_source_item(template_suggestion="curiosity_article"))

        self.assertEqual(contract.template_id, "blog_curiosity_food_v1")
        self.assertEqual(contract.default_category, "food-questions")
        self.assertEqual(contract.get_slot_guidance("background_explanation").soft_min_words, 70)

    def test_select_blog_template_contract_rejects_unknown_template_suggestion(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported template_suggestion"):
            select_blog_template_contract(_build_source_item(template_suggestion="not_supported"))


if __name__ == "__main__":
    unittest.main()
