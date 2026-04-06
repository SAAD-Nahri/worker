from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.formatting import derive_subject_anchor, evaluate_source_item_eligibility, format_source_item_to_draft
from content_engine.templates import get_blog_template_contract
from source_engine.models import SourceItem


def _build_source_item(
    template_suggestion: str = "food_fact_article",
    dedupe_status: str = "unique",
    raw_body_text: str | None = None,
    raw_title: str = "Why This Kitchen Trick Works",
    raw_summary: str = "A short summary about why the trick works.",
    topical_label: str = "food_explainer",
    source_family: str = "food_editorial",
) -> SourceItem:
    body_text = raw_body_text or (
        "This kitchen behavior surprises a lot of people because the visible result looks simple while the underlying food science is doing several things at once. Heat changes texture, moisture changes timing, and ingredient structure affects how quickly a food reacts in the pan.\n\n"
        "The main reason the trick works is that heat, moisture, and ingredient structure all interact in predictable ways over a short period of time. When one part of that balance changes, cooks often see very different results even when they think they followed the same steps.\n\n"
        "When home cooks understand that relationship, they can get more consistent results and avoid common mistakes that feel random but actually follow a pattern. This makes the kitchen process less frustrating and turns a confusing habit into something practical and repeatable.\n\n"
        "That is why simple food facts often lead to better cooking habits. They give people a quick explanation, a useful takeaway, and a reason to keep using the method with more confidence the next time they cook."
    )
    return SourceItem(
        item_id="item-1234567890ab",
        source_id="src_test",
        source_name="Test Source",
        source_family=source_family,
        run_id="run-1",
        source_url="https://example.com/story",
        canonical_url="https://example.com/story",
        discovered_at="2026-04-03T00:00:00+00:00",
        fetched_at="2026-04-03T00:00:00+00:00",
        raw_title=raw_title,
        raw_summary=raw_summary,
        raw_body_text=body_text,
        author_name=None,
        published_at="2026-04-01T00:00:00+00:00",
        topical_label=topical_label,
        freshness_label="fresh",
        normalization_status="normalized",
        dedupe_status=dedupe_status,
        quality_flags=[],
        template_suggestion=template_suggestion,
    )


