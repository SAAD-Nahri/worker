from __future__ import annotations

from datetime import UTC, datetime
import re
import uuid

from source_engine.cleaner import clean_text

from content_engine.models import DraftRecord, DraftSection
from distribution_engine.models import BlogPublishRecord, SocialPackageRecord


FACEBOOK_TARGET_DESTINATION = "facebook_page"
PACKAGE_TEMPLATE_ID_BY_FAMILY = {
    "curiosity_article": "fb_curiosity_hook_v1",
    "food_benefit_article": "fb_soft_cta_post_v1",
    "food_fact_article": "fb_short_caption_v1",
}
COMMENT_TEMPLATE_ID_BY_PACKAGE = {
    "fb_curiosity_hook_v1": "fb_comment_curiosity_reinforcement_v1",
    "fb_short_caption_v1": "fb_comment_link_line_v1",
    "fb_soft_cta_post_v1": "fb_comment_read_more_prompt_v1",
}
SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+")


def prepare_social_package_record(
    draft: DraftRecord,
    blog_publish_record: BlogPublishRecord | None = None,
    created_at: str | None = None,
) -> SocialPackageRecord:
    _validate_draft_ready_for_social(draft)
    _validate_blog_publish_linkage(draft, blog_publish_record)

    timestamp = _resolve_timestamp(created_at)
    package_template_id = select_facebook_package_template_id(draft)
    comment_template_id = COMMENT_TEMPLATE_ID_BY_PACKAGE[package_template_id]
    hook_text = _build_hook_text(draft, package_template_id)
    caption_text = _build_caption_text(draft, package_template_id)
    comment_cta_text = _build_comment_cta_text(draft, comment_template_id, blog_publish_record)
    blog_url = _resolve_confirmed_blog_url(blog_publish_record)
    variant_options = _build_social_variant_options(
        draft,
        package_template_id=package_template_id,
        comment_template_id=comment_template_id,
        blog_publish_record=blog_publish_record,
    )
    _validate_package_shape(
        package_template_id=package_template_id,
        hook_text=hook_text,
        caption_text=caption_text,
        comment_cta_text=comment_cta_text,
    )

    return SocialPackageRecord(
        social_package_id=build_social_package_id(draft.draft_id, created_at=timestamp),
        draft_id=draft.draft_id,
        blog_publish_id=blog_publish_record.blog_publish_id if blog_publish_record else None,
        package_template_id=package_template_id,
        comment_template_id=comment_template_id,
        hook_text=hook_text,
        caption_text=caption_text,
        comment_cta_text=comment_cta_text,
        target_destination=FACEBOOK_TARGET_DESTINATION,
        approval_state="pending_review",
        blog_url=blog_url,
        selected_variant_label="deterministic_primary_v1",
        variant_options=variant_options,
        packaging_notes=None,
        created_at=timestamp,
        updated_at=timestamp,
    )


def select_facebook_package_template_id(draft: DraftRecord) -> str:
    return PACKAGE_TEMPLATE_ID_BY_FAMILY.get(draft.template_family, "fb_short_caption_v1")


def validate_social_package_shape(
    package_template_id: str,
    hook_text: str,
    caption_text: str,
    comment_cta_text: str,
) -> None:
    _validate_package_shape(
        package_template_id=package_template_id,
        hook_text=hook_text,
        caption_text=caption_text,
        comment_cta_text=comment_cta_text,
    )


def build_social_package_id(draft_id: str, created_at: str | None = None) -> str:
    timestamp = _resolve_timestamp(created_at)
    compact_timestamp = timestamp.replace("-", "").replace(":", "").replace("+00:00", "Z")
    return f"social-{draft_id[:12]}-{compact_timestamp}-{uuid.uuid4().hex[:8]}"


def _build_hook_text(draft: DraftRecord, package_template_id: str) -> str:
    title = clean_text(draft.headline_selected)
    answer = _primary_answer_text(draft)

    if package_template_id == "fb_curiosity_hook_v1":
        if title.endswith("?"):
            return title
        if title.lower().startswith(("why ", "what ", "how ", "when ", "where ")):
            return f"{title}?"
        return title

    if package_template_id == "fb_soft_cta_post_v1":
        lead = _first_sentence(draft.excerpt or draft.intro_text or answer)
        return _truncate_words(lead, 16)

    return _truncate_words(title, 14)


