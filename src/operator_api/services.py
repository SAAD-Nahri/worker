from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from content_engine.formatting import evaluate_draft_against_source
from content_engine.health import build_draft_health_report
from content_engine.models import DraftRecord
from content_engine.review import record_draft_review
from content_engine.templates import get_blog_template_contract
from content_engine.storage import (
    DRAFT_RECORDS_PATH,
    DRAFT_REVIEWS_PATH,
    append_draft_records,
    append_draft_review_records,
    load_latest_draft_record,
    read_draft_review_records,
)
from distribution_engine.activation import build_system_activation_readiness_report
from distribution_engine.health import build_distribution_health_report
from distribution_engine.publish_updates import record_blog_publish_update
from distribution_engine.queue_review import record_queue_review
from distribution_engine.review import record_social_package_review
from distribution_engine.schedule_report import build_distribution_schedule_report
from distribution_engine.scheduling import validate_blog_schedule_allowed
from distribution_engine.storage import (
    BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
    BLOG_PUBLISH_RECORDS_PATH,
    FACEBOOK_PUBLISH_RECORDS_PATH,
    QUEUE_ITEM_RECORDS_PATH,
    QUEUE_REVIEW_RECORDS_PATH,
    SOCIAL_PACKAGE_RECORDS_PATH,
    SOCIAL_PACKAGE_REVIEWS_PATH,
    append_blog_facebook_mapping_records,
    append_blog_publish_records,
    append_queue_item_records,
    append_queue_review_records,
    append_social_package_records,
    append_social_package_review_records,
    load_latest_blog_publish_record,
    load_latest_queue_item_record,
    load_latest_social_package_for_blog_publish,
    load_latest_social_package_record,
    read_blog_facebook_mapping_records,
    read_blog_publish_records,
    read_facebook_publish_records,
    read_queue_item_records,
    read_queue_review_records,
    read_social_package_records,
    read_social_package_review_records,
)
from distribution_engine.workflow import prepare_distribution_linkage_records
from media_engine.assets import resolve_asset_readiness
from media_engine.review import record_asset_review
from media_engine.storage import (
    ASSET_RECORDS_PATH,
    ASSET_REVIEWS_PATH,
    MEDIA_BRIEF_RECORDS_PATH,
    append_asset_records,
    append_asset_review_records,
    load_latest_asset_for_blog_publish,
    load_latest_asset_for_draft,
    load_latest_asset_record,
    load_latest_asset_for_social_package,
    load_latest_media_brief_for_draft,
    load_latest_media_brief_record,
    read_asset_records,
    read_asset_review_records,
    read_media_brief_records,
)
from source_engine.storage import SOURCE_ITEMS_PATH, load_latest_source_item


FAST_LANE_PLACEHOLDER = {
    "status": "disabled",
    "phase_gate": "phase_5_5",
    "recommendation_badge": "not_active",
    "confidence_lane": None,
    "shadow_mode": "not_available",
    "message": "Autoapproval remains disabled until Phase 5.5 shadow mode and narrow fast-lane validation are complete.",
}


@dataclass(frozen=True)
class OperatorApiPaths:
    draft_records_path: Path = DRAFT_RECORDS_PATH
    draft_reviews_path: Path = DRAFT_REVIEWS_PATH
    source_items_path: Path = SOURCE_ITEMS_PATH
    blog_publish_records_path: Path = BLOG_PUBLISH_RECORDS_PATH
    social_package_records_path: Path = SOCIAL_PACKAGE_RECORDS_PATH
    social_package_reviews_path: Path = SOCIAL_PACKAGE_REVIEWS_PATH
    media_brief_records_path: Path = MEDIA_BRIEF_RECORDS_PATH
    asset_records_path: Path = ASSET_RECORDS_PATH
    asset_review_records_path: Path = ASSET_REVIEWS_PATH
    facebook_publish_records_path: Path = FACEBOOK_PUBLISH_RECORDS_PATH
    queue_item_records_path: Path = QUEUE_ITEM_RECORDS_PATH
    queue_review_records_path: Path = QUEUE_REVIEW_RECORDS_PATH
    mapping_records_path: Path = BLOG_FACEBOOK_MAPPING_RECORDS_PATH


def build_dashboard_payload(paths: OperatorApiPaths | None = None) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    draft_reviews = read_draft_review_records(active_paths.draft_reviews_path)
    social_reviews = read_social_package_review_records(active_paths.social_package_reviews_path)
    asset_reviews = read_asset_review_records(active_paths.asset_review_records_path)
    queue_reviews = read_queue_review_records(active_paths.queue_review_records_path)
    latest_queue_items = _latest_queue_items_by_lineage(
        read_queue_item_records(active_paths.queue_item_records_path)
    )
    draft_summary, draft_rows = build_draft_health_report(
        draft_records_path=active_paths.draft_records_path,
        draft_reviews_path=active_paths.draft_reviews_path,
    )
    distribution_summary, distribution_rows = build_distribution_health_report(
        blog_publish_records_path=active_paths.blog_publish_records_path,
        social_package_records_path=active_paths.social_package_records_path,
        social_package_reviews_path=active_paths.social_package_reviews_path,
        asset_records_path=active_paths.asset_records_path,
        facebook_publish_records_path=active_paths.facebook_publish_records_path,
        queue_item_records_path=active_paths.queue_item_records_path,
        mapping_records_path=active_paths.mapping_records_path,
    )
    schedule_summary, _ = build_distribution_schedule_report(
        blog_publish_records_path=active_paths.blog_publish_records_path,
        social_package_records_path=active_paths.social_package_records_path,
        social_package_reviews_path=active_paths.social_package_reviews_path,
        facebook_publish_records_path=active_paths.facebook_publish_records_path,
        queue_item_records_path=active_paths.queue_item_records_path,
        mapping_records_path=active_paths.mapping_records_path,
    )
    activation_summary, _, _, _ = build_system_activation_readiness_report(
        draft_records_path=active_paths.draft_records_path,
        blog_publish_records_path=active_paths.blog_publish_records_path,
        social_package_records_path=active_paths.social_package_records_path,
        social_package_reviews_path=active_paths.social_package_reviews_path,
        asset_records_path=active_paths.asset_records_path,
        facebook_publish_records_path=active_paths.facebook_publish_records_path,
        queue_item_records_path=active_paths.queue_item_records_path,
        mapping_records_path=active_paths.mapping_records_path,
    )
    recent_activity = _build_recent_review_activity(
        draft_reviews=draft_reviews,
        social_reviews=social_reviews,
        asset_reviews=asset_reviews,
        queue_reviews=queue_reviews,
    )
    current_alerts = _build_current_operator_alerts(
        distribution_rows=distribution_rows,
        activation_summary=activation_summary,
        latest_queue_items=latest_queue_items,
    )
    priority_drafts = _build_priority_draft_rows(draft_rows)
    priority_social_packages = _build_priority_social_rows(
        build_social_package_inbox_payload(paths=active_paths)["rows"]
    )
    priority_media_assets = _build_priority_media_asset_rows(
        build_media_asset_inbox_payload(paths=active_paths)["rows"]
    )
    priority_queue_items = _build_priority_queue_rows(
        build_queue_inbox_payload(paths=active_paths)["rows"]
    )

    return {
        "drafts": {
            "pending_review_count": draft_summary.operator_signal_counts.get("ready_for_review", 0)
            + draft_summary.operator_signal_counts.get("review_flag_pending", 0),
            "needs_edits_count": draft_summary.operator_signal_counts.get("needs_revision", 0),
            "approved_for_next_step_count": draft_summary.operator_signal_counts.get(
                "approved_ready_for_phase_3", 0
            )
            + draft_summary.operator_signal_counts.get("approved_with_review_flags", 0),
            "summary": draft_summary.to_dict(),
        },
        "social_packages": {
            "pending_review_count": distribution_summary.operator_signal_counts.get(
                "ready_for_social_review", 0
            ),
            "needs_edits_count": distribution_summary.operator_signal_counts.get(
                "social_needs_edits", 0
            ),
            "approved_for_queue_count": distribution_summary.operator_signal_counts.get(
                "approved_for_queue", 0
            )
            + distribution_summary.operator_signal_counts.get("ready_for_facebook_publish", 0)
            + distribution_summary.operator_signal_counts.get("ready_for_facebook_schedule", 0),
        },
        "media_assets": {
            "pending_review_count": distribution_summary.asset_approval_counts.get("pending_review", 0),
            "needs_edits_count": distribution_summary.asset_approval_counts.get("needs_edits", 0),
            "approved_count": distribution_summary.asset_approval_counts.get("approved", 0),
        },
        "queue": {
            "ready_items_count": schedule_summary.ready_for_blog_schedule
            + schedule_summary.ready_for_facebook_schedule
            + distribution_summary.operator_signal_counts.get("approved_for_queue", 0),
            "schedule_collision_count": distribution_summary.rows_with_schedule_alerts,
        },
        "transport": {
            "failure_count": distribution_summary.operator_signal_counts.get("blog_publish_failed", 0)
            + distribution_summary.operator_signal_counts.get("facebook_publish_failed", 0),
            "activation_signal": activation_summary.readiness_signal,
            "activation_blocking_reasons": list(activation_summary.blocking_reasons),
        },
        "recent_activity": recent_activity,
        "current_alerts": current_alerts,
        "priority_drafts": priority_drafts,
        "priority_social_packages": priority_social_packages,
        "priority_media_assets": priority_media_assets,
        "priority_queue_items": priority_queue_items,
        "fast_lane": dict(FAST_LANE_PLACEHOLDER),
        "meta": {
            "latest_draft_snapshot_at": draft_summary.latest_snapshot_at,
            "latest_distribution_snapshot_at": distribution_summary.latest_snapshot_at,
            "draft_row_count": len(draft_rows),
            "distribution_row_count": len(distribution_rows),
        },
    }


