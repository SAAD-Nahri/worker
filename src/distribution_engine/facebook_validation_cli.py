from __future__ import annotations

import argparse
import json
from pathlib import Path

from distribution_engine.facebook_transport import (
    FacebookGraphTransportError,
    FacebookValidationRequestExecutor,
    load_facebook_graph_config,
    validate_facebook_graph_transport,
)
from tracking_engine.audit import record_transport_validation_audit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview or execute a Facebook Graph transport validation using the operator config."
    )
    parser.add_argument(
        "--config-path",
        type=Path,
        required=True,
        help="Path to the operator-provided Facebook Graph config JSON file.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the remote validation request. Without this flag the command returns a dry-run preview only.",
    )
    parser.add_argument(
        "--record-audit",
        action="store_true",
        help="Append an audit record for a real execute-mode transport validation.",
    )
    parser.add_argument(
        "--actor-label",
        default="operator",
        help="Actor label to store when --record-audit is used.",
    )
    parser.add_argument(
        "--audit-records-path",
        type=Path,
        default=None,
        help="Optional override path for tracking audit records.",
    )
    return parser


def main(argv: list[str] | None = None, request_executor: FacebookValidationRequestExecutor | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = load_facebook_graph_config(args.config_path)
    except ValueError as exc:
        parser.error(str(exc))
    if args.record_audit and not args.execute:
        parser.error("--record-audit is only allowed with --execute for real validation runs.")

    try:
        result = validate_facebook_graph_transport(
            config,
            execute=args.execute,
            request_executor=request_executor,
        )
    except FacebookGraphTransportError as exc:
        payload = {
            "execution_mode": "execute",
            "transport_outcome": "failed",
            "config_path": str(args.config_path),
            "error": str(exc),
        }
        if args.record_audit:
            audit_record = record_transport_validation_audit(
                actor_label=args.actor_label,
                entity_type="facebook_transport",
                entity_id=config.page_id,
                event_status="failed",
                event_summary=f"Facebook transport validation failed for page {config.page_id}.",
                execution_mode="execute",
                config_path=str(args.config_path),
                error_message=str(exc),
                audit_records_path=args.audit_records_path,
            )
            payload["audit_record"] = audit_record.to_dict()
        print(json.dumps(payload, sort_keys=True))
        return 1

    summary = result.to_summary_dict()
    summary["transport_outcome"] = "success" if args.execute else "dry_run"
    summary["config_path"] = str(args.config_path)
    if args.record_audit:
        execution_result = result.execution_result
        audit_record = record_transport_validation_audit(
            actor_label=args.actor_label,
            entity_type="facebook_transport",
            entity_id=config.page_id,
            event_status="success",
            event_summary=f"Facebook transport validation succeeded for page {config.page_id}.",
            execution_mode="execute",
            config_path=str(args.config_path),
            validated_identity_id=execution_result.validated_page_id if execution_result else None,
            validated_identity_name=execution_result.validated_page_name if execution_result else None,
            audit_records_path=args.audit_records_path,
        )
        summary["audit_record"] = audit_record.to_dict()
    print(json.dumps(summary, sort_keys=True))
    return 0
