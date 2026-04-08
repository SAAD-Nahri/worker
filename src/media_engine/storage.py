from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from media_engine.models import AssetRecord, AssetReviewRecord, MediaBriefRecord


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
MEDIA_BRIEF_RECORDS_PATH = DATA_DIR / "media_brief_records.jsonl"
ASSET_RECORDS_PATH = DATA_DIR / "asset_records.jsonl"
ASSET_REVIEWS_PATH = DATA_DIR / "asset_review_records.jsonl"


def append_media_brief_records(
    records: Iterable[MediaBriefRecord],
    path: Path = MEDIA_BRIEF_RECORDS_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


def append_asset_records(records: Iterable[AssetRecord], path: Path = ASSET_RECORDS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


def append_asset_review_records(
    records: Iterable[AssetReviewRecord],
    path: Path = ASSET_REVIEWS_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


def read_jsonl_records(path: Path) -> list[dict[str, object]]:
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


def read_media_brief_records(path: Path = MEDIA_BRIEF_RECORDS_PATH) -> list[MediaBriefRecord]:
    return [media_brief_record_from_dict(payload) for payload in read_jsonl_records(path)]


def read_asset_records(path: Path = ASSET_RECORDS_PATH) -> list[AssetRecord]:
    return [asset_record_from_dict(payload) for payload in read_jsonl_records(path)]


def read_asset_review_records(path: Path = ASSET_REVIEWS_PATH) -> list[AssetReviewRecord]:
    return [asset_review_record_from_dict(payload) for payload in read_jsonl_records(path)]


def load_latest_media_brief_record(
    media_brief_id: str,
    path: Path = MEDIA_BRIEF_RECORDS_PATH,
) -> MediaBriefRecord:
    latest_record: MediaBriefRecord | None = None
    for record in read_media_brief_records(path):
        if record.media_brief_id == media_brief_id:
            latest_record = record
    if latest_record is None:
        raise ValueError(f"Unknown media_brief_id: {media_brief_id}")
    return latest_record


def load_latest_media_brief_for_draft(
    draft_id: str,
    path: Path = MEDIA_BRIEF_RECORDS_PATH,
) -> MediaBriefRecord:
    latest_record: MediaBriefRecord | None = None
    for record in read_media_brief_records(path):
        if record.draft_id == draft_id:
            latest_record = record
    if latest_record is None:
        raise ValueError(f"Unknown media brief draft_id: {draft_id}")
    return latest_record


def load_latest_asset_record(asset_record_id: str, path: Path = ASSET_RECORDS_PATH) -> AssetRecord:
    latest_record: AssetRecord | None = None
    for record in read_asset_records(path):
        if record.asset_record_id == asset_record_id:
            latest_record = record
    if latest_record is None:
        raise ValueError(f"Unknown asset_record_id: {asset_record_id}")
    return latest_record


def load_latest_asset_for_draft(draft_id: str, path: Path = ASSET_RECORDS_PATH) -> AssetRecord:
    latest_record: AssetRecord | None = None
    for record in read_asset_records(path):
        if record.draft_id == draft_id:
            latest_record = record
    if latest_record is None:
        raise ValueError(f"Unknown asset draft_id: {draft_id}")
    return latest_record


def load_latest_asset_for_blog_publish(
    blog_publish_id: str,
    path: Path = ASSET_RECORDS_PATH,
) -> AssetRecord:
    latest_record: AssetRecord | None = None
    for record in read_asset_records(path):
        if record.blog_publish_id == blog_publish_id:
            latest_record = record
    if latest_record is None:
        raise ValueError(f"Unknown asset blog_publish_id: {blog_publish_id}")
    return latest_record


def load_latest_asset_for_social_package(
    social_package_id: str,
    path: Path = ASSET_RECORDS_PATH,
) -> AssetRecord:
    latest_record: AssetRecord | None = None
    for record in read_asset_records(path):
        if record.social_package_id == social_package_id:
            latest_record = record
    if latest_record is None:
        raise ValueError(f"Unknown asset social_package_id: {social_package_id}")
    return latest_record


def media_brief_record_from_dict(payload: dict[str, object]) -> MediaBriefRecord:
    normalized = dict(payload)
    return MediaBriefRecord(**normalized)


def asset_record_from_dict(payload: dict[str, object]) -> AssetRecord:
    normalized = dict(payload)
    return AssetRecord(**normalized)


def asset_review_record_from_dict(payload: dict[str, object]) -> AssetReviewRecord:
    normalized = dict(payload)
    review_notes = normalized.get("review_notes")
    if isinstance(review_notes, list):
        normalized["review_notes"] = tuple(str(note) for note in review_notes)
    return AssetReviewRecord(**normalized)