def build_draft_inbox_payload(
    paths: OperatorApiPaths | None = None,
    *,
    search: str | None = None,
    approval_state: str | None = None,
    operator_signal: str | None = None,
    source_domain: str | None = None,
    template_id: str | None = None,
    category: str | None = None,
) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    summary, rows = build_draft_health_report(
        draft_records_path=active_paths.draft_records_path,
        draft_reviews_path=active_paths.draft_reviews_path,
    )
    filtered_rows = _filter_draft_rows(
        [row.to_dict() for row in rows],
        search=search,
        approval_state=approval_state,
        operator_signal=operator_signal,
        source_domain=source_domain,
        template_id=template_id,
        category=category,
    )
    filtered_rows.sort(key=_draft_inbox_sort_key)
    return {
        "summary": _build_filtered_draft_summary(filtered_rows, summary.to_dict()),
        "rows": filtered_rows,
        "applied_filters": _compact_filter_map(
            {
                "search": search,
                "approval_state": approval_state,
                "operator_signal": operator_signal,
                "source_domain": source_domain,
                "template_id": template_id,
                "category": category,
            }
        ),
        "fast_lane": dict(FAST_LANE_PLACEHOLDER),
    }


def build_draft_detail_payload(draft_id: str, paths: OperatorApiPaths | None = None) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    draft = load_latest_draft_record(draft_id, path=active_paths.draft_records_path)
    review_history = [
        review.to_dict()
        for review in read_draft_review_records(active_paths.draft_reviews_path)
        if review.draft_id == draft_id
    ]
    latest_blog_publish = None
    latest_social_package = None
    for blog_publish in read_blog_publish_records(active_paths.blog_publish_records_path):
        if blog_publish.draft_id == draft_id:
            latest_blog_publish = blog_publish
    for social_package in read_social_package_records(active_paths.social_package_records_path):
        if social_package.draft_id == draft_id:
            latest_social_package = social_package
    latest_media_brief = _latest_media_brief_for_draft(draft_id, active_paths)
    latest_asset = _latest_asset_for_draft_or_blog_publish(
        draft_id=draft_id,
        blog_publish_id=latest_blog_publish.blog_publish_id if latest_blog_publish else None,
        active_paths=active_paths,
    )
    asset_complete, asset_block_reason = resolve_asset_readiness(latest_asset)
    return {
        "draft": draft.to_dict(),
        "source_lineage": {
            "source_item_id": draft.source_item_id,
            "source_id": draft.source_id,
            "source_domain": draft.source_domain,
            "source_title": draft.source_title,
            "source_url": draft.source_url,
            "source_published_at": draft.source_published_at,
        },
        "review_history": review_history,
        "downstream": {
            "blog_publish_id": latest_blog_publish.blog_publish_id if latest_blog_publish else None,
            "social_package_id": latest_social_package.social_package_id if latest_social_package else None,
            "media_brief_id": latest_media_brief.media_brief_id if latest_media_brief else None,
            "asset_record_id": latest_asset.asset_record_id if latest_asset else None,
            "asset_complete": asset_complete,
            "asset_block_reason": asset_block_reason,
        },
        "linked_media_brief": latest_media_brief.to_dict() if latest_media_brief else None,
        "linked_asset": latest_asset.to_dict() if latest_asset else None,
        "fast_lane": dict(FAST_LANE_PLACEHOLDER),
    }


def apply_draft_review_action(
    draft_id: str,
    *,
    review_outcome: str,
    review_notes: list[str] | tuple[str, ...] | None,
    reviewer_label: str,
    paths: OperatorApiPaths | None = None,
) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    draft = load_latest_draft_record(draft_id, path=active_paths.draft_records_path)
    updated_draft, review_record = record_draft_review(
        draft,
        review_outcome=review_outcome,
        review_notes=review_notes,
        reviewer_label=reviewer_label,
    )
    append_draft_records([updated_draft], path=active_paths.draft_records_path)
    append_draft_review_records([review_record], path=active_paths.draft_reviews_path)
    return build_draft_detail_payload(updated_draft.draft_id, paths=active_paths)


def apply_draft_headline_variant_selection(
    draft_id: str,
    *,
    headline_variant: str,
    paths: OperatorApiPaths | None = None,
) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    draft = load_latest_draft_record(draft_id, path=active_paths.draft_records_path)
    normalized_variant = headline_variant.strip()
    allowed_variants = [variant.strip() for variant in draft.headline_variants if variant.strip()]
    if not allowed_variants:
        raise ValueError("Draft does not have prepared headline variants to select from.")
    if normalized_variant != draft.headline_selected and normalized_variant not in allowed_variants:
        raise ValueError("Requested headline variant is not available on this draft.")
    if normalized_variant == draft.headline_selected:
        return build_draft_detail_payload(draft_id, paths=active_paths)

    updated_draft = deepcopy(draft)
    updated_draft.headline_selected = normalized_variant
    updated_draft.updated_at = _resolve_timestamp()
    source_item = load_latest_source_item(
        updated_draft.source_item_id,
        path=active_paths.source_items_path,
    )
    _refresh_draft_after_content_change(updated_draft, source_item)
    append_draft_records([updated_draft], path=active_paths.draft_records_path)
    return build_draft_detail_payload(updated_draft.draft_id, paths=active_paths)


def build_social_package_inbox_payload(
    paths: OperatorApiPaths | None = None,
    *,
    search: str | None = None,
    approval_state: str | None = None,
    linkage_state: str | None = None,
) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    latest_packages = _latest_social_packages(
        read_social_package_records(active_paths.social_package_records_path)
    )
    latest_blog_publish_by_id = _latest_blog_publish_by_id(
        read_blog_publish_records(active_paths.blog_publish_records_path)
    )
    latest_review_by_package, review_counts = _latest_social_review_maps(
        read_social_package_review_records(active_paths.social_package_reviews_path)
    )
    latest_queue_by_lineage = _latest_queue_items_by_lineage(
        read_queue_item_records(active_paths.queue_item_records_path)
    )

    rows: list[dict[str, object]] = []
    approval_counts: dict[str, int] = {}
    for package in latest_packages.values():
        blog_publish = latest_blog_publish_by_id.get(package.blog_publish_id or "")
        queue_item = latest_queue_by_lineage.get((package.blog_publish_id or "", "facebook_publish"))
        latest_review = latest_review_by_package.get(package.social_package_id)
        approval_counts[package.approval_state] = approval_counts.get(package.approval_state, 0) + 1
        rows.append(
            {
                "social_package_id": package.social_package_id,
                "draft_id": package.draft_id,
                "blog_publish_id": package.blog_publish_id,
                "linked_blog_title": blog_publish.wordpress_title if blog_publish else None,
                "hook_text": package.hook_text,
                "caption_text": package.caption_text,
                "comment_cta_text": package.comment_cta_text,
                "approval_state": package.approval_state,
                "selected_variant_label": package.selected_variant_label,
                "blog_url": package.blog_url,
                "linkage_state": queue_item.queue_state if queue_item else "unlinked",
                "latest_review_outcome": latest_review.review_outcome if latest_review else None,
                "latest_reviewed_at": latest_review.reviewed_at if latest_review else None,
                "review_count": review_counts.get(package.social_package_id, 0),
                "updated_at": package.updated_at,
            }
        )
    rows = _filter_social_rows(
        rows,
        search=search,
        approval_state=approval_state,
        linkage_state=linkage_state,
    )
    rows.sort(key=_social_inbox_sort_key)
    return {
        "summary": _build_filtered_social_summary(rows, approval_counts),
        "rows": rows,
        "applied_filters": _compact_filter_map(
            {
                "search": search,
                "approval_state": approval_state,
                "linkage_state": linkage_state,
            }
        ),
        "fast_lane": dict(FAST_LANE_PLACEHOLDER),
    }


