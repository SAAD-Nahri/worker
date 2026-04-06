from __future__ import annotations

from datetime import UTC, datetime
import uuid

from source_engine.cleaner import clean_text

from distribution_engine.models import (
    BlogFacebookMappingRecord,
    BlogPublishRecord,
    FacebookPublishRecord,
    QueueItemRecord,
    SocialPackageRecord,
)


def prepare_blog_queue_item_record(
    blog_publish_record: BlogPublishRecord,
    created_at: str | None = None,
) -> QueueItemRecord:
    _validate_blog_publish_record(blog_publish_record)
    timestamp = _resolve_timestamp(created_at)
    queue_state = _resolve_blog_queue_state(blog_publish_record)
    approval_state = _resolve_blog_queue_approval_state(queue_state)
    return QueueItemRecord(
        queue_item_id=build_queue_item_id("blog_publish", blog_publish_record.blog_publish_id, created_at=timestamp),
        queue_type="blog_publish",
        draft_id=blog_publish_record.draft_id,
        blog_publish_id=blog_publish_record.blog_publish_id,
        social_package_id=None,
        queue_state=queue_state,
        approval_state=approval_state,
        scheduled_for=blog_publish_record.scheduled_for_blog,
        last_transition_at=timestamp,
        last_error=blog_publish_record.last_error,
        created_at=timestamp,
        updated_at=timestamp,
    )


def prepare_facebook_queue_item_record(
    blog_publish_record: BlogPublishRecord,
    social_package_record: SocialPackageRecord | None = None,
    facebook_publish_record: FacebookPublishRecord | None = None,
    created_at: str | None = None,
) -> QueueItemRecord:
    _validate_blog_publish_record(blog_publish_record)
    _validate_social_package_linkage(blog_publish_record, social_package_record)
    _validate_facebook_publish_linkage(
        blog_publish_record,
        social_package_record,
        facebook_publish_record,
    )
    timestamp = _resolve_timestamp(created_at)
    queue_state, approval_state, scheduled_for, last_error = _resolve_facebook_queue_state_and_approval(
        blog_publish_record,
        social_package_record,
        facebook_publish_record,
    )
    return QueueItemRecord(
        queue_item_id=build_queue_item_id(
            "facebook_publish",
            blog_publish_record.blog_publish_id,
            created_at=timestamp,
        ),
        queue_type="facebook_publish",
        draft_id=blog_publish_record.draft_id,
        blog_publish_id=blog_publish_record.blog_publish_id,
        social_package_id=social_package_record.social_package_id if social_package_record else None,
        queue_state=queue_state,
        approval_state=approval_state,
        scheduled_for=scheduled_for,
        last_transition_at=timestamp,
        last_error=last_error,
        created_at=timestamp,
        updated_at=timestamp,
    )


def prepare_distribution_linkage_records(
    blog_publish_record: BlogPublishRecord,
    social_package_record: SocialPackageRecord | None = None,
    facebook_publish_record: FacebookPublishRecord | None = None,
    created_at: str | None = None,
) -> tuple[QueueItemRecord, QueueItemRecord, BlogFacebookMappingRecord]:
    timestamp = _resolve_timestamp(created_at)
    blog_queue = prepare_blog_queue_item_record(blog_publish_record, created_at=timestamp)
    facebook_queue = prepare_facebook_queue_item_record(
        blog_publish_record,
        social_package_record=social_package_record,
        facebook_publish_record=facebook_publish_record,
        created_at=timestamp,
    )
    mapping = prepare_blog_facebook_mapping_record(
        blog_publish_record,
        social_package_record=social_package_record,
        facebook_publish_record=facebook_publish_record,
        created_at=timestamp,
    )
    return blog_queue, facebook_queue, mapping


def prepare_blog_facebook_mapping_record(
    blog_publish_record: BlogPublishRecord,
    social_package_record: SocialPackageRecord | None = None,
    facebook_publish_record: FacebookPublishRecord | None = None,
    created_at: str | None = None,
) -> BlogFacebookMappingRecord:
    _validate_blog_publish_record(blog_publish_record)
    _validate_social_package_linkage(blog_publish_record, social_package_record)
    _validate_facebook_publish_linkage(
        blog_publish_record,
        social_package_record,
        facebook_publish_record,
    )
    timestamp = _resolve_timestamp(created_at)
    mapping_status = _resolve_mapping_status(social_package_record, facebook_publish_record)
    return BlogFacebookMappingRecord(
        mapping_id=build_mapping_id(blog_publish_record.blog_publish_id, created_at=timestamp),
        source_item_id=blog_publish_record.source_item_id,
        draft_id=blog_publish_record.draft_id,
        blog_publish_id=blog_publish_record.blog_publish_id,
        social_package_id=social_package_record.social_package_id if social_package_record else None,
        facebook_publish_id=facebook_publish_record.facebook_publish_id if facebook_publish_record else None,
        selected_blog_title=clean_text(blog_publish_record.wordpress_title),
        selected_hook_text=clean_text(social_package_record.hook_text) if social_package_record else "",
        selected_caption_text=clean_text(social_package_record.caption_text) if social_package_record else "",
        selected_comment_cta_text=clean_text(social_package_record.comment_cta_text) if social_package_record else "",
        blog_url=_resolve_confirmed_blog_url(blog_publish_record),
        facebook_destination_type=(
            social_package_record.target_destination if social_package_record else "facebook_page"
        ),
        mapping_status=mapping_status,
        created_at=timestamp,
        updated_at=timestamp,
    )


