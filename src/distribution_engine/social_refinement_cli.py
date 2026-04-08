from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_layer.openai_provider import DEFAULT_OPENAI_PROVIDER_CONFIG_PATH, load_openai_provider_config
from content_engine.storage import DRAFT_RECORDS_PATH, load_latest_draft_record
from distribution_engine.social_refinement import refine_social_package_with_openai
from distribution_engine.storage import (
    BLOG_PUBLISH_RECORDS_PATH,
    SOCIAL_PACKAGE_RECORDS_PATH,
    append_social_package_records,
    load_latest_blog_publish_record,
    load_latest_social_package_record,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate review-safe OpenAI Facebook package variants without changing the selected package."
    )
    parser.add_argument("--social-package-id", required=True, help="Prepared social package identifier to refine.")
    parser.add_argument(
        "--provider",
        required=True,
        choices=("openai",),
        help="Provider used for manual social refinement.",
    )
    parser.add_argument(
        "--openai-config-path",
        type=Path,
        default=DEFAULT_OPENAI_PROVIDER_CONFIG_PATH,
        help="Optional ignored local config path for OpenAI model and timeout settings.",
    )
    parser.add_argument(
        "--desired-variant-count",
        type=int,
        default=2,
        help="Number of OpenAI variants to request. Value is clamped to 1-2.",
    )
    parser.add_argument(
        "--social-package-records-path",
        type=Path,
        default=SOCIAL_PACKAGE_RECORDS_PATH,
        help="Path to the append-only social package records file.",
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
        social_package = load_latest_social_package_record(
            args.social_package_id,
            path=args.social_package_records_path,
        )
        draft = load_latest_draft_record(
            social_package.draft_id,
            path=args.draft_records_path,
        )
        blog_publish_record = None
        if social_package.blog_publish_id:
            blog_publish_record = load_latest_blog_publish_record(
                social_package.blog_publish_id,
                path=args.blog_publish_records_path,
            )
    except ValueError as exc:
        parser.error(str(exc))

    selection_fallback_reason = None
    result = None
    try:
        config = load_openai_provider_config(args.openai_config_path)
    except ValueError as exc:
        selection_fallback_reason = str(exc)
    else:
        result = refine_social_package_with_openai(
            social_package,
            draft,
            config=config,
            blog_publish_record=blog_publish_record,
            desired_variant_count=args.desired_variant_count,
        )
        if result.updated_package is not social_package:
            append_social_package_records([result.updated_package], path=args.social_package_records_path)

    summary = {
        "social_package_id": social_package.social_package_id,
        "provider_requested": args.provider,
        "provider": result.provider_label if result else None,
        "fallback_reason": selection_fallback_reason or (result.fallback_reason if result else None),
        "added_variant_labels": list(result.added_variant_labels) if result else [],
        "selected_variant_label": social_package.selected_variant_label,
        "approval_state": social_package.approval_state,
        "social_package_records_path": str(args.social_package_records_path),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0