def build_social_package_detail_payload(
    social_package_id: str,
    paths: OperatorApiPaths | None = None,
) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    social_package = load_latest_social_package_record(
        social_package_id,
        path=active_paths.social_package_records_path,
    )
    draft = load_latest_draft_record(social_package.draft_id, path=active_paths.draft_records_path)
    blog_publish = None
    if social_package.blog_publish_id:
        blog_publish = load_latest_blog_publish_record(
            social_package.blog_publish_id,
            path=active_paths.blog_publish_records_path,
        )
    linked_asset = _latest_asset_for_social_context(
        social_package_id=social_package.social_package_id,
        blog_publish_id=social_package.blog_publish_id,
        draft_id=social_package.draft_id,
        active_paths=active_paths,
    )
    asset_complete, asset_block_reason = resolve_asset_readiness(linked_asset)
    review_history = [
        review.to_dict()
        for review in read_social_package_review_records(active_paths.social_package_reviews_path)
        if review.social_package_id == social_package_id
    ]
    return {
        "social_package": social_package.to_dict(),
        "linked_blog_publish": blog_publish.to_dict() if blog_publish else None,
        "linked_asset": linked_asset.to_dict() if linked_asset else None,
        "asset_readiness": {
            "asset_complete": asset_complete,
            "asset_block_reason": asset_block_reason,
        },
        "linked_draft": {
            "draft_id": draft.draft_id,
            "headline_selected": draft.headline_selected,
            "headline_variants": list(draft.headline_variants),
            "excerpt": draft.excerpt,
            "template_id": draft.template_id,
            "category": draft.category,
            "ai_assistance_log": [entry.to_dict() for entry in draft.ai_assistance_log],
        },
        "review_history": review_history,
        "fast_lane": dict(FAST_LANE_PLACEHOLDER),
    }


def apply_social_package_review_action(
    social_package_id: str,
    *,
    review_outcome: str,
    review_notes: list[str] | tuple[str, ...] | None,
    reviewer_label: str,
    paths: OperatorApiPaths | None = None,
) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    social_package = load_latest_social_package_record(
        social_package_id,
        path=active_paths.social_package_records_path,
    )
    updated_package, review_record = record_social_package_review(
        social_package,
        review_outcome=review_outcome,
        review_notes=review_notes,
        reviewer_label=reviewer_label,
    )
    append_social_package_records([updated_package], path=active_paths.social_package_records_path)
    append_social_package_review_records([review_record], path=active_paths.social_package_reviews_path)
    _refresh_social_linkage_records(updated_package, active_paths=active_paths)
    return build_social_package_detail_payload(updated_package.social_package_id, paths=active_paths)


def apply_social_package_variant_selection(
    social_package_id: str,
    *,
    variant_label: str,
    paths: OperatorApiPaths | None = None,
) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    social_package = load_latest_social_package_record(
        social_package_id,
        path=active_paths.social_package_records_path,
    )
    selected_variant = _resolve_social_package_variant(social_package, variant_label)
    variant_changed = (
        social_package.hook_text != selected_variant["hook_text"]
        or social_package.caption_text != selected_variant["caption_text"]
        or social_package.comment_cta_text != selected_variant["comment_cta_text"]
        or social_package.selected_variant_label != selected_variant["label"]
    )
    if not variant_changed:
        return build_social_package_detail_payload(social_package_id, paths=active_paths)

    updated_package = deepcopy(social_package)
    updated_package.hook_text = selected_variant["hook_text"]
    updated_package.caption_text = selected_variant["caption_text"]
    updated_package.comment_cta_text = selected_variant["comment_cta_text"]
    updated_package.selected_variant_label = selected_variant["label"]
    updated_package.updated_at = _resolve_timestamp()
    if updated_package.approval_state == "approved":
        updated_package.approval_state = "pending_review"
    append_social_package_records([updated_package], path=active_paths.social_package_records_path)
    _refresh_social_linkage_records(updated_package, active_paths=active_paths)
    return build_social_package_detail_payload(updated_package.social_package_id, paths=active_paths)


def build_media_asset_inbox_payload(
    paths: OperatorApiPaths | None = None,
    *,
    search: str | None = None,
    approval_state: str | None = None,
    asset_source_kind: str | None = None,
) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    latest_assets = _latest_assets(read_asset_records(active_paths.asset_records_path))
    latest_media_briefs = _latest_media_briefs(read_media_brief_records(active_paths.media_brief_records_path))
    latest_blog_publish_by_id = _latest_blog_publish_by_id(
        read_blog_publish_records(active_paths.blog_publish_records_path)
    )
    latest_review_by_asset, review_counts = _latest_asset_review_maps(
        read_asset_review_records(active_paths.asset_review_records_path)
    )

    rows: list[dict[str, object]] = []
    approval_counts: dict[str, int] = {}
    for asset in latest_assets.values():
        linked_brief = latest_media_briefs.get(asset.media_brief_id)
        linked_blog = latest_blog_publish_by_id.get(asset.blog_publish_id or "")
        latest_review = latest_review_by_asset.get(asset.asset_record_id)
        asset_complete, asset_block_reason = resolve_asset_readiness(asset)
        approval_counts[asset.approval_state] = approval_counts.get(asset.approval_state, 0) + 1
        rows.append(
            {
                "asset_record_id": asset.asset_record_id,
                "media_brief_id": asset.media_brief_id,
                "draft_id": asset.draft_id,
                "blog_publish_id": asset.blog_publish_id,
                "social_package_id": asset.social_package_id,
                "asset_source_kind": asset.asset_source_kind,
                "approval_state": asset.approval_state,
                "intended_usage": asset.intended_usage,
                "asset_url_or_path": asset.asset_url_or_path,
                "provenance_reference": asset.provenance_reference,
                "linked_blog_title": linked_blog.wordpress_title if linked_blog else None,
                "brief_goal": linked_brief.brief_goal if linked_brief else None,
                "asset_complete": asset_complete,
                "asset_block_reason": asset_block_reason,
                "latest_review_outcome": latest_review.review_outcome if latest_review else None,
                "latest_reviewed_at": latest_review.reviewed_at if latest_review else None,
                "review_count": review_counts.get(asset.asset_record_id, 0),
                "updated_at": asset.updated_at,
            }
        )
    rows = _filter_media_asset_rows(
        rows,
        search=search,
        approval_state=approval_state,
        asset_source_kind=asset_source_kind,
    )
    rows.sort(key=_media_asset_inbox_sort_key)
    return {
        "summary": _build_filtered_media_asset_summary(rows, approval_counts),
        "rows": rows,
        "applied_filters": _compact_filter_map(
            {
                "search": search,
                "approval_state": approval_state,
                "asset_source_kind": asset_source_kind,
            }
        ),
        "fast_lane": dict(FAST_LANE_PLACEHOLDER),
    }


def build_media_asset_detail_payload(
    asset_record_id: str,
    paths: OperatorApiPaths | None = None,
) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    asset_record = load_latest_asset_record(asset_record_id, path=active_paths.asset_records_path)
    media_brief = load_latest_media_brief_record(
        asset_record.media_brief_id,
        path=active_paths.media_brief_records_path,
    )
    draft = load_latest_draft_record(asset_record.draft_id, path=active_paths.draft_records_path)
    blog_publish = None
    if asset_record.blog_publish_id:
        blog_publish = load_latest_blog_publish_record(
            asset_record.blog_publish_id,
            path=active_paths.blog_publish_records_path,
        )
    social_package = None
    if asset_record.social_package_id:
        social_package = load_latest_social_package_record(
            asset_record.social_package_id,
            path=active_paths.social_package_records_path,
        )
    asset_complete, asset_block_reason = resolve_asset_readiness(asset_record)
    review_history = [
        review.to_dict()
        for review in read_asset_review_records(active_paths.asset_review_records_path)
        if review.asset_record_id == asset_record_id
    ]
    return {
        "asset_record": asset_record.to_dict(),
        "linked_media_brief": media_brief.to_dict(),
        "linked_draft": {
            "draft_id": draft.draft_id,
            "headline_selected": draft.headline_selected,
            "excerpt": draft.excerpt,
            "template_id": draft.template_id,
            "category": draft.category,
        },
        "linked_blog_publish": blog_publish.to_dict() if blog_publish else None,
        "linked_social_package": social_package.to_dict() if social_package else None,
        "asset_readiness": {
            "asset_complete": asset_complete,
            "asset_block_reason": asset_block_reason,
        },
        "review_history": review_history,
        "fast_lane": dict(FAST_LANE_PLACEHOLDER),
    }