def _build_caption_text(draft: DraftRecord, package_template_id: str) -> str:
    answer = _primary_answer_text(draft)
    excerpt = clean_text(draft.excerpt or draft.intro_text)

    if package_template_id == "fb_curiosity_hook_v1":
        return _truncate_words(
            f"{_first_sentence(answer)} The full post breaks it down in a quick, readable way.",
            34,
        )

    if package_template_id == "fb_soft_cta_post_v1":
        return _truncate_words(
            f"{_first_sentence(excerpt or answer)} The blog post lays out the key points without overcomplicating it.",
            34,
        )

    return _truncate_words(
        f"{_first_sentence(excerpt or answer)} The full post gives the clean explanation in one quick read.",
        28,
    )


def _build_comment_cta_text(
    draft: DraftRecord,
    comment_template_id: str,
    blog_publish_record: BlogPublishRecord | None,
) -> str:
    title = clean_text(draft.headline_selected)
    has_blog_url = bool(_resolve_confirmed_blog_url(blog_publish_record))

    if comment_template_id == "fb_comment_curiosity_reinforcement_v1":
        base = "If you want the short answer and the full explanation, I can drop the post here."
        if has_blog_url:
            base = "Full post here if you want the quick answer and the full explanation."
        return _truncate_words(base, 20)

    if comment_template_id == "fb_comment_read_more_prompt_v1":
        base = f"The full post keeps {_title_topic_fragment(title)} in one clean read."
        if has_blog_url:
            base = f"Full post here if you want the practical breakdown on {_title_topic_fragment(title)}."
        return _truncate_words(base, 18)

    base = "I'll drop the full post in the comments for anyone who wants the full explanation."
    if has_blog_url:
        base = "Full post here if you want the full explanation."
    return _truncate_words(base, 18)


def _build_social_variant_options(
    draft: DraftRecord,
    *,
    package_template_id: str,
    comment_template_id: str,
    blog_publish_record: BlogPublishRecord | None,
) -> list[dict[str, str]]:
    title = clean_text(draft.headline_selected)
    answer = _primary_answer_text(draft)
    excerpt = clean_text(draft.excerpt or draft.intro_text or answer)
    variants = [
        {
            "label": "deterministic_primary_v1",
            "hook_text": _build_hook_text(draft, package_template_id),
            "caption_text": _build_caption_text(draft, package_template_id),
            "comment_cta_text": _build_comment_cta_text(
                draft,
                comment_template_id,
                blog_publish_record,
            ),
        },
        {
            "label": "deterministic_supporting_v1",
            "hook_text": _build_supporting_variant_hook(title, package_template_id),
            "caption_text": _build_supporting_variant_caption(excerpt or answer, package_template_id),
            "comment_cta_text": _build_supporting_variant_comment(
                title,
                comment_template_id,
                blog_publish_record,
            ),
        },
        {
            "label": "deterministic_concise_v1",
            "hook_text": _build_concise_variant_hook(title, answer, package_template_id),
            "caption_text": _build_concise_variant_caption(excerpt or answer, package_template_id),
            "comment_cta_text": _build_concise_variant_comment(
                title,
                comment_template_id,
                blog_publish_record,
            ),
        },
    ]
    unique_variants: list[dict[str, str]] = []
    seen_signatures: set[tuple[str, str, str]] = set()
    for variant in variants:
        _validate_package_shape(
            package_template_id=package_template_id,
            hook_text=variant["hook_text"],
            caption_text=variant["caption_text"],
            comment_cta_text=variant["comment_cta_text"],
        )
        signature = (
            variant["hook_text"],
            variant["caption_text"],
            variant["comment_cta_text"],
        )
        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        unique_variants.append(variant)
    return unique_variants


