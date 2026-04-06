from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path

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
    read_queue_item_records,
    read_social_package_records,
    read_social_package_review_records,
)


@dataclass(frozen=True)
class DistributionHealthRow:
    blog_publish_id: str
    draft_id: str
    source_item_id: str
    wordpress_title: str
    wordpress_status: str
    scheduled_for_blog: str | None
    blog_queue_state: str | None
    social_package_id: str | None
    social_approval_state: str | None
    social_review_count: int
    latest_social_review_outcome: str | None
    facebook_publish_id: str | None
    facebook_publish_status: str | None
    scheduled_for_facebook: str | None
    facebook_queue_state: str | None
    mapping_status: str | None
    has_remote_wordpress_post: bool
    has_confirmed_blog_url: bool
    has_facebook_post_id: bool
    last_blog_error: str | None
    last_facebook_error: str | None
    latest_updated_at: str
    operator_signal: str
    consistency_issues: tuple[str, ...] = ()
    schedule_alerts: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "blog_publish_id": self.blog_publish_id,
            "draft_id": self.draft_id,
            "source_item_id": self.source_item_id,
            "wordpress_title": self.wordpress_title,
            "wordpress_status": self.wordpress_status,
            "scheduled_for_blog": self.scheduled_for_blog,
            "blog_queue_state": self.blog_queue_state,
            "social_package_id": self.social_package_id,
            "social_approval_state": self.social_approval_state,
            "social_review_count": self.social_review_count,
            "latest_social_review_outcome": self.latest_social_review_outcome,
            "facebook_publish_id": self.facebook_publish_id,
            "facebook_publish_status": self.facebook_publish_status,
            "scheduled_for_facebook": self.scheduled_for_facebook,
            "facebook_queue_state": self.facebook_queue_state,
            "mapping_status": self.mapping_status,
            "has_remote_wordpress_post": self.has_remote_wordpress_post,
            "has_confirmed_blog_url": self.has_confirmed_blog_url,
            "has_facebook_post_id": self.has_facebook_post_id,
            "last_blog_error": self.last_blog_error,
            "last_facebook_error": self.last_facebook_error,
            "latest_updated_at": self.latest_updated_at,
            "operator_signal": self.operator_signal,
            "consistency_issues": list(self.consistency_issues),
            "schedule_alerts": list(self.schedule_alerts),
        }


@dataclass(frozen=True)
class DistributionHealthSummary:
    latest_snapshot_at: str | None
    total_blog_publish_chains: int
    wordpress_status_counts: dict[str, int]
    social_approval_counts: dict[str, int]
    facebook_publish_status_counts: dict[str, int]
    blog_queue_state_counts: dict[str, int]
    facebook_queue_state_counts: dict[str, int]
    mapping_status_counts: dict[str, int]
    operator_signal_counts: dict[str, int]
    blog_chains_with_social_package: int
    blog_chains_with_remote_wordpress_post: int
    blog_chains_with_confirmed_blog_url: int
    blog_chains_with_facebook_post_id: int
    rows_with_consistency_issues: int
    rows_with_schedule_alerts: int
    consistency_issue_counts: dict[str, int]
    schedule_alert_counts: dict[str, int]
    top_errors: tuple[tuple[str, int], ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "latest_snapshot_at": self.latest_snapshot_at,
            "total_blog_publish_chains": self.total_blog_publish_chains,
            "wordpress_status_counts": dict(self.wordpress_status_counts),
            "social_approval_counts": dict(self.social_approval_counts),
            "facebook_publish_status_counts": dict(self.facebook_publish_status_counts),
            "blog_queue_state_counts": dict(self.blog_queue_state_counts),
            "facebook_queue_state_counts": dict(self.facebook_queue_state_counts),
            "mapping_status_counts": dict(self.mapping_status_counts),
            "operator_signal_counts": dict(self.operator_signal_counts),
            "blog_chains_with_social_package": self.blog_chains_with_social_package,
            "blog_chains_with_remote_wordpress_post": self.blog_chains_with_remote_wordpress_post,
            "blog_chains_with_confirmed_blog_url": self.blog_chains_with_confirmed_blog_url,
            "blog_chains_with_facebook_post_id": self.blog_chains_with_facebook_post_id,
            "rows_with_consistency_issues": self.rows_with_consistency_issues,
            "rows_with_schedule_alerts": self.rows_with_schedule_alerts,
            "consistency_issue_counts": dict(self.consistency_issue_counts),
            "schedule_alert_counts": dict(self.schedule_alert_counts),
            "top_errors": [{"error": error, "count": count} for error, count in self.top_errors],
        }


