from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from distribution_engine.wordpress_validation_cli import main
from distribution_engine.wordpress_transport import WordPressRestTransportError


def _write_config(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "base_url": "https://wordpress.example.com",
                "username": "operator",
                "application_password": "app pass 1234",
                "category_id_by_name": {"food-facts": 7},
                "tag_id_by_name": {"kitchen": 11},
                "timeout_seconds": 12,
            }
        ),
        encoding="utf-8",
    )


class WordPressValidationCliTests(unittest.TestCase):
    def test_wordpress_validation_cli_dry_run_outputs_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "wordpress_config.json"
            _write_config(config_path)

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(["--config-path", str(config_path)])

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            self.assertEqual(payload["execution_mode"], "dry_run")
            self.assertEqual(payload["transport_outcome"], "dry_run")
            self.assertEqual(
                payload["request"]["url"],
                "https://wordpress.example.com/wp-json/wp/v2/users/me?context=edit",
            )

    def test_wordpress_validation_cli_execute_outputs_validated_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "wordpress_config.json"
            _write_config(config_path)

            def _executor(*_args):
                return {
                    "id": 44,
                    "slug": "operator",
                    "name": "Solo Operator",
                    "_response_status_code": 200,
                }

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    ["--config-path", str(config_path), "--execute"],
                    request_executor=_executor,
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            self.assertEqual(payload["transport_outcome"], "success")
            self.assertEqual(payload["execution_result"]["validated_user_id"], "44")
            self.assertEqual(payload["execution_result"]["validated_user_name"], "Solo Operator")

    def test_wordpress_validation_cli_execute_can_record_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "wordpress_config.json"
            audit_path = Path(temp_dir) / "tracking_audit_records.jsonl"
            _write_config(config_path)

            def _executor(*_args):
                return {
                    "id": 44,
                    "slug": "operator",
                    "name": "Solo Operator",
                    "_response_status_code": 200,
                }

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--config-path",
                        str(config_path),
                        "--execute",
                        "--record-audit",
                        "--audit-records-path",
                        str(audit_path),
                    ],
                    request_executor=_executor,
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            self.assertEqual(payload["audit_record"]["event_type"], "transport_validation")
            self.assertEqual(payload["audit_record"]["entity_type"], "wordpress_transport")

    def test_wordpress_validation_cli_execute_returns_nonzero_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "wordpress_config.json"
            _write_config(config_path)

            def _executor(*_args):
                raise WordPressRestTransportError("auth_failed")

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(["--config-path", str(config_path), "--execute"], request_executor=_executor)

            self.assertEqual(exit_code, 1)
            payload = json.loads(buffer.getvalue().strip())
            self.assertEqual(payload["transport_outcome"], "failed")
            self.assertEqual(payload["error"], "auth_failed")


if __name__ == "__main__":
    unittest.main()