def _build_supporting_variant_hook(title: str, package_template_id: str) -> str:
    topic = _title_topic_fragment(title)
    if package_template_id == "fb_curiosity_hook_v1":
        return _truncate_words(f"What to know about {topic}?", 18)
    if package_template_id == "fb_soft_cta_post_v1":
        return _truncate_words(f"A practical look at {topic}", 16)
    return _truncate_words(f"What to know about {topic}", 12)


def _build_concise_variant_hook(title: str, answer: str, package_template_id: str) -> str:
    topic = _title_topic_fragment(title)
    lead = _first_sentence(answer)
    if package_template_id == "fb_curiosity_hook_v1":
        return _truncate_words(f"Why {topic} matters more than people expect?", 18)
    if package_template_id == "fb_soft_cta_post_v1":
        return _truncate_words(lead or f"Why {topic} matters", 16)
    return _truncate_words(f"Why {topic} stands out", 12)


def _build_supporting_variant_caption(base_text: str, package_template_id: str) -> str:
    first_sentence = _first_sentence(base_text)
    if package_template_id == "fb_curiosity_hook_v1":
        return _truncate_words(
            f"{first_sentence} The full post gives the quick context behind the headline question.",
            34,
        )
    if package_template_id == "fb_soft_cta_post_v1":
        return _truncate_words(
            f"{first_sentence} The blog version keeps the practical points easy to scan and easy to reuse.",
            34,
        )
    return _truncate_words(
        f"{first_sentence} The blog post keeps the useful explanation short and easy to follow.",
        28,
    )


def _build_concise_variant_caption(base_text: str, package_template_id: str) -> str:
    first_sentence = _first_sentence(base_text)
    if package_template_id == "fb_curiosity_hook_v1":
        return _truncate_words(
            f"{first_sentence} The blog post explains the short answer without dragging it out.",
            34,
        )
    if package_template_id == "fb_soft_cta_post_v1":
        return _truncate_words(
            f"{first_sentence} The blog post turns the main idea into a quick practical read.",
            34,
        )
    return _truncate_words(
        f"{first_sentence} The full post gives the short answer in one quick read.",
        28,
    )


def _build_supporting_variant_comment(
    title: str,
    comment_template_id: str,
    blog_publish_record: BlogPublishRecord | None,
) -> str:
    has_blog_url = bool(_resolve_confirmed_blog_url(blog_publish_record))
    topic = _title_topic_fragment(title)
    if comment_template_id == "fb_comment_curiosity_reinforcement_v1":
        base = f"I can drop the full post here if you want the fuller context on {topic}."
        if has_blog_url:
            base = f"Full post here if you want the fuller context on {topic}."
        return _truncate_words(base, 20)
    if comment_template_id == "fb_comment_read_more_prompt_v1":
        base = f"The full post keeps the practical takeaway on {topic} in one place."
        if has_blog_url:
            base = f"Full post here if you want the practical takeaway on {topic}."
        return _truncate_words(base, 18)
    base = "I can drop the full post here if you want the fuller explanation."
    if has_blog_url:
        base = "Full post here if you want the fuller explanation."
    return _truncate_words(base, 18)


def _build_concise_variant_comment(
    title: str,
    comment_template_id: str,
    blog_publish_record: BlogPublishRecord | None,
) -> str:
    has_blog_url = bool(_resolve_confirmed_blog_url(blog_publish_record))
    topic = _title_topic_fragment(title)
    if comment_template_id == "fb_comment_curiosity_reinforcement_v1":
        base = "I can drop the full post here if you want the short answer and the longer context."
        if has_blog_url:
            base = "Full post here if you want the short answer and the longer context."
        return _truncate_words(base, 20)
    if comment_template_id == "fb_comment_read_more_prompt_v1":
        base = f"The full post gives the practical answer on {topic} in one clean read."
        if has_blog_url:
            base = f"Full post here if you want the practical answer on {topic}."
        return _truncate_words(base, 18)
    base = "I can drop the full post here if you want the short answer."
    if has_blog_url:
        base = "Full post here if you want the short answer."
    return _truncate_words(base, 18)


