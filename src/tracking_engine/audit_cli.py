from __future__ import annotations

import argparse
import json
from pathlib import Path

from tracking_engine.audit import build_tracking_audit_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize Phase 4 tracking audit records."
    )
    parser.add_argument("--audit-records-path", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    summary, records = build_tracking_audit_report(
        audit_records_path=args.audit_records_path,
    )

    if args.json:
        print(
            json.dumps(
                {
                    "summary": summary.to_dict(),
                    "records": [record.to_dict() for record in records],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    print("Tracking audit summary")
    print("======================")
    print(f"Latest event: {summary.latest_event_at or 'none'}")
    print(f"Total events: {summary.total_events}")
    print(
        "Types: "
        f"normalization_run={summary.normalization_run_count} "
        f"transport_validation={summary.transport_validation_count}"
    )
    print(
        "Statuses: "
        + _format_counts(summary.event_status_counts)
    )
    print(
        "Entity types: "
        + _format_counts(summary.entity_type_counts)
    )
    if not records:
        print("No tracking audit records available.")
        return 0

    header = (
        f"{'event_id':<20} {'event_type':<22} {'entity_type':<22} "
        f"{'status':<10} {'timestamp':<21} {'actor':<14}"
    )
    print(header)
    print("-" * len(header))
    for record in records[:20]:
        print(
            f"{record.event_id:<20} {record.event_type:<22} {record.entity_type:<22} "
            f"{record.event_status:<10} {record.event_timestamp:<21} {record.actor_label:<14}"
        )
        print(f"{'':<20} summary={record.event_summary}")
        if record.error_message:
            print(f"{'':<20} error={record.error_message}")
    return 0


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(
        f"{key}({count})"
        for key, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    )
