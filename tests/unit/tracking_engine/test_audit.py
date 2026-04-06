from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from tracking_engine.audit import (
    build_tracking_audit_report,
    record_tracking_normalization_run,
    record_transport_validation_audit,
)
from tracking_engine.models import PublishChainHistorySummary, PublishExceptionSummary


class TrackingAuditTests(unittest.TestCase):
    def test_record_tracking_normalization_run_appends_expected_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_path = Path(temp_dir) / "tracking_audit_records.jsonl"
            history_summary = PublishChainHistorySummary(
                latest_snapshot_at="2026-04-03T12:00:00Z",
                total_chains=4,
                source_family_counts={"editorial_food": 4},
                template_family_counts={"food_fact_article": 4},
                wordpress_status_counts={"published": 4},
                facebook_publish_status_counts={"published": 2},
                chain_status_counts={"published_facebook": 2, "published_blog": 2},
                chains_with_social_package=4,
                chains_with_facebook_publish=2,
                chains_with_confirmed_blog_url=4,
                chains_with_consistency_issues=1,
                chains_with_schedule_alerts=1,
            )
            exception_summary = PublishExceptionSummary(
                total_exception_chains=2,
                failed_chain_count=1,
                partial_chain_count=1,
                consistency_issue_chains=1,
                schedule_alert_chains=1,
                exception_reason_counts={"blog_publish_failed": 1, "facebook_publish_pending": 1},
            )

            record = record_tracking_normalization_run(
                actor_label="operator",
                view_name="all",
                history_summary=history_summary,
                exception_summary=exception_summary,
                audit_records_path=audit_path,
                event_timestamp="2026-04-03T12:30:00Z",
            )

            self.assertEqual(record.event_type, "normalization_run")
            self.assertEqual(record.view_name, "all")
            self.assertEqual(record.total_chains, 4)
            self.assertEqual(record.exception_chain_count, 2)

            summary, records = build_tracking_audit_report(audit_records_path=audit_path)
            self.assertEqual(summary.total_events, 1)
            self.assertEqual(summary.normalization_run_count, 1)
            self.assertEqual(records[0].event_id, record.event_id)

    def test_build_tracking_audit_report_aggregates_normalization_and_validation_events(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_path = Path(temp_dir) / "tracking_audit_records.jsonl"
            history_summary = PublishChainHistorySummary(
                latest_snapshot_at="2026-04-03T12:00:00Z",
                total_chains=1,
                source_family_counts={},
                template_family_counts={},
                wordpress_status_counts={},
                facebook_publish_status_counts={},
                chain_status_counts={},
                chains_with_social_package=0,
                chains_with_facebook_publish=0,
                chains_with_confirmed_blog_url=0,
                chains_with_consistency_issues=0,
                chains_with_schedule_alerts=0,
            )
            exception_summary = PublishExceptionSummary(
                total_exception_chains=0,
                failed_chain_count=0,
                partial_chain_count=0,
                consistency_issue_chains=0,
                schedule_alert_chains=0,
                exception_reason_counts={},
            )

            record_tracking_normalization_run(
                actor_label="operator",
                view_name="ledger",
                history_summary=history_summary,
                exception_summary=exception_summary,
                audit_records_path=audit_path,
                event_timestamp="2026-04-03T12:00:00Z",
            )
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
            record_transport_validation_audit(
                actor_label="operator",
                entity_type="facebook_transport",
                entity_id="123456789",
                event_status="failed",
                event_summary="Facebook transport validation failed.",
                execution_mode="execute",
                config_path="facebook_config.json",
                error_message="auth_failed",
                audit_records_path=audit_path,
                event_timestamp="2026-04-03T12:20:00Z",
            )

            summary, records = build_tracking_audit_report(audit_records_path=audit_path)
            self.assertEqual(summary.total_events, 3)
            self.assertEqual(summary.normalization_run_count, 1)
            self.assertEqual(summary.transport_validation_count, 2)
            self.assertEqual(summary.failed_event_count, 1)
            self.assertEqual(summary.event_type_counts["transport_validation"], 2)
            self.assertEqual(records[0].entity_type, "facebook_transport")


if __name__ == "__main__":
    unittest.main()
