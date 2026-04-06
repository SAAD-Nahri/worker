from __future__ import annotations

import io
import json
import shutil
import sys
from contextlib import redirect_stdout
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from distribution_engine.activation_cli import main


class SystemActivationCliTests(unittest.TestCase):
    def test_activation_cli_outputs_json(self) -> None:
        root = ROOT / "tests" / "_tmp_activation_cli_case"
        shutil.rmtree(root, ignore_errors=True)
        root.mkdir(parents=True, exist_ok=True)
        try:
            wordpress_config = root / "wordpress_rest_config.local.json"
            facebook_config = root / "facebook_graph_config.local.json"

            wordpress_config.write_text(
                json.dumps(
                    {
                        "base_url": "https://example.com",
                        "username": "wordpress_username",
                        "application_password": "xxxx xxxx xxxx xxxx xxxx xxxx",
                        "category_id_by_name": {"food-questions": 14},
                        "tag_id_by_name": {"food-storage": 201},
                    }
                ),
                encoding="utf-8",
            )
            facebook_config.write_text(
                json.dumps(
                    {
                        "page_id": "123456789012345",
                        "page_access_token": "EAAB_PLACEHOLDER_REPLACE_LOCALLY",
                    }
                ),
                encoding="utf-8",
            )

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "--wordpress-config-path",
                        str(wordpress_config),
                        "--facebook-config-path",
                        str(facebook_config),
                        "--json",
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue())
            self.assertEqual(payload["summary"]["readiness_signal"], "awaiting_real_credentials")
            self.assertEqual(len(payload["config_statuses"]), 2)
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
