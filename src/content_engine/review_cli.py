from __future__ import annotations

import argparse
import json
from pathlib import Path

from content_engine.review import ALLOWED_REVIEW_OUTCOMES, record_draft_review
from content_engine.storage import (
    DRAFT_RECORDS_PATH,
    DRAFT_REVIEWS_PATH,
    append_draft_records,
    append_draft_review_records,
    load_latest_draft_record,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record a structured review outcome for a draft record.")
    parser.add_argument("--draft-id", required=True, help="Draft identifier to review.")
    parser.add_argument(
        "--outcome",
        required=True,
        choices=sorted(ALLOWED_REVIEW_OUTCOMES),
        help="Review outcome to record.",
    )
    parser.add_argument(
        "--note",
        action="append",
        default=[],
        help="Actionable review note. Repeat for multiple notes.",
    )
    parser.add_argument(
        "--reviewer",
        default="solo_operator",
        help="Reviewer label recorded with the decision.",
    )
    parser.add_argument(
        "--draft-records-path",
        type=Path,
        default=DRAFT_RECORDS_PATH,
        help="Path to the append-only draft records file.",
    )
    parser.add_argument(
        "--draft-reviews-path",
        type=Path,
        default=DRAFT_REVIEWS_PATH,
        help="Path to the append-only draft review log.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    draft = load_latest_draft_record(args.draft_id, args.draft_records_path)
    updated_draft, review_record = record_draft_review(
        draft,
        review_outcome=args.outcome,
        review_notes=args.note,
        reviewer_label=args.reviewer,
    )
    append_draft_records([updated_draft], args.draft_records_path)
    append_draft_review_records([review_record], args.draft_reviews_path)

    summary = {
        "draft_id": updated_draft.draft_id,
        "workflow_state": updated_draft.workflow_state,
        "approval_state": updated_draft.approval_state,
        "review_outcome": review_record.review_outcome,
        "review_notes": list(review_record.review_notes),
        "quality_gate_status": updated_draft.quality_gate_status,
        "derivative_risk_level": updated_draft.derivative_risk_level,
        "draft_records_path": str(args.draft_records_path),
        "draft_reviews_path": str(args.draft_reviews_path),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0
