from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.drafts import create_draft_skeleton
from content_engine.routing import recommend_routing_action
from source_engine.models import SourceItem


def _build_source_item(raw_title: str) -> SourceItem:
    return SourceItem(
        item_id="routing-item",
        source_id="src_test",
        source_name="Test Source",
        source_family="food_editorial",
        run_id="run-1",
        source_url="https://example.com/story",
        canonical_url="https://example.com/story",
        discovered_at="2026-04-03T00:00:00+00:00",
        fetched_at="2026-04-03T00:00:00+00:00",
        raw_title=raw_title,
        raw_summary="A short summary about the story.",
        raw_body_text=(
            "This source body is long enough to satisfy draft creation and routing tests. "
            "It exists only to support routing behavior checks in a controlled way."
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


class RoutingTests(unittest.TestCase):
    def test_recommend_routing_action_rejects_blocked_quality(self) -> None:
        item = _build_source_item("Why This Kitchen Trick Works")
        draft = create_draft_skeleton(item, created_at="2026-04-03T12:00:00+00:00")
        draft.quality_gate_status = "blocked"
        draft.quality_flags = ["draft_too_thin"]

        decision = recommend_routing_action(item, draft)

        self.assertEqual(decision.action, "reject_for_v1")
        self.assertIn("blocked_quality_gate", decision.reasons)

    def test_recommend_routing_action_holds_recipe_heavy_sources(self) -> None:
        item = _build_source_item("Tsoureki (Greek Easter Bread)")
        draft = create_draft_skeleton(item, created_at="2026-04-03T12:00:00+00:00")
        draft.quality_gate_status = "review_flag"
        draft.quality_flags = ["source_context_recipe_heavy", "source_context_noisy"]

        decision = recommend_routing_action(item, draft)

        self.assertEqual(decision.action, "hold_for_reroute")
        self.assertIn("source_context_recipe_heavy", decision.reasons)

    def test_recommend_routing_action_holds_listicles(self) -> None:
        item = _build_source_item("10 Italian Street Foods You Need To Try")
        draft = create_draft_skeleton(item, created_at="2026-04-03T12:00:00+00:00")
        draft.quality_gate_status = "review_flag"
        draft.quality_flags = ["semantic_term_noise"]
        draft.derivative_risk_level = "low"

        decision = recommend_routing_action(item, draft)

        self.assertEqual(decision.action, "hold_for_reroute")
        self.assertIn("roundup_or_listicle_title", decision.reasons)

    def test_recommend_routing_action_holds_trailing_sentiment_titles(self) -> None:
        item = _build_source_item("Costco's Automated Pay Stations Are Here \u2014 And Fans Are Underwhelmed")
        draft = create_draft_skeleton(item, created_at="2026-04-03T12:00:00+00:00")
        draft.quality_gate_status = "pass"
        draft.quality_flags = []
        draft.derivative_risk_level = "low"

        decision = recommend_routing_action(item, draft)

        self.assertEqual(decision.action, "hold_for_reroute")
        self.assertIn("trailing_sentiment_clause", decision.reasons)

    def test_recommend_routing_action_reviews_medium_derivative_non_hold_case(self) -> None:
        item = _build_source_item("Sopa Negra (Costa Rican Black Bean Soup)")
        draft = create_draft_skeleton(item, created_at="2026-04-03T12:00:00+00:00")
        draft.quality_gate_status = "review_flag"
        draft.quality_flags = ["derivative_risk_borderline", "derivative_risk_medium"]
        draft.derivative_risk_level = "medium"

        decision = recommend_routing_action(item, draft)

        self.assertEqual(decision.action, "review_only")
        self.assertIn("derivative_risk_medium", decision.reasons)

    def test_recommend_routing_action_holds_recipe_title_with_medium_derivative_risk(self) -> None:
        item = _build_source_item("Red Wine-Braised Short Ribs")
        draft = create_draft_skeleton(item, created_at="2026-04-03T12:00:00+00:00")
        draft.quality_gate_status = "review_flag"
        draft.quality_flags = ["derivative_risk_medium"]
        draft.derivative_risk_level = "medium"

        decision = recommend_routing_action(item, draft)

        self.assertEqual(decision.action, "hold_for_reroute")
        self.assertIn("recipe_title_derivative_medium", decision.reasons)

    def test_recommend_routing_action_holds_venue_novelty_stories(self) -> None:
        item = _build_source_item("This NYC Restaurant Is Supposedly Haunted By Over 20 Ghosts")
        draft = create_draft_skeleton(item, created_at="2026-04-03T12:00:00+00:00")
        draft.quality_gate_status = "pass"
        draft.quality_flags = []
        draft.derivative_risk_level = "low"

        decision = recommend_routing_action(item, draft)

        self.assertEqual(decision.action, "hold_for_reroute")
        self.assertIn("venue_novelty_story", decision.reasons)

    def test_recommend_routing_action_holds_price_comparison_roundups(self) -> None:
        item = _build_source_item("The US States With The Most And Least Expensive McDonald's Big Arch Burger")
        draft = create_draft_skeleton(item, created_at="2026-04-03T12:00:00+00:00")
        draft.quality_gate_status = "pass"
        draft.quality_flags = []
        draft.derivative_risk_level = "low"

        decision = recommend_routing_action(item, draft)

        self.assertEqual(decision.action, "hold_for_reroute")
        self.assertIn("price_comparison_roundup", decision.reasons)

    def test_recommend_routing_action_proceeds_for_clean_fit(self) -> None:
        item = _build_source_item("The Only 2 Foods Jacques Pepin Thinks Twice About Eating")
        draft = create_draft_skeleton(item, created_at="2026-04-03T12:00:00+00:00")
        draft.quality_gate_status = "pass"
        draft.quality_flags = []
        draft.derivative_risk_level = "low"

        decision = recommend_routing_action(item, draft)

        self.assertEqual(decision.action, "proceed")
        self.assertEqual(decision.reasons, ())


if __name__ == "__main__":
    unittest.main()
