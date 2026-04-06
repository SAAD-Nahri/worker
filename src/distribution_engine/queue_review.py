from __future__ import annotations

from datetime import UTC, datetime
import uuid

from source_engine.cleaner import clean_text

from distribution_engine.models import QueueItemRecord, QueueReviewRecord


ALLOWED_QUEUE_REVIEW_OUTCOMES = {"approved", "hold", "removed"}
UPDATED_QUEUE_REVIEW_STATE_BY_OUTCOME = {
    "approved": "approved",
    "hold": "needs_edits",
    "removed": "removed",
}
VAGUE_QUEUE_REVIEW_NOTES = {
    "fix",
    "hold",
    "remove",
    "review",
    "later",
}


def record_queue_review(
    queue_item_record: QueueItemRecord,
    review_outcome: str,
    review_notes: list[str] | tuple[str, ...] | None = None,
    reviewer_label: str = "solo_operator",
    reviewed_at: str | None = None,
) -> QueueReviewRecord:
    if review_outcome not in ALLOWED_QUEUE_REVIEW_OUTCOMES:
        raise ValueError(f"Invalid queue review outcome: {review_outcome}")

    cleaned_notes = _clean_review_notes(review_notes or [])
    if review_outcome in {"hold", "removed"} and not cleaned_notes:
        raise ValueError(
            f"Queue review outcome '{review_outcome}' requires at least one actionable review note."
        )
    if review_outcome == "approved" and queue_item_record.queue_state in {
        "blog_publish_failed",
        "facebook_publish_failed",
    }:
        raise ValueError("Failed queue items cannot be approved for queue until the failure is resolved.")

    timestamp = _resolve_timestamp(reviewed_at)
    return QueueReviewRecord(
        review_id=_build_review_id(queue_item_record.queue_item_id, timestamp),
        queue_item_id=queue_item_record.queue_item_id,
        queue_type=queue_item_record.queue_type,
        draft_id=queue_item_record.draft_id,
        blog_publish_id=queue_item_record.blog_publish_id,
        social_package_id=queue_item_record.social_package_id,
        reviewer_label=clean_text(reviewer_label) or "solo_operator",
        reviewed_at=timestamp,
        review_outcome=review_outcome,
        previous_queue_approval_state=queue_item_record.approval_state,
        updated_queue_review_state=UPDATED_QUEUE_REVIEW_STATE_BY_OUTCOME[review_outcome],
        queue_state_at_review=queue_item_record.queue_state,
        review_notes=tuple(cleaned_notes),
    )


def _build_review_id(queue_item_id: str, reviewed_at: str) -> str:
    compact_timestamp = reviewed_at.replace("-", "").replace(":", "").replace("+00:00", "Z")
    return f"{queue_item_id[:16]}-{compact_timestamp}-{uuid.uuid4().hex[:8]}"


def _clean_review_notes(review_notes: list[str] | tuple[str, ...]) -> list[str]:
    cleaned: list[str] = []
    for note in review_notes:
        normalized = clean_text(note)
        if not normalized:
            continue
        if normalized.lower() in VAGUE_QUEUE_REVIEW_NOTES:
            raise ValueError(f"Queue review note is too vague for the approval workflow: {normalized}")
        if normalized not in cleaned:
            cleaned.append(normalized)
    return cleaned


def _resolve_timestamp(reviewed_at: str | None) -> str:
    if reviewed_at:
        return datetime.fromisoformat(reviewed_at.replace("Z", "+00:00")).isoformat()
    return datetime.now(UTC).isoformat()