def build_distribution_health_report(
    blog_publish_records_path: Path | None = None,
    social_package_records_path: Path | None = None,
    social_package_reviews_path: Path | None = None,
    facebook_publish_records_path: Path | None = None,
    queue_item_records_path: Path | None = None,
    mapping_records_path: Path | None = None,
) -> tuple[DistributionHealthSummary, list[DistributionHealthRow]]:
    blog_publish_path = blog_publish_records_path or BLOG_PUBLISH_RECORDS_PATH
    social_package_path = social_package_records_path or SOCIAL_PACKAGE_RECORDS_PATH
    social_review_path = social_package_reviews_path or SOCIAL_PACKAGE_REVIEWS_PATH
    facebook_publish_path = facebook_publish_records_path or FACEBOOK_PUBLISH_RECORDS_PATH
    queue_item_path = queue_item_records_path or QUEUE_ITEM_RECORDS_PATH
    mapping_path = mapping_records_path or BLOG_FACEBOOK_MAPPING_RECORDS_PATH

    latest_blog_publish_by_id = _latest_blog_publish_by_id(read_blog_publish_records(blog_publish_path))
    latest_social_package_by_blog_publish = _latest_social_package_by_blog_publish(
        read_social_package_records(social_package_path)
    )
    latest_social_review_by_package, social_review_counts = _latest_social_review_maps(
        read_social_package_review_records(social_review_path)
    )
    latest_facebook_publish_by_social_package = _latest_facebook_publish_by_social_package(
        read_facebook_publish_records(facebook_publish_path)
    )
    latest_blog_queue_by_blog_publish, latest_facebook_queue_by_blog_publish = _latest_queue_maps(
        read_queue_item_records(queue_item_path)
    )
    latest_mapping_by_blog_publish = _latest_mapping_by_blog_publish(
        read_blog_facebook_mapping_records(mapping_path)
    )

    rows = [
        _build_row(
            blog_publish=latest_blog_publish_by_id[blog_publish_id],
            social_package=latest_social_package_by_blog_publish.get(blog_publish_id),
            latest_social_review=(
                latest_social_review_by_package.get(
                    latest_social_package_by_blog_publish[blog_publish_id].social_package_id
                )
                if blog_publish_id in latest_social_package_by_blog_publish
                else None
            ),
            social_review_count=(
                social_review_counts.get(
                    latest_social_package_by_blog_publish[blog_publish_id].social_package_id,
                    0,
                )
                if blog_publish_id in latest_social_package_by_blog_publish
                else 0
            ),
            facebook_publish=(
                latest_facebook_publish_by_social_package.get(
                    latest_social_package_by_blog_publish[blog_publish_id].social_package_id
                )
                if blog_publish_id in latest_social_package_by_blog_publish
                else None
            ),
            blog_queue=latest_blog_queue_by_blog_publish.get(blog_publish_id),
            facebook_queue=latest_facebook_queue_by_blog_publish.get(blog_publish_id),
            mapping=latest_mapping_by_blog_publish.get(blog_publish_id),
        )
        for blog_publish_id in latest_blog_publish_by_id
    ]
    rows = _enrich_rows_with_alerts(rows)
    rows.sort(key=_row_sort_key)
    return _build_summary(rows), rows


def _latest_blog_publish_by_id(records: list) -> dict[str, object]:
    latest: dict[str, object] = {}
    for record in records:
        latest[record.blog_publish_id] = record
    return latest


def _latest_social_package_by_blog_publish(records: list) -> dict[str, object]:
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


def _latest_facebook_publish_by_social_package(records: list) -> dict[str, object]:
    latest: dict[str, object] = {}
    for record in records:
        latest[record.social_package_id] = record
    return latest


def _latest_queue_maps(records: list) -> tuple[dict[str, object], dict[str, object]]:
    latest_blog_queue: dict[str, object] = {}
    latest_facebook_queue: dict[str, object] = {}
    for record in records:
        if record.queue_type == "blog_publish":
            latest_blog_queue[record.blog_publish_id] = record
        elif record.queue_type == "facebook_publish":
            latest_facebook_queue[record.blog_publish_id] = record
    return latest_blog_queue, latest_facebook_queue


