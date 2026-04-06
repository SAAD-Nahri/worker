from __future__ import annotations

import argparse
import json
from pathlib import Path

from distribution_engine.health import build_distribution_health_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize current Phase 3 distribution health from latest publish, queue, and mapping snapshots."
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

    summary, rows = build_distribution_health_report(
        blog_publish_records_path=args.blog_publish_records_path,
        social_package_records_path=args.social_package_records_path,
        social_package_reviews_path=args.social_package_reviews_path,
        facebook_publish_records_path=args.facebook_publish_records_path,
        queue_item_records_path=args.queue_item_records_path,
        mapping_records_path=args.mapping_records_path,
    )

    if args.json:
        payload = {
            "summary": summary.to_dict(),
            "rows": [row.to_dict() for row in rows],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print("Distribution health summary")
    print("===========================")
    print(f"Latest distribution snapshot: {summary.latest_snapshot_at or 'none'}")
    print(f"Total blog publish chains: {summary.total_blog_publish_chains}")
    print(
        "WordPress statuses: "
        f"prepared_local={summary.wordpress_status_counts.get('prepared_local', 0)} "
        f"draft_created={summary.wordpress_status_counts.get('draft_created', 0)} "
        f"draft_updated={summary.wordpress_status_counts.get('draft_updated', 0)} "
        f"scheduled={summary.wordpress_status_counts.get('scheduled', 0)} "
        f"published={summary.wordpress_status_counts.get('published', 0)} "
        f"failed={summary.wordpress_status_counts.get('failed', 0)}"
    )
    print(
        "Social approvals: "
        f"none={summary.social_approval_counts.get('none', 0)} "
        f"pending_review={summary.social_approval_counts.get('pending_review', 0)} "
        f"approved={summary.social_approval_counts.get('approved', 0)} "
        f"needs_edits={summary.social_approval_counts.get('needs_edits', 0)} "
        f"rejected={summary.social_approval_counts.get('rejected', 0)}"
    )
    print(
        "Facebook statuses: "
        f"none={summary.facebook_publish_status_counts.get('none', 0)} "
        f"scheduled={summary.facebook_publish_status_counts.get('scheduled', 0)} "
        f"published={summary.facebook_publish_status_counts.get('published', 0)} "
        f"failed={summary.facebook_publish_status_counts.get('failed', 0)}"
    )
    print(
        "Blog queue: "
        f"ready_for_wordpress={summary.blog_queue_state_counts.get('ready_for_wordpress', 0)} "
        f"wordpress_draft_created={summary.blog_queue_state_counts.get('wordpress_draft_created', 0)} "
        f"ready_for_blog_schedule={summary.blog_queue_state_counts.get('ready_for_blog_schedule', 0)} "
        f"scheduled_blog={summary.blog_queue_state_counts.get('scheduled_blog', 0)} "
        f"published_blog={summary.blog_queue_state_counts.get('published_blog', 0)} "
        f"blog_publish_failed={summary.blog_queue_state_counts.get('blog_publish_failed', 0)}"
    )
    print(
        "Facebook queue: "
        f"social_packaging_pending={summary.facebook_queue_state_counts.get('social_packaging_pending', 0)} "
        f"ready_for_social_review={summary.facebook_queue_state_counts.get('ready_for_social_review', 0)} "
        f"approved_for_queue={summary.facebook_queue_state_counts.get('approved_for_queue', 0)} "
        f"scheduled_facebook={summary.facebook_queue_state_counts.get('scheduled_facebook', 0)} "
        f"published_facebook={summary.facebook_queue_state_counts.get('published_facebook', 0)} "
        f"facebook_publish_failed={summary.facebook_queue_state_counts.get('facebook_publish_failed', 0)}"
    )
    print(
        "Coverage: "
        f"social_packages={summary.blog_chains_with_social_package}/{summary.total_blog_publish_chains} "
        f"remote_wordpress_post={summary.blog_chains_with_remote_wordpress_post}/{summary.total_blog_publish_chains} "
        f"confirmed_blog_url={summary.blog_chains_with_confirmed_blog_url}/{summary.total_blog_publish_chains} "
        f"facebook_post_ids={summary.blog_chains_with_facebook_post_id}/{summary.total_blog_publish_chains}"
    )
    print(
        "Operator alerts: "
        f"consistency_issue_rows={summary.rows_with_consistency_issues} "
        f"schedule_alert_rows={summary.rows_with_schedule_alerts}"
    )
    if summary.consistency_issue_counts:
        consistency_bits = ", ".join(
            f"{issue}({count})" for issue, count in sorted(summary.consistency_issue_counts.items())
        )
        print(f"Consistency issues: {consistency_bits}")
    if summary.schedule_alert_counts:
        schedule_bits = ", ".join(
            f"{alert}({count})" for alert, count in sorted(summary.schedule_alert_counts.items())
        )
        print(f"Schedule alerts: {schedule_bits}")
    if summary.top_errors:
        top_errors = ", ".join(f"{error}({count})" for error, count in summary.top_errors)
        print(f"Top errors: {top_errors}")

    if not rows:
        print("No distribution records available.")
        return 0

    header = (
        f"{'blog_publish_id':<34} {'wp_status':<14} {'blog_queue':<24} "
        f"{'social':<14} {'fb_status':<11} {'fb_queue':<24} {'signal':<28}"
    )
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            f"{row.blog_publish_id:<34} {row.wordpress_status:<14} {(row.blog_queue_state or 'missing'):<24} "
            f"{(row.social_approval_state or 'none'):<14} {(row.facebook_publish_status or 'none'):<11} "
            f"{(row.facebook_queue_state or 'missing'):<24} {row.operator_signal:<28}"
        )
        print(
            f"{'':<34} mapping={row.mapping_status or 'missing'} "
            f"remote_wp={str(row.has_remote_wordpress_post).lower()} "
            f"blog_url={str(row.has_confirmed_blog_url).lower()} "
            f"fb_post={str(row.has_facebook_post_id).lower()}"
        )
        if row.consistency_issues:
            print(f"{'':<34} consistency=" + ", ".join(row.consistency_issues))
        if row.schedule_alerts:
            print(f"{'':<34} schedule_alerts=" + ", ".join(row.schedule_alerts))
        if row.last_blog_error or row.last_facebook_error:
            error_bits: list[str] = []
            if row.last_blog_error:
                error_bits.append(f"blog_error={row.last_blog_error}")
            if row.last_facebook_error:
                error_bits.append(f"facebook_error={row.last_facebook_error}")
            print(f"{'':<34} " + " ".join(error_bits))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
