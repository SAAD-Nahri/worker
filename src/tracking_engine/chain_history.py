from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from content_engine.storage import DRAFT_RECORDS_PATH, DRAFT_REVIEWS_PATH, read_draft_records, read_draft_review_records
from distribution_engine.health import DistributionHealthRow, build_distribution_health_report
from distribution_engine.storage import (
    BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
    BLOG_PUBLISH_RECORDS_PATH,
    FACEBOOK_PUBLISH_RECORDS_PATH,
    QUEUE_ITEM_RECORDS_PATH,
    SOCIAL_PACKAGE_RECORDS_PATH,
    SOCIAL_PACKAGE_REVIEWS_PATH,
    read_blog_facebook_mapping_records,
    read_blog_publish_records,
    read_facebook_publish_records,
    read_social_package_records,
)
from source_engine.storage import SOURCE_ITEMS_PATH, read_source_items
from tracking_engine.models import PublishChainHistorySummary, PublishChainSnapshot


def build_publish_chain_history_report(
    source_items_path: Path | None = None,
    draft_records_path: Path | None = None,
    draft_reviews_path: Path | None = None,
    blog_publish_records_path: Path | None = None,
    social_package_records_path: Path | None = None,
    social_package_reviews_path: Path | None = None,
    facebook_publish_records_path: Path | None = None,
    queue_item_records_path: Path | None = None,
    mapping_records_path: Path | None = None,
    snapshot_generated_at: str | None = None,
) -> tuple[PublishChainHistorySummary, list[PublishChainSnapshot]]:
    source_path = source_items_path or SOURCE_ITEMS_PATH
    draft_path = draft_records_path or DRAFT_RECORDS_PATH
    draft_review_path = draft_reviews_path or DRAFT_REVIEWS_PATH
    blog_publish_path = blog_publish_records_path or BLOG_PUBLISH_RECORDS_PATH
    social_package_path = social_package_records_path or SOCIAL_PACKAGE_RECORDS_PATH
    social_review_path = social_package_reviews_path or SOCIAL_PACKAGE_REVIEWS_PATH
    facebook_publish_path = facebook_publish_records_path or FACEBOOK_PUBLISH_RECORDS_PATH
    queue_item_path = queue_item_records_path or QUEUE_ITEM_RECORDS_PATH
    mapping_path = mapping_records_path or BLOG_FACEBOOK_MAPPING_RECORDS_PATH
    generated_at = snapshot_generated_at or _utc_now_timestamp()

    distribution_summary, health_rows = build_distribution_health_report(
        blog_publish_records_path=blog_publish_path,
        social_package_records_path=social_package_path,
        social_package_reviews_path=social_review_path,
        facebook_publish_records_path=facebook_publish_path,
        queue_item_records_path=queue_item_path,
        mapping_records_path=mapping_path,
    )

    latest_source_by_id = _latest_by_key(read_source_items(source_path), "item_id")
    latest_draft_by_id = _latest_by_key(read_draft_records(draft_path), "draft_id")
    latest_blog_publish_by_id = _latest_by_key(read_blog_publish_records(blog_publish_path), "blog_publish_id")
    latest_social_by_id = _latest_by_key(read_social_package_records(social_package_path), "social_package_id")
    latest_facebook_by_id = _latest_by_key(read_facebook_publish_records(facebook_publish_path), "facebook_publish_id")
    latest_mapping_by_blog_publish = _latest_by_key(
        read_blog_facebook_mapping_records(mapping_path), "blog_publish_id"
    )
    draft_review_counts, latest_draft_review_outcomes = _review_maps(
        read_draft_review_records(draft_review_path),
        key_name="draft_id",
        outcome_name="review_outcome",
    )

    snapshots: list[PublishChainSnapshot] = []
    for health_row in health_rows:
        blog_publish = latest_blog_publish_by_id[health_row.blog_publish_id]
        draft = latest_draft_by_id.get(blog_publish.draft_id)
        source_item = latest_source_by_id.get(blog_publish.source_item_id)
        mapping = latest_mapping_by_blog_publish.get(blog_publish.blog_publish_id)
        social_package = _resolve_social_package(health_row, latest_social_by_id)
        facebook_publish = _resolve_facebook_publish(health_row, latest_facebook_by_id)
        snapshots.append(
            _build_snapshot(
                snapshot_generated_at=generated_at,
                health_row=health_row,
                source_item=source_item,
                draft=draft,
                blog_publish=blog_publish,
                social_package=social_package,
                facebook_publish=facebook_publish,
                mapping=mapping,
                draft_review_count=draft_review_counts.get(blog_publish.draft_id, 0),
                latest_draft_review_outcome=latest_draft_review_outcomes.get(blog_publish.draft_id),
            )
        )

    snapshots.sort(key=_snapshot_sort_key)
    summary = _build_summary(snapshots, distribution_summary.latest_snapshot_at)
    return summary, snapshots