def apply_media_asset_review_action(
    asset_record_id: str,
    *,
    review_outcome: str,
    review_notes: list[str] | tuple[str, ...] | None,
    reviewer_label: str,
    paths: OperatorApiPaths | None = None,
) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    asset_record = load_latest_asset_record(asset_record_id, path=active_paths.asset_records_path)
    updated_asset, review_record = record_asset_review(
        asset_record,
        review_outcome=review_outcome,
        review_notes=review_notes,
        reviewer_label=reviewer_label,
    )
    append_asset_records([updated_asset], path=active_paths.asset_records_path)
    append_asset_review_records([review_record], path=active_paths.asset_review_records_path)
    return build_media_asset_detail_payload(updated_asset.asset_record_id, paths=active_paths)


def build_queue_inbox_payload(
    paths: OperatorApiPaths | None = None,
    *,
    queue_type: str | None = None,
    queue_state: str | None = None,
    queue_review_state: str | None = None,
    blocked_only: bool = False,
    schedule_allowed: bool | None = None,
) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    latest_queue_items = _latest_queue_items_by_lineage(
        read_queue_item_records(active_paths.queue_item_records_path)
    )
    latest_blog_publish_by_id = _latest_blog_publish_by_id(
        read_blog_publish_records(active_paths.blog_publish_records_path)
    )
    latest_social_package_by_blog_publish = _latest_social_packages_by_blog_publish(
        read_social_package_records(active_paths.social_package_records_path)
    )
    schedule_summary, schedule_rows = build_distribution_schedule_report(
        blog_publish_records_path=active_paths.blog_publish_records_path,
        social_package_records_path=active_paths.social_package_records_path,
        social_package_reviews_path=active_paths.social_package_reviews_path,
        facebook_publish_records_path=active_paths.facebook_publish_records_path,
        queue_item_records_path=active_paths.queue_item_records_path,
        mapping_records_path=active_paths.mapping_records_path,
    )
    latest_queue_review_by_lineage, queue_review_counts = _latest_queue_review_maps(
        read_queue_review_records(active_paths.queue_review_records_path)
    )
    schedule_row_by_blog_publish = {row.blog_publish_id: row for row in schedule_rows}

    rows: list[dict[str, object]] = []
    queue_state_counts: dict[str, int] = {}
    queue_review_state_counts: dict[str, int] = {}
    for lineage_key, queue_item in latest_queue_items.items():
        blog_publish = latest_blog_publish_by_id.get(queue_item.blog_publish_id or "")
        social_package = latest_social_package_by_blog_publish.get(queue_item.blog_publish_id or "")
        linked_asset = _latest_asset_for_draft_or_blog_publish(
            draft_id=queue_item.draft_id,
            blog_publish_id=queue_item.blog_publish_id,
            active_paths=active_paths,
        )
        asset_complete, asset_block_reason = resolve_asset_readiness(linked_asset)
        latest_review = latest_queue_review_by_lineage.get(lineage_key)
        schedule_row = schedule_row_by_blog_publish.get(queue_item.blog_publish_id or "")
        row_queue_review_state = (
            latest_review.updated_queue_review_state if latest_review else "pending_review"
        )
        action_context = _build_queue_action_context(
            queue_item=queue_item,
            blog_publish=blog_publish,
            latest_review=latest_review,
        )
        queue_state_counts[queue_item.queue_state] = queue_state_counts.get(queue_item.queue_state, 0) + 1
        queue_review_state_counts[row_queue_review_state] = (
            queue_review_state_counts.get(row_queue_review_state, 0) + 1
        )
        rows.append(
            {
                "queue_item_id": queue_item.queue_item_id,
                "queue_type": queue_item.queue_type,
                "draft_id": queue_item.draft_id,
                "blog_publish_id": queue_item.blog_publish_id,
                "social_package_id": queue_item.social_package_id,
                "title": blog_publish.wordpress_title if blog_publish else None,
                "social_package_state": social_package.approval_state if social_package else None,
                "asset_record_id": linked_asset.asset_record_id if linked_asset else None,
                "asset_approval_state": linked_asset.approval_state if linked_asset else None,
                "asset_complete": asset_complete,
                "asset_block_reason": asset_block_reason,
                "queue_state": queue_item.queue_state,
                "approval_state": queue_item.approval_state,
                "queue_review_state": row_queue_review_state,
                "latest_review_outcome": latest_review.review_outcome if latest_review else None,
                "latest_reviewed_at": latest_review.reviewed_at if latest_review else None,
                "review_count": queue_review_counts.get(lineage_key, 0),
                "scheduled_for": queue_item.scheduled_for,
                "schedule_intent": schedule_row.scheduling_signal if schedule_row else None,
                "collision_warnings": list(schedule_row.schedule_alerts) if schedule_row else [],
                "approve_allowed": action_context["approve"][0],
                "approve_block_reason": action_context["approve"][1],
                "schedule_allowed": action_context["schedule"][0],
                "schedule_block_reason": action_context["schedule"][1],
                "updated_at": queue_item.updated_at,
            }
        )
    rows = _filter_queue_rows(
        rows,
        queue_type=queue_type,
        queue_state=queue_state,
        queue_review_state=queue_review_state,
        blocked_only=blocked_only,
        schedule_allowed=schedule_allowed,
    )
    rows.sort(key=_queue_inbox_sort_key)
    return {
        "summary": _build_filtered_queue_summary(
            rows,
            queue_state_counts=queue_state_counts,
            queue_review_state_counts=queue_review_state_counts,
            schedule_summary=schedule_summary.to_dict(),
        ),
        "rows": rows,
        "applied_filters": _compact_filter_map(
            {
                "queue_type": queue_type,
                "queue_state": queue_state,
                "queue_review_state": queue_review_state,
                "blocked_only": blocked_only if blocked_only else None,
                "schedule_allowed": schedule_allowed,
            }
        ),
        "fast_lane": dict(FAST_LANE_PLACEHOLDER),
    }


def build_queue_detail_payload(queue_item_id: str, paths: OperatorApiPaths | None = None) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    queue_item = load_latest_queue_item_record(queue_item_id, path=active_paths.queue_item_records_path)
    blog_publish = None
    if queue_item.blog_publish_id:
        blog_publish = load_latest_blog_publish_record(
            queue_item.blog_publish_id,
            path=active_paths.blog_publish_records_path,
        )
    social_package = None
    if queue_item.social_package_id:
        social_package = load_latest_social_package_record(
            queue_item.social_package_id,
            path=active_paths.social_package_records_path,
        )
    elif queue_item.blog_publish_id:
        try:
            social_package = load_latest_social_package_for_blog_publish(
                queue_item.blog_publish_id,
                path=active_paths.social_package_records_path,
            )
        except ValueError:
            social_package = None
    linked_asset = _latest_asset_for_draft_or_blog_publish(
        draft_id=queue_item.draft_id,
        blog_publish_id=queue_item.blog_publish_id,
        active_paths=active_paths,
    )
    asset_complete, asset_block_reason = resolve_asset_readiness(linked_asset)
    latest_mapping = _latest_mapping_for_blog_publish(queue_item.blog_publish_id, active_paths)
    schedule_summary, schedule_rows = build_distribution_schedule_report(
        blog_publish_records_path=active_paths.blog_publish_records_path,
        social_package_records_path=active_paths.social_package_records_path,
        social_package_reviews_path=active_paths.social_package_reviews_path,
        facebook_publish_records_path=active_paths.facebook_publish_records_path,
        queue_item_records_path=active_paths.queue_item_records_path,
        mapping_records_path=active_paths.mapping_records_path,
    )
    schedule_row = next(
        (
            row
            for row in schedule_rows
            if row.blog_publish_id == queue_item.blog_publish_id
        ),
        None,
    )
    lineage_key = (queue_item.blog_publish_id or "", queue_item.queue_type)
    latest_queue_review_by_lineage, _ = _latest_queue_review_maps(
        read_queue_review_records(active_paths.queue_review_records_path)
    )
    review_history = [
        review.to_dict()
        for review in read_queue_review_records(active_paths.queue_review_records_path)
        if (review.blog_publish_id or "", review.queue_type) == lineage_key
    ]
    latest_queue_review = latest_queue_review_by_lineage.get(lineage_key)
    action_context = _build_queue_action_context(
        queue_item=queue_item,
        blog_publish=blog_publish,
        latest_review=latest_queue_review,
    )
    return {
        "queue_item": queue_item.to_dict(),
        "linked_blog_publish": blog_publish.to_dict() if blog_publish else None,
        "linked_social_package": social_package.to_dict() if social_package else None,
        "linked_asset": linked_asset.to_dict() if linked_asset else None,
        "linked_mapping": latest_mapping.to_dict() if latest_mapping else None,
        "asset_readiness": {
            "asset_complete": asset_complete,
            "asset_block_reason": asset_block_reason,
        },
        "schedule_context": {
            "signal": schedule_row.scheduling_signal if schedule_row else None,
            "alerts": list(schedule_row.schedule_alerts) if schedule_row else [],
            "scheduled_for_blog": schedule_row.scheduled_for_blog if schedule_row else None,
            "scheduled_for_facebook": schedule_row.scheduled_for_facebook if schedule_row else None,
            "schedule_summary": schedule_summary.to_dict(),
        },
        "queue_review_state": latest_queue_review.updated_queue_review_state
        if latest_queue_review
        else "pending_review",
        "allowed_actions": {
            "approve": action_context["approve"][0],
            "approve_block_reason": action_context["approve"][1],
            "hold": action_context["hold"][0],
            "hold_block_reason": action_context["hold"][1],
            "remove": action_context["remove"][0],
            "remove_block_reason": action_context["remove"][1],
            "schedule": action_context["schedule"][0],
            "schedule_block_reason": action_context["schedule"][1],
        },
        "review_history": review_history,
        "fast_lane": dict(FAST_LANE_PLACEHOLDER),
    }


