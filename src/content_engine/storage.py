from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from content_engine.models import AiAssistanceRecord, DraftRecord, DraftReviewRecord, DraftSection


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
DRAFT_RECORDS_PATH = DATA_DIR / "draft_records.jsonl"
DRAFT_REVIEWS_PATH = DATA_DIR / "draft_reviews.jsonl"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def append_draft_records(records: Iterable[DraftRecord], path: Path = DRAFT_RECORDS_PATH) -> None:
    ensure_data_dir()
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


def append_draft_review_records(
    records: Iterable[DraftReviewRecord],
    path: Path = DRAFT_REVIEWS_PATH,
) -> None:
    ensure_data_dir()
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


def read_jsonl_records(path: Path = DRAFT_RECORDS_PATH) -> list[dict[str, object]]:
    if not path.exists():
        return []

    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            records.append(json.loads(stripped))
    return records


def read_draft_records(path: Path = DRAFT_RECORDS_PATH) -> list[DraftRecord]:
    return [draft_record_from_dict(payload) for payload in read_jsonl_records(path)]


def read_draft_review_records(path: Path = DRAFT_REVIEWS_PATH) -> list[DraftReviewRecord]:
    return [draft_review_record_from_dict(payload) for payload in read_jsonl_records(path)]


def load_latest_draft_record(draft_id: str, path: Path = DRAFT_RECORDS_PATH) -> DraftRecord:
    latest_record: DraftRecord | None = None
    for record in read_draft_records(path):
        if record.draft_id == draft_id:
            latest_record = record
    if latest_record is None:
        raise ValueError(f"Unknown draft_id: {draft_id}")
    return latest_record


def draft_record_from_dict(payload: dict[str, object]) -> DraftRecord:
    normalized = dict(payload)
    normalized["sections"] = [
        DraftSection(**section_payload) for section_payload in normalized.get("sections", [])
    ]
    normalized["ai_assistance_log"] = [
        AiAssistanceRecord(**entry) for entry in normalized.get("ai_assistance_log", [])
    ]
    return DraftRecord(**normalized)


def draft_review_record_from_dict(payload: dict[str, object]) -> DraftReviewRecord:
    normalized = dict(payload)
    normalized["review_notes"] = tuple(normalized.get("review_notes", []))
    return DraftReviewRecord(**normalized)
