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

from distribution_engine.facebook_validation_cli import main


def _write_config(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "page_id": "123456789",
                "page_access_token": "page-token-123",
                "api_version": "v24.0",
                "timeout_seconds": 15,
            }
        ),
        encoding="utf-8",
    )


class FacebookValidationCliTests(unittest.TestCase):
    def test_facebook_validation_cli_dry_run_outputs_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "facebook_config.json"
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
                "https://graph.facebook.com/v24.0/123456789?fields=id,name",
            )

    def test_facebook_validation_cli_execute_outputs_validated_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "facebook_config.json"
            _write_config(config_path)

            def _executor(*_args):
                return {
                    "id": "123456789",
                    "name": "Food Facts Page",
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
            self.assertEqual(payload["execution_result"]["validated_page_id"], "123456789")
            self.assertEqual(payload["execution_result"]["validated_page_name"], "Food Facts Page")

    def test_facebook_validation_cli_execute_can_record_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "facebook_config.json"
            audit_path = Path(temp_dir) / "tracking_audit_records.jsonl"
            _write_config(config_path)

            def _executor(*_args):
                return {
                    "id": "123456789",
                    "name": "Food Facts Page",
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
            self.assertEqual(payload["audit_record"]["entity_type"], "facebook_transport")


if __name__ == "__main__":
    unittest.main()
