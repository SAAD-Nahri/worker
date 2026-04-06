from __future__ import annotations

import argparse
import json
from pathlib import Path

from tracking_engine.audit import record_tracking_normalization_run
from tracking_engine.chain_history import build_publish_chain_history_report
from tracking_engine.reporting import (
    build_publish_exception_report,
    build_source_template_activity_summary,
    build_variant_usage_summary,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize Phase 4 publish-chain history from source, draft, and distribution records."
    )
    parser.add_argument("--source-items-path", type=Path, default=None)
    parser.add_argument("--draft-records-path", type=Path, default=None)
    parser.add_argument("--draft-reviews-path", type=Path, default=None)
    parser.add_argument("--blog-publish-records-path", type=Path, default=None)
    parser.add_argument("--social-package-records-path", type=Path, default=None)
    parser.add_argument("--social-package-reviews-path", type=Path, default=None)
    parser.add_argument("--facebook-publish-records-path", type=Path, default=None)
    parser.add_argument("--queue-item-records-path", type=Path, default=None)
    parser.add_argument("--mapping-records-path", type=Path, default=None)
    parser.add_argument(
        "--view",
        choices=("ledger", "exceptions", "activity", "variants", "all"),
        default="ledger",
        help="Select which Phase 4 tracking view to render.",
    )
    parser.add_argument(
        "--record-audit",
        action="store_true",
        help="Append a deliberate Phase 4 normalization-run audit record for this invocation.",
    )
    parser.add_argument(
        "--actor-label",
        default="operator",
        help="Actor label to store when --record-audit is used.",
    )
    parser.add_argument(
        "--audit-records-path",
        type=Path,
        default=None,
        help="Optional override path for tracking audit records.",
    )
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    summary, snapshots = build_publish_chain_history_report(
        source_items_path=args.source_items_path,
        draft_records_path=args.draft_records_path,
        draft_reviews_path=args.draft_reviews_path,
        blog_publish_records_path=args.blog_publish_records_path,
        social_package_records_path=args.social_package_records_path,
        social_package_reviews_path=args.social_package_reviews_path,
        facebook_publish_records_path=args.facebook_publish_records_path,
        queue_item_records_path=args.queue_item_records_path,
        mapping_records_path=args.mapping_records_path,
    )
    exception_summary, exception_rows = build_publish_exception_report(snapshots)
    activity_summary = build_source_template_activity_summary(snapshots)
    variant_summary = build_variant_usage_summary(snapshots)
    audit_record = None
    if args.record_audit:
        audit_record = record_tracking_normalization_run(
            actor_label=args.actor_label,
            view_name=args.view,
            history_summary=summary,
            exception_summary=exception_summary,
            audit_records_path=args.audit_records_path if args.audit_records_path is not None else None,
        )

    if args.json:
        payload = _json_payload(
            view=args.view,
            summary=summary,
            snapshots=snapshots,
            exception_summary=exception_summary,
            exception_rows=exception_rows,
            activity_summary=activity_summary,
            variant_summary=variant_summary,
        )
        if audit_record is not None:
            payload["audit_record"] = audit_record.to_dict()
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    if args.view in {"ledger", "all"}:
        _print_ledger(summary, snapshots)
    if args.view in {"exceptions", "all"}:
        _print_exceptions(exception_summary, exception_rows)
    if args.view in {"activity", "all"}:
        _print_activity(activity_summary)
    if args.view in {"variants", "all"}:
        _print_variants(variant_summary)
    if audit_record is not None:
        print()
        print(f"Audit recorded: {audit_record.event_id}")
    return 0


def _json_payload(
    *,
    view: str,
    summary,
    snapshots,
    exception_summary,
    exception_rows,
    activity_summary,
    variant_summary,
) -> dict[str, object]:
    if view == "ledger":
        return {
            "summary": summary.to_dict(),
            "snapshots": [snapshot.to_dict() for snapshot in snapshots],
        }
    if view == "exceptions":
        return {
            "summary": exception_summary.to_dict(),
            "rows": [row.to_dict() for row in exception_rows],
        }
    if view == "activity":
        return activity_summary.to_dict()
    if view == "variants":
        return variant_summary.to_dict()
    return {
        "ledger": {
            "summary": summary.to_dict(),
            "snapshots": [snapshot.to_dict() for snapshot in snapshots],
        },
        "exceptions": {
            "summary": exception_summary.to_dict(),
            "rows": [row.to_dict() for row in exception_rows],
        },
        "activity": activity_summary.to_dict(),
        "variants": variant_summary.to_dict(),
    }


