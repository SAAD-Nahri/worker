from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
import uuid

from source_engine.cleaner import clean_text

from distribution_engine.models import BlogPublishRecord, FacebookPublishRecord, SocialPackageRecord
from distribution_engine.scheduling import (
    resolve_scheduling_decision,
    validate_facebook_schedule_allowed,
)


ALLOWED_FACEBOOK_PUBLISH_UPDATE_ACTIONS = {
    "scheduled",
    "published",
    "failed",
}
PUBLISH_RESULT_BY_ACTION = {
    "scheduled": "facebook_scheduled",
    "published": "facebook_published",
    "failed": "facebook_publish_failed",
}


def record_facebook_publish_update(
    social_package_record: SocialPackageRecord,
    blog_publish_record: BlogPublishRecord,
    update_action: str,
    existing_publish_record: FacebookPublishRecord | None = None,
    attempted_at: str | None = None,
    facebook_post_id: str | None = None,
    schedule_mode: str | None = None,
    schedule_approved_by: str | None = None,
    schedule_applied_by: str | None = None,
    scheduled_for_facebook: str | None = None,
    published_at_facebook: str | None = None,
    error_message: str | None = None,
) -> FacebookPublishRecord:
    if update_action not in ALLOWED_FACEBOOK_PUBLISH_UPDATE_ACTIONS:
        raise ValueError(f"Invalid Facebook publish update action: {update_action}")

    _validate_social_publish_linkage(social_package_record, blog_publish_record, existing_publish_record)
    _validate_facebook_publish_payload(
        social_package_record=social_package_record,
        blog_publish_record=blog_publish_record,
        update_action=update_action,
        existing_publish_record=existing_publish_record,
        facebook_post_id=facebook_post_id,
        schedule_mode=schedule_mode,
        schedule_approved_by=schedule_approved_by,
        schedule_applied_by=schedule_applied_by,
        scheduled_for_facebook=scheduled_for_facebook,
        published_at_facebook=published_at_facebook,
        error_message=error_message,
    )

    timestamp = _resolve_timestamp(attempted_at)
    updated_record = _create_or_copy_publish_record(
        social_package_record=social_package_record,
        blog_publish_record=blog_publish_record,
        existing_publish_record=existing_publish_record,
        created_at=timestamp,
    )
    updated_record.publish_status = update_action
    updated_record.last_publish_attempt_at = timestamp
    updated_record.last_publish_result = PUBLISH_RESULT_BY_ACTION[update_action]
    updated_record.last_error = clean_text(error_message) or None
    updated_record.updated_at = timestamp

    if facebook_post_id:
        updated_record.facebook_post_id = clean_text(facebook_post_id)

    if update_action == "scheduled":
        resolved_schedule_mode, approved_by, applied_by = resolve_scheduling_decision(
            schedule_mode,
            schedule_approved_by=schedule_approved_by,
            schedule_applied_by=schedule_applied_by,
        )
        validate_facebook_schedule_allowed(
            blog_publish_record,
            scheduled_for_facebook=_resolve_timestamp(scheduled_for_facebook),
        )
        updated_record.schedule_mode = resolved_schedule_mode
        updated_record.schedule_approved_by = approved_by
        updated_record.schedule_applied_by = applied_by
        updated_record.scheduled_for_facebook = _resolve_timestamp(scheduled_for_facebook)
    elif update_action == "published":
        updated_record.published_at_facebook = _resolve_timestamp(published_at_facebook)
        if scheduled_for_facebook:
            updated_record.scheduled_for_facebook = _resolve_timestamp(scheduled_for_facebook)
    elif update_action == "failed":
        updated_record.publish_status = "failed"

    if update_action != "failed":
        updated_record.last_error = None

    return updated_record


def _create_or_copy_publish_record(
    social_package_record: SocialPackageRecord,
    blog_publish_record: BlogPublishRecord,
    existing_publish_record: FacebookPublishRecord | None,
    created_at: str,
) -> FacebookPublishRecord:
    if existing_publish_record is not None:
        return deepcopy(existing_publish_record)
    return FacebookPublishRecord(
        facebook_publish_id=_build_facebook_publish_id(
            social_package_record.social_package_id,
            created_at=created_at,
        ),
        social_package_id=social_package_record.social_package_id,
        draft_id=social_package_record.draft_id,
        blog_publish_id=blog_publish_record.blog_publish_id,
        destination_type=social_package_record.target_destination,
        publish_status="scheduled",
        created_at=created_at,
        updated_at=created_at,
    )


