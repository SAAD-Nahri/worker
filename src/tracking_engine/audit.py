from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from tracking_engine.models import (
    PublishChainHistorySummary,
    PublishExceptionSummary,
    TrackingAuditRecord,
    TrackingAuditSummary,
)
from tracking_engine.storage import TRACKING_AUDIT_RECORDS_PATH, append_tracking_audit_records, read_tracking_audit_records


def record_tracking_normalization_run(
    *,
    actor_label: str,
    view_name: str,
    history_summary: PublishChainHistorySummary,
    exception_summary: PublishExceptionSummary,
    audit_records_path: Path | None = TRACKING_AUDIT_RECORDS_PATH,
    event_timestamp: str | None = None,
) -> TrackingAuditRecord:
    record = TrackingAuditRecord(
        event_id=_new_event_id(),
        event_type="normalization_run",
        entity_type="publish_chain_history",
        entity_id=view_name,
        chain_id=None,
        event_status="success",
        event_summary=f"Generated publish-chain tracking view '{view_name}'.",
        event_timestamp=event_timestamp or _utc_now_timestamp(),
        actor_label=actor_label,
        view_name=view_name,
        execution_mode="on_demand",
        total_chains=history_summary.total_chains,
        exception_chain_count=exception_summary.total_exception_chains,
        consistency_issue_chains=history_summary.chains_with_consistency_issues,
        schedule_alert_chains=history_summary.chains_with_schedule_alerts,
        latest_snapshot_at=history_summary.latest_snapshot_at,
    )
    append_tracking_audit_records([record], path=audit_records_path or TRACKING_AUDIT_RECORDS_PATH)
    return record


def record_transport_validation_audit(
    *,
    actor_label: str,
    entity_type: str,
    entity_id: str,
    event_status: str,
    event_summary: str,
    execution_mode: str,
    config_path: str,
    validated_identity_id: str | None = None,
    validated_identity_name: str | None = None,
    error_message: str | None = None,
    audit_records_path: Path | None = TRACKING_AUDIT_RECORDS_PATH,
    event_timestamp: str | None = None,
) -> TrackingAuditRecord:
    record = TrackingAuditRecord(
        event_id=_new_event_id(),
        event_type="transport_validation",
        entity_type=entity_type,
        entity_id=entity_id,
        chain_id=None,
        event_status=event_status,
        event_summary=event_summary,
        event_timestamp=event_timestamp or _utc_now_timestamp(),
        actor_label=actor_label,
        execution_mode=execution_mode,
        config_path=config_path,
        validated_identity_id=validated_identity_id,
        validated_identity_name=validated_identity_name,
        error_message=error_message,
    )
    append_tracking_audit_records([record], path=audit_records_path or TRACKING_AUDIT_RECORDS_PATH)
    return record


def build_tracking_audit_report(
    audit_records_path: Path | None = TRACKING_AUDIT_RECORDS_PATH,
) -> tuple[TrackingAuditSummary, list[TrackingAuditRecord]]:
    records = read_tracking_audit_records(audit_records_path or TRACKING_AUDIT_RECORDS_PATH)
    records.sort(key=lambda record: (record.event_timestamp, record.event_id), reverse=True)
    summary = TrackingAuditSummary(
        latest_event_at=records[0].event_timestamp if records else None,
        total_events=len(records),
        event_type_counts=dict(Counter(record.event_type for record in records)),
        event_status_counts=dict(Counter(record.event_status for record in records)),
        entity_type_counts=dict(Counter(record.entity_type for record in records)),
        normalization_run_count=sum(1 for record in records if record.event_type == "normalization_run"),
        transport_validation_count=sum(1 for record in records if record.event_type == "transport_validation"),
        failed_event_count=sum(1 for record in records if record.event_status == "failed"),
    )
    return summary, records


def _new_event_id() -> str:
    return f"taudit_{uuid4().hex[:12]}"


def _utc_now_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
