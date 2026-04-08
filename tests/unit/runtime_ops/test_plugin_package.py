from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from runtime_ops.plugin_package import build_wordpress_plugin_package
from runtime_ops.plugin_package_cli import main as build_plugin_package_main


class PluginPackageTests(unittest.TestCase):
    def test_build_wordpress_plugin_package_writes_expected_zip_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plugin_dir = root / "content-ops-approval-ui"
            includes_dir = plugin_dir / "includes"
            assets_dir = plugin_dir / "assets"
            includes_dir.mkdir(parents=True)
            assets_dir.mkdir(parents=True)
            (plugin_dir / "content-ops-approval-ui.php").write_text("<?php\n", encoding="utf-8")
            (plugin_dir / "README.md").write_text("# Plugin\n", encoding="utf-8")
            (includes_dir / "class-content-ops-approval-ui.php").write_text("<?php\n", encoding="utf-8")
            (assets_dir / "admin.css").write_text("body{}\n", encoding="utf-8")
            output_path = root / "content-ops-approval-ui.zip"

            result = build_wordpress_plugin_package(
                source_dir=plugin_dir,
                output_path=output_path,
            )

            self.assertTrue(output_path.exists())
            self.assertEqual(result.plugin_slug, "content-ops-approval-ui")
            self.assertEqual(result.file_count, 4)
            self.assertGreater(result.size_bytes, 0)
            self.assertEqual(result.output_path, output_path.resolve())
            self.assertEqual(len(result.sha256), 64)

            with zipfile.ZipFile(output_path, "r") as archive:
                names = sorted(archive.namelist())

            self.assertEqual(
                names,
                [
                    "content-ops-approval-ui/README.md",
                    "content-ops-approval-ui/assets/admin.css",
                    "content-ops-approval-ui/content-ops-approval-ui.php",
                    "content-ops-approval-ui/includes/class-content-ops-approval-ui.php",
                ],
            )

    def test_build_wordpress_plugin_package_rejects_output_inside_source_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plugin_dir = root / "content-ops-approval-ui"
            plugin_dir.mkdir()
            (plugin_dir / "content-ops-approval-ui.php").write_text("<?php\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "must not be created inside the plugin source directory"):
                build_wordpress_plugin_package(
                    source_dir=plugin_dir,
                    output_path=plugin_dir / "content-ops-approval-ui.zip",
                )

    def test_plugin_package_cli_outputs_json_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plugin_dir = root / "content-ops-approval-ui"
            plugin_dir.mkdir()
            (plugin_dir / "content-ops-approval-ui.php").write_text("<?php\n", encoding="utf-8")
            output_path = root / "content-ops-approval-ui.zip"

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = build_plugin_package_main(
                    [
                        "--source-dir",
                        str(plugin_dir),
                        "--output-path",
                        str(output_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            self.assertEqual(payload["plugin_slug"], "content-ops-approval-ui")
            self.assertEqual(payload["output_path"], str(output_path.resolve()))
            self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
