from __future__ import annotations

import argparse
import json
from pathlib import Path

from content_engine.health import build_draft_health_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize current draft health from latest draft snapshots and review history.")
    parser.add_argument("--draft-records-path", type=Path, default=None, help="Optional path to the draft records JSONL file.")
    parser.add_argument("--draft-reviews-path", type=Path, default=None, help="Optional path to the draft reviews JSONL file.")
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    summary, rows = build_draft_health_report(
        draft_records_path=args.draft_records_path,
        draft_reviews_path=args.draft_reviews_path,
    )

    if args.json:
        payload = {
            "summary": summary.to_dict(),
            "rows": [row.to_dict() for row in rows],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print("Draft health summary")
    print("====================")
    print(f"Latest draft snapshot: {summary.latest_snapshot_at or 'none'}")
    print(f"Total drafts: {summary.total_drafts}")
    print(
        "Quality gates: "
        f"pass={summary.quality_gate_counts.get('pass', 0)} "
        f"review_flag={summary.quality_gate_counts.get('review_flag', 0)} "
        f"blocked={summary.quality_gate_counts.get('blocked', 0)}"
    )
    print(
        "Approval states: "
        f"pending_review={summary.approval_state_counts.get('pending_review', 0)} "
        f"approved={summary.approval_state_counts.get('approved', 0)} "
        f"needs_edits={summary.approval_state_counts.get('needs_edits', 0)} "
        f"rejected={summary.approval_state_counts.get('rejected', 0)}"
    )
    print(
        "Coverage: "
        f"headline_variants={summary.drafts_with_headline_variants}/{summary.total_drafts} "
        f"excerpt={summary.drafts_with_excerpt}/{summary.total_drafts} "
        f"ai_enriched={summary.ai_enriched_drafts}/{summary.total_drafts}"
    )
    print(
        "Routing: "
        f"proceed={summary.routing_action_counts.get('proceed', 0)} "
        f"review_only={summary.routing_action_counts.get('review_only', 0)} "
        f"hold_for_reroute={summary.routing_action_counts.get('hold_for_reroute', 0)} "
        f"reject_for_v1={summary.routing_action_counts.get('reject_for_v1', 0)}"
    )
    if summary.top_quality_flags:
        top_flags = ", ".join(f"{flag}({count})" for flag, count in summary.top_quality_flags)
        print(f"Top quality flags: {top_flags}")
    if summary.top_routing_reasons:
        top_reasons = ", ".join(f"{reason}({count})" for reason, count in summary.top_routing_reasons)
        print(f"Top routing reasons: {top_reasons}")

    if not rows:
        print("No draft records available.")
        return 0

    header = (
        f"{'draft_id':<34} {'quality':<11} {'approval':<14} {'risk':<7} "
        f"{'route':<17} {'reviews':>7} {'ai':>3} {'signal':<26}"
    )
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            f"{row.draft_id:<34} {row.quality_gate_status:<11} {row.approval_state:<14} "
            f"{row.derivative_risk_level:<7} {row.routing_action:<17} {row.review_count:>7} {row.ai_assistance_count:>3} "
            f"{row.operator_signal:<26}"
        )
        if row.routing_reasons:
            print(f"{'':<71} routing_reasons: {', '.join(row.routing_reasons)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
