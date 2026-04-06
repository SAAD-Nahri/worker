from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from source_engine.storage import DATA_DIR, ensure_data_dir, read_jsonl_records
from tracking_engine.models import TrackingAuditRecord


TRACKING_AUDIT_RECORDS_PATH = DATA_DIR / "tracking_audit_records.jsonl"


def append_tracking_audit_records(
    records: Iterable[TrackingAuditRecord],
    path: Path = TRACKING_AUDIT_RECORDS_PATH,
) -> None:
    ensure_data_dir()
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


def read_tracking_audit_records(path: Path = TRACKING_AUDIT_RECORDS_PATH) -> list[TrackingAuditRecord]:
    return [TrackingAuditRecord(**record) for record in read_jsonl_records(path)]