def _primary_answer_text(draft: DraftRecord) -> str:
    for preferred_key in (
        "direct_answer",
        "fast_answer",
        "why_this_food_matters",
        "why_it_happens",
        "background_explanation",
        "example_or_context",
    ):
        section = _section_by_key(draft, preferred_key)
        if section is None:
            continue
        candidate = _section_primary_text(section)
        if candidate:
            return candidate
    fallback = clean_text(draft.excerpt or draft.intro_text or draft.headline_selected)
    if not fallback:
        raise ValueError("Facebook packaging requires readable approved draft text.")
    return fallback


def _section_by_key(draft: DraftRecord, section_key: str) -> DraftSection | None:
    for section in draft.sections:
        if section.section_key == section_key:
            return section
    return None


def _section_primary_text(section: DraftSection) -> str:
    for body_block in section.body_blocks:
        normalized = clean_text(body_block)
        if normalized:
            return normalized
    for bullet in section.bullet_points:
        normalized = clean_text(bullet)
        if normalized:
            return normalized
    return ""


def _title_topic_fragment(title: str) -> str:
    normalized = clean_text(title).rstrip("?!.")
    if normalized.lower().startswith(("why ", "what ", "how ", "when ", "where ")):
        return normalized.split(" ", 1)[1]
    return normalized


def _first_sentence(value: str) -> str:
    normalized = clean_text(value)
    if not normalized:
        return ""
    return SENTENCE_END_RE.split(normalized, maxsplit=1)[0]


def _truncate_words(value: str, max_words: int) -> str:
    words = clean_text(value).split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]).rstrip(" ,;:") + "..."


def _resolve_confirmed_blog_url(blog_publish_record: BlogPublishRecord | None) -> str | None:
    if blog_publish_record is None:
        return None
    blog_url = clean_text(blog_publish_record.wordpress_post_url)
    if not blog_url:
        return None
    if blog_publish_record.wordpress_status in {"prepared_local", ""}:
        return None
    return blog_url


def _validate_package_shape(
    package_template_id: str,
    hook_text: str,
    caption_text: str,
    comment_cta_text: str,
) -> None:
    hook_words = len(clean_text(hook_text).split())
    caption_words = len(clean_text(caption_text).split())
    comment_words = len(clean_text(comment_cta_text).split())
    combined_words = hook_words + caption_words

    if package_template_id == "fb_curiosity_hook_v1" and not 8 <= hook_words <= 18:
        raise ValueError("Curiosity Facebook hooks must stay within 8 to 18 words.")
    if package_template_id == "fb_short_caption_v1" and not 20 <= combined_words <= 45:
        raise ValueError("Short-caption Facebook packages must stay within 20 to 45 words.")
    if package_template_id == "fb_soft_cta_post_v1" and not 25 <= combined_words <= 55:
        raise ValueError("Soft-CTA Facebook packages must stay within 25 to 55 words.")
    if comment_words > 20:
        raise ValueError("Facebook comment CTA text must stay within 20 words.")


def _validate_draft_ready_for_social(draft: DraftRecord) -> None:
    if draft.approval_state != "approved":
        raise ValueError("Facebook packaging requires an approved draft.")
    if not clean_text(draft.headline_selected):
        raise ValueError("Facebook packaging requires a final headline.")
    if not draft.sections:
        raise ValueError("Facebook packaging requires rendered sections.")
    if draft.workflow_state not in {"reviewed", "queued"}:
        raise ValueError("Facebook packaging requires a reviewed approved draft.")


def _validate_blog_publish_linkage(
    draft: DraftRecord,
    blog_publish_record: BlogPublishRecord | None,
) -> None:
    if blog_publish_record is None:
        return
    if blog_publish_record.draft_id != draft.draft_id:
        raise ValueError("Blog publish linkage does not match the approved draft.")
    if not clean_text(blog_publish_record.wordpress_title):
        raise ValueError("Blog publish linkage requires a prepared WordPress title.")


def _resolve_timestamp(created_at: str | None) -> str:
    if created_at:
        return datetime.fromisoformat(created_at.replace("Z", "+00:00")).isoformat()
    return datetime.now(UTC).isoformat()
