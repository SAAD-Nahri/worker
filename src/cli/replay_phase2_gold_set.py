from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.gold_set import (
    DEFAULT_GOLD_SET_MANIFEST_PATH,
    build_gold_set_summary,
    evaluate_gold_set_cases,
    load_gold_set_cases,
)
from source_engine.storage import SOURCE_ITEMS_PATH


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Replay the fixed Phase 2 gold-set acceptance pack.")
    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=DEFAULT_GOLD_SET_MANIFEST_PATH,
        help="Path to the Phase 2 gold-set manifest.",
    )
    parser.add_argument(
        "--source-items-path",
        type=Path,
        default=SOURCE_ITEMS_PATH,
        help="Path to the source-item snapshot used for live gold-set cases.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the full machine-readable summary instead of the human-readable report.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    cases = load_gold_set_cases(path=args.manifest_path)
    results = evaluate_gold_set_cases(cases, source_items_path=args.source_items_path)
    summary = build_gold_set_summary(results)

    if args.json:
        print(json.dumps(summary, sort_keys=True))
    else:
        print(f"Phase 2 gold set: {summary['passed']}/{summary['case_count']} passed")
        for result in results:
            status = "PASS" if result.passed else "FAIL"
            issues = ", ".join(result.issues) if result.issues else "-"
            flags = ", ".join(result.quality_flags) if result.quality_flags else "-"
            print(
                f"{status} | {result.case_id} | routing={result.routing_action} | "
                f"quality={result.quality_gate_status or '-'} | flags={flags} | issues={issues}"
            )

    return 0 if summary["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
