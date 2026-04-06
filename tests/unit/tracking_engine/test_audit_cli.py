from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from tracking_engine.audit import record_transport_validation_audit
from tracking_engine.audit_cli import main


class TrackingAuditCliTests(unittest.TestCase):
    def test_tracking_audit_cli_outputs_json_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_path = Path(temp_dir) / "tracking_audit_records.jsonl"
            record_transport_validation_audit(
                actor_label="operator",
                entity_type="wordpress_transport",
                entity_id="https://wordpress.example.com",
                event_status="success",
                event_summary="WordPress transport validation succeeded.",
                execution_mode="execute",
                config_path="wordpress_config.json",
                validated_identity_id="44",
                validated_identity_name="Solo Operator",
                audit_records_path=audit_path,
                event_timestamp="2026-04-03T12:10:00Z",
            )

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(["--audit-records-path", str(audit_path), "--json"])

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue().strip())
            self.assertEqual(payload["summary"]["total_events"], 1)
            self.assertEqual(payload["records"][0]["entity_type"], "wordpress_transport")


if __name__ == "__main__":
    unittest.main()
