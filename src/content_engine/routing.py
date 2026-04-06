from __future__ import annotations

from dataclasses import dataclass
import re

from source_engine.cleaner import clean_text
from source_engine.models import SourceItem

from content_engine.models import DraftRecord


LISTICLE_TITLE_RE = re.compile(r"^\d+\b")
TRAILING_SENTIMENT_RE = re.compile(r"(?:\u2014|-)\s+(and|but)\b", re.IGNORECASE)
EXPLAINER_PREFIXES = (
    "how ",
    "what ",
    "why ",
    "which ",
    "when ",
    "where ",
    "the only ",
    "this ",
)
LISTICLE_TERMS = (
    "recipes",
    "foods",
    "dishes",
    "things",
)
RECIPE_TITLE_TERMS = (
    "bread",
    "ribs",
    "soup",
    "stew",
)
VENUE_TERMS = (
    "restaurant",
    "bar",
    "cafe",
    "caf\u00e9",
    "diner",
)
VENUE_NOVELTY_TERMS = (
    "ghost",
    "ghosts",
    "haunted",
    "spirit",
    "spirits",
)
PRICE_COMPARISON_TERMS = (
    "most expensive",
    "least expensive",
    "most and least expensive",
    "cheapest",
    "priciest",
)
PRICE_COMPARISON_SCOPE_TERMS = (
    "states",
    "cities",
    "locations",
    "countries",
    "markets",
)
SEMANTIC_REVIEW_FLAGS = {
    "anchor_title_mismatch",
    "derivative_risk_borderline",
    "derivative_risk_medium",
    "semantic_term_noise",
}
HOLD_FOR_REROUTE_FLAGS = {
    "source_context_noisy",
    "source_context_recipe_heavy",
}


@dataclass(frozen=True)
class RoutingDecision:
    action: str
    reasons: tuple[str, ...]


def recommend_routing_action(source_item: SourceItem, draft: DraftRecord) -> RoutingDecision:
    return recommend_routing_action_for_title(source_item.raw_title, draft)


def recommend_routing_action_for_title(raw_title: str, draft: DraftRecord) -> RoutingDecision:
    title = clean_text(raw_title).lower()
    reasons: list[str] = []

    if draft.quality_gate_status == "blocked":
        reasons.append("blocked_quality_gate")
        return RoutingDecision(action="reject_for_v1", reasons=tuple(reasons))

    hold_flags = [flag for flag in draft.quality_flags if flag in HOLD_FOR_REROUTE_FLAGS]
    if hold_flags:
        reasons.extend(hold_flags)
        return RoutingDecision(action="hold_for_reroute", reasons=tuple(dict.fromkeys(reasons)))

    if _looks_like_listicle_title(title):
        reasons.append("roundup_or_listicle_title")
        return RoutingDecision(action="hold_for_reroute", reasons=tuple(reasons))

    if _has_trailing_sentiment_clause(raw_title):
        reasons.append("trailing_sentiment_clause")
        return RoutingDecision(action="hold_for_reroute", reasons=tuple(reasons))

    if _looks_like_venue_novelty_story(title):
        reasons.append("venue_novelty_story")
        return RoutingDecision(action="hold_for_reroute", reasons=tuple(reasons))

    if _looks_like_price_comparison_title(title):
        reasons.append("price_comparison_roundup")
        return RoutingDecision(action="hold_for_reroute", reasons=tuple(reasons))

    if draft.derivative_risk_level == "medium" and _looks_like_recipe_title(title):
        reasons.append("recipe_title_derivative_medium")
        return RoutingDecision(action="hold_for_reroute", reasons=tuple(reasons))

    semantic_flags = [flag for flag in draft.quality_flags if flag in SEMANTIC_REVIEW_FLAGS]
    if semantic_flags:
        reasons.extend(semantic_flags)
        return RoutingDecision(action="review_only", reasons=tuple(dict.fromkeys(reasons)))

    return RoutingDecision(action="proceed", reasons=())


def _looks_like_listicle_title(title: str) -> bool:
    if not LISTICLE_TITLE_RE.search(title):
        return False
    return "you need to try" in title or any(term in title for term in LISTICLE_TERMS)


def _has_trailing_sentiment_clause(raw_title: str) -> bool:
    return bool(TRAILING_SENTIMENT_RE.search(clean_text(raw_title)))


def _looks_like_recipe_title(title: str) -> bool:
    if any(title.startswith(prefix) for prefix in EXPLAINER_PREFIXES):
        return False
    if "(" in title or ")" in title or "?" in title:
        return False
    words = title.split()
    if len(words) > 8:
        return False
    return any(term in title for term in RECIPE_TITLE_TERMS)


def _looks_like_venue_novelty_story(title: str) -> bool:
    return any(term in title for term in VENUE_TERMS) and any(term in title for term in VENUE_NOVELTY_TERMS)


def _looks_like_price_comparison_title(title: str) -> bool:
    if not any(term in title for term in PRICE_COMPARISON_TERMS):
        return False
    return any(term in title for term in PRICE_COMPARISON_SCOPE_TERMS)
