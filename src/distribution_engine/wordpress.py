from __future__ import annotations

from datetime import UTC, datetime
import html
import re
import unicodedata
import uuid

from source_engine.cleaner import clean_text

from content_engine.models import DraftRecord, DraftSection
from distribution_engine.models import BlogPublishRecord


ALLOWED_PUBLISH_INTENTS = {"draft", "schedule", "publish_now"}
WHITESPACE_RE = re.compile(r"\s+")
NON_SLUG_CHARS_RE = re.compile(r"[^a-z0-9]+")


def prepare_blog_publish_record(
    draft: DraftRecord,
    publish_intent: str = "draft",
    created_at: str | None = None,
    allow_non_pass_quality: bool = False,
) -> BlogPublishRecord:
    _validate_draft_ready_for_wordpress(
        draft,
        publish_intent=publish_intent,
        allow_non_pass_quality=allow_non_pass_quality,
    )

    timestamp = _resolve_timestamp(created_at)
    title = clean_text(draft.headline_selected)
    excerpt = clean_text(draft.excerpt or draft.intro_text)
    body_html = render_draft_to_wordpress_html(draft)
    slug = build_wordpress_slug(title)

    return BlogPublishRecord(
        blog_publish_id=build_blog_publish_id(draft.draft_id, created_at=timestamp),
        draft_id=draft.draft_id,
        source_item_id=draft.source_item_id,
        template_id=draft.template_id,
        wordpress_title=title,
        wordpress_slug=slug,
        wordpress_excerpt=excerpt,
        wordpress_body_html=body_html,
        wordpress_category=clean_text(draft.category),
        wordpress_tags=[clean_text(tag) for tag in draft.tag_candidates if clean_text(tag)],
        publish_intent=publish_intent,
        canonical_source_url=clean_text(draft.source_url),
        wordpress_post_id=None,
        wordpress_post_url=None,
        wordpress_status="prepared_local",
        published_at_blog=None,
        last_publish_attempt_at=timestamp,
        last_publish_result="payload_prepared",
        last_error=None,
        created_at=timestamp,
        updated_at=timestamp,
    )


def render_draft_to_wordpress_html(draft: DraftRecord) -> str:
    blocks: list[str] = []

    if draft.intro_text.strip():
        blocks.extend(_render_paragraphs(draft.intro_text))

    for section in draft.sections:
        blocks.append(f"<h2>{html.escape(clean_text(section.section_label))}</h2>")
        blocks.extend(_render_section_content(section))

    if draft.related_read_bridge:
        blocks.extend(_render_paragraphs(draft.related_read_bridge))

    rendered = "\n".join(block for block in blocks if block)
    if not rendered.strip():
        raise ValueError("WordPress body rendering produced no output.")
    return rendered


def build_wordpress_slug(title: str) -> str:
    normalized_title = clean_text(title)
    if not normalized_title:
        raise ValueError("WordPress slug cannot be built from an empty title.")

    ascii_title = unicodedata.normalize("NFKD", normalized_title).encode("ascii", "ignore").decode("ascii")
    slug = NON_SLUG_CHARS_RE.sub("-", ascii_title.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if not slug:
        raise ValueError("WordPress slug could not be derived from the title.")
    return slug


def build_blog_publish_id(draft_id: str, created_at: str | None = None) -> str:
    timestamp = _resolve_timestamp(created_at)
    compact_timestamp = timestamp.replace("-", "").replace(":", "").replace("+00:00", "Z")
    return f"blog-{draft_id[:12]}-{compact_timestamp}-{uuid.uuid4().hex[:8]}"


def _validate_draft_ready_for_wordpress(
    draft: DraftRecord,
    publish_intent: str,
    allow_non_pass_quality: bool,
) -> None:
    if publish_intent not in ALLOWED_PUBLISH_INTENTS:
        raise ValueError(f"Unsupported publish_intent: {publish_intent}")
    if draft.approval_state != "approved":
        raise ValueError("WordPress publishing requires an approved draft.")
    if draft.quality_gate_status != "pass" and not allow_non_pass_quality:
        raise ValueError("WordPress publishing requires a pass-quality draft unless explicitly overridden.")
    if not clean_text(draft.headline_selected):
        raise ValueError("WordPress publishing requires a final headline.")
    if not clean_text(draft.category):
        raise ValueError("WordPress publishing requires a final category.")
    if not clean_text(draft.source_url):
        raise ValueError("WordPress publishing requires a canonical source URL.")
    if not draft.sections:
        raise ValueError("WordPress publishing requires at least one rendered section.")


def _render_section_content(section: DraftSection) -> list[str]:
    blocks: list[str] = []
    for body_block in section.body_blocks:
        blocks.extend(_render_paragraphs(body_block))
    if section.bullet_points:
        list_items = "".join(
            f"<li>{html.escape(_normalize_text(point))}</li>"
            for point in section.bullet_points
            if _normalize_text(point)
        )
        if list_items:
            blocks.append(f"<ul>{list_items}</ul>")
    return blocks


def _render_paragraphs(value: str) -> list[str]:
    paragraphs = [
        _normalize_text(paragraph)
        for paragraph in re.split(r"\n\s*\n", value.strip())
        if _normalize_text(paragraph)
    ]
    if not paragraphs:
        normalized = _normalize_text(value)
        return [f"<p>{html.escape(normalized)}</p>"] if normalized else []
    return [f"<p>{html.escape(paragraph)}</p>" for paragraph in paragraphs]


def _normalize_text(value: str) -> str:
    return WHITESPACE_RE.sub(" ", html.unescape(value or "")).strip()


def _resolve_timestamp(created_at: str | None) -> str:
    if created_at:
        return datetime.fromisoformat(created_at.replace("Z", "+00:00")).isoformat()
    return datetime.now(UTC).isoformat()
