from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from content_engine.routing import recommend_routing_action_for_title
from content_engine.storage import (
    DRAFT_RECORDS_PATH,
    DRAFT_REVIEWS_PATH,
    read_draft_records,
    read_draft_review_records,
)


@dataclass(frozen=True)
class DraftHealthRow:
    draft_id: str
    source_item_id: str
    source_id: str
    source_domain: str
    template_id: str
    category: str
    workflow_state: str
    approval_state: str
    quality_gate_status: str
    derivative_risk_level: str
    quality_flag_count: int
    quality_flags: tuple[str, ...]
    headline_variant_count: int
    has_excerpt: bool
    ai_assistance_count: int
    review_count: int
    latest_review_outcome: str | None
    latest_reviewed_at: str | None
    latest_updated_at: str
    operator_signal: str
    routing_action: str
    routing_reason_count: int
    routing_reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "draft_id": self.draft_id,
            "source_item_id": self.source_item_id,
            "source_id": self.source_id,
            "source_domain": self.source_domain,
            "template_id": self.template_id,
            "category": self.category,
            "workflow_state": self.workflow_state,
            "approval_state": self.approval_state,
            "quality_gate_status": self.quality_gate_status,
            "derivative_risk_level": self.derivative_risk_level,
            "quality_flag_count": self.quality_flag_count,
            "quality_flags": list(self.quality_flags),
            "headline_variant_count": self.headline_variant_count,
            "has_excerpt": self.has_excerpt,
            "ai_assistance_count": self.ai_assistance_count,
            "review_count": self.review_count,
            "latest_review_outcome": self.latest_review_outcome,
            "latest_reviewed_at": self.latest_reviewed_at,
            "latest_updated_at": self.latest_updated_at,
            "operator_signal": self.operator_signal,
            "routing_action": self.routing_action,
            "routing_reason_count": self.routing_reason_count,
            "routing_reasons": list(self.routing_reasons),
        }


@dataclass(frozen=True)
class DraftHealthSummary:
    latest_snapshot_at: str | None
    total_drafts: int
    quality_gate_counts: dict[str, int]
    approval_state_counts: dict[str, int]
    operator_signal_counts: dict[str, int]
    routing_action_counts: dict[str, int]
    category_counts: dict[str, int]
    ai_enriched_drafts: int
    drafts_with_headline_variants: int
    drafts_with_excerpt: int
    top_quality_flags: tuple[tuple[str, int], ...]
    top_routing_reasons: tuple[tuple[str, int], ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "latest_snapshot_at": self.latest_snapshot_at,
            "total_drafts": self.total_drafts,
            "quality_gate_counts": dict(self.quality_gate_counts),
            "approval_state_counts": dict(self.approval_state_counts),
            "operator_signal_counts": dict(self.operator_signal_counts),
            "routing_action_counts": dict(self.routing_action_counts),
            "category_counts": dict(self.category_counts),
            "ai_enriched_drafts": self.ai_enriched_drafts,
            "drafts_with_headline_variants": self.drafts_with_headline_variants,
            "drafts_with_excerpt": self.drafts_with_excerpt,
            "top_quality_flags": [
                {"flag": flag, "count": count} for flag, count in self.top_quality_flags
            ],
            "top_routing_reasons": [
                {"reason": reason, "count": count} for reason, count in self.top_routing_reasons
            ],
        }


def build_draft_health_report(
    draft_records_path: Path | None = None,
    draft_reviews_path: Path | None = None,
) -> tuple[DraftHealthSummary, list[DraftHealthRow]]:
    active_draft_records_path = draft_records_path or DRAFT_RECORDS_PATH
    active_draft_reviews_path = draft_reviews_path or DRAFT_REVIEWS_PATH

    latest_drafts = _latest_draft_snapshots(read_draft_records(active_draft_records_path))
    latest_review_by_draft, review_counts = _latest_review_maps(read_draft_review_records(active_draft_reviews_path))

    rows = [
        _build_row(
            draft=latest_drafts[draft_id],
            latest_review=latest_review_by_draft.get(draft_id),
            review_count=review_counts.get(draft_id, 0),
        )
        for draft_id in latest_drafts
    ]
    rows.sort(key=_row_sort_key)
    return _build_summary(rows), rows


def _latest_draft_snapshots(drafts: list) -> dict[str, object]:
    latest: dict[str, object] = {}
    for draft in drafts:
        latest[draft.draft_id] = draft
    return latest


