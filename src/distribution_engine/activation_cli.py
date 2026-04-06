from __future__ import annotations

import argparse
import json
from pathlib import Path

from distribution_engine.activation import (
    DEFAULT_FACEBOOK_CONFIG_PATH,
    DEFAULT_WORDPRESS_CONFIG_PATH,
    build_system_activation_readiness_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize current Phase 4.5 system-activation readiness from config, drafts, distribution state, and audit records."
    )
    parser.add_argument("--wordpress-config-path", type=Path, default=DEFAULT_WORDPRESS_CONFIG_PATH)
    parser.add_argument("--facebook-config-path", type=Path, default=DEFAULT_FACEBOOK_CONFIG_PATH)
    parser.add_argument("--draft-records-path", type=Path, default=None)
    parser.add_argument("--blog-publish-records-path", type=Path, default=None)
    parser.add_argument("--social-package-records-path", type=Path, default=None)
    parser.add_argument("--social-package-reviews-path", type=Path, default=None)
    parser.add_argument("--facebook-publish-records-path", type=Path, default=None)
    parser.add_argument("--queue-item-records-path", type=Path, default=None)
    parser.add_argument("--mapping-records-path", type=Path, default=None)
    parser.add_argument("--audit-records-path", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    summary, config_statuses, candidate_rows, canary_rows = build_system_activation_readiness_report(
        wordpress_config_path=args.wordpress_config_path,
        facebook_config_path=args.facebook_config_path,
        draft_records_path=args.draft_records_path,
        blog_publish_records_path=args.blog_publish_records_path,
        social_package_records_path=args.social_package_records_path,
        social_package_reviews_path=args.social_package_reviews_path,
        facebook_publish_records_path=args.facebook_publish_records_path,
        queue_item_records_path=args.queue_item_records_path,
        mapping_records_path=args.mapping_records_path,
        audit_records_path=args.audit_records_path,
    )

    if args.json:
        print(
            json.dumps(
                {
                    "summary": summary.to_dict(),
                    "config_statuses": [status.to_dict() for status in config_statuses],
                    "approved_draft_candidates": [row.to_dict() for row in candidate_rows],
                    "local_canary_rows": [row.to_dict() for row in canary_rows],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    print("System activation readiness")
    print("==========================")
    print(f"Signal: {summary.readiness_signal}")
    print(f"Latest distribution snapshot: {summary.latest_distribution_snapshot_at or 'none'}")
    print(f"Latest execute validation: {summary.latest_transport_validation_at or 'none'}")
    print(
        "Counts: "
        f"approved_pass_drafts={summary.approved_pass_draft_count} "
        f"local_canary_chains={summary.local_canary_chain_count} "
        f"wordpress_execute_validations={summary.successful_wordpress_validations} "
        f"facebook_execute_validations={summary.successful_facebook_validations}"
    )
    print("Blocking reasons: " + (", ".join(summary.blocking_reasons) if summary.blocking_reasons else "none"))
    print("")
    print("Config status")
    print("-------------")
    for status in config_statuses:
        print(
            f"{status.config_name}: "
            f"exists={str(status.exists).lower()} "
            f"parse_valid={str(status.parse_valid).lower()} "
            f"ready_for_execute={str(status.ready_for_execute).lower()} "
            f"placeholder_detected={str(status.placeholder_detected).lower()} "
            f"target={status.masked_target or 'none'}"
        )
        if status.missing_fields:
            print("  missing_fields=" + ", ".join(status.missing_fields))
        if status.notes:
            print("  notes=" + ", ".join(status.notes))

    print("")
    print("Approved canary candidates")
    print("-------------------------")
    if not candidate_rows:
        print("No approved pass-quality draft candidates.")
    else:
        for row in candidate_rows[:5]:
            print(
                f"{row.draft_id} template={row.template_id} category={row.category} "
                f"source={row.source_id} updated_at={row.updated_at}"
            )
            print(f"  headline={row.headline_selected}")

    print("")
    print("Local canary chains")
    print("-------------------")
    if not canary_rows:
        print("No local canary chain records found.")
    else:
        for row in canary_rows[:5]:
            print(
                f"{row.blog_publish_id} wp_status={row.wordpress_status} "
                f"blog_queue={row.blog_queue_state or 'none'} "
                f"social={row.social_approval_state or 'none'} "
                f"fb_status={row.facebook_publish_status or 'none'} "
                f"signal={row.operator_signal}"
            )
            print(
                f"  mapping={row.mapping_status or 'none'} "
                f"blog_url={str(row.has_confirmed_blog_url).lower()} "
                f"remote_wp={str(row.has_remote_wordpress_post).lower()} "
                f"fb_post={str(row.has_facebook_post_id).lower()}"
            )

    print("")
    print("Next steps")
    print("----------")
    if not summary.next_steps:
        print("No blocking next steps remain.")
    else:
        for step in summary.next_steps:
            print(f"- {step}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
