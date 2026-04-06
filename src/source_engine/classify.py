from __future__ import annotations

from source_engine.models import SourceItem


CURIOUS_PREFIXES = ("why ", "what ", "how ", "who ", "where ")
CURIOUS_KEYWORDS = {
    "oldest",
    "founded",
    "happens",
    "called",
    "trick",
    "capital",
    "history",
}
BENEFIT_KEYWORDS = {
    "best",
    "benefit",
    "benefits",
    "healthy",
    "healthiest",
    "unhealthiest",
    "good for",
}
KITCHEN_KEYWORDS = {"trick", "technique", "hack", "cooling rack", "fried", "eggs"}
HISTORY_KEYWORDS = {"oldest", "history", "founded", "capital", "origin"}
INGREDIENT_KEYWORDS = {"ingredient", "yogurt", "carrot", "sisig", "coleslaw", "bread", "soup"}


def classify_item(item: SourceItem) -> tuple[str, str]:
    title = item.raw_title.lower()

    if title.startswith(CURIOUS_PREFIXES) or any(keyword in title for keyword in CURIOUS_KEYWORDS):
        template = "curiosity_article"
    elif any(keyword in title for keyword in BENEFIT_KEYWORDS):
        template = "food_benefit_article"
    elif item.source_family == "ingredient_reference":
        template = "food_fact_article"
    else:
        template = "food_fact_article"

    if any(keyword in title for keyword in KITCHEN_KEYWORDS):
        topical_label = "kitchen_tip"
    elif any(keyword in title for keyword in HISTORY_KEYWORDS):
        topical_label = "food_history"
    elif any(keyword in title for keyword in INGREDIENT_KEYWORDS):
        topical_label = "ingredient_explainer"
    elif item.source_family == "curiosity_editorial":
        topical_label = "food_curiosity"
    else:
        topical_label = "food_explainer"

    return template, topical_label
