from __future__ import annotations

from dataclasses import dataclass

from source_engine.models import SourceRecord


VALID_SOURCE_STATUSES = {
    "active",
    "active_primary",
    "active_secondary",
    "active_selective",
    "downgraded",
    "paused",
    "retired",
    "watchlist",
}
NON_INTAKE_STATUSES = {"paused", "retired", "watchlist"}
STATUS_ORDER = {
    "active_primary": 0,
    "active_secondary": 1,
    "active_selective": 2,
    "downgraded": 3,
    "active": 4,
    "watchlist": 5,
    "paused": 6,
    "retired": 7,
}


@dataclass(frozen=True)
class SourceReviewSnapshot:
    current_status: str
    reviewed_items: int
    strong_candidates: int
    weak_or_repetitive_items: int
    fetch_failures: int = 0


@dataclass(frozen=True)
class SourceStatusRecommendation:
    next_status: str
    reason: str


def validate_source_status(record: SourceRecord) -> None:
    if record.status not in VALID_SOURCE_STATUSES:
        raise ValueError(
            f"Source registry record {record.source_id} has invalid status: {record.status}"
        )
    if record.active and record.status in NON_INTAKE_STATUSES:
        raise ValueError(
            f"Source registry record {record.source_id} cannot be active while status is {record.status}"
        )


def status_allows_intake(record: SourceRecord) -> bool:
    return record.active and record.status not in NON_INTAKE_STATUSES


def source_sort_key(record: SourceRecord) -> tuple[int, str, str]:
    return (STATUS_ORDER.get(record.status, 99), record.priority_level, record.source_name.lower())


def recommend_source_status(snapshot: SourceReviewSnapshot) -> SourceStatusRecommendation:
    weak_ratio = (
        snapshot.weak_or_repetitive_items / snapshot.reviewed_items
        if snapshot.reviewed_items
        else 0.0
    )

    if snapshot.fetch_failures >= 3:
        return SourceStatusRecommendation(
            next_status="paused",
            reason="repeated_fetch_failures",
        )
    if snapshot.reviewed_items >= 4 and weak_ratio >= 0.75:
        return SourceStatusRecommendation(
            next_status="paused",
            reason="mostly_weak_or_repetitive_items",
        )
    if snapshot.reviewed_items >= 4 and snapshot.strong_candidates == 0:
        return SourceStatusRecommendation(
            next_status="downgraded",
            reason="zero_strong_candidates_after_review_window",
        )
    if snapshot.current_status == "watchlist" and snapshot.strong_candidates >= 1:
        return SourceStatusRecommendation(
            next_status="active_selective",
            reason="watchlist_source_produced_strong_candidate",
        )
    if snapshot.current_status == "downgraded" and snapshot.strong_candidates >= 1:
        return SourceStatusRecommendation(
            next_status="active_selective",
            reason="downgraded_source_recovered",
        )
    return SourceStatusRecommendation(
        next_status=snapshot.current_status,
        reason="status_unchanged",
    )
