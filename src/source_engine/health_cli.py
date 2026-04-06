from __future__ import annotations

import argparse
import json
from pathlib import Path

from source_engine.health import build_source_health_rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize current source health from the registry, latest run, and source decisions.")
    parser.add_argument("--registry-path", type=Path, default=None, help="Optional path to the source registry JSON file.")
    parser.add_argument("--intake-history-path", type=Path, default=None, help="Optional path to the intake history JSONL file.")
    parser.add_argument("--source-items-path", type=Path, default=None, help="Optional path to the source items JSONL file.")
    parser.add_argument("--source-decisions-path", type=Path, default=None, help="Optional path to the source decisions JSONL file.")
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    latest_run_id, rows = build_source_health_rows(
        registry_path=args.registry_path,
        intake_history_path=args.intake_history_path,
        source_items_path=args.source_items_path,
        source_decisions_path=args.source_decisions_path,
    )

    if args.json:
        payload = {
            "latest_run_id": latest_run_id,
            "rows": [row.to_dict() for row in rows],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print("Source health summary")
    print("=====================")
    print(f"Latest run id: {latest_run_id or 'none'}")
    if not rows:
        print("No source records available.")
        return 0

    header = (
        f"{'source_id':<24} {'status':<18} {'fetch':<8} {'proc':>4} {'uniq':>4} "
        f"{'dup':>4} {'body':>4} {'signal':<24}"
    )
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            f"{row.source_id:<24} {row.registry_status:<18} {row.latest_fetch_status:<8} "
            f"{row.latest_processed_items:>4} {row.latest_unique_items:>4} "
            f"{row.latest_duplicate_items:>4} {row.latest_body_fetched:>4} "
            f"{row.review_signal:<24}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