def apply_queue_review_action(
    queue_item_id: str,
    *,
    review_outcome: str,
    review_notes: list[str] | tuple[str, ...] | None,
    reviewer_label: str,
    paths: OperatorApiPaths | None = None,
) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    queue_item = load_latest_queue_item_record(queue_item_id, path=active_paths.queue_item_records_path)
    review_record = record_queue_review(
        queue_item,
        review_outcome=review_outcome,
        review_notes=review_notes,
        reviewer_label=reviewer_label,
    )
    append_queue_review_records([review_record], path=active_paths.queue_review_records_path)
    return build_queue_detail_payload(queue_item.queue_item_id, paths=active_paths)


def apply_queue_schedule_action(
    queue_item_id: str,
    *,
    scheduled_for: str,
    reviewer_label: str,
    schedule_mode: str = "manual",
    paths: OperatorApiPaths | None = None,
) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    queue_item = load_latest_queue_item_record(queue_item_id, path=active_paths.queue_item_records_path)
    if queue_item.queue_type != "blog_publish":
        raise ValueError(
            "Approval UI V1 supports direct scheduling only for blog queue items. Facebook scheduling stays in the transport stage."
        )

    latest_queue_review_by_lineage, _ = _latest_queue_review_maps(
        read_queue_review_records(active_paths.queue_review_records_path)
    )
    latest_review = latest_queue_review_by_lineage.get((queue_item.blog_publish_id or "", queue_item.queue_type))
    if latest_review is None or latest_review.review_outcome != "approved":
        raise ValueError("Queue scheduling requires an approved queue review first.")

    blog_publish_record = load_latest_blog_publish_record(
        queue_item.blog_publish_id or "",
        path=active_paths.blog_publish_records_path,
    )
    updated_blog_publish = record_blog_publish_update(
        blog_publish_record,
        update_action="scheduled",
        wordpress_post_id=blog_publish_record.wordpress_post_id,
        wordpress_post_url=blog_publish_record.wordpress_post_url,
        schedule_mode=schedule_mode,
        schedule_approved_by=reviewer_label,
        schedule_applied_by=reviewer_label if schedule_mode == "manual" else None,
        scheduled_for_blog=scheduled_for,
    )
    append_blog_publish_records([updated_blog_publish], path=active_paths.blog_publish_records_path)

    social_package = None
    try:
        social_package = load_latest_social_package_for_blog_publish(
            updated_blog_publish.blog_publish_id,
            path=active_paths.social_package_records_path,
        )
    except ValueError:
        social_package = None
    facebook_publish_record = (
        _latest_facebook_publish_for_social_package(social_package.social_package_id, active_paths)
        if social_package
        else None
    )
    blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
        updated_blog_publish,
        social_package_record=social_package,
        facebook_publish_record=facebook_publish_record,
    )
    append_queue_item_records([blog_queue, facebook_queue], path=active_paths.queue_item_records_path)
    append_blog_facebook_mapping_records([mapping], path=active_paths.mapping_records_path)
    return build_queue_detail_payload(blog_queue.queue_item_id, paths=active_paths)


def build_combined_health_payload(paths: OperatorApiPaths | None = None) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    draft_summary, _ = build_draft_health_report(
        draft_records_path=active_paths.draft_records_path,
        draft_reviews_path=active_paths.draft_reviews_path,
    )
    distribution_summary, _ = build_distribution_health_report(
        blog_publish_records_path=active_paths.blog_publish_records_path,
        social_package_records_path=active_paths.social_package_records_path,
        social_package_reviews_path=active_paths.social_package_reviews_path,
        asset_records_path=active_paths.asset_records_path,
        facebook_publish_records_path=active_paths.facebook_publish_records_path,
        queue_item_records_path=active_paths.queue_item_records_path,
        mapping_records_path=active_paths.mapping_records_path,
    )
    schedule_summary, _ = build_distribution_schedule_report(
        blog_publish_records_path=active_paths.blog_publish_records_path,
        social_package_records_path=active_paths.social_package_records_path,
        social_package_reviews_path=active_paths.social_package_reviews_path,
        facebook_publish_records_path=active_paths.facebook_publish_records_path,
        queue_item_records_path=active_paths.queue_item_records_path,
        mapping_records_path=active_paths.mapping_records_path,
    )
    activation_summary, config_statuses, _, _ = build_system_activation_readiness_report(
        draft_records_path=active_paths.draft_records_path,
        blog_publish_records_path=active_paths.blog_publish_records_path,
        social_package_records_path=active_paths.social_package_records_path,
        social_package_reviews_path=active_paths.social_package_reviews_path,
        asset_records_path=active_paths.asset_records_path,
        facebook_publish_records_path=active_paths.facebook_publish_records_path,
        queue_item_records_path=active_paths.queue_item_records_path,
        mapping_records_path=active_paths.mapping_records_path,
    )
    return {
        "draft_health": draft_summary.to_dict(),
        "distribution_health": distribution_summary.to_dict(),
        "distribution_schedule": schedule_summary.to_dict(),
        "activation": {
            "summary": activation_summary.to_dict(),
            "config_statuses": [status.to_dict() for status in config_statuses],
        },
        "fast_lane": dict(FAST_LANE_PLACEHOLDER),
    }


def build_operator_validation_payload(paths: OperatorApiPaths | None = None) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    dashboard = build_dashboard_payload(paths=active_paths)
    drafts = build_draft_inbox_payload(paths=active_paths)
    social_packages = build_social_package_inbox_payload(paths=active_paths)
    media_assets = build_media_asset_inbox_payload(paths=active_paths)
    queue = build_queue_inbox_payload(paths=active_paths)
    combined_health = build_combined_health_payload(paths=active_paths)

    return {
        "status": "ready_for_live_plugin_validation",
        "endpoint_checks": {
            "dashboard_summary": {
                "ok": True,
                "path": "/dashboard/summary",
            },
            "drafts_inbox": {
                "ok": True,
                "path": "/drafts/inbox",
            },
            "social_packages_inbox": {
                "ok": True,
                "path": "/social-packages/inbox",
            },
            "media_assets_inbox": {
                "ok": True,
                "path": "/media-assets/inbox",
            },
            "queue_inbox": {
                "ok": True,
                "path": "/queue/inbox",
            },
            "combined_health": {
                "ok": True,
                "path": "/health/combined",
            },
        },
        "workflow_snapshot": {
            "draft_pending_review_count": dashboard["drafts"]["pending_review_count"],
            "draft_needs_edits_count": dashboard["drafts"]["needs_edits_count"],
            "social_pending_review_count": dashboard["social_packages"]["pending_review_count"],
            "media_pending_review_count": dashboard["media_assets"]["pending_review_count"],
            "queue_ready_items_count": dashboard["queue"]["ready_items_count"],
            "queue_collision_count": dashboard["queue"]["schedule_collision_count"],
            "transport_failure_count": dashboard["transport"]["failure_count"],
            "activation_signal": dashboard["transport"]["activation_signal"],
            "fast_lane_status": dashboard["fast_lane"]["status"],
        },
        "record_counts": {
            "draft_rows": len(drafts["rows"]),
            "social_package_rows": len(social_packages["rows"]),
            "media_asset_rows": len(media_assets["rows"]),
            "queue_rows": len(queue["rows"]),
        },
        "review_surfaces": {
            "draft_review_available": True,
            "social_review_available": True,
            "media_review_available": True,
            "queue_review_available": True,
            "queue_schedule_available": any(row["schedule_allowed"] for row in queue["rows"]),
        },
        "notes": [
            "This validation payload proves backend readiness and current workflow visibility.",
            "Live WordPress-admin validation is still required to verify plugin rendering, settings save flow, and safe admin notices.",
        ],
        "combined_health": combined_health,
    }


