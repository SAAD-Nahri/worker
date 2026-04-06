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

from source_engine.health import build_source_health_rows


class HealthTests(unittest.TestCase):
    def test_build_source_health_rows_combines_registry_run_and_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            registry_path = temp_root / "registry.json"
            intake_history_path = temp_root / "intake_history.jsonl"
            source_items_path = temp_root / "source_items.jsonl"
            source_decisions_path = temp_root / "source_decisions.jsonl"

            registry_payload = [
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
            registry_path.write_text(json.dumps(registry_payload), encoding="utf-8")
            intake_history_path.write_text(
                json.dumps(
                    {
                        "run_id": "run-1",
                        "sources": [
                            {
                                "source_id": "src_test",
                                "status": "ok",
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            source_items_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "run_id": "run-1",
                                "source_id": "src_test",
                                "dedupe_status": "unique",
                                "body_extraction_status": "fetched",
                            }
                        ),
                        json.dumps(
                            {
                                "run_id": "run-1",
                                "source_id": "src_test",
                                "dedupe_status": "exact_duplicate",
                                "body_extraction_status": "skipped_non_unique",
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            source_decisions_path.write_text(
                json.dumps(
                    {
                        "source_id": "src_test",
                        "reviewed_at": "2026-04-02T19:00:00+00:00",
                        "final_status": "active_secondary",
                        "recommendation_reason": "status_unchanged",
                        "applied_to_registry": True,
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            latest_run_id, rows = build_source_health_rows(
                registry_path=registry_path,
                intake_history_path=intake_history_path,
                source_items_path=source_items_path,
                source_decisions_path=source_decisions_path,
            )

            self.assertEqual(latest_run_id, "run-1")
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertEqual(row.latest_fetch_status, "ok")
            self.assertEqual(row.latest_processed_items, 2)
            self.assertEqual(row.latest_unique_items, 1)
            self.assertEqual(row.latest_duplicate_items, 1)
            self.assertEqual(row.latest_body_fetched, 1)
            self.assertEqual(row.review_signal, "stable")

    def test_build_source_health_rows_flags_unapplied_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            registry_path = temp_root / "registry.json"
            intake_history_path = temp_root / "intake_history.jsonl"
            source_items_path = temp_root / "source_items.jsonl"
            source_decisions_path = temp_root / "source_decisions.jsonl"

            registry_path.write_text(
                json.dumps(
                    [
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
                ),
                encoding="utf-8",
            )
            intake_history_path.write_text("", encoding="utf-8")
            source_items_path.write_text("", encoding="utf-8")
            source_decisions_path.write_text(
                json.dumps(
                    {
                        "source_id": "src_test",
                        "reviewed_at": "2026-04-02T19:00:00+00:00",
                        "final_status": "paused",
                        "recommendation_reason": "mostly_weak_or_repetitive_items",
                        "applied_to_registry": False,
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            _, rows = build_source_health_rows(
                registry_path=registry_path,
                intake_history_path=intake_history_path,
                source_items_path=source_items_path,
                source_decisions_path=source_decisions_path,
            )

            self.assertEqual(rows[0].review_signal, "decision_not_applied")

    def test_build_source_health_rows_flags_manual_only_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            registry_path = temp_root / "registry.json"
            intake_history_path = temp_root / "intake_history.jsonl"
            source_items_path = temp_root / "source_items.jsonl"
            source_decisions_path = temp_root / "source_decisions.jsonl"

            registry_path.write_text(
                json.dumps(
                    [
                        {
                            "source_id": "src_test",
                            "source_name": "Test Source",
                            "domain": "example.com",
                            "source_family": "food_editorial",
                            "source_type": "selective_scrape",
                            "primary_topic_fit": "test fit",
                            "active": True,
                            "priority_level": "tier_1",
                            "rss_feed_url": None,
                            "fetch_method": "manual_selective_scrape",
                            "body_extraction_required": False,
                            "freshness_pattern": "daily",
                            "quality_notes": "ok",
                            "risk_notes": "low",
                            "created_at": "2026-04-02T00:00:00Z",
                            "updated_at": "2026-04-02T00:00:00Z",
                            "status": "active_selective",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            intake_history_path.write_text(
                json.dumps(
                    {
                        "run_id": "run-1",
                        "sources": [
                            {
                                "source_id": "src_test",
                                "status": "manual_only",
                                "fallback_action": "manual_selective_scrape_review",
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            source_items_path.write_text("", encoding="utf-8")
            source_decisions_path.write_text("", encoding="utf-8")

            _, rows = build_source_health_rows(
                registry_path=registry_path,
                intake_history_path=intake_history_path,
                source_items_path=source_items_path,
                source_decisions_path=source_decisions_path,
            )

            self.assertEqual(rows[0].latest_fallback_action, "manual_selective_scrape_review")
            self.assertEqual(rows[0].review_signal, "manual_source_mode")

    def test_build_source_health_rows_flags_degraded_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            registry_path = temp_root / "registry.json"
            intake_history_path = temp_root / "intake_history.jsonl"
            source_items_path = temp_root / "source_items.jsonl"
            source_decisions_path = temp_root / "source_decisions.jsonl"

            registry_path.write_text(
                json.dumps(
                    [
                        {
                            "source_id": "src_test",
                            "source_name": "Test Source",
                            "domain": "example.com",
                            "source_family": "food_editorial",
                            "source_type": "rss_plus_fetch",
                            "primary_topic_fit": "test fit",
                            "active": True,
                            "priority_level": "tier_1",
                            "rss_feed_url": None,
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
                ),
                encoding="utf-8",
            )
            intake_history_path.write_text(
                json.dumps(
                    {
                        "run_id": "run-1",
                        "sources": [
                            {
                                "source_id": "src_test",
                                "status": "degraded",
                                "fallback_action": "manual_source_review",
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            source_items_path.write_text("", encoding="utf-8")
            source_decisions_path.write_text("", encoding="utf-8")

            _, rows = build_source_health_rows(
                registry_path=registry_path,
                intake_history_path=intake_history_path,
                source_items_path=source_items_path,
                source_decisions_path=source_decisions_path,
            )

            self.assertEqual(rows[0].review_signal, "fallback_review_required")


if __name__ == "__main__":
    unittest.main()