def _validate_social_publish_linkage(
    social_package_record: SocialPackageRecord,
    blog_publish_record: BlogPublishRecord,
    existing_publish_record: FacebookPublishRecord | None,
) -> None:
    if social_package_record.blog_publish_id != blog_publish_record.blog_publish_id:
        raise ValueError("Facebook publish updates require a social package linked to the same blog publish record.")
    if social_package_record.draft_id != blog_publish_record.draft_id:
        raise ValueError("Facebook publish updates require matching draft lineage.")
    if existing_publish_record is None:
        return
    if existing_publish_record.social_package_id != social_package_record.social_package_id:
        raise ValueError("Existing Facebook publish record does not match the selected social package.")
    if existing_publish_record.blog_publish_id != blog_publish_record.blog_publish_id:
        raise ValueError("Existing Facebook publish record does not match the selected blog publish record.")
    if existing_publish_record.draft_id != social_package_record.draft_id:
        raise ValueError("Existing Facebook publish record does not match the selected draft lineage.")


def _validate_facebook_publish_payload(
    social_package_record: SocialPackageRecord,
    blog_publish_record: BlogPublishRecord,
    update_action: str,
    existing_publish_record: FacebookPublishRecord | None,
    facebook_post_id: str | None,
    schedule_mode: str | None,
    schedule_approved_by: str | None,
    schedule_applied_by: str | None,
    scheduled_for_facebook: str | None,
    published_at_facebook: str | None,
    error_message: str | None,
) -> None:
    if social_package_record.approval_state != "approved":
        raise ValueError("Facebook publish updates require an approved social package.")
    if not clean_text(blog_publish_record.blog_publish_id):
        raise ValueError("Facebook publish updates require blog_publish_id.")
    if not _resolve_confirmed_blog_url(blog_publish_record):
        raise ValueError("Facebook publish updates require a confirmed blog URL before Facebook scheduling.")
    if update_action in {"scheduled", "published"}:
        existing_post_id = existing_publish_record.facebook_post_id if existing_publish_record else ""
        if not (clean_text(facebook_post_id or "") or clean_text(existing_post_id or "")):
            raise ValueError(f"Facebook publish update '{update_action}' requires facebook_post_id.")
    if update_action == "scheduled":
        if not clean_text(scheduled_for_facebook or ""):
            raise ValueError("Facebook publish update 'scheduled' requires scheduled_for_facebook.")
        resolve_scheduling_decision(
            schedule_mode,
            schedule_approved_by=schedule_approved_by,
            schedule_applied_by=schedule_applied_by,
        )
    if update_action == "published" and blog_publish_record.wordpress_status != "published":
        raise ValueError("Facebook published updates require the linked blog publish record to already be published.")
    if update_action == "published" and not clean_text(published_at_facebook or ""):
        raise ValueError("Facebook publish update 'published' requires published_at_facebook.")
    if update_action == "failed" and not clean_text(error_message or ""):
        raise ValueError("Facebook publish update 'failed' requires error_message.")


def _resolve_confirmed_blog_url(blog_publish_record: BlogPublishRecord) -> str | None:
    blog_url = clean_text(blog_publish_record.wordpress_post_url)
    if not blog_url:
        return None
    if blog_publish_record.wordpress_status in {"prepared_local", ""}:
        return None
    return blog_url


def _build_facebook_publish_id(social_package_id: str, created_at: str) -> str:
    compact_timestamp = created_at.replace("-", "").replace(":", "").replace("+00:00", "Z")
    return f"fbpub-{social_package_id[:12]}-{compact_timestamp}-{uuid.uuid4().hex[:8]}"


def _resolve_timestamp(value: str | None) -> str:
    if value:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
    return datetime.now(UTC).isoformat()