def _refresh_draft_after_content_change(draft: DraftRecord, source_item) -> None:
    template_contract = get_blog_template_contract(draft.template_id)
    quality_result = evaluate_draft_against_source(
        draft,
        source_item,
        template_contract=template_contract,
    )
    draft.quality_gate_status = quality_result.quality_gate_status
    draft.quality_flags = list(quality_result.quality_flags)
    draft.derivative_risk_level = quality_result.derivative_risk_level
    draft.derivative_risk_notes = quality_result.derivative_risk_notes
    draft.approval_state = "pending_review"
    draft.workflow_state = "drafted"


def _refresh_social_linkage_records(social_package, *, active_paths: OperatorApiPaths) -> None:
    if not social_package.blog_publish_id:
        return
    blog_publish_record = load_latest_blog_publish_record(
        social_package.blog_publish_id,
        path=active_paths.blog_publish_records_path,
    )
    facebook_publish_record = _latest_facebook_publish_for_social_package(
        social_package.social_package_id,
        active_paths=active_paths,
    )
    blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
        blog_publish_record,
        social_package_record=social_package,
        facebook_publish_record=facebook_publish_record,
    )
    append_queue_item_records(
        [blog_queue, facebook_queue],
        path=active_paths.queue_item_records_path,
    )
    append_blog_facebook_mapping_records([mapping], path=active_paths.mapping_records_path)


def _resolve_social_package_variant(social_package, variant_label: str) -> dict[str, str]:
    normalized_label = (variant_label or "").strip()
    if not normalized_label:
        raise ValueError("A social variant label is required.")
    variant_options = getattr(social_package, "variant_options", None) or []
    if not variant_options:
        raise ValueError("Social package does not have prepared variants to select from.")
    for option in variant_options:
        if str(option.get("label", "")).strip() == normalized_label:
            return {
                "label": normalized_label,
                "hook_text": str(option.get("hook_text", "")).strip(),
                "caption_text": str(option.get("caption_text", "")).strip(),
                "comment_cta_text": str(option.get("comment_cta_text", "")).strip(),
            }
    raise ValueError("Requested social variant is not available on this package.")


def _resolve_timestamp(value: str | None = None) -> str:
    if value:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
    return datetime.now(UTC).isoformat()


def _compact_filter_map(values: dict[str, object]) -> dict[str, object]:
    compact: dict[str, object] = {}
    for key, value in values.items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        compact[key] = value
    return compact


def _filter_draft_rows(
    rows: list[dict[str, object]],
    *,
    search: str | None,
    approval_state: str | None,
    operator_signal: str | None,
    source_domain: str | None,
    template_id: str | None,
    category: str | None,
) -> list[dict[str, object]]:
    search_value = (search or "").strip().lower()
    filtered: list[dict[str, object]] = []
    for row in rows:
        if approval_state and row.get("approval_state") != approval_state:
            continue
        if operator_signal and row.get("operator_signal") != operator_signal:
            continue
        if source_domain and row.get("source_domain") != source_domain:
            continue
        if template_id and row.get("template_id") != template_id:
            continue
        if category and row.get("category") != category:
            continue
        if search_value and not _row_matches_search(
            row,
            search_value,
            keys=(
                "draft_id",
                "source_item_id",
                "source_domain",
                "template_id",
                "category",
                "quality_gate_status",
                "routing_action",
                "operator_signal",
            ),
        ):
            continue
        filtered.append(row)
    return filtered


def _filter_social_rows(
    rows: list[dict[str, object]],
    *,
    search: str | None,
    approval_state: str | None,
    linkage_state: str | None,
) -> list[dict[str, object]]:
    search_value = (search or "").strip().lower()
    filtered: list[dict[str, object]] = []
    for row in rows:
        if approval_state and row.get("approval_state") != approval_state:
            continue
        if linkage_state and row.get("linkage_state") != linkage_state:
            continue
        if search_value and not _row_matches_search(
            row,
            search_value,
            keys=(
                "social_package_id",
                "draft_id",
                "blog_publish_id",
                "linked_blog_title",
                "hook_text",
                "caption_text",
                "comment_cta_text",
                "selected_variant_label",
                "linkage_state",
            ),
        ):
            continue
        filtered.append(row)
    return filtered


def _filter_media_asset_rows(
    rows: list[dict[str, object]],
    *,
    search: str | None,
    approval_state: str | None,
    asset_source_kind: str | None,
) -> list[dict[str, object]]:
    search_value = (search or "").strip().lower()
    filtered: list[dict[str, object]] = []
    for row in rows:
        if approval_state and row.get("approval_state") != approval_state:
            continue
        if asset_source_kind and row.get("asset_source_kind") != asset_source_kind:
            continue
        if search_value and not _row_matches_search(
            row,
            search_value,
            keys=(
                "asset_record_id",
                "media_brief_id",
                "draft_id",
                "blog_publish_id",
                "social_package_id",
                "asset_source_kind",
                "provenance_reference",
                "linked_blog_title",
                "brief_goal",
            ),
        ):
            continue
        filtered.append(row)
    return filtered


def _filter_queue_rows(
    rows: list[dict[str, object]],
    *,
    queue_type: str | None,
    queue_state: str | None,
    queue_review_state: str | None,
    blocked_only: bool,
    schedule_allowed: bool | None,
) -> list[dict[str, object]]:
    filtered: list[dict[str, object]] = []
    for row in rows:
        if queue_type and row.get("queue_type") != queue_type:
            continue
        if queue_state and row.get("queue_state") != queue_state:
            continue
        if queue_review_state and row.get("queue_review_state") != queue_review_state:
            continue
        if blocked_only and not (row.get("approve_block_reason") or row.get("schedule_block_reason")):
            continue
        if schedule_allowed is not None and bool(row.get("schedule_allowed")) != schedule_allowed:
            continue
        filtered.append(row)
    return filtered


def _row_matches_search(row: dict[str, object], search_value: str, *, keys: tuple[str, ...]) -> bool:
    for key in keys:
        value = row.get(key)
        if value is None:
            continue
        if search_value in str(value).lower():
            return True
    return False


def _draft_inbox_sort_key(row: dict[str, object]) -> tuple[int, str, str]:
    return (
        _draft_action_rank(row),
        str(row.get("latest_updated_at", "")),
        str(row.get("draft_id", "")),
    )


def _social_inbox_sort_key(row: dict[str, object]) -> tuple[int, str, str]:
    return (
        _social_action_rank(row),
        str(row.get("updated_at", "")),
        str(row.get("social_package_id", "")),
    )


def _media_asset_inbox_sort_key(row: dict[str, object]) -> tuple[int, str, str]:
    return (
        _media_asset_action_rank(row),
        str(row.get("updated_at", "")),
        str(row.get("asset_record_id", "")),
    )


def _queue_inbox_sort_key(row: dict[str, object]) -> tuple[int, str, str]:
    return (
        _queue_action_rank(row),
        str(row.get("updated_at", "")),
        str(row.get("queue_item_id", "")),
    )


def _draft_action_rank(row: dict[str, object]) -> int:
    operator_signal = str(row.get("operator_signal", ""))
    approval_state = str(row.get("approval_state", ""))
    if operator_signal in {"ready_for_review", "review_flag_pending"} or approval_state == "pending_review":
        return 0
    if operator_signal == "needs_revision" or approval_state == "needs_edits":
        return 1
    if operator_signal == "blocked_quality":
        return 2
    if approval_state == "approved":
        return 3
    if approval_state == "rejected":
        return 4
    return 5


