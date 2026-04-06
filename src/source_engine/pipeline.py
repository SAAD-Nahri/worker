from __future__ import annotations

from datetime import UTC, datetime
import uuid
from pathlib import Path

from source_engine.dedupe import check_duplicate, load_dedupe_index, save_dedupe_index, update_dedupe_index
from source_engine.fetch.article_fetcher import apply_article_body_result, fetch_article_body, should_fetch_article_body
from source_engine.fetch.rss_fetcher import fetch_feed_entries
from source_engine.logging import summarize_body_extraction, summarize_items
from source_engine.normalize import normalize_source_item
from source_engine.registry import active_sources, load_source_registry
from source_engine.storage import (
    DEDUPE_INDEX_PATH,
    DEFAULT_REGISTRY_PATH,
    append_intake_history,
    append_source_items,
    build_run_record,
    ensure_data_dir,
)


def run_source_intake(
    registry_path: Path | None = None,
    limit_per_source: int | None = None,
    fetch_article_bodies: bool = False,
) -> dict[str, object]:
    ensure_data_dir()
    active_registry_path = registry_path or DEFAULT_REGISTRY_PATH
    records = active_sources(load_source_registry(active_registry_path))
    dedupe_index = load_dedupe_index(DEDUPE_INDEX_PATH)

    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    fetch_results = []
    normalized_items = []

    for record in records:
        fetch_result, entries = fetch_feed_entries(record)
        fetch_results.append(fetch_result)
        selected_entries = entries[:limit_per_source] if limit_per_source else entries
        for entry in selected_entries:
            item = normalize_source_item(record, entry, fetch_result.fetched_at)
            item.run_id = run_id
            dedupe_result = check_duplicate(item, dedupe_index)
            item.dedupe_status = dedupe_result.status
            item.matched_item_id = dedupe_result.matched_item_id
            item.dedupe_reason = dedupe_result.reason
            if should_fetch_article_body(record, item, fetch_article_bodies):
                article_result = fetch_article_body(record, item.canonical_url)
                apply_article_body_result(item, article_result)
            elif fetch_article_bodies and record.body_extraction_required and item.dedupe_status != "unique":
                item.body_extraction_status = "skipped_non_unique"
            normalized_items.append(item)
            if dedupe_result.status == "unique":
                dedupe_index = update_dedupe_index(item, dedupe_index)

    append_source_items(normalized_items)
    save_dedupe_index(DEDUPE_INDEX_PATH, dedupe_index)

    item_counts, dedupe_counts = summarize_items(normalized_items)
    body_extraction_counts = summarize_body_extraction(normalized_items)
    run_record = build_run_record(
        run_id=run_id,
        fetch_results=fetch_results,
        item_counts=item_counts,
        dedupe_counts=dedupe_counts,
        body_extraction_counts=body_extraction_counts,
        registry_path=active_registry_path,
        limit_per_source=limit_per_source,
        total_items=len(normalized_items),
        fetch_article_bodies=fetch_article_bodies,
    )
    append_intake_history(run_record)
    return {
        "run_id": run_id,
        "fetch_results": fetch_results,
        "items": normalized_items,
        "item_counts": item_counts,
        "dedupe_counts": dedupe_counts,
        "body_extraction_counts": body_extraction_counts,
        "registry_path": str(active_registry_path),
    }
