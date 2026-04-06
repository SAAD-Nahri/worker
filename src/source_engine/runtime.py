from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
import shutil

from content_engine.storage import DRAFT_RECORDS_PATH, DRAFT_REVIEWS_PATH
from distribution_engine.storage import (
    BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
    BLOG_PUBLISH_RECORDS_PATH,
    FACEBOOK_PUBLISH_RECORDS_PATH,
    QUEUE_ITEM_RECORDS_PATH,
    QUEUE_REVIEW_RECORDS_PATH,
    SOCIAL_PACKAGE_RECORDS_PATH,
    SOCIAL_PACKAGE_REVIEWS_PATH,
)
from source_engine.storage import (
    ARCHIVE_DIR,
    DATA_DIR,
    DEDUPE_INDEX_PATH,
    INTAKE_HISTORY_PATH,
    SOURCE_DECISIONS_PATH,
    SOURCE_ITEMS_PATH,
)
from tracking_engine.storage import TRACKING_AUDIT_RECORDS_PATH


@dataclass(frozen=True)
class RuntimeResetPlan:
    archive_dir: Path
    existing_files: list[Path]
    missing_files: list[Path]


RUNTIME_ARTIFACT_PATHS = (
    SOURCE_ITEMS_PATH,
    INTAKE_HISTORY_PATH,
    DEDUPE_INDEX_PATH,
    SOURCE_DECISIONS_PATH,
    DRAFT_RECORDS_PATH,
    DRAFT_REVIEWS_PATH,
    BLOG_PUBLISH_RECORDS_PATH,
    SOCIAL_PACKAGE_RECORDS_PATH,
    SOCIAL_PACKAGE_REVIEWS_PATH,
    FACEBOOK_PUBLISH_RECORDS_PATH,
    QUEUE_ITEM_RECORDS_PATH,
    QUEUE_REVIEW_RECORDS_PATH,
    BLOG_FACEBOOK_MAPPING_RECORDS_PATH,
    TRACKING_AUDIT_RECORDS_PATH,
)


def build_runtime_reset_plan(
    artifact_paths: list[Path] | tuple[Path, ...] | None = None,
    archive_root: Path | None = None,
    data_dir: Path | None = None,
) -> RuntimeResetPlan:
    active_paths = list(artifact_paths or RUNTIME_ARTIFACT_PATHS)
    allowed_data_dir = data_dir or DATA_DIR
    for path in active_paths:
        _assert_within_data_dir(path, allowed_data_dir)

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    root = archive_root or ARCHIVE_DIR
    archive_dir = root / timestamp
    existing_files = [path for path in active_paths if path.exists()]
    missing_files = [path for path in active_paths if not path.exists()]
    return RuntimeResetPlan(
        archive_dir=archive_dir,
        existing_files=existing_files,
        missing_files=missing_files,
    )


def archive_runtime_state(plan: RuntimeResetPlan) -> list[dict[str, str]]:
    if not plan.existing_files:
        return []

    plan.archive_dir.mkdir(parents=True, exist_ok=True)
    actions: list[dict[str, str]] = []
    for source_path in plan.existing_files:
        destination = plan.archive_dir / source_path.name
        shutil.move(str(source_path), str(destination))
        actions.append(
            {
                "action": "archived",
                "source": str(source_path),
                "destination": str(destination),
            }
        )
    return actions


def _assert_within_data_dir(path: Path, data_dir: Path) -> None:
    resolved_path = path.resolve()
    resolved_data_dir = data_dir.resolve()
    if resolved_data_dir not in (resolved_path, *resolved_path.parents):
        raise ValueError(f"Runtime reset path is outside the data directory: {path}")