def _print_ledger(summary, snapshots) -> None:
    print("Publish chain history summary")
    print("=============================")
    print(f"Latest snapshot: {summary.latest_snapshot_at or 'none'}")
    print(f"Total chains: {summary.total_chains}")
    print(
        "Coverage: "
        f"social_package={summary.chains_with_social_package}/{summary.total_chains} "
        f"facebook_publish={summary.chains_with_facebook_publish}/{summary.total_chains} "
        f"confirmed_blog_url={summary.chains_with_confirmed_blog_url}/{summary.total_chains}"
    )
    print(
        "Alerts: "
        f"consistency_issue_chains={summary.chains_with_consistency_issues} "
        f"schedule_alert_chains={summary.chains_with_schedule_alerts}"
    )
    if not snapshots:
        print("No publish chain records available.")
        return

    header = (
        f"{'chain_id':<34} {'source_family':<18} {'template_family':<22} "
        f"{'wp_status':<14} {'fb_status':<11} {'status':<28}"
    )
    print(header)
    print("-" * len(header))
    for snapshot in snapshots:
        print(
            f"{snapshot.chain_id:<34} {(snapshot.source_family or 'unknown'):<18} "
            f"{(snapshot.template_family or 'unknown'):<22} "
            f"{(snapshot.wordpress_status or 'none'):<14} "
            f"{(snapshot.facebook_publish_status or 'none'):<11} "
            f"{snapshot.chain_status:<28}"
        )
        print(
            f"{'':<34} title={snapshot.selected_blog_title} "
            f"draft_reviews={snapshot.draft_review_count} social_reviews={snapshot.social_review_count}"
        )
        if snapshot.selected_hook_text:
            print(f"{'':<34} hook={snapshot.selected_hook_text}")
        if snapshot.consistency_issues:
            print(f"{'':<34} consistency=" + ", ".join(snapshot.consistency_issues))
        if snapshot.schedule_alerts:
            print(f"{'':<34} schedule_alerts=" + ", ".join(snapshot.schedule_alerts))


def _print_exceptions(summary, rows) -> None:
    print()
    print("Publish exception view")
    print("======================")
    print(f"Total exception chains: {summary.total_exception_chains}")
    print(
        "Breakdown: "
        f"failed={summary.failed_chain_count} "
        f"partial={summary.partial_chain_count} "
        f"consistency_issue_chains={summary.consistency_issue_chains} "
        f"schedule_alert_chains={summary.schedule_alert_chains}"
    )
    if summary.exception_reason_counts:
        print(
            "Reasons: "
            + ", ".join(
                f"{reason}({count})" for reason, count in sorted(summary.exception_reason_counts.items())
            )
        )
    if not rows:
        print("No exception chains detected.")
        return

    header = (
        f"{'chain_id':<34} {'wp_status':<14} {'fb_status':<11} "
        f"{'status':<28} {'reasons':<40}"
    )
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            f"{row.chain_id:<34} {row.wordpress_status:<14} "
            f"{(row.facebook_publish_status or 'none'):<11} "
            f"{row.chain_status:<28} "
            f"{', '.join(row.exception_reasons):<40}"
        )
        if row.consistency_issues:
            print(f"{'':<34} consistency=" + ", ".join(row.consistency_issues))
        if row.schedule_alerts:
            print(f"{'':<34} schedule_alerts=" + ", ".join(row.schedule_alerts))


def _print_activity(summary) -> None:
    print()
    print("Source and template activity summary")
    print("====================================")
    print(f"Total chains: {summary.total_chains}")
    print("By source family: " + _format_counts(summary.counts_by_source_family))
    print("By template family: " + _format_counts(summary.counts_by_template_family))
    print("By category: " + _format_counts(summary.counts_by_category))
    print("By source id: " + _format_counts(summary.counts_by_source_id))
    print("By template id: " + _format_counts(summary.counts_by_template_id))


def _print_variants(summary) -> None:
    print()
    print("Variant usage summary")
    print("=====================")
    print(f"Total chains: {summary.total_chains}")
    print(f"Chains with headline variants: {summary.chains_with_headline_variants}")
    if summary.selected_variant_label_counts:
        print("Selected variant labels: " + _format_counts(summary.selected_variant_label_counts))
    _print_nested_top_counts("Blog titles by template family", summary.blog_title_counts_by_template_family)
    _print_nested_top_counts("Hooks by package template", summary.hook_counts_by_package_template)
    _print_nested_top_counts("Captions by package template", summary.caption_counts_by_package_template)
    _print_nested_top_counts(
        "Comment CTAs by comment template",
        summary.comment_cta_counts_by_comment_template,
    )


def _print_nested_top_counts(title: str, counts: dict[str, dict[str, int]]) -> None:
    if not counts:
        return
    print(title + ":")
    for group, values in sorted(counts.items()):
        top_values = ", ".join(
            f"{value}({count})"
            for value, count in sorted(values.items(), key=lambda item: (-item[1], item[0]))[:3]
        )
        print(f"  {group}: {top_values}")


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(
        f"{key}({count})"
        for key, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    )


if __name__ == "__main__":
    raise SystemExit(main())
