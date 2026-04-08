from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from runtime_ops.backup import (
    build_runtime_backup_plan,
    create_runtime_backup,
    read_runtime_backup_manifest,
    restore_runtime_backup,
)
from runtime_ops.backup_cli import main as create_backup_main
from runtime_ops.restore_cli import main as restore_backup_main


class RuntimeBackupTests(unittest.TestCase):
    def test_create_runtime_backup_writes_bundle_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            config_dir = root / "config"
            backup_dir = root / "backups"
            data_dir.mkdir()
            config_dir.mkdir()
            source_items = data_dir / "source_items.jsonl"
            source_items.write_text('{"item_id":"1"}\n', encoding="utf-8")
            wordpress_config = config_dir / "wordpress_rest_config.local.json"
            wordpress_config.write_text('{"base_url":"https://example.com"}', encoding="utf-8")

            plan = build_runtime_backup_plan(
                backup_root=backup_dir,
                artifact_paths=[source_items, data_dir / "draft_records.jsonl"],
                include_config=True,
                config_paths=[wordpress_config, config_dir / "operator_api.local.json"],
                repo_root=root,
            )
            result = create_runtime_backup(plan)

            self.assertTrue(result.bundle_path.exists())
            manifest = read_runtime_backup_manifest(result.bundle_path)
            self.assertEqual(manifest["data_files"], ["data/source_items.jsonl"])
            self.assertEqual(manifest["missing_data_files"], ["data/draft_records.jsonl"])
            self.assertEqual(manifest["config_files"], ["config/wordpress_rest_config.local.json"])
            self.assertEqual(manifest["missing_config_files"], ["config/operator_api.local.json"])

    def test_restore_runtime_backup_dry_run_reports_actions_without_writing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            data_dir.mkdir()
            artifact = data_dir / "source_items.jsonl"
            artifact.write_text("payload", encoding="utf-8")
            backup_dir = root / "backups"
            plan = build_runtime_backup_plan(
                backup_root=backup_dir,
                artifact_paths=[artifact],
                repo_root=root,
            )
            result = create_runtime_backup(plan)

            target_root = root / "restore_target"
            actions = restore_runtime_backup(
                result.bundle_path,
                target_root=target_root,
                dry_run=True,
            )

            self.assertEqual(len(actions), 1)
            self.assertEqual(actions[0].archive_member, "data/source_items.jsonl")
            self.assertFalse((target_root / "data" / "source_items.jsonl").exists())

    def test_restore_runtime_backup_writes_files_and_rejects_overwrite_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            config_dir = root / "config"
            data_dir.mkdir()
            config_dir.mkdir()
            artifact = data_dir / "source_items.jsonl"
            artifact.write_text("payload", encoding="utf-8")
            openai_config = config_dir / "openai_provider_config.local.json"
            openai_config.write_text('{"model":"gpt-5.4-mini"}', encoding="utf-8")
            backup_dir = root / "backups"
            plan = build_runtime_backup_plan(
                backup_root=backup_dir,
                artifact_paths=[artifact],
                include_config=True,
                config_paths=[openai_config],
                repo_root=root,
            )
            result = create_runtime_backup(plan)

            target_root = root / "restore_target"
            actions = restore_runtime_backup(
                result.bundle_path,
                target_root=target_root,
                restore_config=True,
            )

            self.assertEqual(len(actions), 2)
            self.assertEqual((target_root / "data" / "source_items.jsonl").read_text(encoding="utf-8"), "payload")
            self.assertIn("gpt-5.4-mini", (target_root / "config" / "openai_provider_config.local.json").read_text(encoding="utf-8"))

            with self.assertRaisesRegex(ValueError, "already exists"):
                restore_runtime_backup(
                    result.bundle_path,
                    target_root=target_root,
                    restore_config=True,
                )

            overwrite_actions = restore_runtime_backup(
                result.bundle_path,
                target_root=target_root,
                restore_config=True,
                allow_overwrite=True,
            )
            self.assertEqual(len(overwrite_actions), 2)

    def test_create_runtime_backup_cli_outputs_json_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            data_dir.mkdir()
            artifact = data_dir / "source_items.jsonl"
            artifact.write_text("payload", encoding="utf-8")
            backup_dir = root / "backups"

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = create_backup_main(
                    [
                        "--backup-root",
                        str(backup_dir),
                        "--repo-root",
                        str(root),
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            self.assertTrue(payload["backup_path"].endswith(".zip"))

    def test_restore_runtime_backup_cli_dry_run_outputs_json_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            data_dir.mkdir()
            artifact = data_dir / "source_items.jsonl"
            artifact.write_text("payload", encoding="utf-8")
            backup_dir = root / "backups"
            plan = build_runtime_backup_plan(
                backup_root=backup_dir,
                artifact_paths=[artifact],
                repo_root=root,
            )
            result = create_runtime_backup(plan)

            target_root = root / "restore_target"
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = restore_backup_main(
                    [
                        "--backup-path",
                        str(result.bundle_path),
                        "--target-root",
                        str(target_root),
                        "--dry-run",
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["action_count"], 1)
            self.assertFalse((target_root / "data" / "source_items.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