def _social_action_rank(row: dict[str, object]) -> int:
    approval_state = str(row.get("approval_state", ""))
    linkage_state = str(row.get("linkage_state", ""))
    if approval_state == "pending_review":
        return 0
    if approval_state == "needs_edits":
        return 1
    if approval_state == "approved" and linkage_state in {"ready_for_social_review", "approved_for_queue"}:
        return 2
    if approval_state == "approved":
        return 3
    if approval_state == "rejected":
        return 4
    return 5


def _media_asset_action_rank(row: dict[str, object]) -> int:
    approval_state = str(row.get("approval_state", ""))
    if approval_state == "pending_review":
        return 0
    if approval_state == "needs_edits":
        return 1
    if approval_state == "approved":
        return 2
    if approval_state == "rejected":
        return 3
    return 4


def _queue_action_rank(row: dict[str, object]) -> int:
    queue_review_state = str(row.get("queue_review_state", ""))
    if queue_review_state == "pending_review":
        return 0
    if queue_review_state == "needs_edits":
        return 1
    if row.get("schedule_allowed"):
        return 2
    if row.get("approve_block_reason") or row.get("schedule_block_reason"):
        return 3
    if queue_review_state == "approved":
        return 4
    if queue_review_state == "removed":
        return 5
    return 6


def _build_filtered_draft_summary(
    rows: list[dict[str, object]],
    base_summary: dict[str, object],
) -> dict[str, object]:
    summary = dict(base_summary)
    summary["total_drafts"] = len(rows)
    summary["approval_state_counts"] = dict(Counter(str(row.get("approval_state", "")) for row in rows))
    summary["operator_signal_counts"] = dict(Counter(str(row.get("operator_signal", "")) for row in rows))
    summary["category_counts"] = dict(Counter(str(row.get("category", "")) for row in rows))
    summary["quality_gate_counts"] = dict(Counter(str(row.get("quality_gate_status", "")) for row in rows))
    return summary


def _build_filtered_social_summary(
    rows: list[dict[str, object]],
    approval_counts: dict[str, int],
) -> dict[str, object]:
    filtered_approval_counts = dict(Counter(str(row.get("approval_state", "")) for row in rows))
    return {
        "total_packages": len(rows),
        "approval_counts": filtered_approval_counts or dict(approval_counts),
        "pending_review_count": filtered_approval_counts.get("pending_review", 0),
        "linkage_state_counts": dict(Counter(str(row.get("linkage_state", "")) for row in rows)),
    }


def _build_filtered_media_asset_summary(
    rows: list[dict[str, object]],
    approval_counts: dict[str, int],
) -> dict[str, object]:
    filtered_approval_counts = dict(Counter(str(row.get("approval_state", "")) for row in rows))
    return {
        "total_assets": len(rows),
        "approval_counts": filtered_approval_counts or dict(approval_counts),
        "pending_review_count": filtered_approval_counts.get("pending_review", 0),
        "source_kind_counts": dict(Counter(str(row.get("asset_source_kind", "")) for row in rows)),
    }


def _build_filtered_queue_summary(
    rows: list[dict[str, object]],
    *,
    queue_state_counts: dict[str, int],
    queue_review_state_counts: dict[str, int],
    schedule_summary: dict[str, object],
) -> dict[str, object]:
    filtered_queue_state_counts = dict(Counter(str(row.get("queue_state", "")) for row in rows))
    filtered_review_counts = dict(Counter(str(row.get("queue_review_state", "")) for row in rows))
    return {
        "total_queue_items": len(rows),
        "queue_state_counts": filtered_queue_state_counts or dict(queue_state_counts),
        "queue_review_state_counts": filtered_review_counts or dict(queue_review_state_counts),
        "schedule_summary": schedule_summary,
    }


def _build_priority_draft_rows(rows: list[object], limit: int = 5) -> list[dict[str, object]]:
    converted = [row.to_dict() for row in rows]
    converted.sort(key=_draft_inbox_sort_key)
    return [
        {
            "detail_target_id": row["draft_id"],
            "title": row["draft_id"],
            "subtitle": row["source_domain"],
            "approval_state": row["approval_state"],
            "operator_signal": row["operator_signal"],
        }
        for row in converted[:limit]
    ]


def _build_priority_social_rows(rows: list[dict[str, object]], limit: int = 5) -> list[dict[str, object]]:
    converted = list(rows)
    converted.sort(key=_social_inbox_sort_key)
    return [
        {
            "detail_target_id": row["social_package_id"],
            "title": row.get("linked_blog_title") or row["social_package_id"],
            "subtitle": row.get("selected_variant_label") or row["approval_state"],
            "approval_state": row["approval_state"],
            "linkage_state": row["linkage_state"],
        }
        for row in converted[:limit]
    ]


def _build_priority_media_asset_rows(rows: list[dict[str, object]], limit: int = 5) -> list[dict[str, object]]:
    converted = list(rows)
    converted.sort(key=_media_asset_inbox_sort_key)
    return [
        {
            "detail_target_id": row["asset_record_id"],
            "title": row.get("linked_blog_title") or row["asset_record_id"],
            "subtitle": row["asset_source_kind"],
            "approval_state": row["approval_state"],
            "asset_complete": row["asset_complete"],
        }
        for row in converted[:limit]
    ]


def _build_priority_queue_rows(rows: list[dict[str, object]], limit: int = 5) -> list[dict[str, object]]:
    converted = list(rows)
    converted.sort(key=_queue_inbox_sort_key)
    return [
        {
            "detail_target_id": row["queue_item_id"],
            "title": row.get("title") or row["queue_item_id"],
            "subtitle": row["queue_type"],
            "queue_state": row["queue_state"],
            "queue_review_state": row["queue_review_state"],
        }
        for row in converted[:limit]
    ]


def _latest_blog_publish_by_id(records: list) -> dict[str, object]:
    latest: dict[str, object] = {}
    for record in records:
        latest[record.blog_publish_id] = record
    return latest


def _latest_social_packages(records: list) -> dict[str, object]:
    latest: dict[str, object] = {}
    for record in records:
        latest[record.social_package_id] = record
    return latest


def _latest_media_briefs(records: list) -> dict[str, object]:
    latest: dict[str, object] = {}
    for record in records:
        latest[record.media_brief_id] = record
    return latest


def _latest_assets(records: list) -> dict[str, object]:
    latest: dict[str, object] = {}
    for record in records:
        latest[record.asset_record_id] = record
    return latest


def _latest_social_packages_by_blog_publish(records: list) -> dict[str, object]:
    latest: dict[str, object] = {}
    for record in records:
        if record.blog_publish_id:
            latest[record.blog_publish_id] = record
    return latest


def _latest_social_review_maps(reviews: list) -> tuple[dict[str, object], dict[str, int]]:
    latest_by_package: dict[str, object] = {}
    counts: dict[str, int] = {}
    for review in reviews:
        latest_by_package[review.social_package_id] = review
        counts[review.social_package_id] = counts.get(review.social_package_id, 0) + 1
    return latest_by_package, counts


def _latest_asset_review_maps(reviews: list) -> tuple[dict[str, object], dict[str, int]]:
    latest_by_asset: dict[str, object] = {}
    counts: dict[str, int] = {}
    for review in reviews:
        latest_by_asset[review.asset_record_id] = review
        counts[review.asset_record_id] = counts.get(review.asset_record_id, 0) + 1
    return latest_by_asset, counts


def _latest_queue_items_by_lineage(records: list) -> dict[tuple[str, str], object]:
    latest: dict[tuple[str, str], object] = {}
    for record in records:
        latest[(record.blog_publish_id or "", record.queue_type)] = record
    return latest


def _latest_queue_review_maps(reviews: list) -> tuple[dict[tuple[str, str], object], dict[tuple[str, str], int]]:
    latest_by_lineage: dict[tuple[str, str], object] = {}
    counts: dict[tuple[str, str], int] = {}
    for review in reviews:
        lineage_key = (review.blog_publish_id or "", review.queue_type)
        latest_by_lineage[lineage_key] = review
        counts[lineage_key] = counts.get(lineage_key, 0) + 1
    return latest_by_lineage, counts


def _latest_mapping_for_blog_publish(blog_publish_id: str | None, active_paths: OperatorApiPaths):
    if not blog_publish_id:
        return None
    latest_mapping = None
    for mapping in read_blog_facebook_mapping_records(active_paths.mapping_records_path):
        if mapping.blog_publish_id == blog_publish_id:
            latest_mapping = mapping
    return latest_mapping


