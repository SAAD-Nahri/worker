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

from source_engine.registry import active_sources, load_source_registry


class RegistryTests(unittest.TestCase):
    def test_load_source_registry(self) -> None:
        payload = [
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
            }
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "registry.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            records = load_source_registry(path)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].source_id, "src_test")

    def test_duplicate_source_id_raises_error(self) -> None:
        payload = [
            {
                "source_id": "src_test",
                "source_name": "Test Source A",
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
            },
            {
                "source_id": "src_test",
                "source_name": "Test Source B",
                "domain": "example-two.com",
                "source_family": "food_editorial",
                "source_type": "rss_plus_fetch",
                "primary_topic_fit": "test fit",
                "active": True,
                "priority_level": "tier_1",
                "rss_feed_url": "https://example-two.com/feed",
                "fetch_method": "rss_discovery_plus_article_fetch",
                "body_extraction_required": True,
                "freshness_pattern": "daily",
                "quality_notes": "ok",
                "risk_notes": "low",
                "created_at": "2026-04-02T00:00:00Z",
                "updated_at": "2026-04-02T00:00:00Z",
            },
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "registry.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate source_id"):
                load_source_registry(path)

    def test_invalid_active_paused_status_raises_error(self) -> None:
        payload = [
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
                "status": "paused",
            }
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "registry.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "cannot be active while status is paused"):
                load_source_registry(path)

    def test_active_sources_excludes_non_intake_statuses(self) -> None:
        payload = [
            {
                "source_id": "src_active",
                "source_name": "Active Source",
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
                "status": "active_primary",
            },
            {
                "source_id": "src_watchlist",
                "source_name": "Watchlist Source",
                "domain": "example-two.com",
                "source_family": "food_editorial",
                "source_type": "rss_plus_fetch",
                "primary_topic_fit": "test fit",
                "active": False,
                "priority_level": "tier_3",
                "rss_feed_url": "https://example-two.com/feed",
                "fetch_method": "rss_discovery_plus_article_fetch",
                "body_extraction_required": True,
                "freshness_pattern": "daily",
                "quality_notes": "ok",
                "risk_notes": "low",
                "created_at": "2026-04-02T00:00:00Z",
                "updated_at": "2026-04-02T00:00:00Z",
                "status": "watchlist",
            },
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "registry.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            records = load_source_registry(path)
        filtered = active_sources(records)
        self.assertEqual([record.source_id for record in filtered], ["src_active"])


if __name__ == "__main__":
    unittest.main()