def _latest_review_maps(reviews: list) -> tuple[dict[str, object], dict[str, int]]:
    latest_by_draft: dict[str, object] = {}
    counts: dict[str, int] = {}
    for review in reviews:
        latest_by_draft[review.draft_id] = review
        counts[review.draft_id] = counts.get(review.draft_id, 0) + 1
    return latest_by_draft, counts


def _build_row(draft, latest_review, review_count: int) -> DraftHealthRow:
    routing = recommend_routing_action_for_title(draft.source_title, draft)
    return DraftHealthRow(
        draft_id=draft.draft_id,
        source_item_id=draft.source_item_id,
        source_id=draft.source_id,
        source_domain=draft.source_domain,
        template_id=draft.template_id,
        category=draft.category,
        workflow_state=draft.workflow_state,
        approval_state=draft.approval_state,
        quality_gate_status=draft.quality_gate_status,
        derivative_risk_level=draft.derivative_risk_level,
        quality_flag_count=len(draft.quality_flags),
        quality_flags=tuple(draft.quality_flags),
        headline_variant_count=len(draft.headline_variants),
        has_excerpt=bool(draft.excerpt.strip()),
        ai_assistance_count=len(draft.ai_assistance_log),
        review_count=review_count,
        latest_review_outcome=getattr(latest_review, "review_outcome", None),
        latest_reviewed_at=getattr(latest_review, "reviewed_at", None),
        latest_updated_at=draft.updated_at,
        operator_signal=_operator_signal(draft),
        routing_action=routing.action,
        routing_reason_count=len(routing.reasons),
        routing_reasons=tuple(routing.reasons),
    )


def _operator_signal(draft) -> str:
    if draft.approval_state == "rejected":
        return "rejected"
    if draft.quality_gate_status == "blocked":
        return "blocked_quality"
    if draft.approval_state == "needs_edits" or draft.workflow_state == "needs_revision":
        return "needs_revision"
    if draft.approval_state == "approved":
        if draft.quality_gate_status == "pass":
            return "approved_ready_for_phase_3"
        return "approved_with_review_flags"
    if draft.approval_state == "pending_review" and draft.quality_gate_status == "review_flag":
        return "review_flag_pending"
    if draft.approval_state == "pending_review" and draft.quality_gate_status == "pass":
        return "ready_for_review"
    return "monitor"


def _row_sort_key(row: DraftHealthRow) -> tuple[int, int, str, str]:
    signal_order = {
        "blocked_quality": 0,
        "needs_revision": 1,
        "review_flag_pending": 2,
        "ready_for_review": 3,
        "approved_with_review_flags": 4,
        "approved_ready_for_phase_3": 5,
        "rejected": 6,
        "monitor": 7,
    }
    routing_order = {
        "reject_for_v1": 0,
        "hold_for_reroute": 1,
        "review_only": 2,
        "proceed": 3,
    }
    return (
        signal_order.get(row.operator_signal, 99),
        routing_order.get(row.routing_action, 99),
        row.latest_updated_at,
        row.draft_id,
    )


def _build_summary(rows: list[DraftHealthRow]) -> DraftHealthSummary:
    quality_gate_counts = Counter(row.quality_gate_status for row in rows)
    approval_state_counts = Counter(row.approval_state for row in rows)
    operator_signal_counts = Counter(row.operator_signal for row in rows)
    routing_action_counts = Counter(row.routing_action for row in rows)
    category_counts = Counter(row.category for row in rows)
    quality_flag_counts = Counter(flag for row in rows for flag in row.quality_flags)
    routing_reason_counts = Counter(reason for row in rows for reason in row.routing_reasons)

    return DraftHealthSummary(
        latest_snapshot_at=max((row.latest_updated_at for row in rows), default=None),
        total_drafts=len(rows),
        quality_gate_counts=dict(quality_gate_counts),
        approval_state_counts=dict(approval_state_counts),
        operator_signal_counts=dict(operator_signal_counts),
        routing_action_counts=dict(routing_action_counts),
        category_counts=dict(category_counts),
        ai_enriched_drafts=sum(1 for row in rows if row.ai_assistance_count > 0),
        drafts_with_headline_variants=sum(1 for row in rows if row.headline_variant_count > 0),
        drafts_with_excerpt=sum(1 for row in rows if row.has_excerpt),
        top_quality_flags=tuple(quality_flag_counts.most_common(5)),
        top_routing_reasons=tuple(routing_reason_counts.most_common(5)),
    )
