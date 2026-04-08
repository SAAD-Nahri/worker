from __future__ import annotations

from datetime import UTC, datetime
import uuid

from content_engine.models import DraftRecord
from content_engine.templates import get_blog_template_contract
from distribution_engine.models import BlogPublishRecord, SocialPackageRecord
from media_engine.models import MediaBriefRecord
from source_engine.cleaner import clean_text


BRIEF_GOAL_BY_USAGE = {
    "blog_featured_image": "Prepare one rights-safe featured image that clearly supports the approved WordPress post.",
    "facebook_link_post_image": "Prepare one rights-safe Facebook-ready visual that supports the approved post package without clickbait framing.",
    "blog_and_facebook": "Prepare one rights-safe lead visual that can work as both the WordPress featured image and the Facebook link-post visual.",
}
BASE_PROHIBITED_VISUAL_PATTERNS = (
    "medical-claim imagery",
    "misleading before/after framing",
    "exaggerated clickbait visuals",
    "unclear rights status",
)


def prepare_media_brief_record(
    draft: DraftRecord,
    *,
    blog_publish_record: BlogPublishRecord | None = None,
    social_package_record: SocialPackageRecord | None = None,
    intended_usage: str = "blog_and_facebook",
    created_at: str | None = None,
) -> MediaBriefRecord:
    _validate_draft_ready_for_media(draft)
    _validate_linkage(draft, blog_publish_record=blog_publish_record, social_package_record=social_package_record)

    timestamp = _resolve_timestamp(created_at)
    template_contract = get_blog_template_contract(draft.template_id)
    headline = clean_text(draft.headline_selected)
    excerpt = clean_text(draft.excerpt or draft.intro_text)
    subject_focus = headline or clean_text(draft.source_title)
    tags = [clean_text(tag) for tag in draft.tag_candidates if clean_text(tag)]

    visual_style_notes = [
        f"Keep the main subject directly tied to the approved article focus: {subject_focus}.",
        _resolve_template_visual_note(template_contract.template_family),
        "Use a clean editorial composition with one obvious focal point and no heavy text overlay.",
    ]
    if tags:
        visual_style_notes.append(f"Supporting cues may reference: {', '.join(tags[:3])}.")
    if intended_usage == "blog_and_facebook":
        visual_style_notes.append("Frame the image so it still reads cleanly when cropped for both a WordPress hero slot and a Facebook feed card.")

    alt_text_seed = clean_text(
        f"Illustrative image for an article about {headline or subject_focus}. {excerpt[:140]}".strip()
    )

    return MediaBriefRecord(
        media_brief_id=build_media_brief_id(draft.draft_id, created_at=timestamp),
        draft_id=draft.draft_id,
        blog_publish_id=blog_publish_record.blog_publish_id if blog_publish_record else None,
        social_package_id=social_package_record.social_package_id if social_package_record else None,
        template_family=template_contract.template_family,
        category=clean_text(draft.category),
        tag_candidates=tags,
        brief_goal=BRIEF_GOAL_BY_USAGE[intended_usage],
        subject_focus=subject_focus,
        visual_style_notes=visual_style_notes,
        prohibited_visual_patterns=list(BASE_PROHIBITED_VISUAL_PATTERNS),
        alt_text_seed=alt_text_seed[:220].strip(),
        intended_usage=intended_usage,
        created_at=timestamp,
        updated_at=timestamp,
    )


def build_media_brief_id(draft_id: str, created_at: str | None = None) -> str:
    timestamp = _resolve_timestamp(created_at)
    compact_timestamp = timestamp.replace("-", "").replace(":", "").replace("+00:00", "Z")
    return f"mbrief-{draft_id[:12]}-{compact_timestamp}-{uuid.uuid4().hex[:8]}"


def _validate_draft_ready_for_media(draft: DraftRecord) -> None:
    if draft.approval_state != "approved":
        raise ValueError("Media brief generation requires an approved draft.")
    if not clean_text(draft.headline_selected):
        raise ValueError("Media brief generation requires an approved headline.")
    if not clean_text(draft.category):
        raise ValueError("Media brief generation requires a draft category.")


def _validate_linkage(
    draft: DraftRecord,
    *,
    blog_publish_record: BlogPublishRecord | None,
    social_package_record: SocialPackageRecord | None,
) -> None:
    if blog_publish_record and blog_publish_record.draft_id != draft.draft_id:
        raise ValueError("Media brief blog linkage does not match the draft lineage.")
    if social_package_record and social_package_record.draft_id != draft.draft_id:
        raise ValueError("Media brief social linkage does not match the draft lineage.")
    if blog_publish_record and social_package_record:
        if social_package_record.blog_publish_id != blog_publish_record.blog_publish_id:
            raise ValueError("Media brief social linkage must match the linked blog publish record.")


def _resolve_template_visual_note(template_family: str) -> str:
    if template_family == "food_benefit_article":
        return "Keep the look practical and moderate rather than wellness-hype or dramatic transformation imagery."
    if template_family == "curiosity_article":
        return "Favor a question-led or contrast-led editorial look that explains the topic quickly without sensational framing."
    return "Favor a factual explainer look that supports the answer directly instead of generic stock decoration."


def _resolve_timestamp(created_at: str | None) -> str:
    if created_at:
        return datetime.fromisoformat(created_at.replace("Z", "+00:00")).isoformat()
    return datetime.now(UTC).isoformat()
