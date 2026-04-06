from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime

from source_engine.cleaner import clean_text

from distribution_engine.models import BlogPublishRecord
from distribution_engine.scheduling import resolve_scheduling_decision, validate_blog_schedule_allowed


ALLOWED_BLOG_PUBLISH_UPDATE_ACTIONS = {
    "draft_created",
    "draft_updated",
    "scheduled",
    "published",
    "failed",
}
PUBLISH_RESULT_BY_ACTION = {
    "draft_created": "wordpress_draft_created",
    "draft_updated": "wordpress_draft_updated",
    "scheduled": "wordpress_scheduled",
    "published": "wordpress_published",
    "failed": "wordpress_publish_failed",
}


def record_blog_publish_update(
    blog_publish_record: BlogPublishRecord,
    update_action: str,
    attempted_at: str | None = None,
    wordpress_post_id: str | None = None,
    wordpress_post_url: str | None = None,
    schedule_mode: str | None = None,
    schedule_approved_by: str | None = None,
    schedule_applied_by: str | None = None,
    scheduled_for_blog: str | None = None,
    published_at_blog: str | None = None,
    error_message: str | None = None,
) -> BlogPublishRecord:
    if update_action not in ALLOWED_BLOG_PUBLISH_UPDATE_ACTIONS:
        raise ValueError(f"Invalid WordPress publish update action: {update_action}")

    _validate_publish_update_payload(
        blog_publish_record=blog_publish_record,
        update_action=update_action,
        wordpress_post_id=wordpress_post_id,
        wordpress_post_url=wordpress_post_url,
        schedule_mode=schedule_mode,
        schedule_approved_by=schedule_approved_by,
        schedule_applied_by=schedule_applied_by,
        scheduled_for_blog=scheduled_for_blog,
        published_at_blog=published_at_blog,
        error_message=error_message,
    )

    timestamp = _resolve_timestamp(attempted_at)
    updated_record = deepcopy(blog_publish_record)
    updated_record.wordpress_status = update_action
    updated_record.last_publish_attempt_at = timestamp
    updated_record.last_publish_result = PUBLISH_RESULT_BY_ACTION[update_action]
    updated_record.last_error = clean_text(error_message) or None
    updated_record.updated_at = timestamp

    if wordpress_post_id:
        updated_record.wordpress_post_id = clean_text(wordpress_post_id)
    if wordpress_post_url:
        updated_record.wordpress_post_url = clean_text(wordpress_post_url)

    if update_action == "scheduled":
        resolved_schedule_mode, approved_by, applied_by = resolve_scheduling_decision(
            schedule_mode,
            schedule_approved_by=schedule_approved_by,
            schedule_applied_by=schedule_applied_by,
        )
        validate_blog_schedule_allowed(blog_publish_record, resolved_schedule_mode)
        updated_record.publish_intent = "schedule"
        updated_record.schedule_mode = resolved_schedule_mode
        updated_record.schedule_approved_by = approved_by
        updated_record.schedule_applied_by = applied_by
        updated_record.scheduled_for_blog = _resolve_timestamp(scheduled_for_blog)
    elif update_action == "published":
        updated_record.publish_intent = "publish_now"
        updated_record.published_at_blog = _resolve_timestamp(published_at_blog)
        if scheduled_for_blog:
            updated_record.scheduled_for_blog = _resolve_timestamp(scheduled_for_blog)
    elif update_action == "failed":
        updated_record.wordpress_status = "failed"
    elif update_action in {"draft_created", "draft_updated"}:
        updated_record.published_at_blog = blog_publish_record.published_at_blog
        updated_record.scheduled_for_blog = blog_publish_record.scheduled_for_blog
        updated_record.schedule_mode = blog_publish_record.schedule_mode
        updated_record.schedule_approved_by = blog_publish_record.schedule_approved_by
        updated_record.schedule_applied_by = blog_publish_record.schedule_applied_by

    if update_action != "failed":
        updated_record.last_error = None

    return updated_record


def _validate_publish_update_payload(
    blog_publish_record: BlogPublishRecord,
    update_action: str,
    wordpress_post_id: str | None,
    wordpress_post_url: str | None,
    schedule_mode: str | None,
    schedule_approved_by: str | None,
    schedule_applied_by: str | None,
    scheduled_for_blog: str | None,
    published_at_blog: str | None,
    error_message: str | None,
) -> None:
    if not clean_text(blog_publish_record.blog_publish_id):
        raise ValueError("WordPress publish updates require blog_publish_id.")
    if update_action in {"draft_created", "draft_updated", "scheduled", "published"}:
        if not (clean_text(wordpress_post_id) or clean_text(blog_publish_record.wordpress_post_id or "")):
            raise ValueError(f"WordPress publish update '{update_action}' requires wordpress_post_id.")
    if update_action == "scheduled":
        if not clean_text(scheduled_for_blog or ""):
            raise ValueError("WordPress publish update 'scheduled' requires scheduled_for_blog.")
        resolve_scheduling_decision(
            schedule_mode,
            schedule_approved_by=schedule_approved_by,
            schedule_applied_by=schedule_applied_by,
        )
    if update_action == "published":
        if not clean_text(published_at_blog or ""):
            raise ValueError("WordPress publish update 'published' requires published_at_blog.")
        if not (clean_text(wordpress_post_url or "") or clean_text(blog_publish_record.wordpress_post_url or "")):
            raise ValueError("WordPress publish update 'published' requires wordpress_post_url.")
    if update_action == "failed" and not clean_text(error_message or ""):
        raise ValueError("WordPress publish update 'failed' requires error_message.")


def _resolve_timestamp(value: str | None) -> str:
    if value:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
    return datetime.now(UTC).isoformat()
