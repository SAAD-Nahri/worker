from __future__ import annotations

import argparse
from pathlib import Path

from source_engine.runtime import archive_runtime_state, build_runtime_reset_plan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safely reset generated runtime state by archiving runtime artifacts.")
    parser.add_argument(
        "--archive-root",
        type=Path,
        default=None,
        help="Optional archive root directory. Defaults to data/archive.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Archive the runtime artifacts. Without this flag the command performs a dry run only.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    plan = build_runtime_reset_plan(archive_root=args.archive_root)

    print("Runtime reset plan")
    print("==================")
    print(f"Archive directory: {plan.archive_dir}")
    if plan.existing_files:
        print("Files to archive:")
        for path in plan.existing_files:
            print(f"  {path}")
    else:
        print("Files to archive: none")

    if plan.missing_files:
        print("Files already missing:")
        for path in plan.missing_files:
            print(f"  {path}")

    if not args.execute:
        print("Mode: dry-run only. Re-run with --execute to archive the files.")
        return 0

    actions = archive_runtime_state(plan)
    print("Actions:")
    if not actions:
        print("  no files archived")
        return 0
    for action in actions:
        print(f"  archived {action['source']} -> {action['destination']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