def _latest_mapping_by_blog_publish(records: list) -> dict[str, object]:
    latest: dict[str, object] = {}
    for record in records:
        latest[record.blog_publish_id] = record
    return latest


def _build_row(
    blog_publish,
    social_package,
    latest_social_review,
    social_review_count: int,
    facebook_publish,
    blog_queue,
    facebook_queue,
    mapping,
) -> DistributionHealthRow:
    last_blog_error = _first_non_empty(
        getattr(blog_queue, "last_error", None),
        getattr(blog_publish, "last_error", None),
    )
    last_facebook_error = _first_non_empty(
        getattr(facebook_queue, "last_error", None),
        getattr(facebook_publish, "last_error", None),
    )
    return DistributionHealthRow(
        blog_publish_id=blog_publish.blog_publish_id,
        draft_id=blog_publish.draft_id,
        source_item_id=blog_publish.source_item_id,
        wordpress_title=blog_publish.wordpress_title,
        wordpress_status=blog_publish.wordpress_status,
        scheduled_for_blog=getattr(blog_publish, "scheduled_for_blog", None),
        blog_queue_state=getattr(blog_queue, "queue_state", None),
        social_package_id=getattr(social_package, "social_package_id", None),
        social_approval_state=getattr(social_package, "approval_state", None),
        social_review_count=social_review_count,
        latest_social_review_outcome=getattr(latest_social_review, "review_outcome", None),
        facebook_publish_id=getattr(facebook_publish, "facebook_publish_id", None),
        facebook_publish_status=getattr(facebook_publish, "publish_status", None),
        scheduled_for_facebook=getattr(facebook_publish, "scheduled_for_facebook", None),
        facebook_queue_state=getattr(facebook_queue, "queue_state", None),
        mapping_status=getattr(mapping, "mapping_status", None),
        has_remote_wordpress_post=bool(getattr(blog_publish, "wordpress_post_id", None)),
        has_confirmed_blog_url=bool(getattr(blog_publish, "wordpress_post_url", None)),
        has_facebook_post_id=bool(getattr(facebook_publish, "facebook_post_id", None)),
        last_blog_error=last_blog_error,
        last_facebook_error=last_facebook_error,
        latest_updated_at=_latest_timestamp(
            getattr(blog_publish, "updated_at", ""),
            getattr(social_package, "updated_at", ""),
            getattr(latest_social_review, "reviewed_at", ""),
            getattr(facebook_publish, "updated_at", ""),
            getattr(blog_queue, "updated_at", ""),
            getattr(facebook_queue, "updated_at", ""),
            getattr(mapping, "updated_at", ""),
        ),
        operator_signal=_resolve_operator_signal(
            blog_publish,
            social_package=social_package,
            facebook_publish=facebook_publish,
            blog_queue=blog_queue,
            facebook_queue=facebook_queue,
            mapping=mapping,
            last_blog_error=last_blog_error,
            last_facebook_error=last_facebook_error,
        ),
    )


def _enrich_rows_with_alerts(rows: list[DistributionHealthRow]) -> list[DistributionHealthRow]:
    blog_schedule_collisions, facebook_schedule_collisions = _build_schedule_collision_sets(rows)
    enriched_rows: list[DistributionHealthRow] = []
    for row in rows:
        schedule_alerts: list[str] = []
        if row.blog_publish_id in blog_schedule_collisions:
            schedule_alerts.append("blog_schedule_collision")
        if row.blog_publish_id in facebook_schedule_collisions:
            schedule_alerts.append("facebook_schedule_collision")
        consistency_issues = _resolve_consistency_issues(row)
        enriched_rows.append(
            replace(
                row,
                consistency_issues=tuple(consistency_issues),
                schedule_alerts=tuple(schedule_alerts),
            )
        )
    return enriched_rows