def _latest_by_key(records: list[object], key_name: str) -> dict[str, object]:
    latest: dict[str, object] = {}
    for record in records:
        key = getattr(record, key_name)
        latest[key] = record
    return latest


def _review_maps(records: list[object], *, key_name: str, outcome_name: str) -> tuple[dict[str, int], dict[str, str]]:
    counts: dict[str, int] = {}
    latest_outcomes: dict[str, str] = {}
    for record in records:
        key = getattr(record, key_name)
        counts[key] = counts.get(key, 0) + 1
        latest_outcomes[key] = getattr(record, outcome_name)
    return counts, latest_outcomes


def _resolve_social_package(health_row: DistributionHealthRow, latest_social_by_id: dict[str, object]) -> object | None:
    if not health_row.social_package_id:
        return None
    return latest_social_by_id.get(health_row.social_package_id)


def _resolve_facebook_publish(
    health_row: DistributionHealthRow,
    latest_facebook_by_id: dict[str, object],
) -> object | None:
    if not health_row.facebook_publish_id:
        return None
    return latest_facebook_by_id.get(health_row.facebook_publish_id)


def _build_snapshot(
    *,
    snapshot_generated_at: str,
    health_row: DistributionHealthRow,
    source_item,
    draft,
    blog_publish,
    social_package,
    facebook_publish,
    mapping,
    draft_review_count: int,
    latest_draft_review_outcome: str | None,
) -> PublishChainSnapshot:
    selected_blog_title = _first_non_empty(
        getattr(mapping, "selected_blog_title", None),
        getattr(blog_publish, "wordpress_title", None),
        getattr(draft, "headline_selected", None),
        getattr(source_item, "raw_title", None),
    )
    return PublishChainSnapshot(
        chain_id=blog_publish.blog_publish_id,
        snapshot_generated_at=snapshot_generated_at,
        snapshot_version="v1",
        source_item_id=blog_publish.source_item_id,
        source_id=getattr(source_item, "source_id", getattr(draft, "source_id", "")),
        source_name=getattr(source_item, "source_name", ""),
        source_family=getattr(source_item, "source_family", ""),
        source_title=getattr(source_item, "raw_title", getattr(draft, "source_title", "")),
        source_url=getattr(source_item, "source_url", getattr(draft, "source_url", "")),
        canonical_url=getattr(source_item, "canonical_url", getattr(blog_publish, "canonical_source_url", "")),
        source_published_at=getattr(source_item, "published_at", getattr(draft, "source_published_at", None)),
        source_dedupe_status=getattr(source_item, "dedupe_status", ""),
        draft_id=blog_publish.draft_id,
        template_id=getattr(draft, "template_id", blog_publish.template_id),
        template_family=getattr(draft, "template_family", ""),
        draft_language=getattr(draft, "language", ""),
        draft_workflow_state=getattr(draft, "workflow_state", ""),
        draft_approval_state=getattr(draft, "approval_state", ""),
        quality_gate_status=getattr(draft, "quality_gate_status", ""),
        derivative_risk_level=getattr(draft, "derivative_risk_level", ""),
        category=getattr(draft, "category", ""),
        tag_candidates=tuple(getattr(draft, "tag_candidates", []) or []),
        selected_blog_title=selected_blog_title,
        headline_selected=getattr(draft, "headline_selected", ""),
        headline_variants_count=len(getattr(draft, "headline_variants", []) or []),
        blog_publish_id=blog_publish.blog_publish_id,
        publish_intent=getattr(blog_publish, "publish_intent", ""),
        wordpress_status=blog_publish.wordpress_status,
        wordpress_slug=getattr(blog_publish, "wordpress_slug", ""),
        wordpress_category=getattr(blog_publish, "wordpress_category", ""),
        wordpress_tags=tuple(getattr(blog_publish, "wordpress_tags", []) or []),
        wordpress_post_id=blog_publish.wordpress_post_id,
        wordpress_post_url=blog_publish.wordpress_post_url,
        published_at_blog=getattr(blog_publish, "published_at_blog", None),
        last_blog_publish_result=getattr(blog_publish, "last_publish_result", ""),
        last_blog_publish_error=getattr(blog_publish, "last_error", None),
        social_package_id=getattr(social_package, "social_package_id", None),
        package_template_id=getattr(social_package, "package_template_id", None),
        comment_template_id=getattr(social_package, "comment_template_id", None),
        target_destination=getattr(social_package, "target_destination", None),
        social_approval_state=getattr(social_package, "approval_state", None),
        selected_variant_label=getattr(social_package, "selected_variant_label", None),
        blog_url_used_in_package=getattr(social_package, "blog_url", None),
        social_packaging_notes=getattr(social_package, "packaging_notes", None),
        selected_hook_text=_first_non_empty(
            getattr(mapping, "selected_hook_text", None),
            getattr(social_package, "hook_text", None),
        ),
        selected_caption_text=_first_non_empty(
            getattr(mapping, "selected_caption_text", None),
            getattr(social_package, "caption_text", None),
        ),
        selected_comment_cta_text=_first_non_empty(
            getattr(mapping, "selected_comment_cta_text", None),
            getattr(social_package, "comment_cta_text", None),
        ),
        facebook_publish_id=getattr(facebook_publish, "facebook_publish_id", None),
        facebook_destination_type=getattr(
            facebook_publish,
            "destination_type",
            getattr(mapping, "facebook_destination_type", None),
        ),
        facebook_publish_status=getattr(facebook_publish, "publish_status", None),
        published_at_facebook=getattr(facebook_publish, "published_at_facebook", None),
        last_facebook_publish_result=getattr(facebook_publish, "last_publish_result", None),
        last_facebook_publish_error=getattr(facebook_publish, "last_error", None),
        blog_queue_state=health_row.blog_queue_state,
        facebook_queue_state=health_row.facebook_queue_state,
        mapping_status=health_row.mapping_status,
        draft_review_count=draft_review_count,
        latest_draft_review_outcome=latest_draft_review_outcome,
        social_review_count=health_row.social_review_count,
        latest_social_review_outcome=health_row.latest_social_review_outcome,
        has_confirmed_blog_url=health_row.has_confirmed_blog_url,
        has_facebook_publish_record=health_row.facebook_publish_id is not None,
        chain_status=health_row.operator_signal,
        consistency_issues=health_row.consistency_issues,
        schedule_alerts=health_row.schedule_alerts,
        latest_activity_at=health_row.latest_updated_at,
    )


