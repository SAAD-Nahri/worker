from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from content_engine.models import AiAssistanceRecord


ALLOWED_SOCIAL_PACKAGE_TEMPLATE_IDS = frozenset(
    {
        "fb_curiosity_hook_v1",
        "fb_short_caption_v1",
        "fb_soft_cta_post_v1",
    }
)
ALLOWED_COMMENT_TEMPLATE_IDS = frozenset(
    {
        "fb_comment_link_line_v1",
        "fb_comment_curiosity_reinforcement_v1",
        "fb_comment_read_more_prompt_v1",
    }
)
ALLOWED_SOCIAL_DESTINATIONS = frozenset({"facebook_page"})
ALLOWED_SOCIAL_APPROVAL_STATES = frozenset({"pending_review", "approved", "needs_edits", "rejected"})
ALLOWED_FACEBOOK_PUBLISH_STATUSES = frozenset({"scheduled", "published", "failed"})
ALLOWED_QUEUE_TYPES = frozenset({"blog_publish", "facebook_publish"})
ALLOWED_QUEUE_APPROVAL_STATES = ALLOWED_SOCIAL_APPROVAL_STATES
ALLOWED_BLOG_QUEUE_STATES = frozenset(
    {
        "ready_for_wordpress",
        "wordpress_draft_created",
        "ready_for_blog_schedule",
        "scheduled_blog",
        "published_blog",
        "blog_publish_failed",
    }
)
ALLOWED_FACEBOOK_QUEUE_STATES = frozenset(
    {
        "social_packaging_pending",
        "ready_for_social_review",
        "approved_for_queue",
        "scheduled_facebook",
        "published_facebook",
        "facebook_publish_failed",
    }
)
ALLOWED_MAPPING_STATUSES = frozenset(
    {
        "blog_only",
        "packaged_social_pending",
        "social_queued",
        "social_published",
        "social_publish_failed",
    }
)