def _build_schedule_collision_sets(
    rows: list[DistributionHealthRow],
) -> tuple[set[str], set[str]]:
    blog_schedule_groups: dict[str, list[str]] = {}
    facebook_schedule_groups: dict[str, list[str]] = {}
    for row in rows:
        if row.scheduled_for_blog and row.blog_queue_state == "scheduled_blog":
            blog_schedule_groups.setdefault(row.scheduled_for_blog, []).append(row.blog_publish_id)
        if row.scheduled_for_facebook and row.facebook_queue_state == "scheduled_facebook":
            facebook_schedule_groups.setdefault(row.scheduled_for_facebook, []).append(row.blog_publish_id)

    blog_collisions = {
        blog_publish_id
        for blog_publish_ids in blog_schedule_groups.values()
        if len(blog_publish_ids) > 1
        for blog_publish_id in blog_publish_ids
    }
    facebook_collisions = {
        blog_publish_id
        for blog_publish_ids in facebook_schedule_groups.values()
        if len(blog_publish_ids) > 1
        for blog_publish_id in blog_publish_ids
    }
    return blog_collisions, facebook_collisions


def _resolve_consistency_issues(row: DistributionHealthRow) -> tuple[str, ...]:
    issues: list[str] = []
    if row.blog_queue_state is None or row.facebook_queue_state is None or row.mapping_status is None:
        issues.append("missing_workflow_state")
    if row.wordpress_status == "published":
        if not row.has_confirmed_blog_url:
            issues.append("published_blog_missing_url")
        if row.blog_queue_state not in {None, "published_blog"}:
            issues.append("blog_queue_state_mismatch")
    if row.wordpress_status == "scheduled":
        if not row.scheduled_for_blog:
            issues.append("scheduled_blog_missing_time")
        if row.blog_queue_state not in {None, "scheduled_blog"}:
            issues.append("blog_queue_state_mismatch")
    if row.facebook_publish_status == "published":
        if not row.has_facebook_post_id:
            issues.append("published_facebook_missing_post_id")
        if row.facebook_queue_state not in {None, "published_facebook"}:
            issues.append("facebook_queue_state_mismatch")
        if row.mapping_status != "social_published":
            issues.append("mapping_status_mismatch")
    elif row.facebook_publish_status == "scheduled":
        if not row.scheduled_for_facebook:
            issues.append("scheduled_facebook_missing_time")
        if row.facebook_queue_state not in {None, "scheduled_facebook"}:
            issues.append("facebook_queue_state_mismatch")
        if row.mapping_status != "social_queued":
            issues.append("mapping_status_mismatch")
    elif row.facebook_publish_status == "failed":
        if row.facebook_queue_state not in {None, "facebook_publish_failed"}:
            issues.append("facebook_queue_state_mismatch")
        if row.mapping_status != "social_publish_failed":
            issues.append("mapping_status_mismatch")
    else:
        if row.facebook_queue_state in {"scheduled_facebook", "published_facebook", "facebook_publish_failed"}:
            issues.append("facebook_queue_missing_publish_record")
        if row.mapping_status in {"social_queued", "social_published", "social_publish_failed"}:
            issues.append("mapping_missing_publish_record")
    if row.social_package_id is None:
        if row.facebook_publish_id is not None or row.facebook_publish_status is not None:
            issues.append("facebook_publish_without_social_package")
        if row.mapping_status not in {None, "blog_only"}:
            issues.append("mapping_social_state_without_package")
    else:
        if row.mapping_status == "blog_only":
            issues.append("mapping_missing_social_linkage")
        if row.social_approval_state == "approved" and row.facebook_queue_state == "ready_for_social_review":
            issues.append("approved_social_queue_mismatch")
    if row.scheduled_for_blog and row.scheduled_for_facebook:
        if row.scheduled_for_facebook < row.scheduled_for_blog:
            issues.append("facebook_schedule_before_blog")
    return tuple(dict.fromkeys(issues))


