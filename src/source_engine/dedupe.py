from __future__ import annotations

import json
import re
from pathlib import Path

from source_engine.models import DedupeResult, SourceItem


TITLE_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")
STOPWORDS = {"a", "an", "and", "the", "of", "to", "in", "is", "this", "that", "for", "with"}


def load_dedupe_index(path: Path) -> dict[str, dict[str, str] | dict[str, list[str]]]:
    if not path.exists():
        return {"canonical_urls": {}, "normalized_titles": {}, "title_tokens": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_dedupe_index(path: Path, index: dict[str, dict[str, str] | dict[str, list[str]]]) -> None:
    path.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")


def check_duplicate(
    item: SourceItem, index: dict[str, dict[str, str] | dict[str, list[str]]]
) -> DedupeResult:
    canonical_urls = index.get("canonical_urls", {})
    if item.canonical_url in canonical_urls:
        return DedupeResult(
            status="exact_duplicate",
            reason="canonical_url_match",
            matched_item_id=canonical_urls[item.canonical_url],
        )

    normalized_titles = index.get("normalized_titles", {})
    normalized_title = normalize_title(item.raw_title)
    if normalized_title in normalized_titles:
        return DedupeResult(
            status="near_duplicate",
            reason="normalized_title_match",
            matched_item_id=normalized_titles[normalized_title],
        )

    candidate_tokens = title_tokens(item.raw_title)
    title_token_index = index.get("title_tokens", {})
    for existing_item_id, existing_tokens in title_token_index.items():
        similarity = token_similarity(candidate_tokens, set(existing_tokens))
        if similarity >= 0.85:
            return DedupeResult(
                status="near_duplicate",
                reason=f"title_token_similarity:{similarity:.2f}",
                matched_item_id=existing_item_id,
            )

    return DedupeResult(status="unique", reason="no_duplicate_match")


def update_dedupe_index(
    item: SourceItem, index: dict[str, dict[str, str] | dict[str, list[str]]]
) -> dict[str, dict[str, str] | dict[str, list[str]]]:
    index.setdefault("canonical_urls", {})[item.canonical_url] = item.item_id
    index.setdefault("normalized_titles", {})[normalize_title(item.raw_title)] = item.item_id
    index.setdefault("title_tokens", {})[item.item_id] = sorted(title_tokens(item.raw_title))
    return index


def normalize_title(title: str) -> str:
    lowered = title.lower()
    return TITLE_NORMALIZE_RE.sub(" ", lowered).strip()


def title_tokens(title: str) -> set[str]:
    normalized = normalize_title(title)
    return {token for token in normalized.split() if token and token not in STOPWORDS}


def token_similarity(first: set[str], second: set[str]) -> float:
    if not first or not second:
        return 0.0
    intersection = len(first & second)
    union = len(first | second)
    return intersection / union if union else 0.0
