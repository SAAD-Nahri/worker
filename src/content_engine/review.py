from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
import uuid

from source_engine.cleaner import clean_text

from content_engine.models import DraftRecord, DraftReviewRecord


ALLOWED_REVIEW_OUTCOMES = {"approved", "needs_edits", "rejected"}
WORKFLOW_STATE_BY_OUTCOME = {
    "approved": "reviewed",
    "needs_edits": "needs_revision",
    "rejected": "rejected",
}
APPROVAL_STATE_BY_OUTCOME = {
    "approved": "approved",
    "needs_edits": "needs_edits",
    "rejected": "rejected",
}
VAGUE_REVIEW_NOTES = {
    "fix",
    "improve",
    "improve tone",
    "make better",
    "rewrite",
}


def record_draft_review(
    draft: DraftRecord,
    review_outcome: str,
    review_notes: list[str] | tuple[str, ...] | None = None,
    reviewer_label: str = "solo_operator",
    reviewed_at: str | None = None,
) -> tuple[DraftRecord, DraftReviewRecord]:
    if review_outcome not in ALLOWED_REVIEW_OUTCOMES:
        raise ValueError(f"Invalid draft review outcome: {review_outcome}")

    cleaned_notes = _clean_review_notes(review_notes or [])
    if review_outcome in {"needs_edits", "rejected"} and not cleaned_notes:
        raise ValueError(f"Review outcome '{review_outcome}' requires at least one actionable review note.")
    if review_outcome == "approved" and draft.quality_gate_status == "blocked":
        raise ValueError("Blocked drafts cannot be approved without being reformatted first.")

    timestamp = _resolve_timestamp(reviewed_at)
    updated_draft = deepcopy(draft)
    updated_draft.workflow_state = WORKFLOW_STATE_BY_OUTCOME[review_outcome]
    updated_draft.approval_state = APPROVAL_STATE_BY_OUTCOME[review_outcome]
    updated_draft.review_notes.extend(cleaned_notes)
    updated_draft.updated_at = timestamp

    review_record = DraftReviewRecord(
        review_id=_build_review_id(draft.draft_id, timestamp),
        draft_id=draft.draft_id,
        source_item_id=draft.source_item_id,
        reviewer_label=clean_text(reviewer_label) or "solo_operator",
        reviewed_at=timestamp,
        review_outcome=review_outcome,
        previous_approval_state=draft.approval_state,
        updated_approval_state=updated_draft.approval_state,
        updated_workflow_state=updated_draft.workflow_state,
        quality_gate_status=draft.quality_gate_status,
        derivative_risk_level=draft.derivative_risk_level,
        review_notes=tuple(cleaned_notes),
    )
    return updated_draft, review_record


def _build_review_id(draft_id: str, reviewed_at: str) -> str:
    compact_timestamp = reviewed_at.replace("-", "").replace(":", "").replace("+00:00", "Z")
    return f"{draft_id}-{compact_timestamp}-{uuid.uuid4().hex[:8]}"


def _clean_review_notes(review_notes: list[str] | tuple[str, ...]) -> list[str]:
    cleaned: list[str] = []
    for note in review_notes:
        normalized = clean_text(note)
        if not normalized:
            continue
        if normalized.lower() in VAGUE_REVIEW_NOTES:
            raise ValueError(f"Review note is too vague for the draft workflow: {normalized}")
        if normalized not in cleaned:
            cleaned.append(normalized)
    return cleaned


def _resolve_timestamp(reviewed_at: str | None) -> str:
    if reviewed_at:
        return datetime.fromisoformat(reviewed_at.replace("Z", "+00:00")).isoformat()
    return datetime.now(UTC).isoformat()
