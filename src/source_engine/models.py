from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    source_name: str
    domain: str
    source_family: str
    source_type: str
    primary_topic_fit: str
    active: bool
    priority_level: str
    rss_feed_url: str | None
    fetch_method: str
    body_extraction_required: bool
    freshness_pattern: str
    quality_notes: str
    risk_notes: str
    created_at: str
    updated_at: str
    status: str = "active"
    week_one_target_reviews: int | None = None
    last_reviewed_at: str | None = None
    last_status_reason: str | None = None
    last_review_notes: str | None = None
    retirement_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SourceItem:
    item_id: str
    source_id: str
    source_name: str
    source_family: str
    run_id: str | None
    source_url: str
    canonical_url: str
    discovered_at: str
    fetched_at: str
    raw_title: str
    raw_summary: str
    raw_body_text: str
    author_name: str | None
    published_at: str | None
    topical_label: str
    freshness_label: str
    normalization_status: str
    dedupe_status: str
    body_extraction_status: str | None = None
    body_word_count: int | None = None
    quality_flags: list[str] = field(default_factory=list)
    template_suggestion: str | None = None
    normalized_title: str | None = None
    content_hash: str | None = None
    matched_item_id: str | None = None
    dedupe_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FetchEntry:
    title: str
    link: str
    summary: str
    content: str
    author_name: str | None
    published_at: str | None


@dataclass
class FetchResult:
    source_id: str
    source_name: str
    feed_url: str | None
    fetched_at: str
    status: str
    item_count: int
    error: str | None = None
    fallback_action: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ArticleBodyResult:
    url: str
    status: str
    body_text: str
    word_count: int
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SourceDecisionRecord:
    decision_id: str
    source_id: str
    source_name: str
    reviewed_at: str
    current_status: str
    recommended_status: str
    final_status: str
    reviewed_items: int
    strong_candidates: int
    weak_or_repetitive_items: int
    fetch_failures: int
    recommendation_reason: str
    reviewer_notes: str | None = None
    applied_to_registry: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DedupeResult:
    status: str
    reason: str
    matched_item_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
