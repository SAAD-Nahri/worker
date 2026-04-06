from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
import uuid

from source_engine.cleaner import clean_text

from distribution_engine.models import SocialPackageRecord, SocialPackageReviewRecord


ALLOWED_SOCIAL_REVIEW_OUTCOMES = {"approved", "needs_edits", "rejected"}
VAGUE_REVIEW_NOTES = {
    "fix",
    "improve",
    "make better",
    "rewrite",
    "adjust",
}


def record_social_package_review(
    social_package_record: SocialPackageRecord,
    review_outcome: str,
    review_notes: list[str] | tuple[str, ...] | None = None,
    reviewer_label: str = "solo_operator",
    reviewed_at: str | None = None,
) -> tuple[SocialPackageRecord, SocialPackageReviewRecord]:
    if review_outcome not in ALLOWED_SOCIAL_REVIEW_OUTCOMES:
        raise ValueError(f"Invalid social package review outcome: {review_outcome}")

    cleaned_notes = _clean_review_notes(review_notes or [])
    if review_outcome in {"needs_edits", "rejected"} and not cleaned_notes:
        raise ValueError(
            f"Review outcome '{review_outcome}' requires at least one actionable review note."
        )

    timestamp = _resolve_timestamp(reviewed_at)
    updated_package = deepcopy(social_package_record)
    updated_package.approval_state = review_outcome
    if cleaned_notes:
        updated_package.packaging_notes = " | ".join(cleaned_notes)
    updated_package.updated_at = timestamp

    review_record = SocialPackageReviewRecord(
        review_id=_build_review_id(social_package_record.social_package_id, timestamp),
        social_package_id=social_package_record.social_package_id,
        draft_id=social_package_record.draft_id,
        blog_publish_id=social_package_record.blog_publish_id,
        reviewer_label=clean_text(reviewer_label) or "solo_operator",
        reviewed_at=timestamp,
        review_outcome=review_outcome,
        previous_approval_state=social_package_record.approval_state,
        updated_approval_state=updated_package.approval_state,
        review_notes=tuple(cleaned_notes),
    )
    return updated_package, review_record


def _build_review_id(social_package_id: str, reviewed_at: str) -> str:
    compact_timestamp = reviewed_at.replace("-", "").replace(":", "").replace("+00:00", "Z")
    return f"{social_package_id[:16]}-{compact_timestamp}-{uuid.uuid4().hex[:8]}"


def _clean_review_notes(review_notes: list[str] | tuple[str, ...]) -> list[str]:
    cleaned: list[str] = []
    for note in review_notes:
        normalized = clean_text(note)
        if not normalized:
            continue
        if normalized.lower() in VAGUE_REVIEW_NOTES:
            raise ValueError(f"Review note is too vague for the social package workflow: {normalized}")
        if normalized not in cleaned:
            cleaned.append(normalized)
    return cleaned


def _resolve_timestamp(reviewed_at: str | None) -> str:
    if reviewed_at:
        return datetime.fromisoformat(reviewed_at.replace("Z", "+00:00")).isoformat()
    return datetime.now(UTC).isoformat()
