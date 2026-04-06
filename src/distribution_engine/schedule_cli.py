from __future__ import annotations

import argparse
import json
from pathlib import Path

from distribution_engine.schedule_report import build_distribution_schedule_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize Phase 3 schedule planning state from latest publish, queue, and mapping snapshots."
    )
    parser.add_argument("--blog-publish-records-path", type=Path, default=None)
    parser.add_argument("--social-package-records-path", type=Path, default=None)
    parser.add_argument("--social-package-reviews-path", type=Path, default=None)
    parser.add_argument("--facebook-publish-records-path", type=Path, default=None)
    parser.add_argument("--queue-item-records-path", type=Path, default=None)
    parser.add_argument("--mapping-records-path", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    summary, rows = build_distribution_schedule_report(
        blog_publish_records_path=args.blog_publish_records_path,
        social_package_records_path=args.social_package_records_path,
        social_package_reviews_path=args.social_package_reviews_path,
        facebook_publish_records_path=args.facebook_publish_records_path,
        queue_item_records_path=args.queue_item_records_path,
        mapping_records_path=args.mapping_records_path,
    )

    if args.json:
        print(
            json.dumps(
                {
                    "summary": summary.to_dict(),
                    "rows": [row.to_dict() for row in rows],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    print("Distribution schedule summary")
    print("=============================")
    print(f"Total chains: {summary.total_rows}")
    print(
        "Scheduling signals: "
        f"ready_for_blog_schedule={summary.ready_for_blog_schedule} "
        f"ready_for_facebook_schedule={summary.ready_for_facebook_schedule} "
        f"scheduled_pairs={summary.scheduled_pairs} "
        f"awaiting_facebook_schedule={summary.awaiting_facebook_schedule}"
    )
    print(
        "Schedule alerts: "
        f"rows={summary.rows_with_schedule_alerts}"
    )
    if summary.schedule_alert_counts:
        alert_bits = ", ".join(
            f"{alert}({count})" for alert, count in sorted(summary.schedule_alert_counts.items())
        )
        print(f"Alert counts: {alert_bits}")

    if not rows:
        print("No schedule planning records available.")
        return 0

    header = (
        f"{'blog_publish_id':<34} {'blog_slot':<25} {'facebook_slot':<25} "
        f"{'signal':<28} {'alerts':<30}"
    )
    print(header)
    print("-" * len(header))
    for row in rows:
        alerts = ", ".join(row.schedule_alerts) if row.schedule_alerts else "-"
        print(
            f"{row.blog_publish_id:<34} {(row.scheduled_for_blog or '-'): <25} "
            f"{(row.scheduled_for_facebook or '-'): <25} {row.scheduling_signal:<28} {alerts:<30}"
        )
        print(
            f"{'':<34} blog_queue={(row.blog_queue_state or 'missing')} "
            f"facebook_queue={(row.facebook_queue_state or 'missing')} "
            f"title={row.wordpress_title}"
        )
    return 0
