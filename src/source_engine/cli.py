from __future__ import annotations

import argparse
from pathlib import Path

from source_engine.logging import print_run_summary
from source_engine.pipeline import run_source_intake


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run source intake for all active registry sources.")
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=None,
        help="Optional path to a source registry JSON file.",
    )
    parser.add_argument(
        "--limit-per-source",
        type=int,
        default=5,
        help="Optional cap on feed entries processed per source for a run.",
    )
    parser.add_argument(
        "--fetch-article-bodies",
        action="store_true",
        help="Fetch article-page bodies for unique items that require body extraction.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    result = run_source_intake(
        registry_path=args.registry_path,
        limit_per_source=args.limit_per_source,
        fetch_article_bodies=args.fetch_article_bodies,
    )
    print(f"Run id: {result['run_id']}")
    print_run_summary(
        result["fetch_results"],
        result["item_counts"],
        result["dedupe_counts"],
        result["body_extraction_counts"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
