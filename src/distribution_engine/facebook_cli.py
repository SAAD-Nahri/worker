from __future__ import annotations

import argparse
import json
from pathlib import Path

from content_engine.storage import DRAFT_RECORDS_PATH, load_latest_draft_record
from distribution_engine.facebook import prepare_social_package_record
from distribution_engine.storage import (
    BLOG_PUBLISH_RECORDS_PATH,
    SOCIAL_PACKAGE_RECORDS_PATH,
    append_social_package_records,
    load_latest_blog_publish_record,
    load_latest_social_package_for_draft,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare a Facebook-ready social package record from an approved draft."
    )
    parser.add_argument("--draft-id", required=True, help="Approved draft identifier to package for Facebook.")
    parser.add_argument(
        "--blog-publish-id",
        help="Optional blog publish identifier to link a Facebook package to a prepared WordPress record.",
    )
    parser.add_argument(
        "--allow-repackage",
        action="store_true",
        help="Allow a new primary package record even when one already exists for the draft.",
    )
    parser.add_argument(
        "--draft-records-path",
        type=Path,
        default=DRAFT_RECORDS_PATH,
        help="Path to the append-only draft records file.",
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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        draft = load_latest_draft_record(args.draft_id, path=args.draft_records_path)
        blog_publish_record = None
        if args.blog_publish_id:
            blog_publish_record = load_latest_blog_publish_record(
                args.blog_publish_id,
                path=args.blog_publish_records_path,
            )
        if not args.allow_repackage:
            try:
                existing_package = load_latest_social_package_for_draft(
                    draft.draft_id,
                    path=args.social_package_records_path,
                )
            except ValueError:
                existing_package = None
            if existing_package is not None:
                parser.error(
                    "A primary social package already exists for this draft. "
                    "Use --allow-repackage only when an explicit replacement is intended."
                )
        record = prepare_social_package_record(draft, blog_publish_record=blog_publish_record)
        append_social_package_records([record], path=args.social_package_records_path)
    except ValueError as exc:
        parser.error(str(exc))

    summary = {
        "social_package_id": record.social_package_id,
        "draft_id": record.draft_id,
        "blog_publish_id": record.blog_publish_id,
        "package_template_id": record.package_template_id,
        "comment_template_id": record.comment_template_id,
        "approval_state": record.approval_state,
        "social_package_records_path": str(args.social_package_records_path),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0
