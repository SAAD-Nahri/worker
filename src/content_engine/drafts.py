from __future__ import annotations

from datetime import UTC, datetime
import uuid
from urllib.parse import urlparse

from source_engine.models import SourceItem

from content_engine.models import DraftRecord, DraftSection
from content_engine.templates import BlogTemplateContract, select_blog_template_contract


_SECTION_LABELS = {
    "direct_answer": "The Short Answer",
    "why_it_happens": "Why It Happens",
    "supporting_points": "Key Points",
    "recap": "Recap",
    "why_this_food_matters": "Why This Food Matters",
    "practical_points": "Practical Points",
    "caution_or_limit": "Keep It In Perspective",
    "conclusion": "Conclusion",
    "fast_answer": "Fast Answer",
    "background_explanation": "Background",
    "example_or_context": "Example Or Context",
    "close": "Close",
}


def build_draft_id(source_item_id: str, created_at: str | None = None) -> str:
    timestamp = _resolve_timestamp(created_at)
    compact_timestamp = timestamp.strftime("%Y%m%dT%H%M%SZ")
    return f"draft-{source_item_id[:12]}-{compact_timestamp}-{uuid.uuid4().hex[:8]}"


def create_draft_skeleton(
    source_item: SourceItem,
    template_contract: BlogTemplateContract | None = None,
    created_at: str | None = None,
) -> DraftRecord:
    contract = template_contract or select_blog_template_contract(source_item)
    timestamp = _resolve_timestamp(created_at).isoformat()
    source_url = source_item.canonical_url or source_item.source_url

    return DraftRecord(
        draft_id=build_draft_id(source_item.item_id, created_at=created_at),
        workflow_state="drafted",
        approval_state="pending_review",
        language="en",
        source_item_id=source_item.item_id,
        source_id=source_item.source_id,
        source_url=source_url,
        source_domain=_extract_domain(source_url),
        source_title=source_item.raw_title,
        source_published_at=source_item.published_at,
        template_id=contract.template_id,
        template_family=contract.template_family,
        template_version="v1",
        category=contract.default_category,
        tag_candidates=[],
        headline_selected=source_item.raw_title,
        headline_variants=[],
        intro_text="",
        sections=_build_empty_sections(contract),
        excerpt="",
        related_read_bridge=None,
        # Conservative defaults prevent a skeleton from being mistaken for a ready draft.
        quality_gate_status="blocked",
        quality_flags=["draft_not_formatted", "quality_not_evaluated"],
        derivative_risk_level="high",
        derivative_risk_notes="Skeleton draft created before deterministic formatting and derivative-risk evaluation.",
        ai_assistance_log=[],
        review_notes=[],
        created_at=timestamp,
        updated_at=timestamp,
    )


def _build_empty_sections(template_contract: BlogTemplateContract) -> list[DraftSection]:
    return [
        DraftSection(
            section_key=section_key,
            section_label=_SECTION_LABELS.get(section_key, _fallback_section_label(section_key)),
            position=position,
            body_blocks=[],
            bullet_points=[],
        )
        for position, section_key in enumerate(template_contract.body_section_keys, start=1)
    ]


def _fallback_section_label(section_key: str) -> str:
    return section_key.replace("_", " ").title()


def _extract_domain(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.lower()


def _resolve_timestamp(created_at: str | None) -> datetime:
    if created_at:
        fixed = created_at.replace("Z", "+00:00")
        return datetime.fromisoformat(fixed)
    return datetime.now(UTC)
