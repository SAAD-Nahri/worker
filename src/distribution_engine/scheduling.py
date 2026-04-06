from __future__ import annotations

from datetime import datetime

from source_engine.cleaner import clean_text

from distribution_engine.models import BlogPublishRecord


ALLOWED_SCHEDULE_MODES = frozenset({"manual", "auto"})
DEFAULT_MANUAL_SCHEDULE_ACTOR = "solo_operator"
DEFAULT_AUTO_SCHEDULE_ACTOR = "system_auto_scheduler"
BLOG_SCHEDULABLE_STATUSES = frozenset({"draft_created", "draft_updated", "scheduled"})
FACEBOOK_SCHEDULABLE_BLOG_STATUSES = frozenset({"scheduled", "published"})


def resolve_scheduling_decision(
    schedule_mode: str | None,
    schedule_approved_by: str | None = None,
    schedule_applied_by: str | None = None,
) -> tuple[str, str, str]:
    normalized_mode = clean_text(schedule_mode or "").lower()
    if normalized_mode not in ALLOWED_SCHEDULE_MODES:
        raise ValueError(
            "Scheduling requires schedule_mode to be one of: manual, auto."
        )

    approved_by = clean_text(schedule_approved_by) or DEFAULT_MANUAL_SCHEDULE_ACTOR
    if normalized_mode == "auto":
        applied_by = clean_text(schedule_applied_by) or DEFAULT_AUTO_SCHEDULE_ACTOR
    else:
        applied_by = clean_text(schedule_applied_by) or approved_by

    if normalized_mode == "manual" and applied_by == DEFAULT_AUTO_SCHEDULE_ACTOR:
        raise ValueError("Manual scheduling cannot use the system_auto_scheduler actor.")
    if normalized_mode == "auto" and applied_by != DEFAULT_AUTO_SCHEDULE_ACTOR:
        raise ValueError(
            "Auto scheduling requires schedule_applied_by to be system_auto_scheduler."
        )

    return normalized_mode, approved_by, applied_by


def validate_blog_schedule_allowed(blog_publish_record: BlogPublishRecord, schedule_mode: str) -> None:
    if blog_publish_record.wordpress_status not in BLOG_SCHEDULABLE_STATUSES:
        raise ValueError(
            "WordPress scheduling requires a draft_created or draft_updated blog publish snapshot first."
        )
    if schedule_mode == "auto" and blog_publish_record.publish_intent != "schedule":
        raise ValueError(
            "Auto scheduling requires the blog publish record to be prepared with publish_intent='schedule'."
        )


def validate_facebook_schedule_allowed(
    blog_publish_record: BlogPublishRecord,
    scheduled_for_facebook: str,
) -> None:
    if blog_publish_record.wordpress_status not in FACEBOOK_SCHEDULABLE_BLOG_STATUSES:
        raise ValueError(
            "Facebook scheduling requires the linked blog publish record to already be scheduled or published."
        )
    if blog_publish_record.wordpress_status == "scheduled" and blog_publish_record.scheduled_for_blog:
        facebook_time = _parse_timestamp(scheduled_for_facebook)
        blog_time = _parse_timestamp(blog_publish_record.scheduled_for_blog)
        if facebook_time < blog_time:
            raise ValueError(
                "Facebook scheduling cannot be earlier than the linked scheduled blog publish time."
            )


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