class FormattingTests(unittest.TestCase):
    def test_evaluate_source_item_eligibility_rejects_duplicate_blocked_item(self) -> None:
        item = _build_source_item(dedupe_status="duplicate_blocked")

        result = evaluate_source_item_eligibility(item)

        self.assertFalse(result.is_eligible)
        self.assertIn("non_unique_source_item:duplicate_blocked", result.reasons)

    def test_evaluate_source_item_eligibility_rejects_exact_duplicate_item(self) -> None:
        item = _build_source_item(dedupe_status="exact_duplicate")

        result = evaluate_source_item_eligibility(item)

        self.assertFalse(result.is_eligible)
        self.assertIn("non_unique_source_item:exact_duplicate", result.reasons)

    def test_format_source_item_to_draft_fills_intro_sections_and_excerpt(self) -> None:
        item = _build_source_item()

        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")

        self.assertTrue(draft.intro_text)
        self.assertTrue(draft.excerpt)
        self.assertEqual(draft.template_id, "blog_food_fact_v1")
        self.assertEqual(draft.quality_gate_status, "pass")
        self.assertEqual(draft.quality_flags, [])
        self.assertEqual(draft.category, "food-facts")
        self.assertGreaterEqual(len(draft.tag_candidates), 3)
        self.assertTrue(all(section.body_blocks or section.bullet_points for section in draft.sections))

    def test_format_source_item_to_draft_builds_bullets_for_benefit_points(self) -> None:
        item = _build_source_item(
            template_suggestion="food_benefit_article",
            raw_body_text=(
                "Black beans are filling and easy to use in everyday meals, which is one reason they show up in so many practical home kitchens. They are inexpensive, versatile, and easy to pair with vegetables, rice, soups, and other pantry staples.\n\n"
                "They work well in soups, bowls, and simple weeknight dishes because they add body without demanding complicated prep work. That makes them useful for cooks who want food that feels hearty but still manageable on a busy day.\n\n"
                "They also make it easier to build meals around pantry ingredients because they store well and combine with many different flavors. A pot of beans can stretch across several meals with only a few small changes in seasoning or presentation.\n\n"
                "That is helpful when cooking needs to stay practical and affordable. The value is not in exaggerated claims, but in how dependable the ingredient is when people want food that is simple, satisfying, and easy to keep in rotation."
            ),
        )

        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")
        practical_points = next(section for section in draft.sections if section.section_key == "practical_points")

        self.assertGreaterEqual(len(practical_points.bullet_points), 1)
        self.assertFalse(any(flag.endswith("_length_outside_target") for flag in draft.quality_flags))
        self.assertFalse(any(flag.endswith("_bullet_count_outside_target") for flag in draft.quality_flags))
        self.assertEqual(draft.category, "food-benefits-light")
        self.assertIn("ingredient-basics", draft.tag_candidates)
        self.assertIn("meal-planning", draft.tag_candidates)

    def test_format_source_item_to_draft_keeps_curiosity_template_within_contract(self) -> None:
        item = _build_source_item(
            template_suggestion="curiosity_article",
            raw_title="Why Do Some Cheeses Taste Sharper As They Age?",
            raw_summary="A short food curiosity about aging, texture, and flavor development in familiar cheeses.",
            raw_body_text=(
                "Cheese tastes sharper with age because moisture, enzymes, and time change the texture and flavor in ways that become easier to notice over months of storage. "
                "As the cheese loses water, the flavor feels more concentrated and the structure becomes firmer.\n\n"
                "That process matters because people often describe sharpness as if it were only about heat or intensity, when it is really about how flavor compounds develop and stand out over time. "
                "The same cheese can feel much more assertive later because the balance inside it keeps changing.\n\n"
                "A familiar example is cheddar, which can move from mild and creamy to crumbly and much more pronounced as it ages. "
                "That makes the question easier to understand because the sharper taste is tied to an ordinary process, not a mysterious ingredient.\n\n"
                "The useful answer is that aging changes both flavor concentration and texture. "
                "Once that is clear, the headline question stops sounding mysterious and starts feeling like a practical food explanation."
            ),
        )

        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")

        self.assertEqual(draft.template_id, "blog_curiosity_food_v1")
        self.assertEqual(draft.quality_gate_status, "pass")
        self.assertEqual(draft.quality_flags, [])

    def test_format_source_item_to_draft_rejects_mismatched_template_override(self) -> None:
        item = _build_source_item(template_suggestion="food_fact_article")

        with self.assertRaisesRegex(ValueError, "Template override does not match"):
            format_source_item_to_draft(
                item,
                template_contract=get_blog_template_contract("blog_curiosity_food_v1"),
                created_at="2026-04-03T12:00:00+00:00",
            )

    def test_format_source_item_to_draft_overrides_category_for_ingredient_guides(self) -> None:
        item = _build_source_item(
            raw_title="How Yogurt Changes In The Fridge",
            topical_label="ingredient_explainer",
            source_family="ingredient_reference",
            raw_body_text=(
                "Yogurt changes in the fridge because temperature, moisture, and storage time affect texture in predictable ways. "
                "The ingredient can separate, thicken, or lose some of its initial smoothness depending on how it is stored and how often it is moved.\n\n"
                "That is useful for home cooks because it explains why yogurt behaves differently across meals and recipes. "
                "Once the storage pattern is clear, the ingredient is easier to use with confidence.\n\n"
                "This matters in practice because cooks often want the ingredient to stay dependable for sauces, breakfasts, marinades, and simple snacks. "
                "A short guide to the storage pattern helps them understand why the same container can feel thinner on one day and thicker on another.\n\n"
                "That kind of explanation turns an ordinary ingredient into something easier to plan around. "
                "It also gives the article a cleaner guide shape instead of a vague food fact."
            ),
        )

        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")

        self.assertEqual(draft.category, "ingredient-guides")
        self.assertIn("ingredient-basics", draft.tag_candidates)
        self.assertGreaterEqual(len(draft.tag_candidates), 3)

    def test_format_source_item_to_draft_overrides_category_for_food_history(self) -> None:
        item = _build_source_item(
            template_suggestion="curiosity_article",
            raw_title="What Is The Oldest Soup Tradition Still Served Today?",
            topical_label="food_history",
            source_family="curiosity_editorial",
            raw_body_text=(
                "The oldest soup traditions often survive because they are tied to regional identity, seasonal ingredients, and long cooking habits that remain practical over time. "
                "A dish can stay relevant for centuries when it keeps both cultural meaning and everyday usefulness.\n\n"
                "That historical context matters because food stories are often preserved through family routines, public celebrations, and restaurant menus. "
                "The result is a food tradition that stays alive long after its original context has changed.\n\n"
                "This kind of question also works well as a curiosity article because readers want both a fast answer and enough background to understand why the tradition lasted. "
                "The point is not only to name an old dish, but to show how origin, culture, and repeated use keep a food story alive.\n\n"
                "That gives the draft enough material to explain the historical pattern in a short mobile-friendly way. "
                "It also clearly belongs in the history and culture side of the taxonomy."
            ),
        )

        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")

        self.assertEqual(draft.category, "food-history-culture")
        self.assertIn("food-history", draft.tag_candidates)
        self.assertIn("food-origins", draft.tag_candidates)

    def test_format_source_item_to_draft_flags_recipe_heavy_source_context(self) -> None:
        item = _build_source_item(
            raw_title="Tsoureki (Greek Easter Bread)",
            raw_summary=(
                "Photo: Matt Taylor-Gross • Food Styling: Ben Weiner "
                "This eye-catching braided loaf is traditionally baked with a red-dyed egg on top. "
                "The post Tsoureki (Greek Easter Bread) appeared first on Saveur."
            ),
            raw_body_text=(
                "Also known as lambropsomo, tsoureki is a sweet, brioche-like Greek Easter bread that's braided and shaped into a circle or two long loaves. "
                "It's typically perfumed with mahlepi, decorated with red-dyed eggs, and associated with spring and new life.\n\n"
                "Time 1 hour 30 minutes, plus rising and cooling.\n\n"
                "Photo: Matt Taylor-Gross • Food Styling: Ben Weiner Ingredients.\n\n"
                "8 Tbsp. unsalted butter, melted and cooled, plus more for greasing.\n\n"
                "In a large bowl, stir together the milk and yeast until the yeast is dissolved. Stir in flour and sugar, then let the mixture sit until foamy.\n\n"
                "This eye-catching braided loaf is traditionally baked with a red-dyed egg on top. The bread stands out because it combines festive symbolism with a soft, rich texture.\n\n"
                "Meanwhile, position a rack in the center of the oven and preheat to 350F. Brush the bread with egg wash and bake until deep golden brown."
            ),
        )

        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")

        self.assertIn("Greek Easter Bread", draft.intro_text)
        self.assertNotIn("photo", draft.intro_text.lower())
        self.assertNotIn("matt", draft.intro_text.lower())
        self.assertIn("source_context_recipe_heavy", draft.quality_flags)

    def test_format_source_item_to_draft_prefers_body_supported_food_terms_over_summary_fragments(self) -> None:
        item = _build_source_item(
            raw_title="The Only 2 Foods Jacques Pépin Thinks Twice About Eating",
            raw_summary=(
                "Jacques Pépin is famously openminded about eating different types of food, "
                "but two exceptions prove he'll draw the line somewhere, just not where you may think."
            ),
            raw_body_text=(
                "George Rose/Getty Images We may receive a commission on purchases made from links.\n\n"
                "For all the accolades Jacques Pépin has earned, it is notable that he rarely dismisses ingredients outright. "
                "That is why people pay attention when he says a food is not really for him.\n\n"
                "In an interview, the chef explained that he is not crazy about coconut and also does not care for marshmallows. "
                "Those are the two foods he most clearly singles out, even though he stays open to almost everything else.\n\n"
                "That contrast is what makes the fact interesting. It is less about being picky and more about how unusual it is for a famously curious cook to name two clear exceptions.\n\n"
                "The useful version of the story is simple: the answer is coconut and marshmallows, and the context is that the opinion stands out precisely because it is so rare for him."
            ),
        )

        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")

        self.assertNotIn("prove he'll", draft.intro_text.lower())
        self.assertTrue("coconut" in draft.intro_text.lower() or "marshmallow" in draft.intro_text.lower())

    def test_derive_subject_anchor_skips_trailing_sentiment_clause(self) -> None:
        item = _build_source_item(
            raw_title="Costco's Automated Pay Stations Are Here — And Fans Are Underwhelmed",
            raw_summary=(
                "Costco has finally responded to long checkout-line complaints with a self-checkout option, "
                "but customers are confused, to say the least."
            ),
            raw_body_text=(
                "One of the biggest differences between Sam's Club and Costco is the time-saving checkout experience. "
                "Costco members have long wanted a faster process that feels closer to Scan and Go.\n\n"
                "Costco has started testing automated pay stations in select warehouses. "
                "The change is real, but customer reaction has been mixed because the process still depends on employee scanning.\n\n"
                "That is why the story works better as a consumer-news item than a timeless food fact. "
                "The subject is the automated pay-station rollout itself, not the trailing sentiment phrase.\n\n"
                "The article is still useful as a formatting test because it shows how a dashed title can split into a real subject and a trailing reaction clause. "
                "That makes it a strong guardrail case for future title handling changes."
            ),
        )

        subject_anchor = derive_subject_anchor(item)
        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")

        self.assertEqual(subject_anchor, "Costco's Automated Pay Stations Are Here")
        self.assertIn("Costco's Automated Pay Stations Are Here", draft.intro_text)
        self.assertNotIn("The main point here is And Fans Are Underwhelmed", draft.intro_text)

    def test_derive_subject_anchor_preserves_hyphenated_food_titles(self) -> None:
        item = _build_source_item(
            raw_title="Maryland Half-and-Half Crab Soup",
            raw_summary=(
                "Photo: Doaa Elkady • Food Styling: Thu Buser • Props: Bowls by Jono Pandolfi "
                "Combining both styles of the state's famous dish, this recipe is a cross between a creamy bisque and a brothy chowder."
            ),
            raw_body_text=(
                "Maryland crab soup typically comes in two forms: a rich, creamy style and a brothy, vegetable-packed version. "
                "But the real pro move is to mix them together for what Marylanders often call half-and-half soup.\n\n"
                "This recipe takes the best of that approach by combining the two soups into one for something that's creamy and substantial but still loaded with vegetables. "
                "It is the best of both worlds for people who want the full Maryland idea in one bowl.\n\n"
                "Combining both styles of the state's famous dish, this recipe is a cross between a creamy bisque and a brothy chowder. "
                "That is also why the title should stay intact instead of being split at the internal hyphen."
            ),
        )

        subject_anchor = derive_subject_anchor(item)

        self.assertEqual(subject_anchor, "Maryland Half-and-Half Crab Soup")

    def test_format_source_item_to_draft_filters_props_credit_from_summary_terms(self) -> None:
        item = _build_source_item(
            raw_title="Maryland Half-and-Half Crab Soup",
            raw_summary=(
                "Photo: Doaa Elkady • Food Styling: Thu Buser • Props: Bowls by Jono Pandolfi "
                "Combining both styles of the state's famous dish, this recipe is a cross between a creamy bisque and a brothy chowder."
            ),
            raw_body_text=(
                "Maryland crab soup typically comes in two forms: a rich, creamy style and a brothy, vegetable-packed version. "
                "But the real pro move is to mix them together for what Marylanders often call half-and-half soup.\n\n"
                "This recipe takes the best of that approach by combining the two soups into one for something that's creamy and substantial but still loaded with vegetables. "
                "It is the best of both worlds for people who want the full Maryland idea in one bowl.\n\n"
                "Combining both styles of the state's famous dish, this recipe is a cross between a creamy bisque and a brothy chowder. "
                "That is also why the cleaned intro should not carry photo-credit names into the topic terms.\n\n"
                "The point of the explainer is not to reproduce the recipe card. "
                "The point is to preserve the recognizable Maryland title while keeping the supporting language free of photo and props credits."
            ),
        )

        draft = format_source_item_to_draft(item, created_at="2026-04-03T12:00:00+00:00")

        self.assertIn("Maryland Half-and-Half Crab Soup", draft.intro_text)
        self.assertNotIn("jono", draft.intro_text.lower())
        self.assertNotIn("pandolfi", draft.intro_text.lower())

    def test_format_source_item_to_draft_raises_for_insufficient_text(self) -> None:
        item = _build_source_item(raw_body_text="Too short.")

        with self.assertRaises(ValueError):
            format_source_item_to_draft(item)


if __name__ == "__main__":
    unittest.main()
