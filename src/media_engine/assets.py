from __future__ import annotations

from datetime import UTC, datetime
import uuid

from media_engine.models import AssetRecord, MediaBriefRecord
from source_engine.cleaner import clean_text


def prepare_asset_record(
    media_brief_record: MediaBriefRecord,
    *,
    asset_source_kind: str,
    provenance_reference: str,
    asset_url_or_path: str,
    alt_text: str,
    caption_support_text: str = "",
    created_at: str | None = None,
) -> AssetRecord:
    timestamp = _resolve_timestamp(created_at)
    return AssetRecord(
        asset_record_id=build_asset_record_id(media_brief_record.draft_id, created_at=timestamp),
        media_brief_id=media_brief_record.media_brief_id,
        draft_id=media_brief_record.draft_id,
        blog_publish_id=media_brief_record.blog_publish_id,
        social_package_id=media_brief_record.social_package_id,
        asset_source_kind=asset_source_kind,
        provenance_reference=clean_text(provenance_reference),
        approval_state="pending_review",
        intended_usage=media_brief_record.intended_usage,
        asset_url_or_path=clean_text(asset_url_or_path),
        alt_text=clean_text(alt_text),
        caption_support_text=clean_text(caption_support_text),
        created_at=timestamp,
        updated_at=timestamp,
    )


def resolve_asset_readiness(asset_record: AssetRecord | None) -> tuple[bool, str | None]:
    if asset_record is None:
        return False, "No linked media asset has been selected yet."
    if asset_record.approval_state != "approved":
        return False, f"Linked media asset is still {asset_record.approval_state}."
    return True, None


def build_asset_record_id(draft_id: str, created_at: str | None = None) -> str:
    timestamp = _resolve_timestamp(created_at)
    compact_timestamp = timestamp.replace("-", "").replace(":", "").replace("+00:00", "Z")
    return f"asset-{draft_id[:12]}-{compact_timestamp}-{uuid.uuid4().hex[:8]}"


def _resolve_timestamp(created_at: str | None) -> str:
    if created_at:
        return datetime.fromisoformat(created_at.replace("Z", "+00:00")).isoformat()
    return datetime.now(UTC).isoformat()
