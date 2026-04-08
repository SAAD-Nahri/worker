from __future__ import annotations

import argparse
import json
from pathlib import Path

from content_engine.storage import DRAFT_RECORDS_PATH, load_latest_draft_record
from distribution_engine.storage import (
    BLOG_PUBLISH_RECORDS_PATH,
    SOCIAL_PACKAGE_RECORDS_PATH,
    load_latest_blog_publish_record,
    load_latest_social_package_record,
)
from media_engine.briefs import prepare_media_brief_record
from media_engine.storage import MEDIA_BRIEF_RECORDS_PATH, append_media_brief_records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a media brief from an approved draft.")
    parser.add_argument("--draft-id", required=True, help="Approved draft_id to turn into a media brief.")
    parser.add_argument(
        "--intended-usage",
        default="blog_and_facebook",
        choices=("blog_featured_image", "facebook_link_post_image", "blog_and_facebook"),
        help="How the first asset is expected to be used.",
    )
    parser.add_argument("--blog-publish-id", help="Optional linked blog_publish_id.")
    parser.add_argument("--social-package-id", help="Optional linked social_package_id.")
    parser.add_argument("--draft-records-path", type=Path, default=DRAFT_RECORDS_PATH)
    parser.add_argument("--blog-publish-records-path", type=Path, default=BLOG_PUBLISH_RECORDS_PATH)
    parser.add_argument("--social-package-records-path", type=Path, default=SOCIAL_PACKAGE_RECORDS_PATH)
    parser.add_argument("--media-brief-records-path", type=Path, default=MEDIA_BRIEF_RECORDS_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    draft = load_latest_draft_record(args.draft_id, path=args.draft_records_path)
    blog_publish = (
        load_latest_blog_publish_record(args.blog_publish_id, path=args.blog_publish_records_path)
        if args.blog_publish_id
        else None
    )
    social_package = (
        load_latest_social_package_record(args.social_package_id, path=args.social_package_records_path)
        if args.social_package_id
        else None
    )
    brief_record = prepare_media_brief_record(
        draft,
        blog_publish_record=blog_publish,
        social_package_record=social_package,
        intended_usage=args.intended_usage,
    )
    append_media_brief_records([brief_record], path=args.media_brief_records_path)
    print(json.dumps(brief_record.to_dict(), sort_keys=True))
    return 0
