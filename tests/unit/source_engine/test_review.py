from __future__ import annotations

import json
import sys
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from source_engine.review import record_source_review_decision


REGISTRY_PAYLOAD = [
    {
        "source_id": "src_test",
        "source_name": "Test Source",
        "domain": "example.com",
        "source_family": "food_editorial",
        "source_type": "rss_plus_fetch",
        "primary_topic_fit": "test fit",
        "active": True,
        "priority_level": "tier_1",
        "rss_feed_url": "https://example.com/feed",
        "fetch_method": "rss_discovery_plus_article_fetch",
        "body_extraction_required": True,
        "freshness_pattern": "daily",
        "quality_notes": "ok",
        "risk_notes": "low",
        "created_at": "2026-04-02T00:00:00Z",
        "updated_at": "2026-04-02T00:00:00Z",
        "status": "active_secondary",
    }
]


class ReviewTests(unittest.TestCase):
    def test_record_source_review_decision_logs_recommendation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            registry_path = Path(temp_dir) / "registry.json"
            decision_path = Path(temp_dir) / "source_decisions.jsonl"
            registry_path.write_text(json.dumps(REGISTRY_PAYLOAD), encoding="utf-8")

            decision = record_source_review_decision(
                source_id="src_test",
                reviewed_items=4,
                strong_candidates=0,
                weak_or_repetitive_items=1,
                registry_path=registry_path,
                decision_path=decision_path,
            )

            self.assertEqual(decision.recommended_status, "downgraded")
            logged = decision_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(logged), 1)
            payload = json.loads(logged[0])
            self.assertEqual(payload["source_id"], "src_test")
            self.assertEqual(payload["final_status"], "downgraded")

    def test_record_source_review_decision_can_apply_registry_update(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            registry_path = Path(temp_dir) / "registry.json"
            decision_path = Path(temp_dir) / "source_decisions.jsonl"
            registry_path.write_text(json.dumps(REGISTRY_PAYLOAD), encoding="utf-8")

            decision = record_source_review_decision(
                source_id="src_test",
                reviewed_items=4,
                strong_candidates=0,
                weak_or_repetitive_items=4,
                reviewer_notes="Repeated low-value recipe drift.",
                apply_registry_update=True,
                registry_path=registry_path,
                decision_path=decision_path,
            )

            self.assertEqual(decision.final_status, "paused")
            updated_payload = json.loads(registry_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_payload[0]["status"], "paused")
            self.assertFalse(updated_payload[0]["active"])
            self.assertEqual(updated_payload[0]["last_review_notes"], "Repeated low-value recipe drift.")


if __name__ == "__main__":
    unittest.main()