def _latest_facebook_publish_for_social_package(
    social_package_id: str,
    active_paths: OperatorApiPaths,
):
    latest_record = None
    for record in read_facebook_publish_records(active_paths.facebook_publish_records_path):
        if record.social_package_id == social_package_id:
            latest_record = record
    return latest_record


def _latest_media_brief_for_draft(draft_id: str, active_paths: OperatorApiPaths):
    try:
        return load_latest_media_brief_for_draft(draft_id, path=active_paths.media_brief_records_path)
    except ValueError:
        return None


def _latest_asset_for_draft_or_blog_publish(
    *,
    draft_id: str,
    blog_publish_id: str | None,
    active_paths: OperatorApiPaths,
):
    if blog_publish_id:
        try:
            return load_latest_asset_for_blog_publish(blog_publish_id, path=active_paths.asset_records_path)
        except ValueError:
            pass
    try:
        return load_latest_asset_for_draft(draft_id, path=active_paths.asset_records_path)
    except ValueError:
        return None


def _latest_asset_for_social_context(
    *,
    social_package_id: str,
    blog_publish_id: str | None,
    draft_id: str,
    active_paths: OperatorApiPaths,
):
    try:
        return load_latest_asset_for_social_package(
            social_package_id,
            path=active_paths.asset_records_path,
        )
    except ValueError:
        return _latest_asset_for_draft_or_blog_publish(
            draft_id=draft_id,
            blog_publish_id=blog_publish_id,
            active_paths=active_paths,
        )


def _build_queue_schedule_context(
    *,
    queue_item,
    blog_publish,
    latest_review,
) -> tuple[bool, str | None]:
    if queue_item.queue_type != "blog_publish":
        return (
            False,
            "Approval UI V1 supports direct scheduling only for blog queue items.",
        )
    if blog_publish is None:
        return False, "Queue item is missing its linked blog publish record."
    if latest_review is None or latest_review.review_outcome != "approved":
        return False, "Queue scheduling requires an approved queue review first."
    try:
        validate_blog_schedule_allowed(blog_publish, "manual")
    except ValueError as exc:
        return False, str(exc)
    return True, None


def _build_queue_approve_context(*, queue_item) -> tuple[bool, str | None]:
    if queue_item.queue_state in {"blog_publish_failed", "facebook_publish_failed"}:
        return False, "Failed queue items cannot be approved for queue until the failure is resolved."
    return True, None


def _build_queue_action_context(
    *,
    queue_item,
    blog_publish,
    latest_review,
) -> dict[str, tuple[bool, str | None]]:
    return {
        "approve": _build_queue_approve_context(queue_item=queue_item),
        "hold": (True, None),
        "remove": (True, None),
        "schedule": _build_queue_schedule_context(
            queue_item=queue_item,
            blog_publish=blog_publish,
            latest_review=latest_review,
        ),
    }


def _build_recent_review_activity(
    *,
    draft_reviews: list,
    social_reviews: list,
    asset_reviews: list,
    queue_reviews: list,
    limit: int = 8,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for review in draft_reviews:
        rows.append(
            {
                "activity_type": "draft_review",
                "entity_id": review.draft_id,
                "linked_id": review.source_item_id,
                "detail_target_type": "draft",
                "detail_target_id": review.draft_id,
                "review_outcome": review.review_outcome,
                "updated_state": review.updated_approval_state,
                "reviewer_label": review.reviewer_label,
                "occurred_at": review.reviewed_at,
                "review_notes": list(review.review_notes),
            }
        )
    for review in social_reviews:
        rows.append(
            {
                "activity_type": "social_review",
                "entity_id": review.social_package_id,
                "linked_id": review.blog_publish_id or review.draft_id,
                "detail_target_type": "social_package",
                "detail_target_id": review.social_package_id,
                "review_outcome": review.review_outcome,
                "updated_state": review.updated_approval_state,
                "reviewer_label": review.reviewer_label,
                "occurred_at": review.reviewed_at,
                "review_notes": list(review.review_notes),
            }
        )
    for review in asset_reviews:
        rows.append(
            {
                "activity_type": "asset_review",
                "entity_id": review.asset_record_id,
                "linked_id": review.blog_publish_id or review.draft_id,
                "detail_target_type": "media_asset",
                "detail_target_id": review.asset_record_id,
                "review_outcome": review.review_outcome,
                "updated_state": review.updated_approval_state,
                "reviewer_label": review.reviewer_label,
                "occurred_at": review.reviewed_at,
                "review_notes": list(review.review_notes),
            }
        )
    for review in queue_reviews:
        rows.append(
            {
                "activity_type": "queue_review",
                "entity_id": review.queue_item_id,
                "linked_id": review.blog_publish_id or review.draft_id,
                "detail_target_type": "queue_item",
                "detail_target_id": review.queue_item_id,
                "review_outcome": review.review_outcome,
                "updated_state": review.updated_queue_review_state,
                "reviewer_label": review.reviewer_label,
                "occurred_at": review.reviewed_at,
                "review_notes": list(review.review_notes),
            }
        )
    rows.sort(key=lambda row: (row["occurred_at"], row["activity_type"], row["entity_id"]), reverse=True)
    return rows[:limit]


def _build_current_operator_alerts(
    *,
    distribution_rows: list,
    activation_summary,
    latest_queue_items: dict[tuple[str, str], object],
    limit: int = 8,
) -> list[dict[str, object]]:
    alerts: list[dict[str, object]] = []
    for row in distribution_rows:
        message_parts: list[str] = []
        alert_type: str | None = None
        severity = "warning"
        if row.operator_signal in {"blog_publish_failed", "facebook_publish_failed"}:
            alert_type = "transport_failure"
            severity = "error"
            error_message = row.last_blog_error or row.last_facebook_error or _humanize_signal(
                row.operator_signal
            )
            message_parts.append(error_message)
        if row.consistency_issues:
            if alert_type is None:
                alert_type = "workflow_consistency"
            severity = "error"
            message_parts.append(
                "Consistency: " + ", ".join(_humanize_signal(issue) for issue in row.consistency_issues)
            )
        if row.schedule_alerts:
            if alert_type is None:
                alert_type = "schedule_alert"
            message_parts.append(
                "Schedule: " + ", ".join(_humanize_signal(alert) for alert in row.schedule_alerts)
            )
        if alert_type is None:
            continue
        related_queue_item_id = _resolve_alert_queue_item_id(
            row=row,
            latest_queue_items=latest_queue_items,
        )
        alerts.append(
            {
                "alert_type": alert_type,
                "severity": severity,
                "entity_id": row.blog_publish_id,
                "queue_item_id": related_queue_item_id,
                "title": row.wordpress_title or row.blog_publish_id,
                "message": " | ".join(message_parts),
                "occurred_at": row.latest_updated_at,
            }
        )

    activation_timestamp = (
        activation_summary.latest_transport_validation_at
        or activation_summary.latest_distribution_snapshot_at
        or ""
    )
    for reason in activation_summary.blocking_reasons:
        alerts.append(
            {
                "alert_type": "activation_blocker",
                "severity": "warning",
                "entity_id": reason,
                "title": "Activation blocker",
                "message": _humanize_signal(reason),
                "occurred_at": activation_timestamp,
            }
        )

    alerts.sort(key=lambda row: (row["occurred_at"], row["severity"], row["entity_id"]), reverse=True)
    return alerts[:limit]


def _humanize_signal(value: str) -> str:
    return value.replace("_", " ").strip()


def _resolve_alert_queue_item_id(*, row, latest_queue_items: dict[tuple[str, str], object]) -> str | None:
    blog_queue = latest_queue_items.get((row.blog_publish_id, "blog_publish"))
    facebook_queue = latest_queue_items.get((row.blog_publish_id, "facebook_publish"))

    if row.operator_signal == "blog_publish_failed":
        return blog_queue.queue_item_id if blog_queue else None
    if row.operator_signal == "facebook_publish_failed":
        return facebook_queue.queue_item_id if facebook_queue else None

    if any(alert == "facebook_schedule_collision" for alert in row.schedule_alerts):
        return facebook_queue.queue_item_id if facebook_queue else None
    if any(alert == "blog_schedule_collision" for alert in row.schedule_alerts):
        return blog_queue.queue_item_id if blog_queue else None

    if any("facebook" in issue for issue in row.consistency_issues):
        return facebook_queue.queue_item_id if facebook_queue else None
    if row.consistency_issues:
        return blog_queue.queue_item_id if blog_queue else None

    return None