def _resolve_operator_signal(
    blog_publish,
    *,
    social_package,
    facebook_publish,
    blog_queue,
    facebook_queue,
    mapping,
    last_blog_error: str | None,
    last_facebook_error: str | None,
) -> str:
    if blog_queue is None or facebook_queue is None or mapping is None:
        return "state_incomplete"
    if last_blog_error or blog_queue.queue_state == "blog_publish_failed":
        return "blog_publish_failed"
    if last_facebook_error or facebook_queue.queue_state == "facebook_publish_failed":
        return "facebook_publish_failed"
    if social_package is None:
        return "social_packaging_pending"
    if social_package.approval_state == "rejected":
        return "social_rejected"
    if social_package.approval_state == "needs_edits":
        return "social_needs_edits"
    if facebook_queue.queue_state == "ready_for_social_review":
        return "ready_for_social_review"
    if blog_queue.queue_state == "ready_for_wordpress":
        return "ready_for_wordpress"
    if blog_queue.queue_state == "wordpress_draft_created":
        return "wordpress_draft_created"
    if blog_queue.queue_state == "ready_for_blog_schedule":
        return "ready_for_blog_schedule"
    if facebook_queue.queue_state == "approved_for_queue":
        if blog_publish.wordpress_status == "published":
            return "ready_for_facebook_publish"
        if blog_publish.wordpress_status == "scheduled":
            return "ready_for_facebook_schedule"
        return "approved_for_queue"
    if facebook_queue.queue_state == "scheduled_facebook":
        return "scheduled_facebook"
    if facebook_queue.queue_state == "published_facebook":
        return "published_facebook"
    if blog_queue.queue_state == "scheduled_blog":
        return "scheduled_blog"
    if blog_queue.queue_state == "published_blog":
        return "published_blog"
    if facebook_publish is None and social_package.approval_state == "approved":
        return "approved_for_queue"
    return "monitor"


def _row_sort_key(row: DistributionHealthRow) -> tuple[int, str, str]:
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
        0 if row.consistency_issues else 1 if row.schedule_alerts else 2,
        signal_order.get(row.operator_signal, 99),
        row.latest_updated_at,
        row.blog_publish_id,
    )


def _build_summary(rows: list[DistributionHealthRow]) -> DistributionHealthSummary:
    wordpress_status_counts = Counter(row.wordpress_status for row in rows)
    social_approval_counts = Counter(row.social_approval_state or "none" for row in rows)
    facebook_publish_status_counts = Counter(row.facebook_publish_status or "none" for row in rows)
    blog_queue_state_counts = Counter(row.blog_queue_state or "missing" for row in rows)
    facebook_queue_state_counts = Counter(row.facebook_queue_state or "missing" for row in rows)
    mapping_status_counts = Counter(row.mapping_status or "missing" for row in rows)
    operator_signal_counts = Counter(row.operator_signal for row in rows)
    consistency_issue_counts = Counter(
        issue
        for row in rows
        for issue in row.consistency_issues
    )
    schedule_alert_counts = Counter(
        alert
        for row in rows
        for alert in row.schedule_alerts
    )
    error_counts = Counter(
        error
        for row in rows
        for error in (row.last_blog_error, row.last_facebook_error)
        if error
    )
    return DistributionHealthSummary(
        latest_snapshot_at=max((row.latest_updated_at for row in rows), default=None),
        total_blog_publish_chains=len(rows),
        wordpress_status_counts=dict(wordpress_status_counts),
        social_approval_counts=dict(social_approval_counts),
        facebook_publish_status_counts=dict(facebook_publish_status_counts),
        blog_queue_state_counts=dict(blog_queue_state_counts),
        facebook_queue_state_counts=dict(facebook_queue_state_counts),
        mapping_status_counts=dict(mapping_status_counts),
        operator_signal_counts=dict(operator_signal_counts),
        blog_chains_with_social_package=sum(1 for row in rows if row.social_package_id is not None),
        blog_chains_with_remote_wordpress_post=sum(1 for row in rows if row.has_remote_wordpress_post),
        blog_chains_with_confirmed_blog_url=sum(1 for row in rows if row.has_confirmed_blog_url),
        blog_chains_with_facebook_post_id=sum(1 for row in rows if row.has_facebook_post_id),
        rows_with_consistency_issues=sum(1 for row in rows if row.consistency_issues),
        rows_with_schedule_alerts=sum(1 for row in rows if row.schedule_alerts),
        consistency_issue_counts=dict(consistency_issue_counts),
        schedule_alert_counts=dict(schedule_alert_counts),
        top_errors=tuple(error_counts.most_common(5)),
    )


def _first_non_empty(*values: str | None) -> str | None:
    for value in values:
        if value:
            return value
    return None


def _latest_timestamp(*values: str | None) -> str:
    normalized = [value for value in values if value]
    if not normalized:
        return ""
    return max(normalized)
