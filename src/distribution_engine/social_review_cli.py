from __future__ import annotations

import argparse
import json
from pathlib import Path

from distribution_engine.review import ALLOWED_SOCIAL_REVIEW_OUTCOMES, record_social_package_review
from distribution_engine.storage import (
    BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
    BLOG_PUBLISH_RECORDS_PATH,
    FACEBOOK_PUBLISH_RECORDS_PATH,
    QUEUE_ITEM_RECORDS_PATH,
    SOCIAL_PACKAGE_RECORDS_PATH,
    SOCIAL_PACKAGE_REVIEWS_PATH,
    append_blog_facebook_mapping_records,
    append_queue_item_records,
    append_social_package_records,
    append_social_package_review_records,
    load_latest_blog_publish_record,
    load_latest_facebook_publish_for_social_package,
    load_latest_social_package_record,
)
from distribution_engine.workflow import prepare_distribution_linkage_records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review a prepared social package and record the approval outcome.")
    parser.add_argument("--social-package-id", required=True, help="Prepared social package identifier to review.")
    parser.add_argument(
        "--outcome",
        required=True,
        choices=sorted(ALLOWED_SOCIAL_REVIEW_OUTCOMES),
        help="Review outcome for the selected social package.",
    )
    parser.add_argument(
        "--note",
        action="append",
        default=[],
        help="Actionable review note. Repeat for multiple notes.",
    )
    parser.add_argument(
        "--social-package-records-path",
        type=Path,
        default=SOCIAL_PACKAGE_RECORDS_PATH,
        help="Path to the append-only social package records file.",
    )
    parser.add_argument(
        "--social-package-reviews-path",
        type=Path,
        default=SOCIAL_PACKAGE_REVIEWS_PATH,
        help="Path to the append-only social package review records file.",
    )
    parser.add_argument(
        "--blog-publish-records-path",
        type=Path,
        default=BLOG_PUBLISH_RECORDS_PATH,
        help="Path to the append-only blog publish records file.",
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
        social_package = load_latest_social_package_record(
            args.social_package_id,
            path=args.social_package_records_path,
        )
        updated_package, review_record = record_social_package_review(
            social_package,
            review_outcome=args.outcome,
            review_notes=args.note,
        )
        append_social_package_records([updated_package], path=args.social_package_records_path)
        append_social_package_review_records([review_record], path=args.social_package_reviews_path)

        blog_queue = None
        facebook_queue = None
        mapping = None
        if updated_package.blog_publish_id:
            blog_publish_record = load_latest_blog_publish_record(
                updated_package.blog_publish_id,
                path=args.blog_publish_records_path,
            )
            facebook_publish_record = None
            try:
                facebook_publish_record = load_latest_facebook_publish_for_social_package(
                    updated_package.social_package_id,
                    path=args.facebook_publish_records_path,
                )
            except ValueError:
                facebook_publish_record = None
            blog_queue, facebook_queue, mapping = prepare_distribution_linkage_records(
                blog_publish_record,
                social_package_record=updated_package,
                facebook_publish_record=facebook_publish_record,
            )
            append_queue_item_records([blog_queue, facebook_queue], path=args.queue_item_records_path)
            append_blog_facebook_mapping_records([mapping], path=args.mapping_records_path)
    except ValueError as exc:
        parser.error(str(exc))

    summary = {
        "social_package_id": updated_package.social_package_id,
        "approval_state": updated_package.approval_state,
        "review_id": review_record.review_id,
        "facebook_queue_state": facebook_queue.queue_state if facebook_queue else None,
        "mapping_status": mapping.mapping_status if mapping else None,
        "social_package_reviews_path": str(args.social_package_reviews_path),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0