def _build_summary(
    snapshots: list[PublishChainSnapshot],
    latest_snapshot_at: str | None,
) -> PublishChainHistorySummary:
    source_family_counts = Counter(snapshot.source_family or "unknown" for snapshot in snapshots)
    template_family_counts = Counter(snapshot.template_family or "unknown" for snapshot in snapshots)
    wordpress_status_counts = Counter(snapshot.wordpress_status or "none" for snapshot in snapshots)
    facebook_publish_status_counts = Counter(snapshot.facebook_publish_status or "none" for snapshot in snapshots)
    chain_status_counts = Counter(snapshot.chain_status for snapshot in snapshots)
    return PublishChainHistorySummary(
        latest_snapshot_at=latest_snapshot_at,
        total_chains=len(snapshots),
        source_family_counts=dict(source_family_counts),
        template_family_counts=dict(template_family_counts),
        wordpress_status_counts=dict(wordpress_status_counts),
        facebook_publish_status_counts=dict(facebook_publish_status_counts),
        chain_status_counts=dict(chain_status_counts),
        chains_with_social_package=sum(1 for snapshot in snapshots if snapshot.social_package_id is not None),
        chains_with_facebook_publish=sum(1 for snapshot in snapshots if snapshot.facebook_publish_id is not None),
        chains_with_confirmed_blog_url=sum(1 for snapshot in snapshots if snapshot.has_confirmed_blog_url),
        chains_with_consistency_issues=sum(1 for snapshot in snapshots if snapshot.consistency_issues),
        chains_with_schedule_alerts=sum(1 for snapshot in snapshots if snapshot.schedule_alerts),
    )


def _snapshot_sort_key(snapshot: PublishChainSnapshot) -> tuple[int, str, str]:
    signal_order = {
        "state_incomplete": 0,
        "blog_publish_failed": 1,
        "facebook_publish_failed": 2,
        "social_needs_edits": 3,
        "social_rejected": 4,
        "ready_for_social_review": 5,
        "ready_for_wordpress": 6,
        "wordpress_draft_created": 7,
        "ready_for_blog_schedule": 8,
        "social_packaging_pending": 9,
        "ready_for_facebook_publish": 10,
        "ready_for_facebook_schedule": 11,
        "approved_for_queue": 12,
        "scheduled_blog": 13,
        "published_blog": 14,
        "scheduled_facebook": 15,
        "published_facebook": 16,
        "monitor": 17,
    }
    return (
        0 if snapshot.consistency_issues else 1 if snapshot.schedule_alerts else 2,
        signal_order.get(snapshot.chain_status, 99),
        snapshot.latest_activity_at,
        snapshot.blog_publish_id,
    )


def _first_non_empty(*values: str | None) -> str:
    for value in values:
        if value:
            return value
    return ""


def _utc_now_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
