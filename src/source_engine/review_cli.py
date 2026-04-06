from __future__ import annotations

import argparse
from pathlib import Path

from source_engine.review import record_source_review_decision


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record a source review decision and optionally apply it to the registry.")
    parser.add_argument("--source-id", required=True, help="Source identifier to review.")
    parser.add_argument("--reviewed-items", required=True, type=int, help="Number of items reviewed for this source.")
    parser.add_argument("--strong-candidates", required=True, type=int, help="Number of strong candidates found in the review window.")
    parser.add_argument(
        "--weak-or-repetitive-items",
        required=True,
        type=int,
        help="Number of weak or repetitive items observed in the review window.",
    )
    parser.add_argument("--fetch-failures", type=int, default=0, help="Number of recent fetch failures associated with the source.")
    parser.add_argument("--reviewer-notes", default=None, help="Optional operator notes to store with the decision.")
    parser.add_argument("--final-status", default=None, help="Optional manual override for the final source status.")
    parser.add_argument(
        "--apply-registry-update",
        action="store_true",
        help="Apply the final status back to the source registry after recording the decision.",
    )
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=None,
        help="Optional path to a source registry JSON file.",
    )
    parser.add_argument(
        "--decision-path",
        type=Path,
        default=None,
        help="Optional path for the source decision JSONL log.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    decision = record_source_review_decision(
        source_id=args.source_id,
        reviewed_items=args.reviewed_items,
        strong_candidates=args.strong_candidates,
        weak_or_repetitive_items=args.weak_or_repetitive_items,
        fetch_failures=args.fetch_failures,
        reviewer_notes=args.reviewer_notes,
        final_status=args.final_status,
        apply_registry_update=args.apply_registry_update,
        registry_path=args.registry_path,
        decision_path=args.decision_path,
    )
    print(f"Decision id: {decision.decision_id}")
    print(f"Source: {decision.source_id} ({decision.source_name})")
    print(f"Current status: {decision.current_status}")
    print(f"Recommended status: {decision.recommended_status}")
    print(f"Final status: {decision.final_status}")
    print(f"Applied to registry: {decision.applied_to_registry}")
    print(f"Reason: {decision.recommendation_reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
