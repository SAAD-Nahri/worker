from __future__ import annotations

import argparse
import json
from pathlib import Path

from distribution_engine.storage import (
    BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
    BLOG_PUBLISH_RECORDS_PATH,
    QUEUE_ITEM_RECORDS_PATH,
    SOCIAL_PACKAGE_RECORDS_PATH,
    append_blog_facebook_mapping_records,
    append_queue_item_records,
    load_latest_blog_publish_record,
    load_latest_mapping_for_blog_publish,
    load_latest_queue_item_for_blog_publish,
    load_latest_social_package_record,
)
from distribution_engine.workflow import (
    prepare_distribution_linkage_records,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare initial Phase 3 queue and mapping records from a blog publish record."
    )
    parser.add_argument("--blog-publish-id", required=True, help="Blog publish identifier to link into queue state.")
    parser.add_argument(
        "--social-package-id",
        help="Optional social package identifier to connect to the blog publish record.",
    )
    parser.add_argument(
        "--allow-refresh",
        action="store_true",
        help="Allow new append-only queue and mapping snapshots even when current records already exist.",
    )
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
        social_package_record = None
        if args.social_package_id:
            social_package_record = load_latest_social_package_record(
                args.social_package_id,
                path=args.social_package_records_path,
            )
        if not args.allow_refresh:
            _guard_against_existing_linkage(args.blog_publish_id, args.queue_item_records_path, args.mapping_records_path)
        blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
            blog_publish_record,
            social_package_record=social_package_record,
        )
        append_queue_item_records([blog_queue, facebook_queue], path=args.queue_item_records_path)
        append_blog_facebook_mapping_records([mapping], path=args.mapping_records_path)
    except ValueError as exc:
        parser.error(str(exc))

    summary = {
        "blog_publish_id": blog_publish_record.blog_publish_id,
        "social_package_id": social_package_record.social_package_id if social_package_record else None,
        "blog_queue_item_id": blog_queue.queue_item_id,
        "blog_queue_state": blog_queue.queue_state,
        "facebook_queue_item_id": facebook_queue.queue_item_id,
        "facebook_queue_state": facebook_queue.queue_state,
        "mapping_id": mapping.mapping_id,
        "mapping_status": mapping.mapping_status,
        "queue_item_records_path": str(args.queue_item_records_path),
        "mapping_records_path": str(args.mapping_records_path),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


def _guard_against_existing_linkage(
    blog_publish_id: str,
    queue_item_records_path: Path,
    mapping_records_path: Path,
) -> None:
    existing_signals: list[str] = []
    try:
        load_latest_queue_item_for_blog_publish(
            blog_publish_id,
            queue_type="blog_publish",
            path=queue_item_records_path,
        )
        existing_signals.append("blog queue")
    except ValueError:
        pass
    try:
        load_latest_queue_item_for_blog_publish(
            blog_publish_id,
            queue_type="facebook_publish",
            path=queue_item_records_path,
        )
        existing_signals.append("facebook queue")
    except ValueError:
        pass
    try:
        load_latest_mapping_for_blog_publish(
            blog_publish_id,
            path=mapping_records_path,
        )
        existing_signals.append("mapping")
    except ValueError:
        pass

    if existing_signals:
        raise ValueError(
            "Initial linkage already exists for this blog_publish_id. "
            "Use --allow-refresh only when an explicit replacement snapshot is intended."
        )
