from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from distribution_engine.models import (
    BlogFacebookMappingRecord,
    FacebookPublishRecord,
    BlogPublishRecord,
    QueueItemRecord,
    QueueReviewRecord,
    SocialPackageRecord,
    SocialPackageReviewRecord,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
BLOG_PUBLISH_RECORDS_PATH = DATA_DIR / "blog_publish_records.jsonl"
SOCIAL_PACKAGE_RECORDS_PATH = DATA_DIR / "social_package_records.jsonl"
SOCIAL_PACKAGE_REVIEWS_PATH = DATA_DIR / "social_package_reviews.jsonl"
FACEBOOK_PUBLISH_RECORDS_PATH = DATA_DIR / "facebook_publish_records.jsonl"
QUEUE_ITEM_RECORDS_PATH = DATA_DIR / "queue_item_records.jsonl"
QUEUE_REVIEW_RECORDS_PATH = DATA_DIR / "queue_review_records.jsonl"
BLOG_FACEBOOK_MAPPING_RECORDS_PATH = DATA_DIR / "blog_facebook_mapping_records.jsonl"


def append_blog_publish_records(
    records: Iterable[BlogPublishRecord],
    path: Path = BLOG_PUBLISH_RECORDS_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


def append_social_package_records(
    records: Iterable[SocialPackageRecord],
    path: Path = SOCIAL_PACKAGE_RECORDS_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


def append_social_package_review_records(
    records: Iterable[SocialPackageReviewRecord],
    path: Path = SOCIAL_PACKAGE_REVIEWS_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


def append_facebook_publish_records(
    records: Iterable[FacebookPublishRecord],
    path: Path = FACEBOOK_PUBLISH_RECORDS_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


def append_queue_item_records(
    records: Iterable[QueueItemRecord],
    path: Path = QUEUE_ITEM_RECORDS_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


def append_blog_facebook_mapping_records(
    records: Iterable[BlogFacebookMappingRecord],
    path: Path = BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


def append_queue_review_records(
    records: Iterable[QueueReviewRecord],
    path: Path = QUEUE_REVIEW_RECORDS_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


def read_jsonl_records(path: Path = BLOG_PUBLISH_RECORDS_PATH) -> list[dict[str, object]]:
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


def read_blog_publish_records(path: Path = BLOG_PUBLISH_RECORDS_PATH) -> list[BlogPublishRecord]:
    return [blog_publish_record_from_dict(payload) for payload in read_jsonl_records(path)]


def read_social_package_records(path: Path = SOCIAL_PACKAGE_RECORDS_PATH) -> list[SocialPackageRecord]:
    return [social_package_record_from_dict(payload) for payload in read_jsonl_records(path)]


def read_social_package_review_records(
    path: Path = SOCIAL_PACKAGE_REVIEWS_PATH,
) -> list[SocialPackageReviewRecord]:
    return [social_package_review_record_from_dict(payload) for payload in read_jsonl_records(path)]


def read_facebook_publish_records(
    path: Path = FACEBOOK_PUBLISH_RECORDS_PATH,
) -> list[FacebookPublishRecord]:
    return [facebook_publish_record_from_dict(payload) for payload in read_jsonl_records(path)]


def read_queue_item_records(path: Path = QUEUE_ITEM_RECORDS_PATH) -> list[QueueItemRecord]:
    return [queue_item_record_from_dict(payload) for payload in read_jsonl_records(path)]


def read_queue_review_records(path: Path = QUEUE_REVIEW_RECORDS_PATH) -> list[QueueReviewRecord]:
    return [queue_review_record_from_dict(payload) for payload in read_jsonl_records(path)]


def read_blog_facebook_mapping_records(
    path: Path = BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
) -> list[BlogFacebookMappingRecord]:
    return [blog_facebook_mapping_record_from_dict(payload) for payload in read_jsonl_records(path)]


def load_latest_blog_publish_record(
    blog_publish_id: str,
    path: Path = BLOG_PUBLISH_RECORDS_PATH,
) -> BlogPublishRecord:
    latest_record: BlogPublishRecord | None = None
    for record in read_blog_publish_records(path):
        if record.blog_publish_id == blog_publish_id:
            latest_record = record
    if latest_record is None:
        raise ValueError(f"Unknown blog_publish_id: {blog_publish_id}")
    return latest_record


def load_latest_social_package_record(
    social_package_id: str,
    path: Path = SOCIAL_PACKAGE_RECORDS_PATH,
) -> SocialPackageRecord:
    latest_record: SocialPackageRecord | None = None
    for record in read_social_package_records(path):
        if record.social_package_id == social_package_id:
            latest_record = record
    if latest_record is None:
        raise ValueError(f"Unknown social_package_id: {social_package_id}")
    return latest_record


def load_latest_social_package_for_draft(
    draft_id: str,
    path: Path = SOCIAL_PACKAGE_RECORDS_PATH,
) -> SocialPackageRecord:
    latest_record: SocialPackageRecord | None = None
    for record in read_social_package_records(path):
        if record.draft_id == draft_id:
            latest_record = record
    if latest_record is None:
        raise ValueError(f"Unknown social package draft_id: {draft_id}")
    return latest_record


def load_latest_social_package_for_blog_publish(
    blog_publish_id: str,
    path: Path = SOCIAL_PACKAGE_RECORDS_PATH,
) -> SocialPackageRecord:
    latest_record: SocialPackageRecord | None = None
    for record in read_social_package_records(path):
        if record.blog_publish_id == blog_publish_id:
            latest_record = record
    if latest_record is None:
        raise ValueError(f"Unknown social package blog_publish_id: {blog_publish_id}")
    return latest_record


def load_latest_facebook_publish_record(
    facebook_publish_id: str,
    path: Path = FACEBOOK_PUBLISH_RECORDS_PATH,
) -> FacebookPublishRecord:
    latest_record: FacebookPublishRecord | None = None
    for record in read_facebook_publish_records(path):
        if record.facebook_publish_id == facebook_publish_id:
            latest_record = record
    if latest_record is None:
        raise ValueError(f"Unknown facebook_publish_id: {facebook_publish_id}")
    return latest_record


def load_latest_facebook_publish_for_social_package(
    social_package_id: str,
    path: Path = FACEBOOK_PUBLISH_RECORDS_PATH,
) -> FacebookPublishRecord:
    latest_record: FacebookPublishRecord | None = None
    for record in read_facebook_publish_records(path):
        if record.social_package_id == social_package_id:
            latest_record = record
    if latest_record is None:
        raise ValueError(f"Unknown Facebook publish social_package_id: {social_package_id}")
    return latest_record


def load_latest_facebook_publish_for_blog_publish(
    blog_publish_id: str,
    path: Path = FACEBOOK_PUBLISH_RECORDS_PATH,
) -> FacebookPublishRecord:
    latest_record: FacebookPublishRecord | None = None
    for record in read_facebook_publish_records(path):
        if record.blog_publish_id == blog_publish_id:
            latest_record = record
    if latest_record is None:
        raise ValueError(f"Unknown Facebook publish blog_publish_id: {blog_publish_id}")
    return latest_record


def load_latest_queue_item_record(
    queue_item_id: str,
    path: Path = QUEUE_ITEM_RECORDS_PATH,
) -> QueueItemRecord:
    latest_record: QueueItemRecord | None = None
    for record in read_queue_item_records(path):
        if record.queue_item_id == queue_item_id:
            latest_record = record
    if latest_record is None:
        raise ValueError(f"Unknown queue_item_id: {queue_item_id}")
    return latest_record


def load_latest_queue_item_for_blog_publish(
    blog_publish_id: str,
    queue_type: str,
    path: Path = QUEUE_ITEM_RECORDS_PATH,
) -> QueueItemRecord:
    latest_record: QueueItemRecord | None = None
    for record in read_queue_item_records(path):
        if record.blog_publish_id == blog_publish_id and record.queue_type == queue_type:
            latest_record = record
    if latest_record is None:
        raise ValueError(
            f"Unknown queue item for blog_publish_id={blog_publish_id} and queue_type={queue_type}"
        )
    return latest_record


def load_latest_mapping_record(
    mapping_id: str,
    path: Path = BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
) -> BlogFacebookMappingRecord:
    latest_record: BlogFacebookMappingRecord | None = None
    for record in read_blog_facebook_mapping_records(path):
        if record.mapping_id == mapping_id:
            latest_record = record
    if latest_record is None:
        raise ValueError(f"Unknown mapping_id: {mapping_id}")
    return latest_record


def load_latest_mapping_for_blog_publish(
    blog_publish_id: str,
    path: Path = BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
) -> BlogFacebookMappingRecord:
    latest_record: BlogFacebookMappingRecord | None = None
    for record in read_blog_facebook_mapping_records(path):
        if record.blog_publish_id == blog_publish_id:
            latest_record = record
    if latest_record is None:
        raise ValueError(f"Unknown mapping for blog_publish_id: {blog_publish_id}")
    return latest_record


def blog_publish_record_from_dict(payload: dict[str, object]) -> BlogPublishRecord:
    normalized = dict(payload)
    return BlogPublishRecord(**normalized)


def social_package_record_from_dict(payload: dict[str, object]) -> SocialPackageRecord:
    normalized = dict(payload)
    return SocialPackageRecord(**normalized)


def social_package_review_record_from_dict(payload: dict[str, object]) -> SocialPackageReviewRecord:
    normalized = dict(payload)
    review_notes = normalized.get("review_notes")
    if isinstance(review_notes, list):
        normalized["review_notes"] = tuple(str(note) for note in review_notes)
    return SocialPackageReviewRecord(**normalized)


def facebook_publish_record_from_dict(payload: dict[str, object]) -> FacebookPublishRecord:
    normalized = dict(payload)
    return FacebookPublishRecord(**normalized)


def queue_item_record_from_dict(payload: dict[str, object]) -> QueueItemRecord:
    normalized = dict(payload)
    return QueueItemRecord(**normalized)


def queue_review_record_from_dict(payload: dict[str, object]) -> QueueReviewRecord:
    normalized = dict(payload)
    review_notes = normalized.get("review_notes")
    if isinstance(review_notes, list):
        normalized["review_notes"] = tuple(str(note) for note in review_notes)
    return QueueReviewRecord(**normalized)


def blog_facebook_mapping_record_from_dict(payload: dict[str, object]) -> BlogFacebookMappingRecord:
    normalized = dict(payload)
    return BlogFacebookMappingRecord(**normalized)
