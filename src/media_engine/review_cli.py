from __future__ import annotations

import argparse
import json
from pathlib import Path

from media_engine.review import record_asset_review
from media_engine.storage import (
    ASSET_RECORDS_PATH,
    ASSET_REVIEWS_PATH,
    append_asset_records,
    append_asset_review_records,
    load_latest_asset_record,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review a media asset and append the updated approval state.")
    parser.add_argument("--asset-record-id", required=True, help="asset_record_id to review.")
    parser.add_argument(
        "--review-outcome",
        required=True,
        choices=("approved", "needs_edits", "rejected"),
        help="Approved, needs edits, or rejected.",
    )
    parser.add_argument("--review-note", action="append", default=[], help="Actionable review note. Repeat as needed.")
    parser.add_argument("--reviewer-label", default="solo_operator")
    parser.add_argument("--asset-records-path", type=Path, default=ASSET_RECORDS_PATH)
    parser.add_argument("--asset-reviews-path", type=Path, default=ASSET_REVIEWS_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    asset_record = load_latest_asset_record(args.asset_record_id, path=args.asset_records_path)
    updated_asset, review_record = record_asset_review(
        asset_record,
        review_outcome=args.review_outcome,
        review_notes=args.review_note,
        reviewer_label=args.reviewer_label,
    )
    append_asset_records([updated_asset], path=args.asset_records_path)
    append_asset_review_records([review_record], path=args.asset_reviews_path)
    print(
        json.dumps(
            {
                "asset_record": updated_asset.to_dict(),
                "review_record": review_record.to_dict(),
            },
            sort_keys=True,
        )
    )
    return 0
