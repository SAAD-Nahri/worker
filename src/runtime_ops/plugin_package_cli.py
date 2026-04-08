from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_ops.plugin_package import (
    DEFAULT_APPROVAL_UI_PACKAGE_PATH,
    DEFAULT_APPROVAL_UI_SOURCE_DIR,
    build_wordpress_plugin_package,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a WordPress plugin zip package for the Content Ops Approval UI."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_APPROVAL_UI_SOURCE_DIR,
        help="Plugin directory that should be zipped.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=DEFAULT_APPROVAL_UI_PACKAGE_PATH,
        help="Zip file path to write.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = build_wordpress_plugin_package(
        source_dir=args.source_dir,
        output_path=args.output_path,
    )
    print(json.dumps(result.to_dict(), sort_keys=True))
    return 0
