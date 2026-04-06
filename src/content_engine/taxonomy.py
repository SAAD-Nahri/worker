from __future__ import annotations

import re

from source_engine.cleaner import clean_text
from source_engine.models import SourceItem

from content_engine.models import BlogTemplateContract


ALLOWED_CATEGORIES = frozenset(
    {
        "food-facts",
        "ingredient-guides",
        "food-questions",
        "food-history-culture",
        "food-benefits-light",
    }
)
QUESTION_PREFIXES = ("why ", "what ", "how ", "who ", "where ")
TOPICAL_CATEGORY_OVERRIDES = {
    "ingredient_explainer": "ingredient-guides",
    "food_history": "food-history-culture",
}
TEMPLATE_BASE_TAGS = {
    "food_fact_article": ("practical-cooking", "food-science"),
    "food_benefit_article": ("ingredient-basics", "meal-planning", "pantry-cooking"),
    "curiosity_article": ("question-angle", "food-curiosities"),
}
TOPICAL_LABEL_TAGS = {
    "kitchen_tip": ("kitchen-tips",),
    "ingredient_explainer": ("ingredient-basics",),
    "food_history": ("food-history", "food-origins", "food-culture"),
    "food_curiosity": ("food-curiosities",),
}
KEYWORD_TAG_RULES = (
    (("heat", "moisture", "texture", "temperature", "browning", "science"), "food-science"),
    (("pantry", "weeknight", "meal", "meals", "staples"), "meal-planning"),
    (("pantry", "staples", "beans"), "pantry-cooking"),
    (("storage", "stored", "store", "shelf"), "food-storage"),
    (("origin", "origins", "history", "founded", "century"), "food-origins"),
    (("culture", "cultural", "traditional", "regional", "cuisine"), "food-culture"),
    (("myth", "trick", "hack"), "kitchen-myths"),
    (("tip", "tips", "technique", "method"), "kitchen-tips"),
)
GENERIC_TAG_TERMS = {
    "benefit",
    "benefits",
    "fact",
    "facts",
    "food",
    "guide",
    "guides",
    "history",
    "ingredient",
    "ingredients",
    "kitchen",
    "meal",
    "meals",
    "question",
    "questions",
    "result",
    "results",
}
CONTROLLED_TAGS = frozenset(
    {
        "food-science",
        "practical-cooking",
        "ingredient-basics",
        "meal-planning",
        "pantry-cooking",
        "question-angle",
        "food-curiosities",
        "food-history",
        "food-origins",
        "food-culture",
        "kitchen-tips",
        "kitchen-myths",
        "food-storage",
    }
)
TAG_RE = re.compile(r"[^a-z0-9]+")


def assign_category_and_tags(
    source_item: SourceItem,
    template_contract: BlogTemplateContract,
    topic_terms: list[str],
) -> tuple[str, list[str]]:
    category = _select_primary_category(source_item, template_contract)
    tags: list[str] = []
    combined_text = clean_text(
        " ".join(
            [
                source_item.raw_title,
                source_item.raw_summary,
                source_item.raw_body_text,
                " ".join(topic_terms),
            ]
        )
    ).lower()

    _extend_unique(tags, TEMPLATE_BASE_TAGS.get(template_contract.template_family, ()), category)
    _extend_unique(tags, TOPICAL_LABEL_TAGS.get(source_item.topical_label, ()), category)

    if source_item.raw_title.lower().startswith(QUESTION_PREFIXES):
        _extend_unique(tags, ("question-angle",), category)

    for keywords, tag in KEYWORD_TAG_RULES:
        if any(keyword in combined_text for keyword in keywords):
            _extend_unique(tags, (tag,), category)

    if len(tags) < 3:
        _extend_unique(tags, _derive_topic_tags(topic_terms), category)

    if "kitchen-myths" in tags and "kitchen-tips" in tags:
        tags.remove("kitchen-tips")

    return category, tags[:6]


def _select_primary_category(source_item: SourceItem, template_contract: BlogTemplateContract) -> str:
    override = TOPICAL_CATEGORY_OVERRIDES.get(source_item.topical_label)
    if override:
        return override
    return template_contract.default_category


def _derive_topic_tags(topic_terms: list[str]) -> tuple[str, ...]:
    derived: list[str] = []
    for term in topic_terms:
        tag = _normalize_tag(term)
        if not tag:
            continue
        if tag in CONTROLLED_TAGS or tag in ALLOWED_CATEGORIES:
            continue
        if len(tag) > 24 or tag.count("-") > 2:
            continue
        pieces = [piece for piece in tag.split("-") if piece]
        if not pieces or len(pieces) > 2:
            continue
        if all(piece in GENERIC_TAG_TERMS for piece in pieces):
            continue
        derived.append(tag)
        if len(derived) == 3:
            break
    return tuple(derived)


def _normalize_tag(value: str) -> str:
    normalized = TAG_RE.sub("-", clean_text(value).lower()).strip("-")
    return normalized


def _extend_unique(target: list[str], values: tuple[str, ...], category: str) -> None:
    for value in values:
        if value == category:
            continue
        if value not in target:
            target.append(value)
