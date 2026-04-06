from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from source_engine.models import FetchResult, SourceDecisionRecord, SourceItem


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
DEFAULT_REGISTRY_PATH = DATA_DIR / "source_registry.json"
SOURCE_ITEMS_PATH = DATA_DIR / "source_items.jsonl"
INTAKE_HISTORY_PATH = DATA_DIR / "intake_history.jsonl"
DEDUPE_INDEX_PATH = DATA_DIR / "dedupe_index.json"
SOURCE_DECISIONS_PATH = DATA_DIR / "source_decisions.jsonl"
ARCHIVE_DIR = DATA_DIR / "archive"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def write_registry(path: Path, records: list[dict[str, object]]) -> None:
    ensure_data_dir()
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def append_source_items(items: Iterable[SourceItem]) -> None:
    ensure_data_dir()
    with SOURCE_ITEMS_PATH.open("a", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item.to_dict(), sort_keys=True) + "\n")


def append_intake_history(run_record: dict[str, object]) -> None:
    ensure_data_dir()
    with INTAKE_HISTORY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(run_record, sort_keys=True) + "\n")


def append_source_decisions(decisions: Iterable[SourceDecisionRecord], path: Path = SOURCE_DECISIONS_PATH) -> None:
    ensure_data_dir()
    with path.open("a", encoding="utf-8") as handle:
        for decision in decisions:
            handle.write(json.dumps(decision.to_dict(), sort_keys=True) + "\n")


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


def read_source_items(path: Path = SOURCE_ITEMS_PATH) -> list[SourceItem]:
    return [SourceItem(**record) for record in read_jsonl_records(path)]


def load_latest_source_item(item_id: str, path: Path = SOURCE_ITEMS_PATH) -> SourceItem:
    latest_item: SourceItem | None = None
    for item in read_source_items(path):
        if item.item_id == item_id:
            latest_item = item
    if latest_item is None:
        raise ValueError(f"Unknown source item_id: {item_id}")
    return latest_item


def build_run_record(
    run_id: str,
    fetch_results: list[FetchResult],
    item_counts: dict[str, int],
    dedupe_counts: dict[str, int],
    body_extraction_counts: dict[str, int],
    registry_path: Path,
    limit_per_source: int | None,
    total_items: int,
    fetch_article_bodies: bool,
) -> dict[str, object]:
    return {
        "run_id": run_id,
        "source_count": len(fetch_results),
        "total_items": total_items,
        "registry_path": str(registry_path),
        "limit_per_source": limit_per_source,
        "fetch_article_bodies": fetch_article_bodies,
        "sources": [result.to_dict() for result in fetch_results],
        "item_counts": item_counts,
        "dedupe_counts": dedupe_counts,
        "body_extraction_counts": body_extraction_counts,
    }
