from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from content_engine.health import build_draft_health_report
from content_engine.review import record_draft_review
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
    blog_publish_records_path: Path = BLOG_PUBLISH_RECORDS_PATH
    social_package_records_path: Path = SOCIAL_PACKAGE_RECORDS_PATH
    social_package_reviews_path: Path = SOCIAL_PACKAGE_REVIEWS_PATH
    facebook_publish_records_path: Path = FACEBOOK_PUBLISH_RECORDS_PATH
    queue_item_records_path: Path = QUEUE_ITEM_RECORDS_PATH
    queue_review_records_path: Path = QUEUE_REVIEW_RECORDS_PATH
    mapping_records_path: Path = BLOG_FACEBOOK_MAPPING_RECORDS_PATH


def build_dashboard_payload(paths: OperatorApiPaths | None = None) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    draft_reviews = read_draft_review_records(active_paths.draft_reviews_path)
    social_reviews = read_social_package_review_records(active_paths.social_package_reviews_path)
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
        facebook_publish_records_path=active_paths.facebook_publish_records_path,
        queue_item_records_path=active_paths.queue_item_records_path,
        mapping_records_path=active_paths.mapping_records_path,
    )
    recent_activity = _build_recent_review_activity(
        draft_reviews=draft_reviews,
        social_reviews=social_reviews,
        queue_reviews=queue_reviews,
    )
    current_alerts = _build_current_operator_alerts(
        distribution_rows=distribution_rows,
        activation_summary=activation_summary,
        latest_queue_items=latest_queue_items,
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
            ),
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
        "fast_lane": dict(FAST_LANE_PLACEHOLDER),
        "meta": {
            "latest_draft_snapshot_at": draft_summary.latest_snapshot_at,
            "latest_distribution_snapshot_at": distribution_summary.latest_snapshot_at,
            "draft_row_count": len(draft_rows),
            "distribution_row_count": len(distribution_rows),
        },
    }


def build_draft_inbox_payload(paths: OperatorApiPaths | None = None) -> dict[str, object]:
    active_paths = paths or OperatorApiPaths()
    summary, rows = build_draft_health_report(
        draft_records_path=active_paths.draft_records_path,
        draft_reviews_path=active_paths.draft_reviews_path,
    )
    return {
        "summary": summary.to_dict(),
        "rows": [row.to_dict() for row in rows],
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
        },
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


def build_social_package_inbox_payload(paths: OperatorApiPaths | None = None) -> dict[str, object]:
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
    rows.sort(key=lambda row: (row["approval_state"], row["updated_at"], row["social_package_id"]))
    return {
        "summary": {
            "total_packages": len(rows),
            "approval_counts": approval_counts,
            "pending_review_count": approval_counts.get("pending_review", 0),
        },
        "rows": rows,
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
    review_history = [
        review.to_dict()
        for review in read_social_package_review_records(active_paths.social_package_reviews_path)
        if review.social_package_id == social_package_id
    ]
    return {
        "social_package": social_package.to_dict(),
        "linked_blog_publish": blog_publish.to_dict() if blog_publish else None,
        "linked_draft": {
            "draft_id": draft.draft_id,
            "headline_selected": draft.headline_selected,
            "excerpt": draft.excerpt,
            "template_id": draft.template_id,
            "category": draft.category,
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

    if updated_package.blog_publish_id:
        blog_publish_record = load_latest_blog_publish_record(
            updated_package.blog_publish_id,
            path=active_paths.blog_publish_records_path,
        )
        facebook_publish_record = _latest_facebook_publish_for_social_package(
            updated_package.social_package_id,
            active_paths=active_paths,
        )
        blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
            blog_publish_record,
            social_package_record=updated_package,
            facebook_publish_record=facebook_publish_record,
        )
        append_queue_item_records(
            [blog_queue, facebook_queue],
            path=active_paths.queue_item_records_path,
        )
        append_blog_facebook_mapping_records([mapping], path=active_paths.mapping_records_path)

    return build_social_package_detail_payload(updated_package.social_package_id, paths=active_paths)


def build_queue_inbox_payload(paths: OperatorApiPaths | None = None) -> dict[str, object]:
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
        latest_review = latest_queue_review_by_lineage.get(lineage_key)
        schedule_row = schedule_row_by_blog_publish.get(queue_item.blog_publish_id or "")
        queue_review_state = (
            latest_review.updated_queue_review_state if latest_review else "pending_review"
        )
        action_context = _build_queue_action_context(
            queue_item=queue_item,
            blog_publish=blog_publish,
            latest_review=latest_review,
        )
        queue_state_counts[queue_item.queue_state] = queue_state_counts.get(queue_item.queue_state, 0) + 1
        queue_review_state_counts[queue_review_state] = (
            queue_review_state_counts.get(queue_review_state, 0) + 1
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
                "queue_state": queue_item.queue_state,
                "approval_state": queue_item.approval_state,
                "queue_review_state": queue_review_state,
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
    rows.sort(key=lambda row: (row["queue_type"], row["queue_state"], row["updated_at"], row["queue_item_id"]))
    return {
        "summary": {
            "total_queue_items": len(rows),
            "queue_state_counts": queue_state_counts,
            "queue_review_state_counts": queue_review_state_counts,
            "schedule_summary": schedule_summary.to_dict(),
        },
        "rows": rows,
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
        "linked_mapping": latest_mapping.to_dict() if latest_mapping else None,
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
            "queue_ready_items_count": dashboard["queue"]["ready_items_count"],
            "queue_collision_count": dashboard["queue"]["schedule_collision_count"],
            "transport_failure_count": dashboard["transport"]["failure_count"],
            "activation_signal": dashboard["transport"]["activation_signal"],
            "fast_lane_status": dashboard["fast_lane"]["status"],
        },
        "record_counts": {
            "draft_rows": len(drafts["rows"]),
            "social_package_rows": len(social_packages["rows"]),
            "queue_rows": len(queue["rows"]),
        },
        "review_surfaces": {
            "draft_review_available": True,
            "social_review_available": True,
            "queue_review_available": True,
            "queue_schedule_available": any(row["schedule_allowed"] for row in queue["rows"]),
        },
        "notes": [
            "This validation payload proves backend readiness and current workflow visibility.",
            "Live WordPress-admin validation is still required to verify plugin rendering, settings save flow, and safe admin notices.",
        ],
        "combined_health": combined_health,
    }


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
