from __future__ import annotations

import json
from pathlib import Path

from source_engine.models import SourceRecord
from source_engine.source_status import source_sort_key, status_allows_intake, validate_source_status


REQUIRED_FIELDS = {
    "source_id",
    "source_name",
    "domain",
    "source_family",
    "source_type",
    "primary_topic_fit",
    "active",
    "priority_level",
    "fetch_method",
    "body_extraction_required",
    "freshness_pattern",
    "quality_notes",
    "risk_notes",
    "created_at",
    "updated_at",
}


def load_source_registry(path: Path) -> list[SourceRecord]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Source registry must be a list of source records.")

    records: list[SourceRecord] = []
    seen_source_ids: set[str] = set()
    for index, raw in enumerate(payload, start=1):
        missing = REQUIRED_FIELDS - set(raw)
        if missing:
            raise ValueError(
                f"Source registry record {index} is missing required fields: "
                f"{', '.join(sorted(missing))}"
            )
        source_id = raw.get("source_id", "")
        if source_id in seen_source_ids:
            raise ValueError(f"Source registry contains duplicate source_id: {source_id}")
        seen_source_ids.add(source_id)
        record = SourceRecord(**raw)
        validate_source_status(record)
        records.append(record)
    return records


def active_sources(records: list[SourceRecord]) -> list[SourceRecord]:
    return sorted(
        (record for record in records if status_allows_intake(record)),
        key=source_sort_key,
    )