@dataclass
class BlogPublishRecord:
    blog_publish_id: str
    draft_id: str
    source_item_id: str
    template_id: str
    wordpress_title: str
    wordpress_slug: str
    wordpress_excerpt: str
    wordpress_body_html: str
    wordpress_category: str
    wordpress_tags: list[str] = field(default_factory=list)
    publish_intent: str = "draft"
    canonical_source_url: str = ""
    wordpress_post_id: str | None = None
    wordpress_post_url: str | None = None
    wordpress_status: str = "prepared_local"
    schedule_mode: str | None = None
    schedule_approved_by: str | None = None
    schedule_applied_by: str | None = None
    scheduled_for_blog: str | None = None
    published_at_blog: str | None = None
    last_publish_attempt_at: str = ""
    last_publish_result: str = ""
    last_error: str | None = None
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SocialPackageRecord:
    social_package_id: str
    draft_id: str
    blog_publish_id: str | None
    package_template_id: str
    comment_template_id: str
    hook_text: str
    caption_text: str
    comment_cta_text: str
    target_destination: str = "facebook_page"
    approval_state: str = "pending_review"
    blog_url: str | None = None
    selected_variant_label: str | None = None
    variant_options: list[dict[str, str]] = field(default_factory=list)
    ai_assistance_log: list[AiAssistanceRecord] = field(default_factory=list)
    packaging_notes: str | None = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        if self.package_template_id not in ALLOWED_SOCIAL_PACKAGE_TEMPLATE_IDS:
            raise ValueError(f"Unsupported package_template_id: {self.package_template_id}")
        if self.comment_template_id not in ALLOWED_COMMENT_TEMPLATE_IDS:
            raise ValueError(f"Unsupported comment_template_id: {self.comment_template_id}")
        if self.target_destination not in ALLOWED_SOCIAL_DESTINATIONS:
            raise ValueError(f"Unsupported target_destination: {self.target_destination}")
        if self.approval_state not in ALLOWED_SOCIAL_APPROVAL_STATES:
            raise ValueError(f"Unsupported approval_state: {self.approval_state}")
        if not self.hook_text.strip():
            raise ValueError("Social package record requires hook_text.")
        if not self.caption_text.strip():
            raise ValueError("Social package record requires caption_text.")
        if not self.comment_cta_text.strip():
            raise ValueError("Social package record requires comment_cta_text.")
        labels: set[str] = set()
        for option in self.variant_options:
            label = str(option.get("label", "")).strip()
            hook_text = str(option.get("hook_text", "")).strip()
            caption_text = str(option.get("caption_text", "")).strip()
            comment_cta_text = str(option.get("comment_cta_text", "")).strip()
            if not label:
                raise ValueError("Social package variant options require label.")
            if label in labels:
                raise ValueError(f"Duplicate social package variant label: {label}")
            if not hook_text or not caption_text or not comment_cta_text:
                raise ValueError(
                    f"Social package variant option '{label}' requires hook_text, caption_text, and comment_cta_text."
                )
            labels.add(label)
        if self.selected_variant_label and self.variant_options and self.selected_variant_label not in labels:
            raise ValueError(
                f"selected_variant_label '{self.selected_variant_label}' is not present in variant_options."
            )
        for entry in self.ai_assistance_log:
            if not getattr(entry, "skill_name", "").strip():
                raise ValueError("Social package AI assistance entries require skill_name.")
            if not getattr(entry, "target_field", "").strip():
                raise ValueError("Social package AI assistance entries require target_field.")
            if not getattr(entry, "model_label", "").strip():
                raise ValueError("Social package AI assistance entries require model_label.")
            if not getattr(entry, "created_at", "").strip():
                raise ValueError("Social package AI assistance entries require created_at.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SocialPackageReviewRecord:
    review_id: str
    social_package_id: str
    draft_id: str
    blog_publish_id: str | None
    reviewer_label: str
    reviewed_at: str
    review_outcome: str
    previous_approval_state: str
    updated_approval_state: str
    review_notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FacebookPublishRecord:
    facebook_publish_id: str
    social_package_id: str
    draft_id: str
    blog_publish_id: str
    destination_type: str = "facebook_page"
    publish_status: str = "scheduled"
    facebook_post_id: str | None = None
    schedule_mode: str | None = None
    schedule_approved_by: str | None = None
    schedule_applied_by: str | None = None
    scheduled_for_facebook: str | None = None
    published_at_facebook: str | None = None
    last_publish_attempt_at: str = ""
    last_publish_result: str = ""
    last_error: str | None = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        if self.destination_type not in ALLOWED_SOCIAL_DESTINATIONS:
            raise ValueError(f"Unsupported destination_type: {self.destination_type}")
        if self.publish_status not in ALLOWED_FACEBOOK_PUBLISH_STATUSES:
            raise ValueError(f"Unsupported Facebook publish_status: {self.publish_status}")
        if not self.social_package_id.strip():
            raise ValueError("Facebook publish records require social_package_id.")
        if not self.draft_id.strip():
            raise ValueError("Facebook publish records require draft_id.")
        if not self.blog_publish_id.strip():
            raise ValueError("Facebook publish records require blog_publish_id.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class QueueItemRecord:
    queue_item_id: str
    queue_type: str
    draft_id: str
    blog_publish_id: str | None
    social_package_id: str | None
    queue_state: str
    approval_state: str
    scheduled_for: str | None = None
    last_transition_at: str = ""
    last_error: str | None = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        if self.queue_type not in ALLOWED_QUEUE_TYPES:
            raise ValueError(f"Unsupported queue_type: {self.queue_type}")
        if self.approval_state not in ALLOWED_QUEUE_APPROVAL_STATES:
            raise ValueError(f"Unsupported queue approval_state: {self.approval_state}")
        if self.queue_type == "blog_publish" and self.queue_state not in ALLOWED_BLOG_QUEUE_STATES:
            raise ValueError(f"Unsupported blog queue_state: {self.queue_state}")
        if self.queue_type == "facebook_publish" and self.queue_state not in ALLOWED_FACEBOOK_QUEUE_STATES:
            raise ValueError(f"Unsupported facebook queue_state: {self.queue_state}")
        if not self.draft_id.strip():
            raise ValueError("Queue item requires draft_id.")
        if self.queue_type == "blog_publish" and not (self.blog_publish_id or "").strip():
            raise ValueError("Blog queue items require blog_publish_id.")
        if self.queue_type == "facebook_publish" and not (self.blog_publish_id or "").strip():
            raise ValueError("Facebook queue items require blog_publish_id.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class QueueReviewRecord:
    review_id: str
    queue_item_id: str
    queue_type: str
    draft_id: str
    blog_publish_id: str | None
    social_package_id: str | None
    reviewer_label: str
    reviewed_at: str
    review_outcome: str
    previous_queue_approval_state: str
    updated_queue_review_state: str
    queue_state_at_review: str
    review_notes: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.queue_type not in ALLOWED_QUEUE_TYPES:
            raise ValueError(f"Unsupported queue_type: {self.queue_type}")
        if not self.queue_item_id.strip():
            raise ValueError("Queue review record requires queue_item_id.")
        if not self.draft_id.strip():
            raise ValueError("Queue review record requires draft_id.")
        if self.blog_publish_id is not None and not self.blog_publish_id.strip():
            raise ValueError("Queue review record blog_publish_id must be blank or non-empty text.")
        if self.social_package_id is not None and not self.social_package_id.strip():
            raise ValueError("Queue review record social_package_id must be blank or non-empty text.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BlogFacebookMappingRecord:
    mapping_id: str
    source_item_id: str
    draft_id: str
    blog_publish_id: str
    social_package_id: str | None
    facebook_publish_id: str | None
    selected_blog_title: str
    selected_hook_text: str = ""
    selected_caption_text: str = ""
    selected_comment_cta_text: str = ""
    blog_url: str | None = None
    facebook_destination_type: str = "facebook_page"
    mapping_status: str = "blog_only"
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        if self.mapping_status not in ALLOWED_MAPPING_STATUSES:
            raise ValueError(f"Unsupported mapping_status: {self.mapping_status}")
        if self.facebook_destination_type not in ALLOWED_SOCIAL_DESTINATIONS:
            raise ValueError(f"Unsupported facebook_destination_type: {self.facebook_destination_type}")
        if not self.source_item_id.strip():
            raise ValueError("Mapping record requires source_item_id.")
        if not self.draft_id.strip():
            raise ValueError("Mapping record requires draft_id.")
        if not self.blog_publish_id.strip():
            raise ValueError("Mapping record requires blog_publish_id.")
        if not self.selected_blog_title.strip():
            raise ValueError("Mapping record requires selected_blog_title.")
        has_social_selection = any(
            field.strip()
            for field in (
                self.selected_hook_text,
                self.selected_caption_text,
                self.selected_comment_cta_text,
            )
        )
        if self.mapping_status == "blog_only":
            if self.social_package_id is not None:
                raise ValueError("blog_only mapping records must not set social_package_id.")
            if has_social_selection:
                raise ValueError("blog_only mapping records must not set selected social fields.")
        else:
            if not (self.social_package_id or "").strip():
                raise ValueError("Social mapping records require social_package_id.")
            if not has_social_selection:
                raise ValueError("Social mapping records require selected social fields.")
        if self.mapping_status == "social_published" and not (self.facebook_publish_id or "").strip():
            raise ValueError("social_published mapping records require facebook_publish_id.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
