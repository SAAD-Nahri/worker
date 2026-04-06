from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from distribution_engine.health import build_distribution_health_report


@dataclass(frozen=True)
class DistributionScheduleRow:
    blog_publish_id: str
    wordpress_title: str
    blog_queue_state: str | None
    facebook_queue_state: str | None
    scheduled_for_blog: str | None
    scheduled_for_facebook: str | None
    scheduling_signal: str
    schedule_alerts: tuple[str, ...]
    operator_signal: str

    def to_dict(self) -> dict[str, object]:
        return {
            "blog_publish_id": self.blog_publish_id,
            "wordpress_title": self.wordpress_title,
            "blog_queue_state": self.blog_queue_state,
            "facebook_queue_state": self.facebook_queue_state,
            "scheduled_for_blog": self.scheduled_for_blog,
            "scheduled_for_facebook": self.scheduled_for_facebook,
            "scheduling_signal": self.scheduling_signal,
            "schedule_alerts": list(self.schedule_alerts),
            "operator_signal": self.operator_signal,
        }


@dataclass(frozen=True)
class DistributionScheduleSummary:
    total_rows: int
    scheduling_signal_counts: dict[str, int]
    blog_schedule_slot_counts: dict[str, int]
    facebook_schedule_slot_counts: dict[str, int]
    rows_with_schedule_alerts: int
    schedule_alert_counts: dict[str, int]
    ready_for_blog_schedule: int
    ready_for_facebook_schedule: int
    scheduled_pairs: int
    awaiting_facebook_schedule: int

    def to_dict(self) -> dict[str, object]:
        return {
            "total_rows": self.total_rows,
            "scheduling_signal_counts": dict(self.scheduling_signal_counts),
            "blog_schedule_slot_counts": dict(self.blog_schedule_slot_counts),
            "facebook_schedule_slot_counts": dict(self.facebook_schedule_slot_counts),
            "rows_with_schedule_alerts": self.rows_with_schedule_alerts,
            "schedule_alert_counts": dict(self.schedule_alert_counts),
            "ready_for_blog_schedule": self.ready_for_blog_schedule,
            "ready_for_facebook_schedule": self.ready_for_facebook_schedule,
            "scheduled_pairs": self.scheduled_pairs,
            "awaiting_facebook_schedule": self.awaiting_facebook_schedule,
        }


def build_distribution_schedule_report(
    *,
    blog_publish_records_path: Path | None = None,
    social_package_records_path: Path | None = None,
    social_package_reviews_path: Path | None = None,
    facebook_publish_records_path: Path | None = None,
    queue_item_records_path: Path | None = None,
    mapping_records_path: Path | None = None,
) -> tuple[DistributionScheduleSummary, list[DistributionScheduleRow]]:
    _, health_rows = build_distribution_health_report(
        blog_publish_records_path=blog_publish_records_path,
        social_package_records_path=social_package_records_path,
        social_package_reviews_path=social_package_reviews_path,
        facebook_publish_records_path=facebook_publish_records_path,
        queue_item_records_path=queue_item_records_path,
        mapping_records_path=mapping_records_path,
    )
    rows = [
        DistributionScheduleRow(
            blog_publish_id=row.blog_publish_id,
            wordpress_title=row.wordpress_title,
            blog_queue_state=row.blog_queue_state,
            facebook_queue_state=row.facebook_queue_state,
            scheduled_for_blog=row.scheduled_for_blog,
            scheduled_for_facebook=row.scheduled_for_facebook,
            scheduling_signal=_resolve_scheduling_signal(row),
            schedule_alerts=row.schedule_alerts,
            operator_signal=row.operator_signal,
        )
        for row in health_rows
    ]
    rows.sort(key=_row_sort_key)
    return _build_summary(rows), rows


def _resolve_scheduling_signal(row) -> str:
    if row.schedule_alerts:
        return "collision_review"
    if row.blog_queue_state == "ready_for_blog_schedule":
        return "ready_for_blog_schedule"
    if row.facebook_queue_state == "approved_for_queue":
        if row.wordpress_status == "published":
            return "ready_for_facebook_publish"
        if row.wordpress_status == "scheduled":
            return "ready_for_facebook_schedule"
    if row.blog_queue_state == "scheduled_blog" and row.facebook_queue_state == "scheduled_facebook":
        return "scheduled_pair"
    if row.blog_queue_state == "scheduled_blog" and row.facebook_queue_state != "scheduled_facebook":
        return "awaiting_facebook_schedule"
    if row.facebook_queue_state == "scheduled_facebook":
        return "facebook_scheduled"
    if row.blog_queue_state == "published_blog" and row.facebook_queue_state == "published_facebook":
        return "published_pair"
    return "monitor"


def _row_sort_key(row: DistributionScheduleRow) -> tuple[int, str, str, str]:
    signal_order = {
        "collision_review": 0,
        "ready_for_blog_schedule": 1,
        "ready_for_facebook_schedule": 2,
        "ready_for_facebook_publish": 3,
        "awaiting_facebook_schedule": 4,
        "scheduled_pair": 5,
        "facebook_scheduled": 6,
        "published_pair": 7,
        "monitor": 8,
    }
    return (
        signal_order.get(row.scheduling_signal, 99),
        row.scheduled_for_blog or row.scheduled_for_facebook or "",
        row.scheduled_for_facebook or "",
        row.blog_publish_id,
    )


def _build_summary(rows: list[DistributionScheduleRow]) -> DistributionScheduleSummary:
    scheduling_signal_counts = Counter(row.scheduling_signal for row in rows)
    blog_slot_counts = Counter(row.scheduled_for_blog for row in rows if row.scheduled_for_blog)
    facebook_slot_counts = Counter(row.scheduled_for_facebook for row in rows if row.scheduled_for_facebook)
    schedule_alert_counts = Counter(
        alert
        for row in rows
        for alert in row.schedule_alerts
    )
    return DistributionScheduleSummary(
        total_rows=len(rows),
        scheduling_signal_counts=dict(scheduling_signal_counts),
        blog_schedule_slot_counts=dict(blog_slot_counts),
        facebook_schedule_slot_counts=dict(facebook_slot_counts),
        rows_with_schedule_alerts=sum(1 for row in rows if row.schedule_alerts),
        schedule_alert_counts=dict(schedule_alert_counts),
        ready_for_blog_schedule=scheduling_signal_counts.get("ready_for_blog_schedule", 0),
        ready_for_facebook_schedule=scheduling_signal_counts.get("ready_for_facebook_schedule", 0),
        scheduled_pairs=scheduling_signal_counts.get("scheduled_pair", 0),
        awaiting_facebook_schedule=scheduling_signal_counts.get("awaiting_facebook_schedule", 0),
    )