def build_queue_item_id(queue_type: str, blog_publish_id: str, created_at: str | None = None) -> str:
    timestamp = _resolve_timestamp(created_at)
    compact_timestamp = timestamp.replace("-", "").replace(":", "").replace("+00:00", "Z")
    prefix = "blogq" if queue_type == "blog_publish" else "fbq"
    return f"{prefix}-{blog_publish_id[:12]}-{compact_timestamp}-{uuid.uuid4().hex[:8]}"


def build_mapping_id(blog_publish_id: str, created_at: str | None = None) -> str:
    timestamp = _resolve_timestamp(created_at)
    compact_timestamp = timestamp.replace("-", "").replace(":", "").replace("+00:00", "Z")
    return f"map-{blog_publish_id[:12]}-{compact_timestamp}-{uuid.uuid4().hex[:8]}"


def _validate_blog_publish_record(blog_publish_record: BlogPublishRecord) -> None:
    if not clean_text(blog_publish_record.blog_publish_id):
        raise ValueError("Workflow preparation requires blog_publish_id.")
    if not clean_text(blog_publish_record.draft_id):
        raise ValueError("Workflow preparation requires draft_id.")
    if not clean_text(blog_publish_record.source_item_id):
        raise ValueError("Workflow preparation requires source_item_id.")
    if not clean_text(blog_publish_record.wordpress_title):
        raise ValueError("Workflow preparation requires a prepared WordPress title.")


def _validate_social_package_linkage(
    blog_publish_record: BlogPublishRecord,
    social_package_record: SocialPackageRecord | None,
) -> None:
    if social_package_record is None:
        return
    if social_package_record.draft_id != blog_publish_record.draft_id:
        raise ValueError("Social package linkage does not match the blog publish draft.")
    if social_package_record.blog_publish_id != blog_publish_record.blog_publish_id:
        raise ValueError(
            "Social package linkage requires a package prepared against the same blog_publish_id."
        )


def _validate_facebook_publish_linkage(
    blog_publish_record: BlogPublishRecord,
    social_package_record: SocialPackageRecord | None,
    facebook_publish_record: FacebookPublishRecord | None,
) -> None:
    if facebook_publish_record is None:
        return
    if social_package_record is None:
        raise ValueError("Facebook publish linkage requires a linked social package record.")
    if facebook_publish_record.blog_publish_id != blog_publish_record.blog_publish_id:
        raise ValueError("Facebook publish linkage does not match the blog publish record.")
    if facebook_publish_record.social_package_id != social_package_record.social_package_id:
        raise ValueError("Facebook publish linkage does not match the social package record.")
    if facebook_publish_record.draft_id != blog_publish_record.draft_id:
        raise ValueError("Facebook publish linkage does not match the draft lineage.")


def _resolve_blog_queue_state(blog_publish_record: BlogPublishRecord) -> str:
    if clean_text(blog_publish_record.last_error):
        return "blog_publish_failed"
    if clean_text(blog_publish_record.published_at_blog) or blog_publish_record.wordpress_status == "published":
        return "published_blog"
    if blog_publish_record.wordpress_status == "scheduled":
        return "scheduled_blog"
    if blog_publish_record.wordpress_status in {"draft_created", "draft_updated"}:
        if blog_publish_record.publish_intent == "schedule":
            return "ready_for_blog_schedule"
        return "wordpress_draft_created"
    if clean_text(blog_publish_record.wordpress_post_id):
        return "wordpress_draft_created"
    return "ready_for_wordpress"


def _resolve_blog_queue_approval_state(queue_state: str) -> str:
    if queue_state in {"scheduled_blog", "published_blog"}:
        return "approved"
    if queue_state == "blog_publish_failed":
        return "needs_edits"
    return "pending_review"


def _resolve_facebook_queue_state_and_approval(
    blog_publish_record: BlogPublishRecord,
    social_package_record: SocialPackageRecord | None,
    facebook_publish_record: FacebookPublishRecord | None,
) -> tuple[str, str, str | None, str | None]:
    if social_package_record is None:
        return ("social_packaging_pending", "pending_review", None, None)

    if facebook_publish_record is not None:
        if facebook_publish_record.publish_status == "failed":
            return (
                "facebook_publish_failed",
                "needs_edits",
                facebook_publish_record.scheduled_for_facebook,
                facebook_publish_record.last_error,
            )
        if facebook_publish_record.publish_status == "published":
            return (
                "published_facebook",
                "approved",
                facebook_publish_record.scheduled_for_facebook,
                None,
            )
        if facebook_publish_record.publish_status == "scheduled":
            return (
                "scheduled_facebook",
                "approved",
                facebook_publish_record.scheduled_for_facebook,
                None,
            )

    if social_package_record.approval_state == "approved":
        if _resolve_confirmed_blog_url(blog_publish_record):
            return ("approved_for_queue", "approved", None, None)
        return ("social_packaging_pending", "approved", None, None)

    return ("ready_for_social_review", social_package_record.approval_state, None, None)


def _resolve_mapping_status(
    social_package_record: SocialPackageRecord | None,
    facebook_publish_record: FacebookPublishRecord | None,
) -> str:
    if social_package_record is None:
        return "blog_only"
    if facebook_publish_record is None:
        return "packaged_social_pending"
    if facebook_publish_record.publish_status == "published":
        return "social_published"
    if facebook_publish_record.publish_status == "failed":
        return "social_publish_failed"
    return "social_queued"


def _resolve_confirmed_blog_url(blog_publish_record: BlogPublishRecord) -> str | None:
    blog_url = clean_text(blog_publish_record.wordpress_post_url)
    if not blog_url:
        return None
    if blog_publish_record.wordpress_status in {"prepared_local", ""}:
        return None
    return blog_url


def _resolve_timestamp(created_at: str | None) -> str:
    if created_at:
        return datetime.fromisoformat(created_at.replace("Z", "+00:00")).isoformat()
    return datetime.now(UTC).isoformat()
