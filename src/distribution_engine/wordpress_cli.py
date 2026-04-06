from __future__ import annotations

import argparse
import json
from pathlib import Path

from content_engine.storage import DRAFT_RECORDS_PATH, load_latest_draft_record
from distribution_engine.storage import BLOG_PUBLISH_RECORDS_PATH, append_blog_publish_records
from distribution_engine.wordpress import ALLOWED_PUBLISH_INTENTS, prepare_blog_publish_record


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare a WordPress-ready publish record from an approved draft.")
    parser.add_argument("--draft-id", required=True, help="Approved draft identifier to prepare for WordPress.")
    parser.add_argument(
        "--publish-intent",
        default="draft",
        choices=sorted(ALLOWED_PUBLISH_INTENTS),
        help="Initial WordPress publish intent for the prepared record.",
    )
    parser.add_argument(
        "--allow-non-pass-quality",
        action="store_true",
        help="Allow explicit preparation from an approved draft whose quality status is not 'pass'.",
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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        draft = load_latest_draft_record(args.draft_id, path=args.draft_records_path)
        record = prepare_blog_publish_record(
            draft,
            publish_intent=args.publish_intent,
            allow_non_pass_quality=args.allow_non_pass_quality,
        )
        append_blog_publish_records([record], path=args.blog_publish_records_path)
    except ValueError as exc:
        parser.error(str(exc))

    summary = {
        "blog_publish_id": record.blog_publish_id,
        "draft_id": record.draft_id,
        "wordpress_slug": record.wordpress_slug,
        "wordpress_status": record.wordpress_status,
        "publish_intent": record.publish_intent,
        "blog_publish_records_path": str(args.blog_publish_records_path),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0
