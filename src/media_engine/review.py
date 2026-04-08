from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
import uuid

from media_engine.models import AssetRecord, AssetReviewRecord
from source_engine.cleaner import clean_text


ALLOWED_ASSET_REVIEW_OUTCOMES = {"approved", "needs_edits", "rejected"}
VAGUE_REVIEW_NOTES = {
    "fix",
    "improve",
    "adjust",
    "replace",
}


def record_asset_review(
    asset_record: AssetRecord,
    review_outcome: str,
    review_notes: list[str] | tuple[str, ...] | None = None,
    reviewer_label: str = "solo_operator",
    reviewed_at: str | None = None,
) -> tuple[AssetRecord, AssetReviewRecord]:
    if review_outcome not in ALLOWED_ASSET_REVIEW_OUTCOMES:
        raise ValueError(f"Invalid asset review outcome: {review_outcome}")

    cleaned_notes = _clean_review_notes(review_notes or [])
    if review_outcome in {"needs_edits", "rejected"} and not cleaned_notes:
        raise ValueError(f"Review outcome '{review_outcome}' requires at least one actionable review note.")

    timestamp = _resolve_timestamp(reviewed_at)
    updated_asset = deepcopy(asset_record)
    updated_asset.approval_state = review_outcome
    updated_asset.updated_at = timestamp

    review_record = AssetReviewRecord(
        review_id=_build_review_id(asset_record.asset_record_id, timestamp),
        asset_record_id=asset_record.asset_record_id,
        media_brief_id=asset_record.media_brief_id,
        draft_id=asset_record.draft_id,
        blog_publish_id=asset_record.blog_publish_id,
        social_package_id=asset_record.social_package_id,
        reviewer_label=clean_text(reviewer_label) or "solo_operator",
        reviewed_at=timestamp,
        review_outcome=review_outcome,
        previous_approval_state=asset_record.approval_state,
        updated_approval_state=updated_asset.approval_state,
        review_notes=tuple(cleaned_notes),
    )
    return updated_asset, review_record


def _build_review_id(asset_record_id: str, reviewed_at: str) -> str:
    compact_timestamp = reviewed_at.replace("-", "").replace(":", "").replace("+00:00", "Z")
    return f"{asset_record_id[:16]}-{compact_timestamp}-{uuid.uuid4().hex[:8]}"


def _clean_review_notes(review_notes: list[str] | tuple[str, ...]) -> list[str]:
    cleaned: list[str] = []
    for note in review_notes:
        normalized = clean_text(note)
        if not normalized:
            continue
        if normalized.lower() in VAGUE_REVIEW_NOTES:
            raise ValueError(f"Asset review note is too vague for the media workflow: {normalized}")
        if normalized not in cleaned:
            cleaned.append(normalized)
    return cleaned


def _resolve_timestamp(reviewed_at: str | None) -> str:
    if reviewed_at:
        return datetime.fromisoformat(reviewed_at.replace("Z", "+00:00")).isoformat()
    return datetime.now(UTC).isoformat()
