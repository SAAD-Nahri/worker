from __future__ import annotations

import argparse
import json
from pathlib import Path

from distribution_engine.publish_updates import (
    ALLOWED_BLOG_PUBLISH_UPDATE_ACTIONS,
    record_blog_publish_update,
)
from distribution_engine.storage import (
    BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
    BLOG_PUBLISH_RECORDS_PATH,
    FACEBOOK_PUBLISH_RECORDS_PATH,
    QUEUE_ITEM_RECORDS_PATH,
    SOCIAL_PACKAGE_RECORDS_PATH,
    append_blog_facebook_mapping_records,
    append_blog_publish_records,
    append_queue_item_records,
    load_latest_facebook_publish_for_social_package,
    load_latest_blog_publish_record,
    load_latest_social_package_for_blog_publish,
)
from distribution_engine.workflow import prepare_distribution_linkage_records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Record a local WordPress publish-state update and refresh queue/mapping snapshots."
    )
    parser.add_argument("--blog-publish-id", required=True, help="Blog publish identifier to update.")
    parser.add_argument(
        "--action",
        required=True,
        choices=sorted(ALLOWED_BLOG_PUBLISH_UPDATE_ACTIONS),
        help="Local WordPress publish-state update to record.",
    )
    parser.add_argument("--wordpress-post-id", help="WordPress post identifier when one exists.")
    parser.add_argument("--wordpress-post-url", help="WordPress post URL when one exists.")
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
    parser.add_argument("--scheduled-for-blog", help="Scheduled publish time for a scheduled blog post.")
    parser.add_argument("--published-at-blog", help="Published timestamp when the blog post is live.")
    parser.add_argument("--error", help="Error detail for a failed WordPress publish attempt.")
    parser.add_argument(
        "--blog-publish-records-path",
        type=Path,
        default=BLOG_PUBLISH_RECORDS_PATH,
        help="Path to the append-only blog publish records file.",
    )
    parser.add_argument(
        "--social-package-records-path",
        type=Path,
        default=SOCIAL_PACKAGE_RECORDS_PATH,
        help="Path to the append-only social package records file.",
    )
    parser.add_argument(
        "--queue-item-records-path",
        type=Path,
        default=QUEUE_ITEM_RECORDS_PATH,
        help="Path to the append-only queue item records file.",
    )
    parser.add_argument(
        "--facebook-publish-records-path",
        type=Path,
        default=FACEBOOK_PUBLISH_RECORDS_PATH,
        help="Path to the append-only Facebook publish records file.",
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
        blog_publish_record = load_latest_blog_publish_record(
            args.blog_publish_id,
            path=args.blog_publish_records_path,
        )
        updated_blog_publish = record_blog_publish_update(
            blog_publish_record,
            update_action=args.action,
            wordpress_post_id=args.wordpress_post_id,
            wordpress_post_url=args.wordpress_post_url,
            schedule_mode=args.schedule_mode,
            schedule_approved_by=args.schedule_approved_by,
            schedule_applied_by=args.schedule_applied_by,
            scheduled_for_blog=args.scheduled_for_blog,
            published_at_blog=args.published_at_blog,
            error_message=args.error,
        )
        append_blog_publish_records([updated_blog_publish], path=args.blog_publish_records_path)

        social_package = None
        try:
            social_package = load_latest_social_package_for_blog_publish(
                updated_blog_publish.blog_publish_id,
                path=args.social_package_records_path,
            )
        except ValueError:
            social_package = None
        facebook_publish_record = None
        if social_package is not None:
            try:
                facebook_publish_record = load_latest_facebook_publish_for_social_package(
                    social_package.social_package_id,
                    path=args.facebook_publish_records_path,
                )
            except ValueError:
                facebook_publish_record = None

        blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
            updated_blog_publish,
            social_package_record=social_package,
            facebook_publish_record=facebook_publish_record,
        )
        append_queue_item_records([blog_queue, facebook_queue], path=args.queue_item_records_path)
        append_blog_facebook_mapping_records([mapping], path=args.mapping_records_path)
    except ValueError as exc:
        parser.error(str(exc))

    summary = {
        "blog_publish_id": updated_blog_publish.blog_publish_id,
        "wordpress_status": updated_blog_publish.wordpress_status,
        "schedule_mode": updated_blog_publish.schedule_mode,
        "blog_queue_state": blog_queue.queue_state,
        "facebook_queue_state": facebook_queue.queue_state,
        "mapping_status": mapping.mapping_status,
        "blog_publish_records_path": str(args.blog_publish_records_path),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0
