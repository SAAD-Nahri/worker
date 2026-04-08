from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_ops.backup import BACKUPS_DIR, REPO_ROOT, build_runtime_backup_plan, create_runtime_backup


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a runtime backup bundle for data/ and optional local config.")
    parser.add_argument(
        "--backup-root",
        type=Path,
        default=BACKUPS_DIR,
        help="Directory that will receive the runtime backup zip bundle.",
    )
    parser.add_argument(
        "--include-config",
        action="store_true",
        help="Include config/*.local.json files in the bundle. Use only when the destination is already secure.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repo root whose data/ and optional config/ directories should be bundled.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    plan = build_runtime_backup_plan(
        backup_root=args.backup_root,
        include_config=args.include_config,
        repo_root=args.repo_root,
    )
    result = create_runtime_backup(plan)
    print(json.dumps(result.to_dict(), sort_keys=True))
    return 0
