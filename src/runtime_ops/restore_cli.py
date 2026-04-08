from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_ops.backup import REPO_ROOT, restore_runtime_backup


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Restore runtime backup contents into a repo working copy.")
    parser.add_argument("--backup-path", type=Path, required=True, help="Path to the runtime backup zip bundle.")
    parser.add_argument(
        "--target-root",
        type=Path,
        default=REPO_ROOT,
        help="Repo root that should receive restored data/ and optional config/ files.",
    )
    parser.add_argument(
        "--restore-config",
        action="store_true",
        help="Also restore config/*.local.json members from the bundle.",
    )
    parser.add_argument(
        "--allow-overwrite",
        action="store_true",
        help="Allow restoring over existing files in the target working copy.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview restore actions without writing any files.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    actions = restore_runtime_backup(
        args.backup_path,
        target_root=args.target_root,
        restore_config=args.restore_config,
        allow_overwrite=args.allow_overwrite,
        dry_run=args.dry_run,
    )
    print(
        json.dumps(
            {
                "backup_path": str(args.backup_path),
                "target_root": str(args.target_root),
                "restore_config": args.restore_config,
                "allow_overwrite": args.allow_overwrite,
                "dry_run": args.dry_run,
                "action_count": len(actions),
                "actions": [action.to_dict() for action in actions],
            },
            sort_keys=True,
        )
    )
    return 0
