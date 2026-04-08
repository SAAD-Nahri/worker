from __future__ import annotations

import argparse
import json
from pathlib import Path

from media_engine.assets import prepare_asset_record
from media_engine.storage import (
    ASSET_RECORDS_PATH,
    MEDIA_BRIEF_RECORDS_PATH,
    append_asset_records,
    load_latest_media_brief_record,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Register a candidate media asset against an existing media brief.")
    parser.add_argument("--media-brief-id", required=True, help="media_brief_id to attach the asset to.")
    parser.add_argument(
        "--asset-source-kind",
        required=True,
        choices=("owned", "licensed", "ai_generated"),
        help="Tracked provenance class for the asset.",
    )
    parser.add_argument("--provenance-reference", required=True, help="License note, prompt reference, or owned-asset origin.")
    parser.add_argument("--asset-url-or-path", required=True, help="Local path or URL for the selected asset.")
    parser.add_argument("--alt-text", required=True, help="Operator-reviewed alt text for the asset.")
    parser.add_argument("--caption-support-text", default="", help="Optional supporting caption or usage note.")
    parser.add_argument("--media-brief-records-path", type=Path, default=MEDIA_BRIEF_RECORDS_PATH)
    parser.add_argument("--asset-records-path", type=Path, default=ASSET_RECORDS_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    media_brief = load_latest_media_brief_record(args.media_brief_id, path=args.media_brief_records_path)
    asset_record = prepare_asset_record(
        media_brief,
        asset_source_kind=args.asset_source_kind,
        provenance_reference=args.provenance_reference,
        asset_url_or_path=args.asset_url_or_path,
        alt_text=args.alt_text,
        caption_support_text=args.caption_support_text,
    )
    append_asset_records([asset_record], path=args.asset_records_path)
    print(json.dumps(asset_record.to_dict(), sort_keys=True))
    return 0
