from __future__ import annotations

import argparse
import json
from pathlib import Path

from distribution_engine.facebook_publish_updates import (
    ALLOWED_FACEBOOK_PUBLISH_UPDATE_ACTIONS,
    record_facebook_publish_update,
)
from distribution_engine.storage import (
    BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
    BLOG_PUBLISH_RECORDS_PATH,
    FACEBOOK_PUBLISH_RECORDS_PATH,
    QUEUE_ITEM_RECORDS_PATH,
    SOCIAL_PACKAGE_RECORDS_PATH,
    append_blog_facebook_mapping_records,
    append_facebook_publish_records,
    append_queue_item_records,
    load_latest_blog_publish_record,
    load_latest_facebook_publish_for_social_package,
    load_latest_social_package_record,
)
from distribution_engine.workflow import prepare_distribution_linkage_records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Record a local Facebook publish-state update and refresh queue/mapping snapshots."
    )
    parser.add_argument("--social-package-id", required=True, help="Approved social package identifier to update.")
    parser.add_argument(
        "--action",
        required=True,
        choices=sorted(ALLOWED_FACEBOOK_PUBLISH_UPDATE_ACTIONS),
        help="Local Facebook publish-state update to record.",
    )
    parser.add_argument("--facebook-post-id", help="Facebook post identifier when one exists.")
    parser.add_argument(
        "--schedule-mode",
        choices=["manual", "auto"],
        help="Required for scheduled actions. Use manual for operator scheduling or auto for policy-approved auto scheduling.",
    )
    parser.add_argument(
        "--schedule-approved-by",
        help="Operator or policy label that approved the schedule decision.",
    )
    parser.add_argument(
        "--schedule-applied-by",
        help="Actor that applied the schedule. Use system_auto_scheduler for auto scheduling.",
    )
    parser.add_argument(
        "--scheduled-for-facebook",
        help="Scheduled publish time for a scheduled Facebook post.",
    )
    parser.add_argument(
        "--published-at-facebook",
        help="Published timestamp when the Facebook post is live.",
    )
    parser.add_argument("--error", help="Error detail for a failed Facebook publish attempt.")
    parser.add_argument(
        "--social-package-records-path",
        type=Path,
        default=SOCIAL_PACKAGE_RECORDS_PATH,
        help="Path to the append-only social package records file.",
    )
    parser.add_argument(
        "--blog-publish-records-path",
        type=Path,
        default=BLOG_PUBLISH_RECORDS_PATH,
        help="Path to the append-only blog publish records file.",
    )
    parser.add_argument(
        "--facebook-publish-records-path",
        type=Path,
        default=FACEBOOK_PUBLISH_RECORDS_PATH,
        help="Path to the append-only Facebook publish records file.",
    )
    parser.add_argument(
        "--queue-item-records-path",
        type=Path,
        default=QUEUE_ITEM_RECORDS_PATH,
        help="Path to the append-only queue item records file.",
    )
    parser.add_argument(
        "--mapping-records-path",
        type=Path,
        default=BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
        help="Path to the append-only blog/Facebook mapping records file.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        social_package = load_latest_social_package_record(
            args.social_package_id,
            path=args.social_package_records_path,
        )
        if not social_package.blog_publish_id:
            raise ValueError("Facebook publish updates require a social package linked to blog_publish_id.")
        blog_publish_record = load_latest_blog_publish_record(
            social_package.blog_publish_id,
            path=args.blog_publish_records_path,
        )
        existing_publish_record = None
        try:
            existing_publish_record = load_latest_facebook_publish_for_social_package(
                social_package.social_package_id,
                path=args.facebook_publish_records_path,
            )
        except ValueError:
            existing_publish_record = None

        updated_facebook_publish = record_facebook_publish_update(
            social_package,
            blog_publish_record,
            update_action=args.action,
            existing_publish_record=existing_publish_record,
            facebook_post_id=args.facebook_post_id,
            schedule_mode=args.schedule_mode,
            schedule_approved_by=args.schedule_approved_by,
            schedule_applied_by=args.schedule_applied_by,
            scheduled_for_facebook=args.scheduled_for_facebook,
            published_at_facebook=args.published_at_facebook,
            error_message=args.error,
        )
        append_facebook_publish_records(
            [updated_facebook_publish],
            path=args.facebook_publish_records_path,
        )

        blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
            blog_publish_record,
            social_package_record=social_package,
            facebook_publish_record=updated_facebook_publish,
        )
        append_queue_item_records([blog_queue, facebook_queue], path=args.queue_item_records_path)
        append_blog_facebook_mapping_records([mapping], path=args.mapping_records_path)
    except ValueError as exc:
        parser.error(str(exc))

    summary = {
        "social_package_id": social_package.social_package_id,
        "facebook_publish_id": updated_facebook_publish.facebook_publish_id,
        "publish_status": updated_facebook_publish.publish_status,
        "schedule_mode": updated_facebook_publish.schedule_mode,
        "facebook_queue_state": facebook_queue.queue_state,
        "mapping_status": mapping.mapping_status,
        "facebook_publish_records_path": str(args.facebook_publish_records_path),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0
